 Venix Security
O Venix Security é um sistema de segurança escolar que se conecta a três câmeras IP e usa reconhecimento facial para controlar a saída de alunos. Ele compara o rosto de quem busca a criança com um banco de fotos de pessoas autorizadas pela escola e pelos responsáveis, e emite um alerta de autorizado ou não autorizado para os monitores.
Como funciona
1.  As câmeras IP, instaladas na entrada e na saída da escola, capturam o rosto de quem chega para buscar o aluno.
2.  O sistema compara o rosto com o banco de fotos de pessoas autorizadas.
3.  Se a pessoa for autorizada pela escola e pelos responsáveis, os monitores recebem um alerta de autorizado.
4.  Se a pessoa não for reconhecida ou não estiver autorizada, os monitores recebem um alerta de não autorizado e a saída da criança não é liberada.
Tecnologias
• Cloudflare Workers
• Cloudflare D1 (banco de dados SQLite)
• JavaScript (app.js)
• HTML e CSS (index.html e style.css)
• Câmeras IP com reconhecimento facial
Estrutura do projeto
• index.html: página principal do sistema
• style.css: estilos da interface
• app.js: lógica da aplicação
• README.md: documentação do projeto
• LEIA-ME.txt: instruções em texto simples
Privacidade e proteção de dados
Este sistema trata dados pessoais sensíveis, como imagens faciais de alunos e responsáveis, protegidos pela LGPD, a Lei Geral de Proteção de Dados. O uso exige consentimento específico dos responsáveis, o acesso às fotos é restrito à equipe autorizada da escola, e os dados devem ser armazenados de forma segura e apagados quando deixarem de ser necessários.
O sistema serve de apoio à decisão dos monitores, que sempre têm a palavra final sobre a saída do aluno, pois o reconhecimento facial pode errar.
Importante: não publique fotos reais de alunos ou responsáveis neste repositório.
Como usar
1.  Clone o repositório.
2.  Configure o banco de dados Cloudflare D1.
3.  Publique o Worker na sua conta Cloudflare.
4.  Conecte as câmeras IP e cadastre as pessoas autorizadas.
Autor
Criado por venix102030.
