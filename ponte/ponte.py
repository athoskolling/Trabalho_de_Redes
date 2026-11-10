# Ponte entre a interface web e o servidor do Quiz.
#
# O navegador não sabe abrir socket TCP nem UDP, só WebSocket. Esta ponte faz o
# papel do cliente.py: para cada aba aberta no navegador (uma conexão WebSocket)
# ela abre um TCP e um UDP até o servidor.py e traduz as mensagens:
#
#   navegador  <-- WebSocket (JSON) -->  ponte.py  <-- TCP + UDP (texto) -->  servidor.py
#
# Executar:  python ponte/ponte.py     (precisa de: pip install websockets; o servidor.py precisa estar rodando)

import json
import os
import socket
import threading
from websockets.exceptions import ConnectionClosed
from websockets.sync.server import serve

PORTA_SERVIDOR = 5000        # porta TCP do servidor.py
PORTA_PONTE = 8765           # porta do WebSocket que o navegador usa
# Endereço onde a ponte escuta: localhost por padrão; no Docker vem 0.0.0.0 pela variável HOST_PONTE
HOST_PONTE = os.environ.get("HOST_PONTE", "localhost")


def ler_placar(texto):
    """'Ana:0,Bruno:1' -> [{'nome': 'Ana', 'pontos': 0}, {'nome': 'Bruno', 'pontos': 1}]"""
    placar = []
    for item in texto.split(","):
        if ":" in item:
            nome, pontos = item.rsplit(":", 1)
            placar.append({"nome": nome, "pontos": int(pontos)})
    return placar


class Sessao:
    """Uma sessão = um jogador = uma aba do navegador."""

    def __init__(self, ws):
        self.ws = ws
        self.tcp = None                 # socket TCP com o servidor (None antes do ENTRAR)
        self.leitor = None              # leitura do TCP linha por linha
        self.udp = None                 # socket UDP que recebe os avisos
        self.trava = threading.Lock()   # um pedido TCP por vez (a resposta tem que casar com o pedido)

    def enviar(self, objeto):
        """Manda um JSON para o navegador."""
        self.ws.send(json.dumps(objeto, ensure_ascii=False))

    def pedir(self, linha):
        """Envia um comando por TCP e devolve a linha de resposta do servidor."""
        with self.trava:
            self.tcp.sendall((linha + "\n").encode("utf-8"))
            # O TCP é um fluxo de bytes sem fronteira: readline acumula até chegar o \n
            resposta = self.leitor.readline()
        if not resposta:
            raise ConnectionError("servidor_desconectado")
        return resposta.strip()

    # ---------- mensagens vindas do navegador ----------
    def entrar(self, ip, nome):
        """Abre o TCP e o UDP com o servidor e envia o ENTRAR."""
        try:
            self.tcp = socket.create_connection((ip, PORTA_SERVIDOR), timeout=5)
        except OSError:
            self.enviar({"tipo": "erro", "codigo": "servidor_indisponivel"})
            return
        self.tcp.settimeout(None)
        self.leitor = self.tcp.makefile("r", encoding="utf-8", newline="\n")

        # UDP na porta 0: o sistema escolhe uma porta livre (igual ao cliente.py)
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind(("0.0.0.0", 0))
        self.udp.settimeout(1)          # para a thread dos avisos perceber quando a sessão fecha
        porta_udp = self.udp.getsockname()[1]

        resposta = self.pedir(f"ENTRAR {porta_udp} {nome}")
        partes = resposta.split(" ")
        if partes[0] == "OK":
            self.enviar({"tipo": "entrou", "id": int(partes[1]), "organizador": partes[2] == "1"})
            threading.Thread(target=self.tratar_avisos, daemon=True).start()
        else:
            self.enviar({"tipo": "erro", "codigo": resposta.replace("ERRO ", "")})

    def comando_simples(self, linha, acao):
        """INICIAR e RESPONDER: a resposta é só OK ou ERRO <codigo>."""
        resposta = self.pedir(linha)
        if resposta == "OK":
            self.enviar({"tipo": "ok", "acao": acao})
        else:
            self.enviar({"tipo": "erro", "codigo": resposta.replace("ERRO ", "")})

    # ---------- avisos UDP: servidor -> ponte -> navegador ----------
    def tratar_avisos(self):
        """Thread que espera os avisos UDP e busca por TCP os dados de cada um."""
        try:
            while True:
                try:
                    # UDP preserva a fronteira: um datagrama = um aviso, sem precisar de \n
                    dados, origem = self.udp.recvfrom(1024)
                except socket.timeout:
                    continue
                partes = dados.decode("utf-8").split()
                # o aviso só notifica; os dados oficiais vêm por TCP
                if partes[0] == "RODADA_ABERTA":
                    self.buscar_pergunta()
                elif partes[0] == "RODADA_ENCERRADA":
                    self.buscar_resultado(partes[1])
                elif partes[0] == "FIM_JOGO":
                    self.buscar_placar_final()
        except (OSError, ConnectionClosed):
            pass  # a sessão foi fechada

    def buscar_pergunta(self):
        """Pede a pergunta da rodada aberta e entrega ao navegador."""
        # PERGUNTA|<rodada>|<texto>|<alt1>|<alt2>|<alt3>|<alt4>|<segundos>
        campos = self.pedir("PERGUNTA").split("|")
        if campos[0] == "PERGUNTA":
            self.enviar({"tipo": "pergunta", "rodada": int(campos[1]), "texto": campos[2],
                         "alternativas": campos[3:7], "segundos": int(campos[7])})

    def buscar_resultado(self, rodada):
        """Pede o resultado da rodada encerrada e entrega ao navegador."""
        # RESULTADO|<rodada>|<correta>|<quem_acertou>|<placar>
        campos = self.pedir(f"RESULTADO {rodada}").split("|")
        if campos[0] == "RESULTADO":
            acertaram = [] if campos[3] == "ninguem" else campos[3].split(",")
            self.enviar({"tipo": "resultado", "rodada": int(campos[1]), "correta": int(campos[2]),
                         "acertaram": acertaram, "placar": ler_placar(campos[4])})

    def buscar_placar_final(self):
        """Pede o placar final com os vencedores e entrega ao navegador."""
        # PLACAR|<nome>:<pontos>,...|FIM|<vencedores>
        campos = self.pedir("PLACAR").split("|")
        vencedores = campos[3].split(",") if len(campos) > 3 else []
        self.enviar({"tipo": "fim", "placar": ler_placar(campos[1]), "vencedores": vencedores})

    def fechar(self):
        """Encerra a sessão: o servidor vê o TCP fechar e marca o jogador como inativo."""
        if self.tcp:
            self.tcp.close()
        if self.udp:
            self.udp.close()


def atender(ws):
    """Chamada em uma thread própria para cada aba que conecta."""
    sessao = Sessao(ws)
    try:
        for texto in ws:
            try:
                msg = json.loads(texto)
                tipo = msg["tipo"]
                if tipo == "entrar":
                    sessao.entrar(msg["ip"], msg["nome"])
                elif sessao.tcp is None:
                    sessao.enviar({"tipo": "erro", "codigo": "nao_cadastrado"})
                elif tipo == "iniciar":
                    sessao.comando_simples("INICIAR", "iniciar")
                elif tipo == "responder":
                    sessao.comando_simples(f"RESPONDER {msg['rodada']} {msg['alternativa']}", "responder")
                else:
                    sessao.enviar({"tipo": "erro", "codigo": "comando_desconhecido"})
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                sessao.enviar({"tipo": "erro", "codigo": "mensagem_invalida"})
    except ConnectionClosed:
        pass  # o navegador fechou a aba
    except OSError:
        # o servidor caiu: avisa o navegador antes de fechar
        try:
            sessao.enviar({"tipo": "erro", "codigo": "servidor_desconectado"})
        except ConnectionClosed:
            pass
    finally:
        sessao.fechar()


if __name__ == "__main__":
    # Sobe o servidor WebSocket que o navegador usa (uma thread por aba)
    with serve(atender, HOST_PONTE, PORTA_PONTE) as servidor:
        print(f"Ponte rodando em ws://{HOST_PONTE}:{PORTA_PONTE}")
        servidor.serve_forever()
