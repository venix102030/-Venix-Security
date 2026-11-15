# Venix Security

Descreva aqui, em uma ou duas frases, o que o projeto faz.

## Tecnologias

- Cloudflare Workers
- Cloudflare D1 (banco de dados SQLite)
- Wrangler (CLI da Cloudflare)

## Configuração

1. Instale as dependências:

```bash
npm install
```

2. Crie o banco de dados D1:

```bash
npx wrangler d1 create nome-do-seu-banco
```

3. Copie o `database_id` exibido e adicione ao arquivo `wrangler.jsonc`:

```jsonc
{
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "nome-do-seu-banco",
      "database_id": "uuid-completo-aqui"
    }
  ]
}
```

## Deploy

```bash
npx wrangler deploy
```

## Desenvolvimento local

```bash
npx wrangler dev
```

## Licença

Defina a licença do projeto (por exemplo, MIT).
