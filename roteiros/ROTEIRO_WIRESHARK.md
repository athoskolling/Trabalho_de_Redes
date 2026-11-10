# Roteiro com Wireshark: Quiz Competitivo em Rede

Este roteiro **complementa** o `ROTEIRO_DE_TESTES.md`. Você executa os mesmos testes, mas com o Wireshark capturando, para entregar o arquivo `.pcapng` e mostrar na prática o TCP e o UDP funcionando.

**Como preencher:** nas colunas **Achei?** e **Resultado**, escreva `OK` e, se quiser, o número do pacote na captura.

## Sumário

1. [Preparação da captura](#1-preparação-da-captura)
2. [Execução](#2-execução)
3. [O que procurar na captura](#3-o-que-procurar-na-captura) (W1 a W12)
4. [O que cada achado prova](#4-o-que-cada-achado-prova)
5. [Teste extra: mensagem TCP partida](#5-teste-extra-mensagem-tcp-partida-no-wireshark) (W13)
6. [Entre computadores](#6-entre-computadores)
7. [Entrega](#7-entrega)

---

## 1. Preparação da captura

1. Abra o Wireshark.
2. Escolha a interface:
   - **`lo` (loopback)** se servidor e clientes estão na mesma máquina (`127.0.0.1`).
   - A **placa de rede** (Wi-Fi ou Ethernet) se o teste for entre computadores.
3. Dê um clique duplo na interface para começar a capturar.
4. Só **depois** inicie o servidor e os clientes, para a captura pegar os `ENTRAR`.

> No Linux, o Wireshark pode pedir permissão para capturar. Se não listar interfaces, rode com `sudo wireshark`.

### Filtros úteis (digite na barra de filtro)

| Filtro | O que mostra |
|---|---|
| `tcp.port == 5000` | Só os comandos e respostas TCP do jogo |
| `udp` | Só os avisos UDP (use `udp && !dns` se aparecer ruído) |
| `tcp.port == 5000 \|\| udp` | Tudo do jogo (use este durante a captura) |
| `tcp.port == 5000 && tcp.len > 0` | TCP só com dados, sem os ACKs vazios |
| `tcp.flags.syn == 1` | O início das conexões (handshake) |
| `tcp.flags.fin == 1 \|\| tcp.flags.reset == 1` | O encerramento das conexões |

Para ler o conteúdo de uma mensagem: clique no pacote, depois **botão direito > Follow > TCP Stream**. Para os avisos UDP, olhe a seção **Data** no painel de detalhes do pacote.

---

## 2. Execução

1. Faça a captura começar.
2. Inicie o servidor, a partir da raiz do projeto:

   ```bash
   cd servidor && rm -f servidor.log && python servidor.py
   ```

3. Execute o `ROTEIRO_DE_TESTES.md` com os 3 clientes (`python cliente.py`).
4. No mínimo, passe por: entrada dos 3 jogadores, `INICIAR`, uma rodada completa, uma resposta duplicada, uma entrada inválida e a saída de um cliente.
5. Pare a captura (botão quadrado vermelho).
6. Salve: **File > Save As**, nome `captura_quiz.pcapng`.

---

## 3. O que procurar na captura

Cada item abaixo é uma evidência de um requisito do enunciado. Marque quando achar.

| # | O que procurar | Filtro | Como reconhecer | Achei? |
|---|---|---|---|---|
| W1 | **Handshake TCP** dos 3 clientes | `tcp.flags.syn == 1` | Pacotes `SYN`, `SYN/ACK`, `ACK` para a porta 5000, de 3 portas de origem diferentes | |
| W2 | **Cadastro** | `tcp.port == 5000 && tcp.len > 0` | `ENTRAR <porta_udp> <nome>` do cliente e `OK <id> <organizador>` do servidor | |
| W3 | **A porta UDP no ENTRAR é a porta de destino dos avisos** | `udp` | A porta enviada no `ENTRAR` aparece como porta de destino do datagrama UDP | |
| W4 | **Aviso UDP de abertura** | `udp` | Datagrama com `RODADA_ABERTA 1`, um para cada jogador ativo | |
| W5 | **Pergunta por TCP** | `tcp.port == 5000` | `PERGUNTA` e a resposta `PERGUNTA\|1\|...\|<segundos>`, **sem** a alternativa correta | |
| W6 | **Resposta do jogador** | `tcp.port == 5000` | `RESPONDER 1 <n>` e `OK` | |
| W7 | **Resposta duplicada** | `tcp.port == 5000` | Segundo `RESPONDER` seguido de `ERRO resposta_duplicada` | |
| W8 | **Aviso UDP de encerramento** | `udp` | Datagrama com `RODADA_ENCERRADA 1` | |
| W9 | **Resultado oficial por TCP** | `tcp.port == 5000` | `RESULTADO 1` e `RESULTADO\|1\|<correta>\|<acertaram>\|<placar>` | |
| W10 | **Entrada inválida** | `tcp.port == 5000` | `BLABLA` seguido de `ERRO comando_desconhecido`, e a conexão continua | |
| W11 | **Fim do jogo** | `udp` e `tcp.port == 5000` | `FIM_JOGO` por UDP e `PLACAR\|...\|FIM\|<vencedores>` por TCP | |
| W12 | **Encerramento de um cliente** | `tcp.flags.fin == 1 \|\| tcp.flags.reset == 1` | `FIN` ou `RST` da conexão do jogador que saiu, e as outras conexões seguem trocando dados | |

---

## 4. O que cada achado prova

- **UDP só avisa, TCP é oficial (W4, W5, W8, W9):** o datagrama UDP traz só o tipo e o número da rodada. Os dados da pergunta, o resultado e o placar chegam por TCP.
- **UDP não tem confirmação:** repare que não há resposta a nenhum datagrama UDP, ao contrário do TCP, que tem `ACK`.
- **TCP é um fluxo de bytes (teste 25 do roteiro base):** se você rodar o teste da mensagem partida (`PLAC` e depois `AR\n`), vão aparecer **dois** segmentos TCP de dados, e o servidor só responde depois do segundo.
- **Cada cliente é uma conexão diferente (W1):** as portas de origem mudam, então a identificação não depende só do IP.

---

## 5. Teste extra: mensagem TCP partida no Wireshark

Com a captura rodando, execute:

```bash
(printf 'PLAC'; sleep 1; printf 'AR\n') | nc 127.0.0.1 5000
```

Procure em `tcp.port == 5000 && tcp.len > 0`:

1. Um segmento do cliente com `PLAC` (4 bytes).
2. Cerca de 1 segundo depois, outro com `AR\n` (3 bytes).
3. **Uma única** resposta `PLACAR|...` do servidor, depois do segundo segmento.

| # | Teste | Resultado |
|---|---|---|
| W13 | Dois segmentos do cliente e uma só resposta do servidor | |

---

## 6. Entre computadores

- Capture na máquina do **servidor**, na placa de rede (não em `lo`).
- Libere a porta TCP **5000** no firewall.
- Os IPs dos pacotes serão os das máquinas, em vez de `127.0.0.1`.
- Os avisos UDP irão para o IP de cada cliente e para a porta UDP que ele informou no `ENTRAR`.

---

## 7. Entrega

- [ ] `captura_quiz.pcapng` salvo
- [ ] Opcional: um print do filtro `tcp.port == 5000 || udp` mostrando uma rodada, para o relatório
- [ ] Os itens W1 a W13 marcados como encontrados (ou anotados, se faltou algum)
