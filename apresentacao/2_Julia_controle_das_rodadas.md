# Parte 2 — Júlia: Controle das rodadas e programa principal

**Arquivo:** `servidor.py` (`controlar_partida` e programa principal) — **Tempo estimado:** 1 a 2 min

## Fala

Obrigada, Athos. Eu vou explicar o coração do jogo, que é a função `controlar_partida`. Ela roda em **uma thread própria**, para não travar o atendimento dos clientes.

Ela faz um laço de **10 rodadas**. Em cada uma, o servidor faz o seguinte:

1. **Abre a rodada.** Limpa as respostas, define um prazo de **20 segundos** e manda o aviso UDP `RODADA_ABERTA`.
2. **Espera.** O servidor fica esperando até o tempo acabar **ou até todos os jogadores ativos responderem**. O que vier primeiro encerra a espera.
3. **Encerra e pontua.** Fecha a rodada e confere as respostas com a alternativa correta, dando **1 ponto por acerto**. Isso acontece dentro do `lock_rodada`. Assim, toda resposta que recebeu OK entra na contagem e nenhuma chega atrasada no meio do cálculo.
4. **Guarda o resultado oficial.** Monta a mensagem `RESULTADO` com a rodada, a resposta certa, quem acertou e o placar. Depois manda o aviso UDP `RODADA_ENCERRADA`.
5. **Pausa de 5 segundos** antes da próxima rodada.

Depois da décima rodada, o servidor marca a partida como terminada e manda o aviso `FIM_JOGO`.

No **programa principal**, o servidor carrega as perguntas e cria o socket TCP. Ele usa `SO_REUSEADDR` para poder reiniciar rápido na mesma porta e escuta em `0.0.0.0`, aceitando conexões de outras máquinas. Depois entra num laço infinito: a cada cliente que conecta, **cria uma thread** só para ele. Por isso vários jogadores podem jogar ao mesmo tempo.

Agora o Murilo mostra o que acontece dentro de cada thread de cliente.
