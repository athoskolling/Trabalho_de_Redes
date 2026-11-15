# Parte 2 — Júlia: Controle das rodadas

**Arquivo:** `servidor.py` (`controlar_partida` e programa principal) — **Tempo: ~2 min**

## Fala

Obrigada, Athos. Eu explico o coração do jogo: o controle das rodadas. Ele roda em uma **thread própria**, para não travar o atendimento dos jogadores.

São **10 rodadas**. Em cada uma, o servidor abre a rodada e avisa todo mundo por UDP. Os jogadores têm **20 segundos** para responder, ou menos se todos responderem antes. Depois, o servidor encerra a rodada, confere as respostas, dá **1 ponto por acerto** e guarda o resultado. Então avisa o fim da rodada, espera 5 segundos e começa a próxima. No fim das 10, manda o aviso de fim de jogo.

No programa principal, o servidor fica esperando conexões na porta 5000. A cada jogador que conecta, ele cria **uma thread**, por isso vários jogadores podem jogar ao mesmo tempo.

Agora o Murilo mostra o que o servidor faz com cada jogador.
