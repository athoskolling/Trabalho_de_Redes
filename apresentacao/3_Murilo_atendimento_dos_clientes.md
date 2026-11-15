# Parte 3 — Murilo: Atendimento dos clientes

**Arquivo:** `servidor.py` (`atender_cliente`) — **Tempo: ~2,5 min** — leia o texto abaixo do jeito que está.

---

Valeu, Júlia. Eu fico com a função atender cliente, que roda uma vez para cada jogador conectado. Ela funciona como o tradutor do protocolo: lê um comando que chegou pelo TCP, valida, decide a resposta e envia de volta.

Os comandos são seis.

O primeiro é ENTRAR, que cadastra o jogador. O jogador manda a porta UDP em que quer receber os avisos e o seu nome. O servidor confere se esse jogador já está cadastrado, se a partida já começou e se a porta é válida. Se estiver tudo certo, responde OK com o número do jogador. O primeiro jogador que entra é automaticamente o organizador da partida.

O segundo é INICIAR. Só o organizador pode usar, e só quando já existem pelo menos três jogadores ativos. Se as condições forem atendidas, o servidor responde OK e dispara a thread de controle das rodadas que a Júlia acabou de explicar.

O terceiro é PERGUNTA. Ele devolve a pergunta da rodada que está aberta, com as quatro alternativas e quantos segundos ainda faltam. Se não existir rodada aberta, o servidor responde com erro.

O quarto é RESPONDER, que é o comando com mais validações. O servidor verifica se o jogador está cadastrado, se a rodada ainda está aberta, se o número da rodada está certo, se a alternativa é de um a quatro e se aquele jogador ainda não tinha respondido. Cada jogador só pode responder uma vez por rodada. Tudo isso acontece dentro do mesmo lock usado no fechamento da rodada, para a rodada não fechar bem no meio da checagem.

O quinto é RESULTADO, que devolve o resultado de uma rodada, mas só depois que ela foi encerrada.

E o sexto é PLACAR, que mostra a pontuação de todos. Depois do fim do jogo, o placar vem ordenado do maior para o menor e informa o vencedor, ou os vencedores, se houver empate.

Qualquer comando que não esteja nessa lista recebe a resposta de comando desconhecido.

Por fim, se a conexão de um jogador cair, o servidor trata o erro sem derrubar a partida. O jogador passa a ficar inativo, mas a pontuação dele é mantida.

Agora o Luiz apresenta o cliente.
