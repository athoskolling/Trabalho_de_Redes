# Parte 4 — Luiz: Cliente e conclusão

**Arquivo:** `cliente.py` — **Tempo: ~2 min**

## Fala

Obrigado, Murilo. Eu apresento o **cliente**, que é o programa do jogador.

Ele conecta ao servidor por TCP, pede o nome do jogador e abre um socket UDP para receber os avisos. Ele trabalha com **duas threads**: uma lê o que o jogador digita e outra escuta os avisos UDP, assim a digitação não trava.

O cliente reage sozinho aos avisos. Quando a rodada abre, ele pede a **pergunta** e mostra na tela. Quando a rodada fecha, ele pede o **resultado**. No fim do jogo, pede o **placar final**.

Para facilitar, o jogador responde só com **a, b, c ou d**, e o cliente converte para o formato do protocolo.

Resumindo: o projeto usa **TCP** para dados confiáveis, **UDP** para avisos, **threads** para vários jogadores ao mesmo tempo e um **log** de tudo que acontece. Obrigado, ficamos à disposição para perguntas.
