# Parte 1 — Athos: Introdução e base do servidor

**Arquivo:** `servidor.py` (início) — **Tempo: ~2,5 min** — leia o texto abaixo do jeito que está.

---

Boa tarde, professor, boa tarde, pessoal. Nosso trabalho é um Quiz Competitivo em Rede, feito em Python usando sockets. Ele tem dois programas: o servidor, que controla a partida, e o cliente, que é o programa que cada jogador usa.

Eu vou começar explicando a ideia geral e depois a base do servidor.

A principal decisão do projeto foi usar dois protocolos ao mesmo tempo. O TCP, na porta 5000, é usado para os comandos dos jogadores e para as respostas oficiais do servidor, porque o TCP garante que a mensagem chega inteira e na ordem. Já o UDP é usado só para avisos de eventos, que são três: rodada aberta, rodada encerrada e fim de jogo. O aviso UDP não carrega nenhum dado do jogo. Ele só diz que algo aconteceu, e então o cliente vai buscar a informação de verdade pelo TCP.

O servidor guarda todo o estado da partida: a lista de jogadores, com nome, endereço e pontos, a rodada atual, as respostas recebidas, os resultados e o placar. Toda a comunicação é feita em texto, uma mensagem por linha.

Agora, o começo do código do servidor tem quatro funções de apoio.

A primeira carrega as perguntas, lendo o arquivo perguntas ponto txt, onde cada linha tem a pergunta, as quatro alternativas e qual é a correta.

A segunda lê as mensagens que chegam pelo TCP. Isso é necessário porque o TCP é um fluxo de bytes e não separa as mensagens sozinho. Então a função vai juntando os pedaços até encontrar o fim da linha, e só então entrega a mensagem completa.

A terceira envia os avisos UDP para todos os jogadores que ainda estão ativos. Se der erro com um jogador, ela registra o problema e continua com os outros, para a partida não parar.

E a quarta grava um registro, ou log, de tudo que acontece, com hora, protocolo, quem enviou e o conteúdo. Esse log vai para um arquivo e para a tela, e usa um lock, que é um cadeado, para que duas threads não escrevam ao mesmo tempo e misturem as linhas.

Com essa base pronta, a Júlia vai explicar como as rodadas funcionam.
