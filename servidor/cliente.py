
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


# ---------- Escuta dos avisos UDP ----------
def escutar_udp():
    while True:
        dados, origem = udp.recvfrom(1024)
        print("\n[AVISO]", dados.decode("utf-8"))


aviso = threading.Thread(target=escutar_udp, daemon=True)
aviso.start()

# ---------- Laço principal: comandos do jogador ----------
# Exemplos: INICIAR, PERGUNTA, RESPONDER 1 3, RESULTADO 1, PLACAR
while True:
    comando = input("> ")
    if comando == "sair":
        break
    client.sendall((comando + "\n").encode('utf-8'))  # o \n marca o fim da mensagem
    data = client.recv(1024)
    print(data.decode('utf-8').strip())

client.close()
