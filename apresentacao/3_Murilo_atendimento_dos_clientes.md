# Parte 3 — Murilo: Atendimento dos clientes

**Arquivo:** `servidor.py` (`atender_cliente`) — **Tempo: ~2 min**

## Fala

Valeu, Júlia. Eu fico com a parte que atende cada jogador. Ela lê os comandos que chegam por TCP, valida e responde.

Os principais comandos são:

- **ENTRAR**: cadastra o jogador. O primeiro a entrar vira o **organizador**.
- **INICIAR**: só o organizador pode usar, e só com **pelo menos 3 jogadores**.
- **PERGUNTA**: devolve a pergunta da rodada aberta, com as alternativas e o tempo restante.
- **RESPONDER**: registra a resposta. O servidor valida a rodada e a alternativa, e aceita **só uma resposta por jogador por rodada**.
- **RESULTADO** e **PLACAR**: mostram o resultado da rodada e a pontuação.

Se o comando for inválido, o servidor devolve uma mensagem de erro. Se um jogador sai, ele fica inativo, mas **os pontos dele são mantidos**.

Agora o Luiz apresenta o cliente.
