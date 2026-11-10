# Interface web do Quiz Competitivo em Rede — Design

Data: 2026-11-06

## Objetivo

Criar uma interface gráfica, em TypeScript, que reproduza a tela "Quiz — Pergunta" do arquivo `telatrabalho_redes.figcraft`, mais uma tela de entrada, conectada ao `servidor.py` existente.

Restrições:
- O autor quer entender e escrever parte do código. O trabalho é dividido para isso (ver "Divisão do trabalho").
- Prazo: cerca de 2 dias, com 4 a 5 horas de trabalho efetivo.
- `servidor/servidor.py`, `servidor/cliente.py` e `servidor/perguntas.txt` não são alterados.

## Escopo

Dentro:
- Tela **Entrar**: IP do servidor e nome.
- Tela **Pergunta**: igual ao figcraft, com as adaptações da seção "Diferenças em relação ao design".
- Painel simples de **resultado da rodada** (alternativa correta e placar) exibido depois de cada rodada.
- `ponte/ponte.py`: ponte entre WebSocket e o protocolo TCP/UDP do servidor.

Fora:
- Telas de lobby e de placar final separadas. O botão INICIAR do organizador e o placar final aparecem como elementos simples dentro da tela Pergunta.
- Testes automatizados (apenas teste manual com 3 abas).
- Alterações no protocolo ou no servidor.

## Arquitetura

```
servidor.py (intacto)
   ⇅  TCP (comandos) + UDP (avisos)
ponte.py  (Python, biblioteca websockets, uma sessão por aba)
   ⇅  WebSocket, mensagens JSON
React + Vite + TypeScript (navegador)
```

O navegador não abre sockets TCP/UDP, por isso a ponte existe. Cada conexão WebSocket cria uma sessão de jogo: um socket TCP e um socket UDP para o servidor, como o `cliente.py` faz.

Dependência nova: `websockets` (Python), usada só pela ponte.

### Ponte (`ponte.py`)

Responsabilidades:
- Abrir o TCP e o UDP quando o navegador envia `entrar` e mandar `ENTRAR <porta_udp> <nome>` ao servidor.
- Acumular os bytes recebidos por TCP até encontrar `\n`, porque o TCP não preserva fronteira de mensagem. O `cliente.py` usa `recv(1024)` sem buffer, e a ponte não repete isso.
- Serializar os pedidos TCP com um lock, para que cada resposta seja ligada ao pedido certo.
- Reagir aos avisos UDP:
  - `RODADA_ABERTA n`: envia `PERGUNTA` por TCP e entrega a pergunta ao navegador.
  - `RODADA_ENCERRADA n`: envia `RESULTADO n` e `PLACAR` e entrega ao navegador.
  - `FIM_JOGO`: envia `PLACAR` e entrega o placar final.
- Traduzir as respostas de texto (`PERGUNTA|1|...`, `RESULTADO|...`, `PLACAR|...`, `ERRO ...`) para JSON.
- Fechar os sockets quando o WebSocket cair.

### Mensagens WebSocket (JSON)

Navegador → ponte:
- `{ "tipo": "entrar", "ip": string, "nome": string }`
- `{ "tipo": "iniciar" }`
- `{ "tipo": "responder", "rodada": number, "alternativa": 1|2|3|4 }`

Ponte → navegador:
- `{ "tipo": "entrou", "id": number, "organizador": boolean }`
- `{ "tipo": "pergunta", "rodada": number, "texto": string, "alternativas": string[4], "segundos": number }`
- `{ "tipo": "resultado", "rodada": number, "correta": number, "acertaram": string[], "placar": {nome: string, pontos: number}[] }`
- `{ "tipo": "fim", "placar": {...}[], "vencedores": string[] }`
- `{ "tipo": "erro", "codigo": string }` (o código vem do servidor, por exemplo `partida_em_andamento`, ou é `servidor_indisponivel`)
- `{ "tipo": "ok", "acao": "iniciar" | "responder" }`

Os tipos exatos ficam em `src/tipos.ts`.

### Front (React + Vite + TypeScript)

```
src/
  tipos.ts              tipos das mensagens
  useServidor.ts        hook: abre o WebSocket, mantém o estado do jogo
  App.tsx               alterna entre Entrar e Pergunta
  telas/Entrar.tsx
  telas/Pergunta.tsx
  componentes/Alternativa.tsx
  componentes/BarraProgresso.tsx
  estilo.css            tokens de cor do design como variáveis CSS
```

Tokens do design (lidos do figcraft):
- Fundo: `#FEDC97`
- Card e texto escuro: `#033F63`
- Alternativa: `#286670`
- Alternativa selecionada e texto secundário no card: `#B5B682`
- Barra de progresso (trilho): `#7C9885`
- Largura do card 880px, alternativas 784×72px, círculo da letra 40px.

## Diferenças em relação ao design

| Design | Implementação | Motivo |
|---|---|---|
| Botão "Próxima →" | Botão "Responder", que envia a alternativa selecionada | O servidor avança as rodadas, por tempo ou quando todos respondem |
| "Quiz · Geografia" | "Quiz · Redes" | As perguntas são de redes |
| "Pergunta 3 de 10" e barra | Rodada atual de 10, valor fixo | O servidor sempre tem 10 rodadas |
| "Pontuação: 2 de 2 corretas" | Pontos do jogador vindos do `PLACAR` | Dados oficiais ficam no servidor |
| (não existe) | Contagem regressiva de 20 s | O servidor envia `segundos_restantes`; a UI conta localmente |
| (não existe) | Painel de resultado, botão INICIAR (só organizador), placar final | Necessários para o jogo funcionar |

## Tratamento de erros

- Servidor fora do ar ou IP errado: a ponte envia `erro / servidor_indisponivel` e a tela Entrar mostra a mensagem.
- `ERRO partida_em_andamento`, `ERRO poucos_jogadores`, `ERRO resposta_duplicada` e os demais: exibidos como mensagem curta na tela.
- WebSocket caiu: a UI volta à tela Entrar com aviso.
- Limitações herdadas do servidor (nome com `,` `:` `|`, nomes repetidos) não são tratadas, e a tela Entrar rejeita esses caracteres no nome.

## Divisão do trabalho (4 a 5 h)

Atualizado em 2026-11-06: o autor pediu um agente professor que o guie passo a passo.

1. Claude criou o esqueleto (Vite + React + TS em `interface/`) e a `ponte.py`. A ponte foi testada com `servidor.py` e 3 jogadores simulados (partida completa, placar conferido, erros `partida_em_andamento` e `servidor_indisponivel`).
2. O agente `professor` (`.claude/agents/professor.md`, sem permissão de escrita) guia o autor, um passo por vez, para escrever à mão todos os arquivos de `interface/src/`: `tipos.ts`, `estilo.css`, `BarraProgresso.tsx`, `Alternativa.tsx`, `Pergunta.tsx`, `useServidor.ts`, `Entrar.tsx` e a ligação em `App.tsx`. Ele confere cada passo com `npx tsc -b` e leitura do arquivo.
3. Teste manual: `servidor.py`, `ponte.py` e 3 abas do navegador jogando uma partida completa.

## Critérios de sucesso

- A tela Pergunta fica visualmente igual ao figcraft, com as diferenças da tabela acima.
- 3 abas completam as 10 rodadas, com resposta, resultado, placar e vencedores corretos.
- O `servidor.log` continua sendo gerado normalmente.
- O autor consegue explicar a ponte e os componentes que escreveu.
