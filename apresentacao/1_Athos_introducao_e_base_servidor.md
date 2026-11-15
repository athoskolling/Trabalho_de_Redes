# Parte 1 — Athos: Introdução e base do servidor

**Arquivo:** `servidor.py` (início) — **Tempo estimado:** 1 a 2 min

## Fala

Boa tarde, pessoal. Nosso trabalho é um **Quiz Competitivo em Rede**, feito em Python com sockets. Temos dois programas: o **servidor** e o **cliente**. Vou apresentar a ideia geral e a base do servidor.

A comunicação usa **dois protocolos ao mesmo tempo**. O **TCP**, na porta 5000, leva os comandos dos jogadores e as respostas oficiais do servidor. O **UDP** serve só para **avisos de eventos**: rodada aberta, rodada encerrada e fim de jogo. O aviso UDP não traz dados, só avisa que algo aconteceu. Quem busca a informação de verdade é o cliente, por TCP.

O servidor guarda **todo o estado da partida**. Isso inclui a lista de jogadores com nome, IP, porta UDP e pontos, a rodada atual, as respostas recebidas e os resultados. O protocolo é de texto, com uma mensagem por linha, terminada em `\n`.

Agora as funções auxiliares. A `carregar_perguntas` lê o arquivo `perguntas.txt`, onde cada linha tem pergunta, quatro alternativas e a correta, separadas por barra vertical.

A `ler_mensagem` existe porque o TCP é um **fluxo de bytes**, sem fronteira de mensagem. Ela vai lendo e guardando num buffer até aparecer o `\n`, e só então devolve a linha completa.

A `enviar_aviso` manda um datagrama UDP para todos os jogadores ativos. Se falhar com um jogador, ela registra o erro e continua com os outros.

E a `registrar` grava cada evento no arquivo `servidor.log` e na tela, com hora, protocolo, direção, quem e conteúdo. Ela usa um **lock** para duas threads não misturarem linhas no arquivo.

Agora passo para a Júlia, que vai explicar como as rodadas funcionam.
