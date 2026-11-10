# Roteiro de Testes: Quiz Competitivo em Rede

> Este é o roteiro **base**, sem Wireshark. A captura de pacotes está em `ROTEIRO_WIRESHARK.md`.

Este roteiro cobre tudo que o enunciado do Trabalho Prático 2 pede para demonstrar e para registrar no relatório de testes. Cada teste tem **o que fazer**, **o que deve acontecer** e uma coluna **Resultado** para você preencher durante a execução.

> **Dica:** use o `cliente.py` (terminal) para os testes. Ele deixa você mandar comandos inválidos, o que a interface web não permite. A interface web é um extra.

---

## 1. Preparação

### 1.1 Iniciar o servidor

Apague o log antigo, porque o servidor acrescenta linhas ao arquivo em vez de recriá-lo.

```bash
cd ~/Projects/Trabalho_de_Redes/servidor
rm -f servidor.log
python servidor.py
```

Deve aparecer: `10 perguntas carregadas` e `Servidor TCP aguardando conexão...`.

### 1.2 Iniciar os clientes

Abra **um terminal por jogador** (mínimo 3):

```bash
cd ~/Projects/Trabalho_de_Redes/servidor
python cliente.py
```

- **IP do servidor:** `127.0.0.1` se for na mesma máquina. Se for entre computadores, use o IP da máquina do servidor.
- **Nome:** use `Ana`, `Bruno` e `Carla`, nessa ordem de entrada. A Ana será a organizadora.

### 1.3 Comandos do jogador

| Comando | O que faz |
|---|---|
| `INICIAR` | Começa a partida (só o organizador) |
| `PERGUNTA` | Mostra a pergunta da rodada aberta |
| `RESPONDER <rodada> <1 a 4>` | Envia a resposta, por exemplo `RESPONDER 1 3` |
| `RESULTADO <rodada>` | Mostra o resultado de uma rodada encerrada |
| `PLACAR` | Mostra a pontuação atual |
| `sair` | Fecha o cliente |

Os avisos UDP chegam sozinhos na tela, marcados com `[AVISO]`.

---

## 2. Testes de cadastro e início

| # | O que fazer | O que deve acontecer | Resultado |
|---|---|---|---|
| 1 | Ana, Bruno e Carla entram, um por vez | `OK 1 1` (Ana, organizadora), `OK 2 0`, `OK 3 0` | |
| 2 | Antes de a Carla entrar, a Ana digita `INICIAR` | `ERRO poucos_jogadores` | |
| 3 | O Bruno digita `INICIAR` | `ERRO nao_organizador` | |
| 4 | Com os 3 conectados, a Ana digita `INICIAR` | `OK`, e os 3 clientes recebem `[AVISO] RODADA_ABERTA 1` | |
| 5 | A Ana digita `INICIAR` de novo | `ERRO ja_iniciada` | |
| 6 | Um 4º cliente tenta entrar depois do início | `ERRO partida_em_andamento` | |
| 6b | Num cliente já cadastrado, digite `ENTRAR 5555 Outro` | `ERRO ja_cadastrado` (não cria segundo jogador) | |

**Requisitos cobertos:** registro por nome, mínimo de 3 jogadores, só o organizador inicia, identificação por nome e porta UDP (e não só pelo IP).

---

## 3. Testes de rodada (demonstração obrigatória)

Faça estes testes durante as rodadas 1 a 4. A resposta correta de cada pergunta está em `perguntas.txt`, no último campo da linha.

| # | O que fazer | O que deve acontecer | Resultado |
|---|---|---|---|
| 7 | Nos 3 clientes: `PERGUNTA` | Mesma pergunta para todos, com o tempo restante, **sem a resposta correta** | |
| 8 | Durante a rodada, `RESULTADO 1` | `ERRO rodada_nao_encerrada` (a resposta correta só sai depois) | |
| 9 | **Resposta correta:** Ana responde a alternativa certa | `OK` | |
| 10 | **Resposta incorreta:** Bruno responde uma alternativa errada | `OK` | |
| 11 | **Ausência de resposta:** a Carla não responde. Espere os 20 s | A rodada fecha por tempo, e a Carla fica com 0 pontos nela | |
| 12 | Depois do `RODADA_ENCERRADA 1`, digite `RESULTADO 1` | `RESULTADO\|1\|<correta>\|<quem acertou>\|<placar>`, com a Ana pontuando | |
| 13 | Na rodada 2, a Ana responde duas vezes | 1ª `OK`, 2ª `ERRO resposta_duplicada` | |
| 14 | Na rodada 2, depois do `RODADA_ENCERRADA 2`, a Carla digita `RESPONDER 2 1` | `ERRO rodada_encerrada` (resposta atrasada) | |
| 15 | Na rodada 3, os 3 respondem rápido | A rodada fecha **antes** dos 20 s | |
| 16 | Digite `RESPONDER 99 1` | `ERRO rodada_invalida` | |

**Requisitos cobertos:** mesma pergunta para todos, uma resposta por rodada, janela de 20 s, encerramento antecipado, 1 ponto por acerto, rejeição de duplicada e atrasada, resposta correta só depois do encerramento.

---

## 4. Testes de entrada inválida (demonstração obrigatória)

O servidor deve responder com erro e **continuar funcionando**.

| # | O que digitar | O que deve acontecer | Resultado |
|---|---|---|---|
| 17 | `BLABLA` | `ERRO comando_desconhecido` | |
| 18 | `RESPONDER 4 9` (alternativa fora de 1 a 4) | `ERRO alternativa_invalida` | |
| 19 | `RESPONDER 4` (faltando campo) | `ERRO comando_desconhecido` | |
| 20 | Apenas Enter (linha vazia) | `ERRO comando_desconhecido` | |
| 21 | Logo em seguida, `PLACAR` | Resposta normal, provando que o servidor seguiu de pé | |

---

## 5. Teste de desconexão (demonstração obrigatória)

| # | O que fazer | O que deve acontecer | Resultado |
|---|---|---|---|
| 22 | Em uma rodada aberta, feche o Bruno com `sair` (ou Ctrl+C) | O servidor **não cai**. No log aparece `jogador Bruno saiu (conexão encerrada)` | |
| 23 | Os outros dois jogadores respondem | A rodada fecha assim que os **ativos** responderem, sem esperar o Bruno | |
| 24 | `PLACAR` em um cliente que sobrou | O Bruno continua listado, com os pontos que já tinha | |

**Requisito coberto:** encerrar as rodadas mesmo com cliente desconectado.

---

## 6. Teste do TCP com mensagem partida em dois pedaços

O enunciado exige acumular bytes até achar o fim da mensagem (`\n`). Prove isso no servidor, com o `nc` (netcat):

```bash
(printf 'PLAC'; sleep 1; printf 'AR\n') | nc 127.0.0.1 5000
```

**O que deve acontecer:** o servidor espera o `\n` e só depois responde `PLACAR|...`. Ele não trata `PLAC` como uma mensagem completa. Para ver as duas mensagens no mesmo envio:

```bash
printf 'PLACAR\nPLACAR\n' | nc 127.0.0.1 5000
```

Isso deve gerar **duas respostas**.

| # | Teste | Resultado |
|---|---|---|
| 25 | Mensagem partida (`PLAC` + `AR\n`) gera uma resposta | |
| 26 | Duas mensagens num envio geram duas respostas | |

---

## 7. Fim de jogo e placar final

Deixe a partida chegar à décima rodada. São cerca de 5 minutos: 10 rodadas, até 20 s cada, mais 5 s de pausa.

| # | O que fazer | O que deve acontecer | Resultado |
|---|---|---|---|
| 27 | Ao fim da rodada 10 | Todos recebem `[AVISO] FIM_JOGO` | |
| 28 | `PLACAR` | `PLACAR\|<nome>:<pts>,...\|FIM\|<vencedores>` | |
| 29 | **Empate:** nas rodadas, faça dois jogadores com a mesma pontuação máxima | Os vencedores listam **todos** os empatados | |

---

## 8. O UDP é só um aviso (TCP é a fonte oficial)

| # | O que fazer | O que deve acontecer | Resultado |
|---|---|---|---|
| 30 | Depois de um `RODADA_ABERTA`, use `PERGUNTA` por TCP | A pergunta oficial vem por TCP | |
| 31 | Depois de um `RODADA_ENCERRADA`, use `RESULTADO n` por TCP | O resultado oficial vem por TCP | |

Se um datagrama UDP se perder, o jogador continua conseguindo consultar tudo por TCP.

---

## 9. Conferência do log

Abra o `servidor.log` ao final:

```bash
cat servidor.log
```

Cada linha deve ter este formato: `HH:MM:SS | protocolo | direção | origem/destino | tipo | conteúdo`.

- [ ] Há linhas `TCP RECEBIDO` e `TCP ENVIADO`
- [ ] Há linhas `UDP ENVIADO` (`RODADA_ABERTA`, `RODADA_ENCERRADA`, `FIM_JOGO`)
- [ ] Há linhas `ESTADO MUDANCA` para: jogador entrou, jogador saiu, partida iniciada, rodada aberta, rodada encerrada (com placar) e fim do jogo

---

## 10. Entre computadores (opcional)

O enunciado prefere testes entre máquinas. Se possível:

1. Rode o `servidor.py` em uma máquina e descubra o IP dela com `ip -4 a` (Linux) ou `ipconfig` (Windows).
2. Libere a porta TCP **5000** no firewall dessa máquina.
3. Nas outras máquinas, rode `python cliente.py` e digite o IP do servidor.

---

## 11. Rodando com a interface web (extra)

Não faz parte do que o enunciado exige.

```bash
cd ~/Projects/Trabalho_de_Redes && sudo docker compose up --build
```

Abra `http://localhost:5173` em 3 abas. No campo de IP, digite `servidor`. Em outra máquina, abra `http://IP_DA_ANFITRIA:5173`.

---

## 12. O que entregar

- [ ] `servidor.py`, `cliente.py` e `perguntas.txt`
- [ ] `README.md` com os campos `[PREENCHER]` resolvidos e os nomes de todos os integrantes
- [ ] Este roteiro, com a coluna **Resultado** preenchida (é o relatório de testes)
- [ ] `servidor.log` de uma execução com 3 clientes
- [ ] Captura do Wireshark (`.pcapng`), feita com o `ROTEIRO_WIRESHARK.md`

---

## 13. Limitações conhecidas (para mencionar se perguntarem)

- Não há validação de nomes repetidos nem de nomes com `,` `:` `|`, que quebrariam o placar.
- Se o organizador sair antes do início, ninguém mais consegue iniciar.
- Não há reconexão durante a partida (o enunciado não exige).
