# Servidor do Quiz Competitivo em Rede.
# Integrantes do grupo: Athos Nunes Kolling, Júlia Roos Costa, Murilo Teribele Carvalho, Luiz Eduardo Haubert
 
# - TCP (porta 5000): comandos dos jogadores e respostas oficiais do servidor.
# - UDP: apenas avisos de eventos (RODADA_ABERTA, RODADA_ENCERRADA, FIM_JOGO).
# - O servidor guarda todo o estado da partida: jogadores, rodadas, respostas e placar.
# - Protocolo de texto: uma mensagem por linha, terminada em "\n".

 
import socket
import threading
import time
 
# ---------- Estado da partida ----------
jogadores = []  # cada jogador: nome, ip, udp_porta, ativo, pontos (id = posição + 1)
lock = threading.Lock()  # protege a lista de jogadores
partida_iniciada = False
rodada_atual = 0
rodada_aberta = False
respostas = {}  # id do jogador -> alternativa escolhida na rodada atual
tempo_fim = 0  # instante em que a rodada atual fecha
perguntas = []  # cada item: [texto, alt1, alt2, alt3, alt4, correta]
resultados = {}  # número da rodada -> mensagem RESULTADO já pronta
partida_terminou = False
lock_log = threading.Lock()  # evita linhas misturadas no arquivo de log
 
 
# ---------- Funções auxiliares ----------
def carregar_perguntas():
    # Lê perguntas.txt (formato: pergunta|alt1|alt2|alt3|alt4|correta).
    arquivo = open("perguntas.txt", encoding="utf-8")
    for linha in arquivo:
        perguntas.append(linha.strip().split("|"))
    arquivo.close()
 
 
def ler_mensagem(conn, buffer):
    # Lê do TCP até completar uma linha (TCP é fluxo de bytes, sem fronteira de mensagem).
    # Retorna (linha, resto do buffer); linha é None se o cliente fechou a conexão.
    while b"\n" not in buffer:
        dados = conn.recv(4096)
        if not dados:
            return None, buffer
        buffer += dados
 
    linha, resto = buffer.split(b"\n", 1)
    return linha.decode("utf-8"), resto
 
 
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 
 
def enviar_aviso(texto):
    # Envia um aviso UDP a todos os jogadores ativos.
    for j in jogadores:
        if j["ativo"]:
            udp.sendto(texto.encode("utf-8"), (j["ip"], j["udp_porta"]))
            registrar("UDP", "ENVIADO", f"{j['ip']}:{j['udp_porta']}", texto.split()[0], texto)
 
 
def registrar(protocolo, direcao, quem, tipo, conteudo):
    # Grava uma linha no log (arquivo e tela): hora | protocolo | direção | origem/destino | tipo | conteúdo.
    horario = time.strftime("%H:%M:%S")
    linha_log = f"{horario} | {protocolo} | {direcao} | {quem} | {tipo} | {conteudo}"
    with lock_log:
        arquivo = open("servidor.log", "a", encoding="utf-8")
        arquivo.write(linha_log + "\n")
        arquivo.close()
    print(linha_log)
 
 
# ---------- Controle das rodadas ----------
def controlar_partida():
    # Roda em uma thread própria: conduz as 10 rodadas e o fim do jogo.
    global rodada_atual, rodada_aberta, respostas, tempo_fim, partida_terminou
    for n in range(1, 11):
        # Abre a rodada: limpa as respostas e define o prazo de 20 segundos
        rodada_atual = n
        respostas = {}
        tempo_fim = time.time() + 20
        rodada_aberta = True
        enviar_aviso(f"RODADA_ABERTA {n}")
        registrar("ESTADO", "-", "-", "MUDANCA", f"rodada {n} aberta")
 
        # Espera até o tempo acabar ou até todos os jogadores ativos responderem
        while time.time() < tempo_fim:
            ativos = sum(1 for j in jogadores if j["ativo"])
            if len(respostas) >= ativos:
                break
            time.sleep(0.2)
 
        # Encerra a rodada e calcula a pontuação (1 ponto por acerto)
        rodada_aberta = False
        acertaram = []
        for id_jogador in list(respostas):
            if respostas[id_jogador] == perguntas[n - 1][5]:
                jogadores[id_jogador - 1]["pontos"] += 1
                acertaram.append(jogadores[id_jogador - 1]["nome"])
 
        # Guarda o resultado oficial; os jogadores o consultam depois via TCP
        placar = ",".join(f"{j['nome']}:{j['pontos']}" for j in jogadores)
        quem = ",".join(acertaram) if acertaram else "ninguem"
        resultados[n] = f"RESULTADO|{n}|{perguntas[n - 1][5]}|{quem}|{placar}"
        enviar_aviso(f"RODADA_ENCERRADA {n}")
        registrar("ESTADO", "-", "-", "MUDANCA", f"rodada {n} encerrada; placar {placar}")
        time.sleep(5)  # pausa entre rodadas
 
    partida_terminou = True
    enviar_aviso("FIM_JOGO")
    registrar("ESTADO", "-", "-", "MUDANCA", "fim do jogo")
 
 
# ---------- Atendimento de cada cliente (uma thread por conexão) ----------
def atender_cliente(conn, addr):
    # Recebe comandos de um cliente, responde a cada um e trata a saída dele.
    global partida_iniciada
    buffer = b""
    jogador_id = None  # só ganha valor depois de ENTRAR
    while True:
        linha, buffer = ler_mensagem(conn, buffer)
 
        if linha is None:
            break
        # Separa o comando em palavras e registra a mensagem recebida
        partes = linha.split()
        tipo = partes[0] if len(partes) > 0 else "VAZIA"
        registrar("TCP", "RECEBIDO", f"{addr[0]}:{addr[1]}", tipo, linha)
 
        # ENTRAR porta_udp nome -> OK id organizador (o primeiro a entrar é o organizador)
        if len(partes) > 0 and partes[0] == "ENTRAR" and jogador_id is not None:
            resposta = "ERRO ja_cadastrado"  # esta conexão já tem um jogador

        elif len(partes) > 0 and partes[0] == "ENTRAR" and partida_iniciada:
            resposta = "ERRO partida_em_andamento"
 
        elif len(partes) >= 3 and partes[0] == "ENTRAR" and partes[1].isdigit():
            with lock:
                jogadores.append({"nome": " ".join(partes[2:]), "ip": addr[0], "udp_porta": int(partes[1]), "ativo": True, "pontos":0})
                jogador_id = len(jogadores)
            registrar("ESTADO", "-", "-", "MUDANCA", f"jogador {jogadores[jogador_id - 1]['nome']} entrou com id {jogador_id}")
            if jogador_id == 1:
                resposta = "OK 1 1"
            else:
                resposta = f"OK {jogador_id} 0"
 
        # INICIAR: só o organizador, com pelo menos 3 jogadores ativos
        elif linha == "INICIAR":
            if jogador_id != 1:
                resposta = "ERRO nao_organizador"
            elif partida_iniciada:
                resposta = "ERRO ja_iniciada"
            elif sum(1 for j in jogadores if j["ativo"]) < 3:
                resposta = "ERRO poucos_jogadores"
            else:
                partida_iniciada = True
                resposta = "OK"
                partida = threading.Thread(target=controlar_partida, daemon=True)
                partida.start()
                registrar("ESTADO", "-", "-", "MUDANCA", "partida iniciada pelo organizador")
 
        # PERGUNTA: devolve a pergunta da rodada aberta e o tempo restante
        elif linha == "PERGUNTA":
            if not rodada_aberta:
                resposta = "ERRO sem_rodada_aberta"
            else:
                p = perguntas[rodada_atual - 1]
                segundos = int(tempo_fim - time.time())
                resposta = f"PERGUNTA|{rodada_atual}|{p[0]}|{p[1]}|{p[2]}|{p[3]}|{p[4]}|{segundos}"
 
        # RESPONDER rodada alternativa: valida a resposta (uma por jogador por rodada)
        elif len(partes) == 3 and partes[0] == "RESPONDER":
            if jogador_id is None:
                resposta = "ERRO nao_cadastrado"
            elif not rodada_aberta:
                resposta = "ERRO rodada_encerrada"
            elif partes[1] != str(rodada_atual):
                resposta = "ERRO rodada_invalida"
            elif partes[2] not in ("1", "2", "3", "4"):
                resposta = "ERRO alternativa_invalida"
            elif jogador_id in respostas:
                resposta = "ERRO resposta_duplicada"
            else:
                respostas[jogador_id] = partes[2]
                resposta = "OK"
 
        # RESULTADO n: só existe depois que a rodada n foi encerrada
        elif len(partes) == 2 and partes[0] == "RESULTADO":
            if partes[1].isdigit() and int(partes[1]) in resultados:
                resposta = resultados[int(partes[1])]
            else:
                resposta = "ERRO rodada_nao_encerrada"
 
        # PLACAR: pontuação atual; depois do fim do jogo inclui os vencedores (empate = vários)
        elif linha == "PLACAR":
            placar = ",".join(f"{j['nome']}:{j['pontos']}" for j in jogadores)
            resposta = "PLACAR|" + placar
            if partida_terminou:
                maior = max(j["pontos"] for j in jogadores)
                vencedores = ",".join(j["nome"] for j in jogadores if j["pontos"] == maior)
                resposta += f"|FIM|{vencedores}"
        else:
            resposta = "ERRO comando_desconhecido"
 
        # Registra e envia a resposta
        tipo_resposta = resposta.split("|")[0].split()[0]
        registrar("TCP", "ENVIADO", f"{addr[0]}:{addr[1]}", tipo_resposta, resposta)
 
        conn.sendall((resposta + "\n").encode("utf-8"))
 
    # Conexão encerrada: o jogador fica inativo, mas sua pontuação é mantida
    if jogador_id is not None:
        jogadores[jogador_id - 1]["ativo"] = False
        registrar("ESTADO", "-", "-", "MUDANCA", f"jogador {jogadores[jogador_id - 1]['nome']} saiu (conexão encerrada)")
 
    conn.close()
 
    print(f"Conexão encerrada com {addr}")
 
 
# ---------- Programa principal ----------
carregar_perguntas()
print(f"{len(perguntas)} perguntas carregadas")
 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 5000))
server.listen()
print("Servidor TCP aguardando conexão...")
 
# Uma thread para cada cliente que conecta
while True:
    conn, addr = server.accept()
    print(f"Conectado por {addr}")
    t = threading.Thread(target=atender_cliente, args=(conn, addr), daemon=True)
    t.start()