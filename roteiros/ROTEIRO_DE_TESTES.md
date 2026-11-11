# Roteiro de Testes: Quiz Competitivo em Rede

> Este é o roteiro **base**, sem Wireshark. A captura de pacotes está em `ROTEIRO_WIRESHARK.md`.

Este roteiro é um **passo a passo**: siga na ordem, de cima para baixo, digitando exatamente o que está escrito. Todos os testes cabem em **uma partida só**, de uns 4 minutos. Depois de preenchido, ele é o relatório de testes.

**Como preencher a coluna Resultado:** escreva `OK` se apareceu o esperado, ou anote o que apareceu de diferente.

| | |
|---|---|
| **Data do teste** | |
| **Quem testou** | |
| **Sistema e versão do Python** | |
| **Mesma máquina ou entre computadores** | |

## Sumário

| Parte | O que acontece | Testes |
|---|---|---|
| [A. Preparação](#a-preparação) | Abrir os 5 terminais | |
| [B. Antes de iniciar a partida](#b-antes-de-iniciar-a-partida-sem-pressa) | Cadastro, entradas inválidas, mensagem TCP partida | 1, 2, 3, 6b, 17, 19, 20, 21, 25, 26 |
| [C. A partida](#c-a-partida-rodada-por-rodada) | As 10 rodadas | 4 a 16, 18, 22 a 31 |
| [D. Conferência do log](#d-conferência-do-log) | Abrir o `servidor.log` | |
| [E. Se algo der errado](#e-se-algo-der-errado) | Como recomeçar | |
| [F. Extras](#f-extras-opcionais) | Entre computadores | |
| [G. O que entregar](#g-o-que-entregar) | | |
| [H. Limitações conhecidas](#h-limitações-conhecidas-para-mencionar-se-perguntarem) | | |

Os números dos testes não estão em ordem porque seguem a ordem em que é mais fácil executar.

---

## A. Preparação

### A.1 O que você precisa

- Python 3 instalado. Nos comandos abaixo está escrito `python`; se no seu Linux o comando for `python3`, use `python3`.
- A pasta do projeto no computador.
- **5 terminais abertos**, todos dentro da pasta `servidor/` do projeto:

| Terminal | Para que serve |
|---|---|
| **T1** | O servidor |
| **T2** | Cliente da **Ana** (a organizadora) |
| **T3** | Cliente do **Bruno** |
| **T4** | Cliente da **Carla** |
| **T5** | Extra: teste da mensagem partida e o 4º jogador (Davi) |

Deixe os terminais T2, T3 e T4 lado a lado na tela, para ver os três ao mesmo tempo. Em cada um dos 5, entre na pasta:

```bash
cd servidor
```

> **Dica:** faça uma partida de treino antes da oficial. São só 4 minutos e você pega o ritmo. Dá para fazer sozinho, mas com um colega cuidando de um dos terminais fica mais tranquilo.

### A.2 Iniciar o servidor (T1)

Primeiro apague o log antigo, porque o servidor acrescenta linhas ao arquivo em vez de recriá-lo.

Linux:

```bash
rm -f servidor.log
python servidor.py
```

Windows:

```bat
del servidor.log
python servidor.py
```

No Windows, se o `del` avisar que não encontrou o arquivo, tudo bem: é porque ainda não existia.

**Deve aparecer no T1:**

```
10 perguntas carregadas
Servidor TCP aguardando conexão...
```

Daqui em diante, **não mexa mais no T1**. Ele só vai mostrando as linhas do log.

---

## B. Antes de iniciar a partida (sem pressa)

Nesta parte não há cronômetro. Faça com calma.

### B.1 Ana e Bruno entram

**No T2:**

```bash
python cliente.py
```

Ele pergunta duas coisas. Responda:

```
IP do servidor: 127.0.0.1
Seu nome: Ana
```

**No T3**, a mesma coisa, com o nome `Bruno`.

Depois de entrar, cada cliente mostra a resposta do servidor e uma linha `>` esperando comandos.

| # | Onde | O que deve aparecer | Resultado |
|---|---|---|---|
| 1a | T2 (Ana) | `Recebido: OK 1 1` (id 1, é a organizadora) | |
| 1b | T3 (Bruno) | `Recebido: OK 2 0` (id 2, não é organizador) | |

### B.2 Tentar iniciar sem poder

Ainda só com 2 jogadores:

| # | Onde | Digite | O que deve aparecer | Resultado |
|---|---|---|---|---|
| 2 | T2 (Ana) | `INICIAR` | `ERRO poucos_jogadores` | |
| 3 | T3 (Bruno) | `INICIAR` | `ERRO nao_organizador` | |

### B.3 Carla entra

**No T4:** `python cliente.py`, IP `127.0.0.1`, nome `Carla`.

| # | Onde | Digite | O que deve aparecer | Resultado |
|---|---|---|---|---|
| 1c | T4 (Carla) | (entrar) | `Recebido: OK 3 0` | |
| 6b | T4 (Carla) | `ENTRAR 5555 Outro` | `ERRO ja_cadastrado` (não cria um segundo jogador) | |

### B.4 Entradas inválidas

Tudo no **T3 (Bruno)**. O servidor deve responder com erro e **continuar funcionando**.

| # | Digite | O que deve aparecer | Resultado |
|---|---|---|---|
| 17 | `BLABLA` | `ERRO comando_desconhecido` | |
| 19 | `RESPONDER 4` (faltando um campo) | `ERRO comando_desconhecido` | |
| 20 | Só aperte Enter (linha vazia) | `ERRO comando_desconhecido` | |
| 21 | `PLACAR` | `PLACAR\|Ana:0,Bruno:0,Carla:0`, provando que o servidor segue de pé | |

### B.5 Mensagem TCP partida em dois pedaços

O TCP não tem fronteira de mensagem, então o servidor precisa juntar os bytes até achar o `\n`. Estes dois comandos provam isso. Rode no **T5**, um de cada vez (copie e cole a linha inteira):

**Teste 25:** envia `PLAC`, espera 1 segundo e envia `AR\n`.

```bash
python -c "import socket,time; s=socket.create_connection(('127.0.0.1',5000)); s.sendall(b'PLAC'); time.sleep(1); s.sendall(b'AR\n'); print(s.recv(4096).decode())"
```

**Teste 26:** envia duas mensagens `PLACAR\n` coladas, de uma vez só.

```bash
python -c "import socket,time; s=socket.create_connection(('127.0.0.1',5000)); s.sendall(b'PLACAR\nPLACAR\n'); time.sleep(1); print(s.recv(4096).decode())"
```

| # | O que deve aparecer no T5 | Resultado |
|---|---|---|
| 25 | **Uma** linha `PLACAR\|Ana:0,Bruno:0,Carla:0`, que só sai depois de 1 segundo | |
| 26 | **Duas** linhas `PLACAR\|Ana:0,Bruno:0,Carla:0` | |

No T1 dá para ver que o servidor só registrou o `PLACAR` do teste 25 depois de receber o segundo pedaço.

No Linux, o mesmo teste também pode ser feito com o `nc`: `(printf 'PLAC'; sleep 1; printf 'AR\n') | nc 127.0.0.1 5000`.

---

## C. A partida, rodada por rodada

### Leia antes de começar

- Cada rodada dura **20 segundos**, com **5 segundos** de pausa entre uma e outra. A partir do `INICIAR`, o relógio não para.
- **Truque para não correr:** dá para deixar um comando digitado no terminal **sem apertar Enter** e só apertar Enter na hora certa. O roteiro avisa quando preparar.
- Os avisos do servidor aparecem sozinhos, no meio da tela, assim: `[AVISO] RODADA_ABERTA 1`. Eles podem bagunçar a linha que você está digitando, mas o texto digitado **não se perde**: é só continuar e apertar Enter.
- O número depois de `RESPONDER` é sempre o número da rodada. Se você perder o tempo de uma rodada, veja a [parte E](#e-se-algo-der-errado).

Gabarito das perguntas (está no `perguntas.txt`):

| Rodada | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Alternativa certa | 1 | 2 | 3 | 3 | 3 | 1 | 1 | 3 | 2 | 4 |

### Preparar antes do INICIAR

Deixe digitado, **sem apertar Enter**:

- T3 (Bruno): `PERGUNTA`

### Rodada 1: resposta certa, resposta errada e ausência de resposta

Faça nesta ordem:

| # | Onde | Faça | O que deve aparecer | Resultado |
|---|---|---|---|---|
| 4 | T2 (Ana) | Digite `INICIAR` | `OK`. Nos três clientes aparece `[AVISO] RODADA_ABERTA 1` | |
| 7 | T3 (Bruno) | Aperte Enter (o `PERGUNTA` já estava digitado) | `PERGUNTA\|1\|O que o DNS faz?\|...\|<segundos>`, com as 4 alternativas e o tempo restante, **sem dizer qual é a certa** | |
| 8 | T2 (Ana) | Digite `RESULTADO 1` | `ERRO rodada_nao_encerrada` (a resposta certa só sai depois) | |
| 9 | T2 (Ana) | Digite `RESPONDER 1 1` (certa) | `OK` | |
| 10 | T3 (Bruno) | Digite `RESPONDER 1 2` (errada) | `OK` | |
| 11 | T4 (Carla) | **Não responda.** Espere os 20 segundos | Aparece `[AVISO] RODADA_ENCERRADA 1` nos três. A rodada fechou por tempo | |
| 12 | T2 (Ana) | Digite `RESULTADO 1` | `RESULTADO\|1\|1\|Ana\|Ana:1,Bruno:0,Carla:0` (só a Ana pontuou) | |

O teste 12 pode ser feito a qualquer momento depois do encerramento, até durante a rodada 2.

Os testes 7 e 12 também cobrem os testes **30** e **31**: depois do aviso UDP, a pergunta e o resultado oficiais vêm por TCP.

| # | O que foi comprovado | Resultado |
|---|---|---|
| 30 | Depois do `RODADA_ABERTA`, a pergunta oficial veio por TCP (teste 7) | |
| 31 | Depois do `RODADA_ENCERRADA`, o resultado oficial veio por TCP (teste 12) | |

### Rodada 2: resposta duplicada, alternativa inválida e resposta atrasada

Espere aparecer `[AVISO] RODADA_ABERTA 2`. O Bruno **não responde** nesta rodada.

| # | Onde | Faça | O que deve aparecer | Resultado |
|---|---|---|---|---|
| 13a | T2 (Ana) | Digite `RESPONDER 2 2` | `OK` | |
| 13b | T2 (Ana) | Digite `RESPONDER 2 2` de novo | `ERRO resposta_duplicada` | |
| 18 | T4 (Carla) | Digite `RESPONDER 2 9` | `ERRO alternativa_invalida` | |
| 14 | T4 (Carla) | Digite `RESPONDER 2 1` e **não aperte Enter**. Espere aparecer `[AVISO] RODADA_ENCERRADA 2` e aí aperte Enter na hora | `ERRO rodada_encerrada` (resposta atrasada) | |

No teste 14 você tem 5 segundos depois do aviso. Se demorar mais que isso, a resposta vira `ERRO rodada_invalida`, porque a rodada 3 já abriu.

**Enquanto espera a rodada 2 acabar**, prepare a rodada 3, deixando digitado **sem apertar Enter**:

- T2 (Ana): `RESPONDER 3 1`
- T3 (Bruno): `RESPONDER 3 3`

### Rodada 3: a rodada fecha antes dos 20 segundos

Espere aparecer `[AVISO] RODADA_ABERTA 3`. Só então:

| # | Onde | Faça | O que deve aparecer | Resultado |
|---|---|---|---|---|
| 15a | T2 (Ana) | Aperte Enter (`RESPONDER 3 1`, errada) | `OK` | |
| 15b | T3 (Bruno) | Aperte Enter (`RESPONDER 3 3`, certa) | `OK` | |
| 15c | T4 (Carla) | Digite `RESPONDER 3 3` (certa) | `OK` | |
| 15 | Os três | Olhe a tela | `[AVISO] RODADA_ENCERRADA 3` aparece **logo depois** da terceira resposta, sem esperar os 20 segundos | |

Placar neste ponto: Ana 2, Bruno 1, Carla 1.

### Rodada 4: partida já iniciada

Espere aparecer `[AVISO] RODADA_ABERTA 4`. **Ninguém responde a pergunta** nesta rodada (isso é importante para o empate no final). A rodada dura os 20 segundos inteiros, então dá tempo:

| # | Onde | Faça | O que deve aparecer | Resultado |
|---|---|---|---|---|
| 5 | T2 (Ana) | Digite `INICIAR` | `ERRO ja_iniciada` | |
| 16 | T3 (Bruno) | Digite `RESPONDER 99 1` | `ERRO rodada_invalida` | |
| 6 | T5 | Rode `python cliente.py`, IP `127.0.0.1`, nome `Davi` | `Recebido: ERRO partida_em_andamento`. Depois digite `sair` para fechar esse cliente | |

O teste 6 pode passar da rodada 4 sem problema: ele funciona em qualquer momento depois do início.

### Rodada 5: um jogador desconecta

Espere aparecer `[AVISO] RODADA_ABERTA 5`.

| # | Onde | Faça | O que deve aparecer | Resultado |
|---|---|---|---|---|
| 22 | T3 (Bruno) | Digite `sair` | O cliente do Bruno fecha. No T1, o servidor **não cai** e aparece `jogador Bruno saiu (conexão encerrada)` | |
| 23a | T2 (Ana) | Digite `RESPONDER 5 1` (errada) | `OK` | |
| 23b | T4 (Carla) | Digite `RESPONDER 5 3` (certa) | `OK` | |
| 23 | T2 e T4 | Olhe a tela | `[AVISO] RODADA_ENCERRADA 5` aparece logo, **sem esperar o Bruno** | |
| 24 | T2 (Ana) | Digite `PLACAR` | `PLACAR\|Ana:2,Bruno:1,Carla:2` (o Bruno continua na lista, com o ponto que tinha) | |

Depois do `sair`, não aparece mais nenhum aviso no T3. É o esperado.

### Rodadas 6 a 10: terminar a partida

Em cada rodada, espere o `[AVISO] RODADA_ABERTA` e responda **a alternativa certa** no T2 (Ana) e no T4 (Carla). Assim que as duas respondem, a rodada fecha.

| Rodada | Digite no T2 (Ana) e no T4 (Carla) |
|---|---|
| 6 | `RESPONDER 6 1` |
| 7 | `RESPONDER 7 1` |
| 8 | `RESPONDER 8 3` |
| 9 | `RESPONDER 9 2` |
| 10 | `RESPONDER 10 4` |

### Fim de jogo

| # | Onde | Faça | O que deve aparecer | Resultado |
|---|---|---|---|---|
| 27 | T2 e T4 | Espere uns 5 segundos depois da rodada 10 | `[AVISO] FIM_JOGO` | |
| 28 | T2 (Ana) | Digite `PLACAR` | `PLACAR\|Ana:7,Bruno:1,Carla:7\|FIM\|Ana,Carla` | |
| 29 | | Confira o fim da linha | **Empate:** as duas vencedoras aparecem depois do `FIM` | |

Se alguma resposta saiu diferente do roteiro, os pontos mudam e pode não dar empate. O que importa no teste 28 é o formato `PLACAR|...|FIM|<vencedores>`, com quem tem mais pontos. Para o teste 29 (empate), o jeito mais simples é repetir a partida.

Para encerrar: digite `sair` no T2 e no T4. No T1, pare o servidor com Ctrl+C (no Windows, se o Ctrl+C não responder, feche a janela).

---

## D. Conferência do log

O arquivo `servidor.log` fica na pasta `servidor/`. Abra em qualquer editor de texto, ou no terminal:

```bash
cat servidor.log
```

No Windows, use `type servidor.log`.

Cada linha tem este formato: `HH:MM:SS | protocolo | direção | origem/destino | tipo | conteúdo`.

- [ ] Há linhas `TCP | RECEBIDO` e `TCP | ENVIADO`
- [ ] Há linhas `UDP | ENVIADO` (`RODADA_ABERTA`, `RODADA_ENCERRADA`, `FIM_JOGO`)
- [ ] Há linhas `ESTADO | - | - | MUDANCA` para: jogador entrou, jogador saiu, partida iniciada, rodada aberta, rodada encerrada (com placar) e fim do jogo

**Guarde este arquivo:** ele faz parte da entrega e não vai para o Git. Copie para um lugar seguro antes de rodar o servidor de novo.

---

## E. Se algo der errado

- **Perdi o tempo de um teste numa rodada.** Faça o mesmo teste na rodada seguinte, trocando o número da rodada no comando (por exemplo, `RESPONDER 3 9` em vez de `RESPONDER 2 9`). A rodada 4 está folgada para isso.
- **Apertei Enter antes da rodada abrir.** A resposta é `ERRO rodada_encerrada` e não conta como resposta. Digite de novo quando a rodada abrir.
- **Quero recomeçar do zero.** Feche os clientes (`sair`), pare o servidor no T1 (Ctrl+C), apague o `servidor.log` e volte para o passo [A.2](#a2-iniciar-o-servidor-t1).
- **O cliente não conecta.** O servidor não está rodando no T1, ou o IP digitado está errado.
- **O servidor não inicia e reclama da porta 5000.** Já existe outro servidor rodando. Feche o terminal antigo.

---

## F. Extras (opcionais)

### F.1 Entre computadores

Funciona entre computadores que estejam na **mesma rede**. A rede da Unisinos não permite, então lá o teste é local.

1. Rode o `servidor.py` em uma máquina e descubra o IP dela com `ip -4 a` (Linux) ou `ipconfig` (Windows).
2. Libere a porta TCP **5000** no firewall dessa máquina.
3. Nas outras máquinas, rode `python cliente.py` e digite o IP do servidor no lugar de `127.0.0.1`.

---

## G. O que entregar

- [ ] `servidor.py`, `cliente.py` e `perguntas.txt` (pasta `servidor/`)
- [ ] `README.md` com os campos `[PREENCHER]` resolvidos e os nomes de todos os integrantes
- [ ] Este roteiro, com a coluna **Resultado** preenchida (é o relatório de testes)
- [ ] `servidor.log` de uma execução com 3 clientes (fica em `servidor/` e não vai para o Git)
- [ ] Captura do Wireshark (`.pcapng`), feita com o `ROTEIRO_WIRESHARK.md`

---

## H. Limitações conhecidas (para mencionar se perguntarem)

- Não há validação de nomes repetidos nem de nomes com `,` `:` `|`, que quebrariam o placar.
- Se o organizador sair antes do início, ninguém mais consegue iniciar.
- Não há reconexão durante a partida (o enunciado não exige).
