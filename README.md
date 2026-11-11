QUIZ COMPETITIVO EM REDE

Integrantes: Athos Nunes Kolling, Júlia Roos Costa, Murilo Teribele e Luiz Haubert


1. TEMA, LINGUAGEM E DEPENDENCIAS

Tema: Opção 1, Quiz competitivo em rede.
Linguagem: Python. Funciona em Python 3.8 ou superior.
Dependências: nenhuma além da biblioteca padrão (socket, threading, time).
Sistema usado nos testes: Windows.


2. ARQUIVOS

servidor.py: servidor. Guarda o estado oficial da partida e grava o log.
cliente.py: cliente de texto (terminal). Mostra as alternativas como a), b), c), d) e aceita a resposta pela letra.
perguntas.txt: 10 perguntas, uma por linha, no formato pergunta|alt1|alt2|alt3|alt4|correta (correta é um número de 1 a 4). Deve ficar na mesma pasta do servidor.py.
servidor.log: criado pelo servidor ao rodar (log da execução).


3. COMO EXECUTAR

1) Abra um terminal na pasta do projeto e inicie o servidor:
   python servidor.py

2) Em outros terminais (um por jogador, mínimo 3), inicie os clientes:
   python cliente.py
   O cliente pergunta o IP do servidor (use 127.0.0.1 se estiver no mesmo computador) e o nome do jogador (pode ter espaços).

3) O primeiro jogador a entrar é o organizador. Com pelo menos 3 jogadores conectados, ele digita INICIAR. A primeira pergunta aparece na hora.

4) As perguntas passam sozinhas: cada pergunta aparece na tela de todos os jogadores, que têm 20 segundos para responder. Depois que a rodada fecha há uma pausa de 5 segundos e a próxima pergunta aparece.

5) Comandos do jogador (na linha ">"):
   a, b, c ou d: responde a pergunta que está na tela (forma mais simples de jogar).
   PERGUNTA: mostra de novo a pergunta da rodada aberta, com as alternativas a), b), c) e d) e o tempo restante.
   RESPONDER <rodada> <1 a 4>: forma completa da resposta, por exemplo RESPONDER 1 3.
   RESPONDER <rodada> <a a d>: forma completa com letra, por exemplo RESPONDER 1 c.
   RESULTADO <rodada>: mostra o resultado de uma rodada já encerrada.
   PLACAR: mostra a pontuação atual (e os vencedores ao fim do jogo).
   INICIAR: só o organizador, começa a partida.
   sair: encerra o cliente.

6) Os avisos de rodada chegam sozinhos na tela, marcados com [AVISO]. Quando chega o aviso de rodada aberta, o cliente pede a pergunta ao servidor por TCP e a mostra sem o jogador digitar nada. Do mesmo jeito, no aviso de rodada encerrada ele busca e mostra o RESULTADO da rodada, e no aviso de fim de jogo busca e mostra o PLACAR final. O aviso e a pergunta podem aparecer no meio da linha que você está digitando; isso é só visual, continue digitando e aperte Enter.

Exemplo de rodada no terminal do jogador:

   [AVISO] RODADA_ABERTA 1
   Rodada 1: O que o DNS faz?
     a) Traduz nomes de domínio em endereços IP
     b) Envia e-mails
     c) Transfere arquivos
     d) Atribui endereços IP automaticamente
   Tempo restante: 19s  (responda digitando a, b, c ou d)
   > a
   OK
   [AVISO] RODADA_ENCERRADA 1
   RESULTADO|1|1|Ana,Bruno|Ana:1,Bruno:1,Carla Souza:0
   (5 segundos depois)
   [AVISO] RODADA_ABERTA 2
   Rodada 2: ...

Se o aviso UDP se perder, a pergunta não aparece sozinha. O jogador digita PERGUNTA para buscá-la por TCP. Se ele digitar só a letra antes de o cliente saber qual é a rodada atual, o cliente não envia nada e mostra "Rodada desconhecida. Digite PERGUNTA primeiro.".

Antes de uma execução oficial, apague o servidor.log antigo, porque o servidor acrescenta linhas ao arquivo (não o recria).


4. ENDERECOS E PORTAS

TCP: servidor em 0.0.0.0:5000. Usado para os comandos dos jogadores e as respostas do servidor.
UDP: cada cliente usa uma porta livre escolhida pelo sistema (bind na porta 0). Usado para os avisos enviados pelo servidor.

A porta UDP de cada cliente é informada ao servidor na mensagem ENTRAR. O servidor envia os avisos para o IP de origem da conexão TCP daquele cliente e a porta UDP informada.


5. REGRAS DO JOGO

- Mínimo de 3 jogadores para iniciar. Só o organizador (primeiro a entrar, id 1) inicia.
- Depois do início, novos jogadores não entram (ERRO partida_em_andamento).
- São 10 rodadas, uma pergunta por rodada, cada rodada com 20 segundos.
- A rodada fecha por tempo ou quando todos os jogadores ativos já responderam.
- Cada jogador responde uma vez por rodada. Acerto vale 1 ponto; erro e ausência de resposta valem 0.
- Há uma pausa de 5 segundos entre rodadas. Depois da rodada 10 o servidor envia FIM_JOGO.
- Ao fim das 10 rodadas, o PLACAR traz também os vencedores. Em caso de empate, todos os empatados no maior placar são vencedores.
- Jogador que desconecta fica inativo, mantém seus pontos e não trava as rodadas.


6. PROTOCOLO

6.1 Formato

- Todas as mensagens são texto UTF-8, uma por linha, terminada em \n.
- Nos comandos do cliente, os campos são separados por espaço. Nas respostas do servidor, usa-se "|" entre os campos, "," entre itens de uma lista e ":" entre nome e pontos.
- O TCP é um fluxo de bytes, sem fronteira de mensagem. Por isso o servidor acumula os bytes recebidos em um buffer e só processa uma mensagem quando encontra o \n. Uma mensagem que chega em dois pedaços é respondida uma vez; duas mensagens no mesmo envio geram duas respostas.
- O UDP preserva a fronteira de cada datagrama, então os avisos não precisam de \n.
- O nome do jogador é tudo que vem depois da porta UDP, então pode ter espaços (por exemplo: Ana Paula).
- As letras a, b, c e d existem só na interface do cliente. No protocolo a alternativa é sempre um número de 1 a 4: o cliente converte a letra antes de enviar (a=1, b=2, c=3, d=4). Por exemplo, digitar "c" na rodada 1 envia "RESPONDER 1 3".
- Para saber o número da rodada ao converter a letra, o cliente usa o aviso UDP RODADA_ABERTA e, como informação oficial, o número que vem na resposta TCP de PERGUNTA.

6.2 Mensagens TCP (cliente envia, servidor responde)

ENTRAR <porta_udp> <nome>
  Sucesso: OK <id> <organizador>
  O id é 1, 2, 3... pela ordem de chegada. O organizador é 1 para o primeiro jogador e 0 para os demais.
  Erros: ERRO partida_em_andamento (partida já iniciada), ERRO porta_invalida (porta UDP fora de 1 a 65535), ERRO ja_cadastrado (ENTRAR repetido na mesma conexão)

INICIAR
  Sucesso: OK
  Erros: ERRO nao_organizador, ERRO ja_iniciada, ERRO poucos_jogadores (menos de 3 ativos)

PERGUNTA
  Sucesso: PERGUNTA|<rodada>|<texto>|<alt1>|<alt2>|<alt3>|<alt4>|<segundos_restantes>
  A resposta correta nunca é enviada.
  Erro: ERRO sem_rodada_aberta

RESPONDER <rodada> <alternativa>
  Sucesso: OK
  Erros: ERRO nao_cadastrado, ERRO rodada_encerrada, ERRO rodada_invalida, ERRO alternativa_invalida, ERRO resposta_duplicada

RESULTADO <rodada>
  Sucesso: RESULTADO|<rodada>|<correta>|<quem_acertou>|<placar>
  quem_acertou é uma lista de nomes separados por vírgula, ou "ninguem".
  Erro: ERRO rodada_nao_encerrada

PLACAR
  Sucesso: PLACAR|<nome>:<pontos>,<nome>:<pontos>,...
  Depois do fim do jogo, os jogadores vêm ordenados por pontos, do maior para o menor (classificação), e acrescenta no final: |FIM|<vencedores>

Qualquer outra coisa
  Resposta: ERRO comando_desconhecido

6.3 Avisos UDP (servidor envia, sem resposta)

RODADA_ABERTA <rodada>: quando uma rodada começa. Ao receber, o cliente envia PERGUNTA por TCP e mostra a pergunta.
RODADA_ENCERRADA <rodada>: quando a rodada fecha (o resultado já está disponível em RESULTADO). Ao receber, o cliente envia RESULTADO <rodada> por TCP e mostra o resultado.
FIM_JOGO: depois da última rodada (o placar final está disponível em PLACAR). Ao receber, o cliente envia PLACAR por TCP e mostra o placar final.

O aviso UDP serve só para notificar. Os dados oficiais sempre vêm por TCP, então o jogo funciona mesmo se um datagrama se perder: o jogador pode consultar PERGUNTA, RESULTADO e PLACAR quando quiser.

6.4 Exemplos (-> é TCP, => é UDP)

Entrada de três jogadores:

  Ana -> ENTRAR 52311 Ana
  servidor -> OK 1 1
  Bruno -> ENTRAR 52312 Bruno
  servidor -> OK 2 0
  Carla -> ENTRAR 52313 Carla Souza
  servidor -> OK 3 0

Início e primeira rodada:

  Ana -> INICIAR
  servidor -> OK
  servidor => RODADA_ABERTA 1
  Bruno -> PERGUNTA               (enviado sozinho pelo cliente ao receber o aviso)
  servidor -> PERGUNTA|1|<texto da pergunta>|<alt1>|<alt2>|<alt3>|<alt4>|19
  Bruno -> RESPONDER 1 3          (Bruno digitou "c" no terminal)
  servidor -> OK
  Bruno -> RESPONDER 1 2          (Bruno digitou "b")
  servidor -> ERRO resposta_duplicada
  Carla -> RESPONDER 1 9
  servidor -> ERRO alternativa_invalida
  servidor => RODADA_ENCERRADA 1
  Ana -> RESULTADO 1
  servidor -> RESULTADO|1|3|Bruno|Ana:0,Bruno:1,Carla Souza:0

Fim do jogo:

  servidor => FIM_JOGO
  Ana -> PLACAR
  servidor -> PLACAR|Bruno:6,Carla Souza:6,Ana:4|FIM|Bruno,Carla Souza


7. SERVIDOR: CONCORRENCIA E ESTADO

- A thread principal só aceita conexões (accept) e cria uma thread por cliente.
- Uma thread separada (controlar_partida) conduz as rodadas e o cronômetro.
- No cliente, duas threads usam o mesmo socket TCP (a do teclado e a dos avisos, que busca a pergunta, o resultado e o placar sozinha). Um Lock garante que cada comando receba a sua própria resposta.
- O estado oficial fica no servidor: lista de jogadores (nome, IP, porta UDP, ativo, pontos), rodada atual, respostas da rodada e resultados já calculados.
- Um Lock protege o cadastro na lista de jogadores e outro Lock protege a escrita no arquivo de log.
- Um terceiro Lock (lock_rodada) protege rodada_aberta e as respostas: a checagem e a gravação do RESPONDER e o fechamento da rodada (rodada_aberta = False e cálculo dos pontos) não se intercalam. Assim, toda resposta que recebeu OK é pontuada.
- O id do jogador é sua posição na lista mais 1. Quem sai da conexão fica ativo = False.


8. LOGS

O servidor grava, no arquivo servidor.log e na tela, uma linha por evento no formato:

  HH:MM:SS | protocolo | direção | origem/destino | tipo | conteúdo

- protocolo: TCP, UDP ou ESTADO.
- direção: RECEBIDO, ENVIADO ou "-" (mudanças de estado).
- origem/destino: ip:porta do cliente (ou "-" nas mudanças de estado).
- tipo: primeira palavra da mensagem (ENTRAR, OK, RODADA_ABERTA...) ou MUDANCA.
- conteúdo: a mensagem completa, ou a descrição da mudança de estado.

Exemplo:

  14:02:11 | TCP | RECEBIDO | 127.0.0.1:51822 | ENTRAR | ENTRAR 52311 Ana
  14:02:11 | ESTADO | - | - | MUDANCA | jogador Ana entrou com id 1
  14:02:11 | TCP | ENVIADO | 127.0.0.1:51822 | OK | OK 1 1
  14:02:40 | UDP | ENVIADO | 127.0.0.1:52311 | RODADA_ABERTA | RODADA_ABERTA 1

Mudanças de estado registradas: entrada e saída de jogador, início da partida, rodada aberta, rodada encerrada (com o placar) e fim do jogo.

Cada cliente também grava um log no arquivo cliente_<nome>.log (espaços do nome trocados por "_"), no mesmo formato, só no arquivo (não na tela). Ele registra as mensagens TCP enviadas e recebidas (origem/destino = ip:porta do servidor) e os avisos UDP recebidos (origem = ip:porta do servidor).

Exemplo:

  14:02:11 | TCP | ENVIADO | 127.0.0.1:5000 | ENTRAR | ENTRAR 52311 Ana
  14:02:11 | TCP | RECEBIDO | 127.0.0.1:5000 | OK | OK 1 1
  14:02:40 | UDP | RECEBIDO | 127.0.0.1:61234 | RODADA_ABERTA | RODADA_ABERTA 1


9. TRATAMENTO DE ERROS E LIMITACOES

- Mensagem desconhecida ou malformada recebe ERRO e a conexão continua.
- Cliente que fecha a conexão não derruba o servidor nem trava a rodada: ele deixa de ser contado entre os ativos.
- Limitações conhecidas:
  - Não há validação de nomes repetidos nem de nomes com os caracteres "," ":" ou "|".
  - Se o organizador sair antes do início, ninguém mais consegue iniciar.
  - O servidor não aceita reconexão de um jogador durante a partida.
  - Uma letra digitada durante a pausa de 5 segundos entre rodadas vai para a rodada que acabou de fechar e recebe ERRO rodada_encerrada; basta digitar de novo quando a nova pergunta aparecer.
  - Se todos os jogadores saírem, as rodadas restantes abrem e fecham na hora (não há ativos para esperar) e o jogo termina.


10. ENTREGA

O ZIP contém servidor.py, cliente.py, perguntas.txt, este README, o relatório de testes, o log de uma execução com 3 clientes e a captura do Wireshark (.pcapng, interface de loopback quando o teste é local).
