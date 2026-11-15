# Parte 3 — Murilo: Atendimento dos clientes

**Arquivo:** `servidor.py` (`atender_cliente`) — **Tempo: até 2,5 min**

## Fala

Valeu, Júlia. Eu fico com a função `atender_cliente`. Ela roda uma vez para cada cliente conectado e funciona como o **tradutor do protocolo**: lê um comando, decide a resposta e envia.

O laço lê uma linha, registra no log e verifica qual é o comando. Os comandos são estes:

- **ENTRAR porta_udp nome:** cadastra o jogador. Valida se ele já estava cadastrado, se a partida já começou e se a porta é válida. Se der certo, responde `OK id organizador`. **O primeiro a entrar vira o organizador.**
- **INICIAR:** só o organizador pode usar, e só com **no mínimo 3 jogadores ativos**. Se estiver tudo certo, ele dispara a thread de `controlar_partida` que a Júlia explicou.
- **PERGUNTA:** devolve a pergunta da rodada aberta, com as quatro alternativas e o tempo restante. Se não tem rodada aberta, dá erro.
- **RESPONDER rodada alternativa:** é o comando com mais validações. Ele checa se o jogador está cadastrado, se a rodada está aberta, se o número da rodada confere, se a alternativa vai de 1 a 4 e se ele já respondeu. **É uma resposta por jogador por rodada.** Tudo isso fica dentro do `lock_rodada`, para a rodada não fechar entre a checagem e a gravação.
- **RESULTADO n:** devolve o resultado da rodada n, mas só se ela já foi encerrada.
- **PLACAR:** mostra a pontuação atual. Depois do fim do jogo, ele ordena do maior para o menor e inclui os **vencedores**. Se houver empate, aparecem vários.

Qualquer outro comando recebe `ERRO comando_desconhecido`.

No final, o bloco `finally` trata a saída do jogador. Se a conexão cair, ele fica **inativo, mas a pontuação dele é mantida**. Os erros de conexão, como fechamento abrupto no Windows, também são tratados para o servidor não cair.

Agora o Luiz apresenta o lado do cliente.
