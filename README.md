# Quiz Competitivo em Rede

Trabalho Prático 2 de Redes: um quiz de 10 rodadas em que os jogadores mandam os comandos por **TCP** e recebem os avisos de rodada por **UDP**.

**Integrantes:** Athos Nunes Kolling, Júlia Roos Costa, Murilo Teribele Carvalho, Luiz Eduardo Haubert

## Sumário

1. [Tema, linguagem e dependências](#1-tema-linguagem-e-dependências)
2. [Arquivos](#2-arquivos)
3. [Como executar](#3-como-executar)
4. [Endereços e portas](#4-endereços-e-portas)
5. [Regras do jogo](#5-regras-do-jogo)
6. [Protocolo](#6-protocolo)
7. [Servidor: concorrência e estado](#7-servidor-concorrência-e-estado)
8. [Logs](#8-logs)
9. [Tratamento de erros e limitações](#9-tratamento-de-erros-e-limitações)
10. [Entrega](#10-entrega)
11. [Interface web (extra)](#11-interface-web-extra)

---

## 1. Tema, linguagem e dependências

| | |
|---|---|
| **Tema** | Opção 1, Quiz competitivo em rede |
| **Linguagem** | Python 3 ([PREENCHER: versão usada nos testes]). Funciona em Python 3.8 ou superior |
| **Dependências** | Nenhuma além da biblioteca padrão (`socket`, `threading`, `time`) |
| **Sistema usado nos testes** | [PREENCHER: Windows ou Linux] |

A interface web (extra, [seção 11](#11-interface-web-extra)) usa também a biblioteca `websockets` e o Node.js.

---

## 2. Arquivos

```
servidor/     servidor.py, cliente.py e perguntas.txt (o trabalho em si)
roteiros/     roteiro de testes e roteiro de captura no Wireshark
ponte/        ponte.py (extra)
interface/    interface web (extra)
design/       desenho de referência da interface (extra)
```

O trabalho em si fica na pasta `servidor/`:

| Arquivo | O que é |
|---|---|
| `servidor.py` | Servidor. Guarda o estado oficial da partida e grava o log. |
| `cliente.py` | Cliente de texto (terminal). |
| `perguntas.txt` | 10 perguntas, uma por linha. Deve ficar na mesma pasta do `servidor.py`. |
| `servidor.log` | Criado pelo servidor ao rodar (log da execução). |

Formato de cada linha do `perguntas.txt`, em que `correta` é um número de 1 a 4:

```
pergunta|alt1|alt2|alt3|alt4|correta
```

Extras, fora do que o enunciado exige ([seção 11](#11-interface-web-extra)): `ponte/ponte.py`, a pasta `interface/` e os arquivos do Docker (`docker-compose.yml` na raiz e um `Dockerfile` em cada pasta).

---

## 3. Como executar

**1) Inicie o servidor**, em um terminal na pasta `servidor/`:

```bash
cd servidor
python servidor.py
```

**2) Inicie os clientes**, em outros terminais (um por jogador, mínimo 3), também na pasta `servidor/`:

```bash
python cliente.py
```

O cliente pergunta o IP do servidor (use `127.0.0.1` se estiver no mesmo computador) e o nome do jogador (pode ter espaços).

**3) Comece a partida.** O primeiro jogador a entrar é o organizador. Com pelo menos 3 jogadores conectados, ele digita `INICIAR`.

**4) Jogue**, digitando os comandos na linha `>`:

| Comando | O que faz |
|---|---|
| `PERGUNTA` | Mostra a pergunta da rodada aberta. |
| `RESPONDER <rodada> <1 a 4>` | Envia a resposta, por exemplo `RESPONDER 1 3`. |
| `RESULTADO <rodada>` | Mostra o resultado de uma rodada já encerrada. |
| `PLACAR` | Mostra a pontuação atual (e os vencedores ao fim do jogo). |
| `INICIAR` | Só o organizador: começa a partida. |
| `sair` | Encerra o cliente. |

Os avisos de rodada chegam sozinhos na tela, marcados com `[AVISO]`.

> **Atenção:** antes de uma execução oficial, apague o `servidor.log` antigo, porque o servidor acrescenta linhas ao arquivo (não o recria).

### Em várias máquinas

Funciona entre computadores que estejam na **mesma rede** (por exemplo, o Wi-Fi de casa):

1. Rode o `servidor.py` em uma máquina e descubra o IP dela com `ipconfig` (Windows) ou `ip -4 a` (Linux).
2. Nas outras máquinas, rode o `cliente.py` e digite esse IP no lugar de `127.0.0.1`.
3. Se não conectar, libere a porta TCP 5000 no firewall da máquina do servidor. Se os `[AVISO]` não chegarem, libere o UDP de entrada nas máquinas dos clientes.

A rede da Unisinos não permite conexão entre máquinas dos alunos, então lá o teste é feito em um computador só, com `127.0.0.1`.

---

## 4. Endereços e portas

| Protocolo | Endereço | Para que serve |
|---|---|---|
| **TCP** | Servidor em `0.0.0.0:5000` | Comandos dos jogadores e respostas do servidor. |
| **UDP** | Cada cliente usa uma porta livre escolhida pelo sistema (bind na porta 0) | Avisos enviados pelo servidor. |

A porta UDP de cada cliente é informada ao servidor na mensagem `ENTRAR`. O servidor envia os avisos para o IP de origem da conexão TCP daquele cliente e a porta UDP informada.

---

## 5. Regras do jogo

- Mínimo de 3 jogadores para iniciar. Só o organizador (primeiro a entrar, id 1) inicia.
- Depois do início, novos jogadores não entram (`ERRO partida_em_andamento`).
- São 10 rodadas, uma pergunta por rodada, cada rodada com 20 segundos.
- A rodada fecha por tempo ou quando todos os jogadores ativos já responderam.
- Cada jogador responde uma vez por rodada. Acerto vale 1 ponto; erro e ausência de resposta valem 0.
- Há uma pausa de 5 segundos entre rodadas.
- Ao fim das 10 rodadas, o `PLACAR` traz também os vencedores. Em caso de empate, todos os empatados no maior placar são vencedores.
- Jogador que desconecta fica inativo, mantém seus pontos e não trava as rodadas.

---

## 6. Protocolo

### 6.1 Formato

- Todas as mensagens são texto UTF-8, uma por linha, terminada em `\n`.
- Nos comandos do cliente, os campos são separados por espaço. Nas respostas do servidor, usa-se `|` entre os campos, `,` entre itens de uma lista e `:` entre nome e pontos.
- O TCP é um fluxo de bytes, sem fronteira de mensagem. Por isso o servidor acumula os bytes recebidos em um buffer e só processa uma mensagem quando encontra o `\n`. Uma mensagem que chega em dois pedaços é respondida uma vez; duas mensagens no mesmo envio geram duas respostas.
- O UDP preserva a fronteira de cada datagrama, então os avisos não precisam de `\n`.
- O nome do jogador é tudo que vem depois da porta UDP, então pode ter espaços (por exemplo: `Ana Paula`).

### 6.2 Mensagens TCP (cliente envia, servidor responde)

**`ENTRAR <porta_udp> <nome>`**

- Sucesso: `OK <id> <organizador>`
- O id é 1, 2, 3... pela ordem de chegada. O organizador é 1 para o primeiro jogador e 0 para os demais.
- Erros: `ERRO partida_em_andamento` (partida já iniciada), `ERRO ja_cadastrado` (a conexão já tem um jogador)

**`INICIAR`**

- Sucesso: `OK`
- Erros: `ERRO nao_organizador`, `ERRO ja_iniciada`, `ERRO poucos_jogadores` (menos de 3 ativos)

**`PERGUNTA`**

- Sucesso: `PERGUNTA|<rodada>|<texto>|<alt1>|<alt2>|<alt3>|<alt4>|<segundos_restantes>`
- A resposta correta nunca é enviada.
- Erro: `ERRO sem_rodada_aberta`

**`RESPONDER <rodada> <alternativa>`**

- Sucesso: `OK`
- Erros: `ERRO nao_cadastrado`, `ERRO rodada_encerrada`, `ERRO rodada_invalida`, `ERRO alternativa_invalida`, `ERRO resposta_duplicada`

**`RESULTADO <rodada>`**

- Sucesso: `RESULTADO|<rodada>|<correta>|<quem_acertou>|<placar>`
- `quem_acertou` é uma lista de nomes separados por vírgula, ou `ninguem`.
- Erro: `ERRO rodada_nao_encerrada`

**`PLACAR`**

- Sucesso: `PLACAR|<nome>:<pontos>,<nome>:<pontos>,...`
- Depois do fim do jogo, acrescenta no final: `|FIM|<vencedores>`

**Qualquer outra coisa**

- Resposta: `ERRO comando_desconhecido`

### 6.3 Avisos UDP (servidor envia, sem resposta)

| Aviso | Quando é enviado |
|---|---|
| `RODADA_ABERTA <rodada>` | Quando uma rodada começa. |
| `RODADA_ENCERRADA <rodada>` | Quando a rodada fecha (o resultado já está disponível em `RESULTADO`). |
| `FIM_JOGO` | Depois da última rodada (o placar final está disponível em `PLACAR`). |

O aviso UDP serve só para notificar. Os dados oficiais sempre vêm por TCP, então o jogo funciona mesmo se um datagrama se perder: o jogador pode consultar `PERGUNTA`, `RESULTADO` e `PLACAR` quando quiser.

### 6.4 Exemplos

Nos exemplos, `->` é TCP e `=>` é UDP.

Entrada de três jogadores:

```
Ana -> ENTRAR 52311 Ana
servidor -> OK 1 1
Bruno -> ENTRAR 52312 Bruno
servidor -> OK 2 0
Carla -> ENTRAR 52313 Carla Souza
servidor -> OK 3 0
```

Início e primeira rodada:

```
Ana -> INICIAR
servidor -> OK
servidor => RODADA_ABERTA 1
Bruno -> PERGUNTA
servidor -> PERGUNTA|1|<texto da pergunta>|<alt1>|<alt2>|<alt3>|<alt4>|17
Bruno -> RESPONDER 1 3
servidor -> OK
Bruno -> RESPONDER 1 2
servidor -> ERRO resposta_duplicada
Carla -> RESPONDER 1 9
servidor -> ERRO alternativa_invalida
servidor => RODADA_ENCERRADA 1
Ana -> RESULTADO 1
servidor -> RESULTADO|1|3|Bruno|Ana:0,Bruno:1,Carla Souza:0
```

Fim do jogo:

```
servidor => FIM_JOGO
Ana -> PLACAR
servidor -> PLACAR|Ana:4,Bruno:6,Carla Souza:6|FIM|Bruno,Carla Souza
```

---

## 7. Servidor: concorrência e estado

- A thread principal só aceita conexões (`accept`) e cria uma thread por cliente.
- Uma thread separada (`controlar_partida`) conduz as rodadas e o cronômetro.
- O estado oficial fica no servidor: lista de jogadores (nome, IP, porta UDP, ativo, pontos), rodada atual, respostas da rodada e resultados já calculados.
- Um `Lock` protege o cadastro na lista de jogadores e outro `Lock` protege a escrita no arquivo de log.
- O id do jogador é sua posição na lista mais 1. Quem sai da conexão fica `ativo = False`.

---

## 8. Logs

O servidor grava, no arquivo `servidor.log` e na tela, uma linha por evento no formato:

```
HH:MM:SS | protocolo | direção | origem/destino | tipo | conteúdo
```

| Campo | Valores |
|---|---|
| protocolo | `TCP`, `UDP` ou `ESTADO`. |
| direção | `RECEBIDO`, `ENVIADO` ou `-` (mudanças de estado). |
| origem/destino | `ip:porta` do cliente (ou `-` nas mudanças de estado). |
| tipo | Primeira palavra da mensagem (`ENTRAR`, `OK`, `RODADA_ABERTA`...) ou `MUDANCA`. |
| conteúdo | A mensagem completa, ou a descrição da mudança de estado. |

Exemplo:

```
14:02:11 | TCP | RECEBIDO | 127.0.0.1:51822 | ENTRAR | ENTRAR 52311 Ana
14:02:11 | ESTADO | - | - | MUDANCA | jogador Ana entrou com id 1
14:02:11 | TCP | ENVIADO | 127.0.0.1:51822 | OK | OK 1 1
14:02:40 | UDP | ENVIADO | 127.0.0.1:52311 | RODADA_ABERTA | RODADA_ABERTA 1
```

Mudanças de estado registradas: entrada e saída de jogador, início da partida, rodada aberta, rodada encerrada (com o placar) e fim do jogo.

---

## 9. Tratamento de erros e limitações

- Mensagem desconhecida ou malformada recebe `ERRO` e a conexão continua.
- Cliente que fecha a conexão não derruba o servidor nem trava a rodada: ele deixa de ser contado entre os ativos.

Limitações conhecidas:

- Não há validação de nomes repetidos nem de nomes com os caracteres `,` `:` ou `|`.
- Se o organizador sair antes do início, ninguém mais consegue iniciar.
- O servidor não aceita reconexão de um jogador durante a partida.

---

## 10. Entrega

O ZIP contém:

- `servidor.py`, `cliente.py` e `perguntas.txt`
- este README
- o relatório de testes
- o log de uma execução com 3 clientes
- a captura do Wireshark (`.pcapng`, interface de loopback quando o teste é local)

Os roteiros usados para os testes e para a captura ficam na pasta `roteiros/`.

---

## 11. Interface web (extra)

Não faz parte do que o enunciado exige. O `servidor.py` e o protocolo são os mesmos; a interface é só outro cliente.

O navegador não abre socket TCP nem UDP, só WebSocket. Por isso existe a ponte (`ponte/ponte.py`): para cada aba do navegador ela abre um TCP e um UDP até o servidor, como o `cliente.py` faz, e traduz as mensagens para JSON.

```
navegador <- WebSocket (JSON) -> ponte.py <- TCP + UDP -> servidor.py
```

**Portas:** a ponte escuta em 8765 (WebSocket) e a página é servida em 5173.

### Com Docker

A partir da raiz do projeto:

```bash
docker compose up --build
```

Abra `http://localhost:5173` em 3 abas. No campo de IP do servidor, digite `servidor`.

### Sem Docker

Em três terminais, a partir da raiz do projeto:

```bash
cd servidor && python servidor.py
```

```bash
pip install websockets && python ponte/ponte.py
```

```bash
cd interface && npm install && npm run dev
```

Abra `http://localhost:5173` em 3 abas. No campo de IP do servidor, digite `127.0.0.1`.

### Observações

- A ponte escuta em `localhost` por padrão. Para aceitar navegadores de outras máquinas (é o que o Docker faz), defina a variável de ambiente `HOST_PONTE=0.0.0.0` antes de iniciá-la.
- O arquivo `interface/README.md` explica o que faz cada arquivo da interface.
