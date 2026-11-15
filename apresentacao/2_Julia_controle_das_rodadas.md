# Parte 2 — Júlia: Controle das rodadas

**Arquivo:** `servidor.py` (`controlar_partida` e programa principal) — **Tempo: ~2,5 min** — leia o texto abaixo do jeito que está.

---

Obrigada, Athos. Eu vou explicar a parte que conduz o jogo, que é a função controlar partida, e depois o programa principal do servidor.

A função controlar partida roda em uma thread própria, ou seja, em paralelo com o resto do servidor. Isso é importante, porque enquanto ela cuida do tempo das rodadas, o servidor continua atendendo os jogadores normalmente.

O jogo tem dez rodadas, e cada rodada segue sempre os mesmos passos.

Primeiro, o servidor abre a rodada. Ele limpa as respostas da rodada anterior, define o prazo de vinte segundos e envia o aviso UDP de rodada aberta para todos os jogadores.

Segundo, ele espera. O servidor fica verificando a cada instante se o tempo acabou ou se todos os jogadores ativos já responderam. O que acontecer primeiro encerra a espera, então se todo mundo responder rápido, o jogo não perde tempo.

Terceiro, ele encerra a rodada e calcula a pontuação. Cada resposta correta vale um ponto. Esse cálculo é feito dentro de um lock, para garantir que nenhuma resposta chegue no meio da conta. Assim, toda resposta que o servidor aceitou com OK entra na pontuação.

Quarto, ele guarda o resultado oficial, que contém o número da rodada, a alternativa correta, quem acertou e o placar. Depois, manda o aviso UDP de rodada encerrada. Os jogadores usam esse aviso para pedir o resultado pelo TCP.

Quinto, ele faz uma pausa de cinco segundos e começa a próxima rodada.

Depois da décima rodada, o servidor marca a partida como terminada e envia o aviso de fim de jogo.

Agora, o programa principal. Ele carrega as perguntas, cria o socket TCP e fica esperando conexões, escutando em todas as interfaces da máquina, para que jogadores de outros computadores consigam entrar. Cada vez que um jogador conecta, o servidor cria uma nova thread só para ele. É por isso que vários jogadores conseguem jogar ao mesmo tempo, sem um atrapalhar o outro.

Agora o Murilo vai mostrar como o servidor atende cada jogador.
