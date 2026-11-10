# Interface web do Quiz de Redes

Interface gráfica (React + TypeScript) do quiz. É um extra: o trabalho funciona só com `servidor.py` e `cliente.py`.

O navegador não abre socket TCP nem UDP, só WebSocket. Por isso a página conversa com a `ponte/ponte.py`, e a ponte conversa com o `servidor.py`:

    navegador  <-- WebSocket (JSON) -->  ponte.py  <-- TCP + UDP -->  servidor.py

## Como rodar

Com o `servidor.py` e a `ponte.py` já rodando:

    npm install     (só na primeira vez; cria a pasta node_modules)
    npm run dev     (abre em http://localhost:5173)

Ou tudo de uma vez pelo Docker, a partir da raiz do projeto: `docker compose up --build`.

## O código (pasta src/)

| Arquivo | O que faz |
|---|---|
| `main.tsx` | Ponto de entrada: coloca o `App` dentro da página. |
| `App.tsx` | Decide qual tela mostrar: Entrar ou Pergunta. |
| `useServidor.ts` | Abre o WebSocket com a ponte, envia os comandos e guarda o estado do jogo. É o equivalente do `cliente.py`. |
| `types.ts` | Formato das mensagens JSON trocadas com a ponte. |
| `telas/Entrar.tsx` | Tela inicial: IP do servidor e nome do jogador. |
| `telas/Pergunta.tsx` | Tela do jogo: sala de espera, pergunta, resultado da rodada e placar final. |
| `componentes/Alternativa.tsx` | Botão de uma alternativa (A, B, C, D). |
| `componentes/BarraProgresso.tsx` | Barra que mostra a rodada atual de 10. |
| `index.css` | Cores e estilo de todas as telas. |

## Arquivos de configuração (não precisa mexer)

| Arquivo | O que faz |
|---|---|
| `index.html` | A página em si: uma `<div id="root">` vazia, que o React preenche. |
| `package.json` | Lista as dependências (React, Vite, TypeScript) e os comandos `npm run dev` e `npm run build`. |
| `package-lock.json` | Gerado pelo npm: trava as versões exatas das dependências. Não se edita à mão. |
| `vite.config.ts` | Configuração do Vite, a ferramenta que serve a página no `npm run dev`. |
| `tsconfig.json` | Configuração do TypeScript (o verificador de tipos). |
| `public/favicon.svg` | Ícone que aparece na aba do navegador. |
| `Dockerfile` e `.dockerignore` | Receita para rodar a interface no Docker (usada pelo `docker compose`). |
| `node_modules/` | Dependências baixadas pelo `npm install`. Não vai para o Git. |
| `dist/` | Site pronto, gerado pelo `npm run build`. Não vai para o Git. |
