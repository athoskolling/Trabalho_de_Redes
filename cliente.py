
# Cliente do Quiz Competitivo em Rede.
 
# - TCP: envia os comandos digitados pelo jogador e mostra a resposta do servidor.
# - UDP: recebe os avisos do servidor (RODADA_ABERTA, RODADA_ENCERRADA, FIM_JOGO) em uma thread separada, para não travar a digitação.

 
import socket
import threading
 
# ---------- Conexão TCP com o servidor ----------
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
servidor_ip = input("IP do servidor: ")  # 127.0.0.1 se o servidor estiver no mesmo computador
client.connect((servidor_ip, 5000))
 
nome = input("Seu nome: ")
 
# ---------- Socket UDP para receber avisos ----------
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind(("0.0.0.0", 0))  # porta 0: o sistema escolhe uma porta livre (permite vários clientes no mesmo PC)
porta_udp = udp.getsockname()[1]  # getsockname() devolve (ip, porta)
 
# ---------- Cadastro no servidor ----------
# Protocolo: ENTRAR porta_udp nome  ->  OK id organizador
mensagem = f"ENTRAR {porta_udp} {nome}\n"
client.sendall(mensagem.encode('utf-8'))
 
data = client.recv(1024)
print('Recebido:', data.decode('utf-8'))

# O socket TCP é usado por duas threads (a do teclado e a dos avisos, que busca a
# pergunta sozinha). O lock garante que cada envio receba a sua própria resposta.
lock_tcp = threading.Lock()


def enviar(comando):
    # Envia um comando pelo TCP e devolve a resposta do servidor (sem o \n).
    with lock_tcp:
        client.sendall((comando + "\n").encode('utf-8'))  # o \n marca o fim da mensagem
        return client.recv(1024).decode('utf-8').strip()

 
# ---------- Alternativas por letra ----------
# O jogador pode digitar só "a", "b", "c" ou "d"; o cliente converte para
# "RESPONDER <rodada> <1-4>" antes de enviar. O servidor não muda.
LETRAS = {"a": "1", "b": "2", "c": "3", "d": "4"}
rodada_conhecida = None  # última rodada que o cliente conhece (aviso UDP ou resposta PERGUNTA)


def traduzir_comando(comando):
    # Devolve o comando no formato do protocolo, ou None se não der para enviar.
    texto = comando.strip()

    # Só a letra: "a" -> "RESPONDER <rodada> 1"
    if texto.lower() in LETRAS:
        if rodada_conhecida is None:
            print("Rodada desconhecida. Digite PERGUNTA primeiro.")
            return None
        return f"RESPONDER {rodada_conhecida} {LETRAS[texto.lower()]}"

    # Forma completa com letra: "RESPONDER 1 a" -> "RESPONDER 1 1"
    partes = texto.split()
    if len(partes) == 3 and partes[0] == "RESPONDER" and partes[2].lower() in LETRAS:
        return f"RESPONDER {partes[1]} {LETRAS[partes[2].lower()]}"

    return comando  # qualquer outro comando segue igual


def mostrar_resposta(texto):
    # Mostra a PERGUNTA com as letras a) b) c) d); o resto é impresso como veio.
    global rodada_conhecida
    campos = texto.split("|")
    if campos[0] == "PERGUNTA" and len(campos) == 8:
        rodada_conhecida = int(campos[1])  # informação oficial (TCP) atualiza a rodada
        print(f"Rodada {campos[1]}: {campos[2]}")
        for letra, alternativa in zip("abcd", campos[3:7]):
            print(f"  {letra}) {alternativa}")
        print(f"Tempo restante: {campos[7]}s  (responda digitando a, b, c ou d)")
    else:
        print(texto)


# ---------- Escuta dos avisos UDP ----------
def escutar_udp():
    global rodada_conhecida
    while True:
        dados, origem = udp.recvfrom(1024)
        texto = dados.decode("utf-8")
        partes = texto.split()
        print("\n[AVISO]", texto)
        if len(partes) == 2 and partes[0] == "RODADA_ABERTA" and partes[1].isdigit():
            rodada_conhecida = int(partes[1])
            # A pergunta aparece sozinha: o cliente pede a PERGUNTA oficial por TCP
            mostrar_resposta(enviar("PERGUNTA"))
 
 
aviso = threading.Thread(target=escutar_udp, daemon=True)
aviso.start()
 
# ---------- Laço principal: comandos do jogador ----------
# Exemplos: INICIAR, PERGUNTA, a, RESPONDER 1 3, RESPONDER 1 c, RESULTADO 1, PLACAR
while True:
    comando = input("> ")
    if comando == "sair":
        break
    comando = traduzir_comando(comando)
    if comando is None:
        continue
    mostrar_resposta(enviar(comando))
 
client.close()
 