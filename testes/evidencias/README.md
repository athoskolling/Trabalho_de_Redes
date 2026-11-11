# Evidências da execução do roteiro de testes

Registro de uma execução completa do `roteiros/ROTEIRO_DE_TESTES.md` (partes A a D), com screenshots.

- **Data:** 11/11/2026, das 01:57:02 às 01:59:14 (horários do `servidor.log`)
- **Ambiente:** Linux, Python 3.14.8, tudo na mesma máquina (`127.0.0.1`)
- **Programas:** `servidor/servidor.py` e `servidor/cliente.py` do repositório, sem alteração
- **Jogadores:** Athos, Julia e Murilo, no lugar de Ana, Bruno e Carla do roteiro
- **Resultado:** as 40 linhas de teste do roteiro deram o resultado esperado. Além do roteiro, o `PERGUNTA` da rodada 1 foi feito nos três clientes, para mostrar a mesma pergunta em todos

| No roteiro | Nesta execução |
|---|---|
| T2, Ana (organizadora) | Athos |
| T3, Bruno | Julia |
| T4, Carla | Murilo |
| T1, servidor | Servidor |
| T5, extra | Extra |

## Como foi feito

Os comandos não foram digitados à mão. Um script abriu uma janela de terminal com 5 painéis (`tmux`), enviou a cada painel as teclas do roteiro e tirou os screenshots da janela com o `grim`. Os clientes são processos `cliente.py` de verdade, e o que aparece nas imagens é a saída real deles.

Em todas as imagens: em cima, Athos, Julia e Murilo; embaixo, o servidor (log ao vivo) e o terminal extra.

O `servidor.log` desta pasta é a cópia do log completo dessa execução (169 linhas).

## Prints por exigência do enunciado (Moodle)

### Demonstração específica do Quiz (seção 3 do enunciado)

| O enunciado pede | Print | O que olhar |
|---|---|---|
| Participação de 3 jogadores | `02-tres-jogadores-cadastrados.png` | `OK 1 1`, `OK 2 0` e `OK 3 0` nos três clientes |
| Resposta correta e incorreta | `05-resposta-correta-e-incorreta.png` e `06-ausencia-de-resposta-e-resultado.png` | Athos responde a 1 (certa), Julia a 2 (errada); no resultado só o Athos pontua |
| Ausência de resposta | `06-ausencia-de-resposta-e-resultado.png` | Murilo não responde, a rodada fecha aos 20 s e ele fica com 0 |
| Rejeição de resposta duplicada | `07-resposta-duplicada.png` | Athos: `OK` e depois `ERRO resposta_duplicada` |
| Rejeição de resposta atrasada | `08-resposta-atrasada.png` | Murilo: `ERRO rodada_encerrada` depois do `RODADA_ENCERRADA 2` |
| Placar final | `12-placar-final-empate.png` | `PLACAR\|Athos:7,Julia:1,Murilo:7\|FIM\|Athos,Murilo` |

### Demonstração geral (seção 10 do enunciado)

| O enunciado pede | Print | O que olhar |
|---|---|---|
| Funcionamento com 3 clientes | todos | três clientes na mesma sessão |
| Tratamento de uma entrada inválida | `03-entrada-invalida-e-delimitacao-tcp.png` | Julia: `BLABLA`, `RESPONDER 4` e linha vazia dão `ERRO comando_desconhecido`; o `PLACAR` seguinte responde normal |
| Encerramento de um cliente sem queda do servidor | `11-cliente-desconectado-servidor-continua.png` | Julia sai; o servidor registra a saída e a rodada 5 fecha só com Athos e Murilo |

### Requisitos do tema e requisitos comuns

| Requisito | Print | O que olhar |
|---|---|---|
| Organizador inicia só com 3 jogadores | `02-tres-jogadores-cadastrados.png` | `ERRO poucos_jogadores` e `ERRO nao_organizador` |
| Identificação não depende só do IP | `02-tres-jogadores-cadastrados.png` e `13-log-em-arquivo.png` | mesmo IP `127.0.0.1`, portas TCP diferentes, e cada `ENTRAR` informa nome e porta UDP |
| Mesma pergunta a todos os jogadores | `04-mesma-pergunta-para-todos.png` | `PERGUNTA\|1\|O que o DNS faz?...` igual nos três, sem a alternativa certa |
| Resposta correta só depois do encerramento | `05-resposta-correta-e-incorreta.png` | `RESULTADO 1` com a rodada aberta dá `ERRO rodada_nao_encerrada` |
| Uma resposta por jogador por rodada | `07-resposta-duplicada.png` | `ERRO resposta_duplicada` |
| Janela de 20 s, com fim antecipado se todos respondem | `06-ausencia-de-resposta-e-resultado.png` e `09-encerramento-antecipado.png` | rodada 1 dura 20 s; rodada 3 fecha em 1 s |
| 1 ponto por acerto, placar acumulado | `06-ausencia-de-resposta-e-resultado.png` e `11-cliente-desconectado-servidor-continua.png` | `RESULTADO\|1\|1\|Athos\|Athos:1,Julia:0,Murilo:0` e `PLACAR\|Athos:2,Julia:1,Murilo:2` |
| Classificação final com todos os vencedores no empate | `12-placar-final-empate.png` | `FIM\|Athos,Murilo` |
| Rodadas encerram mesmo com cliente desconectado | `11-cliente-desconectado-servidor-continua.png` | rodada 5 fecha em 2 s sem a Julia |
| Entrada depois do início é recusada | `10-partida-ja-iniciada.png` | Davi: `ERRO partida_em_andamento`; Athos: `ERRO ja_iniciada` |
| TCP: acumular bytes até o fim da mensagem (`\n`) | `03-entrada-invalida-e-delimitacao-tcp.png` | painel Extra: `PLAC` + `AR\n` dá uma resposta; `PLACAR\nPLACAR\n` dá duas |
| UDP só avisa, TCP é o oficial | `04-mesma-pergunta-para-todos.png` e `06-ausencia-de-resposta-e-resultado.png` | o `[AVISO]` traz só o número da rodada; pergunta e resultado vêm por TCP |
| Log em arquivo: horário, protocolo, direção, origem/destino, tipo e mudanças de estado | `13-log-em-arquivo.png` | início do `servidor.log` (TCP) e as linhas `ESTADO`; as linhas `UDP \| ENVIADO` aparecem no painel Servidor dos outros prints |

`01-servidor-iniciado.png` mostra só o servidor no ar, antes dos clientes.

## Resultado de cada teste

### B. Antes de iniciar a partida

| # | Quem | Comando | Obtido | Situação |
|---|---|---|---|---|
| 1a | Athos | entra | `Recebido: OK 1 1` | OK |
| 1b | Julia | entra | `Recebido: OK 2 0` | OK |
| 2 | Athos | `INICIAR` | `ERRO poucos_jogadores` | OK |
| 3 | Julia | `INICIAR` | `ERRO nao_organizador` | OK |
| 1c | Murilo | entra | `Recebido: OK 3 0` | OK |
| 6b | Murilo | `ENTRAR 5555 Outro` | `ERRO ja_cadastrado` | OK |
| 17 | Julia | `BLABLA` | `ERRO comando_desconhecido` | OK |
| 19 | Julia | `RESPONDER 4` | `ERRO comando_desconhecido` | OK |
| 20 | Julia | linha vazia | `ERRO comando_desconhecido` | OK |
| 21 | Julia | `PLACAR` | `PLACAR\|Athos:0,Julia:0,Murilo:0` | OK |
| 25 | Extra | `PLAC` + `AR\n` | uma linha `PLACAR\|Athos:0,Julia:0,Murilo:0` | OK |
| 26 | Extra | `PLACAR\nPLACAR\n` | duas linhas `PLACAR\|Athos:0,Julia:0,Murilo:0` | OK |

### C. A partida

| # | Quem | Comando | Obtido | Situação |
|---|---|---|---|---|
| 4 | Athos | `INICIAR` | `OK`; `[AVISO] RODADA_ABERTA 1` nos três | OK |
| 7 | Julia | `PERGUNTA` | `PERGUNTA\|1\|O que o DNS faz?\|...\|19`, sem a alternativa certa | OK |
| 8 | Athos | `RESULTADO 1` com a rodada aberta | `ERRO rodada_nao_encerrada` | OK |
| 9 | Athos | `RESPONDER 1 1` | `OK` | OK |
| 10 | Julia | `RESPONDER 1 2` | `OK` | OK |
| 11 | Murilo | não responde | rodada aberta 01:57:17, encerrada 01:57:37 (20 s) | OK |
| 12 | Athos | `RESULTADO 1` | `RESULTADO\|1\|1\|Athos\|Athos:1,Julia:0,Murilo:0` | OK |
| 30 | | pergunta oficial por TCP | comprovado no teste 7 | OK |
| 31 | | resultado oficial por TCP | comprovado no teste 12 | OK |
| 13a | Athos | `RESPONDER 2 2` | `OK` | OK |
| 13b | Athos | `RESPONDER 2 2` de novo | `ERRO resposta_duplicada` | OK |
| 18 | Murilo | `RESPONDER 2 9` | `ERRO alternativa_invalida` | OK |
| 14 | Murilo | `RESPONDER 2 1` depois do encerramento | `ERRO rodada_encerrada` | OK |
| 15a | Athos | `RESPONDER 3 1` | `OK` | OK |
| 15b | Julia | `RESPONDER 3 3` | `OK` | OK |
| 15c | Murilo | `RESPONDER 3 3` | `OK` | OK |
| 15 | os três | | rodada aberta 01:58:07, encerrada 01:58:08; placar `Athos:2,Julia:1,Murilo:1` | OK |
| 5 | Athos | `INICIAR` | `ERRO ja_iniciada` | OK |
| 16 | Julia | `RESPONDER 99 1` | `ERRO rodada_invalida` | OK |
| 6 | Extra | entra como `Davi` | `Recebido: ERRO partida_em_andamento` | OK |
| 22 | Julia | `sair` | servidor segue; `jogador Julia saiu (conexão encerrada)` | OK |
| 23a | Athos | `RESPONDER 5 1` | `OK` | OK |
| 23b | Murilo | `RESPONDER 5 3` | `OK` | OK |
| 23 | | | rodada aberta 01:58:38, encerrada 01:58:40, sem esperar a Julia | OK |
| 24 | Athos | `PLACAR` | `PLACAR\|Athos:2,Julia:1,Murilo:2` | OK |
| 27 | Athos e Murilo | fim da rodada 10 | `[AVISO] FIM_JOGO` | OK |
| 28 | Athos | `PLACAR` | `PLACAR\|Athos:7,Julia:1,Murilo:7\|FIM\|Athos,Murilo` | OK |
| 29 | | empate | os dois vencedores depois do `FIM` | OK |

### D. Log

- `TCP | RECEBIDO` e `TCP | ENVIADO`: presentes
- `UDP | ENVIADO` com `RODADA_ABERTA`, `RODADA_ENCERRADA` e `FIM_JOGO`: presentes
- `ESTADO | - | - | MUDANCA` para jogador entrou, jogador saiu, partida iniciada, rodada aberta, rodada encerrada (com placar) e fim do jogo: presentes

## O que esta execução não cobre

- Entre computadores (F.1) e interface web (F.2): não executados.
- Windows: só Linux.
- Wireshark: não houve captura. O `.pcapng` precisa de outra execução, com o `ROTEIRO_WIRESHARK.md`.
