
from flask import (
    Flask, render_template, request, jsonify, send_file,
    Response
)
import sqlite3
import io
import os
from datetime import datetime, date

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "database.db")


# ---------- BANCO DE DADOS ----------

def conectar():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def iniciar_banco():
    with conectar() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            turma TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            parentesco TEXT NOT NULL,
            telefone TEXT,
            foto BLOB
        );

        CREATE TABLE IF NOT EXISTS autorizacoes (
            pessoa_id INTEGER NOT NULL,
            aluno_id INTEGER NOT NULL,
            valido_ate TEXT,
            bloqueado INTEGER DEFAULT 0,
            PRIMARY KEY (pessoa_id, aluno_id),
            FOREIGN KEY (pessoa_id) REFERENCES pessoas(id)
                ON DELETE CASCADE,
            FOREIGN KEY (aluno_id) REFERENCES alunos(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS saidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pessoa_id INTEGER NOT NULL,
            aluno_id INTEGER NOT NULL,
            horario TEXT NOT NULL,
            FOREIGN KEY (pessoa_id) REFERENCES pessoas(id),
            FOREIGN KEY (aluno_id) REFERENCES alunos(id)
        );
        """)


def erro(msg, codigo=400):
    return jsonify({"erro": msg}), codigo


def dados_pessoa(foto=True):
    arquivo = request.files.get("foto")
    imagem = arquivo.read() if arquivo and arquivo.filename else None

    return (
        request.form.get("nome", "").strip(),
        request.form.get("parentesco", "").strip(),
        request.form.get("telefone", "").strip(),
        imagem
    )


# ---------- INTERFACE ----------

@app.route("/")
def inicio():
    return render_template("index.html")


# ---------- ALUNOS ----------

@app.route("/api/alunos", methods=["GET", "POST"])
def alunos():
    with conectar() as con:
        if request.method == "GET":
            rows = con.execute(
                "SELECT * FROM alunos ORDER BY nome"
            ).fetchall()
            return jsonify([dict(r) for r in rows])

        d = request.get_json(silent=True) or {}
        nome = str(d.get("nome", "")).strip()
        turma = str(d.get("turma", "")).strip()

        if not nome or not turma:
            return erro("Informe nome e turma.")

        con.execute(
            "INSERT INTO alunos (nome, turma) VALUES (?, ?)",
            (nome, turma)
        )
        return jsonify({"msg": "Aluno cadastrado."})


@app.route("/api/alunos/<int:id>", methods=["PUT", "DELETE"])
def aluno_item(id):
    with conectar() as con:
        if request.method == "DELETE":
            con.execute("DELETE FROM alunos WHERE id = ?", (id,))
            return jsonify({"msg": "Aluno excluído."})

        d = request.get_json(silent=True) or {}
        nome = str(d.get("nome", "")).strip()
        turma = str(d.get("turma", "")).strip()

        if not nome or not turma:
            return erro("Informe nome e turma.")

        cur = con.execute(
            "UPDATE alunos SET nome=?, turma=? WHERE id=?",
            (nome, turma, id)
        )
        if cur.rowcount == 0:
            return erro("Aluno não encontrado.", 404)

        return jsonify({"msg": "Aluno atualizado."})


# ---------- RESPONSÁVEIS ----------

@app.route("/api/pessoas", methods=["GET", "POST"])
def pessoas():
    with conectar() as con:
        if request.method == "GET":
            rows = con.execute("""
                SELECT id, nome, parentesco, telefone
                FROM pessoas ORDER BY nome
            """).fetchall()
            return jsonify([dict(r) for r in rows])

        nome, parentesco, telefone, foto = dados_pessoa()

        if not nome or not parentesco:
            return erro("Informe nome e parentesco.")

        if not foto:
            return erro("Envie uma foto do responsável.")

        con.execute("""
            INSERT INTO pessoas (nome, parentesco, telefone, foto)
            VALUES (?, ?, ?, ?)
        """, (nome, parentesco, telefone, foto))

        return jsonify({"msg": "Responsável cadastrado."})


@app.route("/api/pessoas/<int:id>", methods=["PUT", "DELETE"])
def pessoa_item(id):
    with conectar() as con:
        if request.method == "DELETE":
            con.execute("DELETE FROM pessoas WHERE id=?", (id,))
            return jsonify({"msg": "Responsável excluído."})

        nome, parentesco, telefone, foto = dados_pessoa()

        if not nome or not parentesco:
            return erro("Informe nome e parentesco.")

        if foto:
            con.execute("""
                UPDATE pessoas
                SET nome=?, parentesco=?, telefone=?, foto=?
                WHERE id=?
            """, (nome, parentesco, telefone, foto, id))
        else:
            con.execute("""
                UPDATE pessoas
                SET nome=?, parentesco=?, telefone=?
                WHERE id=?
            """, (nome, parentesco, telefone, id))

        return jsonify({"msg": "Responsável atualizado."})


@app.route("/fotos/<int:id>")
def foto_pessoa(id):
    with conectar() as con:
        row = con.execute(
            "SELECT foto FROM pessoas WHERE id=?", (id,)
        ).fetchone()

    if not row or not row["foto"]:
        return "", 404

    return send_file(
        io.BytesIO(row["foto"]),
        mimetype="image/jpeg"
    )


# ---------- AUTORIZAÇÕES ----------

@app.route("/api/autorizacoes", methods=["GET", "POST"])
def autorizacoes():
    with conectar() as con:
        if request.method == "GET":
            rows = con.execute("""
                SELECT a.pessoa_id, a.aluno_id,
                       a.valido_ate, a.bloqueado,
                       p.nome AS pessoa,
                       al.nome AS aluno,
                       al.turma
                FROM autorizacoes a
                JOIN pessoas p ON p.id = a.pessoa_id
                JOIN alunos al ON al.id = a.aluno_id
                ORDER BY p.nome, al.nome
            """).fetchall()

            resultado = []
            for r in rows:
                item = dict(r)
                if item["bloqueado"]:
                    item["situacao"] = "BLOQUEADO"
                elif (item["valido_ate"] and
                      item["valido_ate"] < date.today().isoformat()):
                    item["situacao"] = "EXPIRADA"
                else:
                    item["situacao"] = "AUTORIZADO"
                resultado.append(item)

            return jsonify(resultado)

        d = request.get_json(silent=True) or {}

        try:
            pessoa_id = int(d["pessoa_id"])
            aluno_id = int(d["aluno_id"])
        except (KeyError, ValueError, TypeError):
            return erro("Selecione responsável e aluno.")

        valido = d.get("valido_ate") or None
        bloqueado = 1 if d.get("bloqueado") else 0

        con.execute("""
            INSERT INTO autorizacoes
            (pessoa_id, aluno_id, valido_ate, bloqueado)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(pessoa_id, aluno_id)
            DO UPDATE SET
                valido_ate=excluded.valido_ate,
                bloqueado=excluded.bloqueado
        """, (pessoa_id, aluno_id, valido, bloqueado))

        return jsonify({"msg": "Autorização salva."})


@app.route("/api/autorizacoes/<int:pessoa_id>/<int:aluno_id>",
           methods=["DELETE"])
def remover_autorizacao(pessoa_id, aluno_id):
    with conectar() as con:
        con.execute("""
            DELETE FROM autorizacoes
            WHERE pessoa_id=? AND aluno_id=?
        """, (pessoa_id, aluno_id))
    return jsonify({"msg": "Autorização removida."})


# ---------- PORTARIA E SAÍDAS ----------

@app.route("/api/resumo")
def resumo():
    hoje = date.today().isoformat()

    with conectar() as con:
        alunos = con.execute(
            "SELECT COUNT(*) FROM alunos"
        ).fetchone()[0]

        pessoas = con.execute(
            "SELECT COUNT(*) FROM pessoas"
        ).fetchone()[0]

        saidas = con.execute("""
            SELECT COUNT(*) FROM saidas
            WHERE date(horario) = ?
        """, (hoje,)).fetchone()[0]

    return jsonify({
        "alunos": alunos,
        "pessoas": pessoas,
        "saidas_hoje": saidas
    })


@app.route("/api/status")
def status():
    # Aguardando integração com as câmeras.
    return jsonify({
        "status": "aguardando",
        "pessoa": None,
        "alunos": []
    })


@app.route("/api/saida", methods=["POST"])
def registrar_saida():
    d = request.get_json(silent=True) or {}

    try:
        pessoa_id = int(d["pessoa_id"])
        aluno_id = int(d["aluno_id"])
    except (KeyError, ValueError, TypeError):
        return erro("Dados de saída inválidos.")

    with conectar() as con:
        autorizacao = con.execute("""
            SELECT * FROM autorizacoes
            WHERE pessoa_id=? AND aluno_id=?
        """, (pessoa_id, aluno_id)).fetchone()

        if not autorizacao:
            return erro("Responsável sem autorização.", 403)

        if autorizacao["bloqueado"]:
            return erro("Responsável bloqueado.", 403)

        validade = autorizacao["valido_ate"]
        if validade and validade < date.today().isoformat():
            return erro("Autorização expirada.", 403)

        con.execute("""
            INSERT INTO saidas (pessoa_id, aluno_id, horario)
            VALUES (?, ?, ?)
        """, (
            pessoa_id,
            aluno_id,
            datetime.now().astimezone().isoformat(timespec="seconds")
        ))

    return jsonify({"msg": "Saída registrada com sucesso."})


@app.route("/api/saidas")
def listar_saidas():
    with conectar() as con:
        rows = con.execute("""
            SELECT s.horario,
                   p.nome AS pessoa,
                   a.nome AS aluno,
                   a.turma
            FROM saidas s
            JOIN pessoas p ON p.id=s.pessoa_id
            JOIN alunos a ON a.id=s.aluno_id
            ORDER BY s.id DESC
            LIMIT 500
        """).fetchall()

    return jsonify([dict(r) for r in rows])


# ---------- CÂMERA (ESPERANDO CONFIGURAÇÃO) ----------

@app.route("/video")
def video():
    imagem = """
    <svg xmlns="http://www.w3.org/2000/svg"
         width="640" height="360">
      <rect width="100%" height="100%" fill="#101b2d"/>
      <text x="50%" y="50%" fill="white"
            text-anchor="middle" font-size="22">
        CÂMERA NÃO CONFIGURADA
      </text>
    </svg>
    """
    return Response(imagem, mimetype="image/svg+xml")


# ---------- INICIALIZAÇÃO ----------

iniciar_banco()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
