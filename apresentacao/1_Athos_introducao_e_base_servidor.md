# Parte 1 — Athos: Introdução e base do servidor

**Arquivo:** `servidor.py` (início) — **Tempo: ~2 min**

## Fala

Boa tarde, pessoal. Nosso trabalho é um **Quiz Competitivo em Rede**, feito em Python com sockets. São dois programas: o **servidor** e o **cliente**.

A ideia central é usar **dois protocolos**. O **TCP**, na porta 5000, leva os comandos dos jogadores e as respostas oficiais. O **UDP** serve só para **avisos**: rodada aberta, rodada encerrada e fim de jogo. Quando o cliente recebe o aviso, ele busca a informação de verdade por TCP.

O servidor guarda **todo o estado da partida**: jogadores, rodada atual, respostas e placar. As mensagens são texto, uma por linha.

No começo do servidor ficam as funções de apoio. Uma carrega as perguntas do arquivo `perguntas.txt`. Outra lê as mensagens do TCP, juntando os pedaços até completar uma linha. Outra envia os avisos UDP. E a última grava tudo em um **log**, que serve para acompanhar a partida.

Agora a Júlia explica como as rodadas funcionam.
