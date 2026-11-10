# Ponte entre a interface web e o servidor do Quiz.
#
# O navegador não sabe abrir socket TCP nem UDP, só WebSocket. Esta ponte faz o
# papel do cliente.py: para cada aba aberta no navegador (uma conexão WebSocket)
# ela abre um TCP e um UDP até o servidor.py e traduz as mensagens:
#
#   navegador  <-- WebSocket (JSON) -->  ponte.py  <-- TCP + UDP (texto) -->  servidor.py
#
# Executar:  .venv/bin/python ponte.py     (o servidor.py precisa estar rodando)

import asyncio
import json
import os
import websockets

PORTA_SERVIDOR = 5000        # porta TCP do servidor.py
PORTA_PONTE = 8765           # porta do WebSocket que o navegador usa
# Endereço onde a ponte escuta: localhost por padrão; no Docker vem 0.0.0.0 pela variável HOST_PONTE
HOST_PONTE = os.environ.get("HOST_PONTE", "localhost")


class AvisosUDP(asyncio.DatagramProtocol):
    """Recebe os avisos UDP do servidor e joga cada um numas fila."""

    def __init__(self, fila: asyncio.Queue):
        self.fila = fila

    def datagram_received(self, dados, origem):
        # UDP preserva a fronteira: um datagrama = um aviso, sem precisar de \n
        self.fila.put_nowait(dados.decode("utf-8").strip())


class Sessao:
    """Uma sessão = um jogador = uma aba do navegador."""

    def __init__(self, ws):
        self.ws = ws
        self.leitor = None            # leitura do TCP
        self.escritor = None          # escrita no TCP
        self.udp = None               # transporte UDP
        self.fila_avisos = asyncio.Queue()
        self.trava = asyncio.Lock()   # um pedido TCP por vez (resposta tem que casar com o pedido)
        self.tarefa_avisos = None

    # ---------- utilidades ----------
    async def enviar(self, objeto: dict):
        """Manda um JSON para o navegador."""
        await self.ws.send(json.dumps(objeto, ensure_ascii=False))

    async def pedir(self, linha: str) -> str:
        """Envia um comando por TCP e devolve a linha de resposta do servidor.

        O TCP é um fluxo de bytes sem fronteira. Por isso a resposta só é considerada
        completa quando chega o \\n (readline faz esse acúmulo para nós).
        """
        async with self.trava:
            self.escritor.write((linha + "\n").encode("utf-8"))
            await self.escritor.drain()
            resposta = await self.leitor.readline()
        if not resposta:
            raise ConnectionError("servidor_desconectado")
        return resposta.decode("utf-8").strip()

    # ---------- mensagens vindas do navegador ----------
    async def entrar(self, ip: str, nome: str):
        """Abre o TCP e o UDP com o servidor e envia o ENTRAR."""
        try:
            self.leitor, self.escritor = await asyncio.wait_for(
                asyncio.open_connection(ip, PORTA_SERVIDOR), timeout=5)
        except (OSError, asyncio.TimeoutError):
            await self.enviar({"tipo": "erro", "codigo": "servidor_indisponivel"})
            return

        # UDP na porta 0: o sistema escolhe uma porta livre (igual ao cliente.py)
        loop = asyncio.get_running_loop()
        self.udp, _ = await loop.create_datagram_endpoint(
            lambda: AvisosUDP(self.fila_avisos), local_addr=("0.0.0.0", 0))
        porta_udp = self.udp.get_extra_info("sockname")[1]

        resposta = await self.pedir(f"ENTRAR {porta_udp} {nome}")
        partes = resposta.split(" ")
        if partes[0] == "OK":
            await self.enviar({"tipo": "entrou", "id": int(partes[1]),
                               "organizador": partes[2] == "1"})
            self.tarefa_avisos = asyncio.create_task(self.tratar_avisos())
        else:
            await self.enviar({"tipo": "erro", "codigo": resposta.replace("ERRO ", "")})

    async def comando_simples(self, linha: str, acao: str):
        """INICIAR e RESPONDER: a resposta é só OK ou ERRO <codigo>."""
        resposta = await self.pedir(linha)
        if resposta == "OK":
            await self.enviar({"tipo": "ok", "acao": acao})
        else:
            await self.enviar({"tipo": "erro", "codigo": resposta.replace("ERRO ", "")})

    # ---------- avisos UDP: servidor -> ponte -> navegador ----------
    async def tratar_avisos(self):
        """Fica esperando avisos UDP e busca por TCP os dados de cada um."""
        while True:
            aviso = await self.fila_avisos.get()
            tipo = aviso.split(" ")[0]
            if tipo == "RODADA_ABERTA":
                # o aviso só notifica; os dados oficiais vêm por TCP
                await self.buscar_pergunta()
            elif tipo == "RODADA_ENCERRADA":
                rodada = aviso.split(" ")[1]
                await self.buscar_resultado(rodada)
            elif tipo == "FIM_JOGO":
                await self.buscar_placar_final()

    async def buscar_pergunta(self):
        """Pede a pergunta da rodada aberta e entrega ao navegador."""
        # PERGUNTA|<rodada>|<texto>|<alt1>|<alt2>|<alt3>|<alt4>|<segundos>
        resposta = await self.pedir("PERGUNTA")
        campos = resposta.split("|")
        if campos[0] != "PERGUNTA":
            return
        await self.enviar({"tipo": "pergunta", "rodada": int(campos[1]),
                           "texto": campos[2], "alternativas": campos[3:7],
                           "segundos": int(campos[7])})

    async def buscar_resultado(self, rodada: str):
        """Pede o resultado da rodada encerrada e entrega ao navegador."""
        # RESULTADO|<rodada>|<correta>|<quem_acertou>|<placar>
        resposta = await self.pedir(f"RESULTADO {rodada}")
        campos = resposta.split("|")
        if campos[0] != "RESULTADO":
            return
        acertaram = [] if campos[3] == "ninguem" else campos[3].split(",")
        await self.enviar({"tipo": "resultado", "rodada": int(campos[1]),
                           "correta": int(campos[2]), "acertaram": acertaram,
                           "placar": ler_placar(campos[4])})

    async def buscar_placar_final(self):
        """Pede o placar final com os vencedores e entrega ao navegador."""
        # PLACAR|<nome>:<pontos>,...|FIM|<vencedores>
        resposta = await self.pedir("PLACAR")
        campos = resposta.split("|")
        vencedores = campos[3].split(",") if len(campos) > 3 else []
        await self.enviar({"tipo": "fim", "placar": ler_placar(campos[1]),
                           "vencedores": vencedores})

    def fechar(self):
        """Encerra a sessão: o servidor vê o TCP fechar e marca o jogador como inativo."""
        if self.tarefa_avisos:
            self.tarefa_avisos.cancel()
        if self.escritor:
            self.escritor.close()
        if self.udp:
            self.udp.close()


def ler_placar(texto: str) -> list:
    """'Ana:0,Bruno:1' -> [{'nome': 'Ana', 'pontos': 0}, {'nome': 'Bruno', 'pontos': 1}]"""
    placar = []
    for item in texto.split(","):
        if ":" in item:
            nome, pontos = item.rsplit(":", 1)
            placar.append({"nome": nome, "pontos": int(pontos)})
    return placar


async def atender(ws):
    """Chamada uma vez para cada aba que conecta."""
    sessao = Sessao(ws)
    try:
        async for texto in ws:
            try:
                msg = json.loads(texto)
                tipo = msg["tipo"]
                if tipo == "entrar":
                    await sessao.entrar(msg["ip"], msg["nome"])
                elif tipo == "iniciar":
                    await sessao.comando_simples("INICIAR", "iniciar")
                elif tipo == "responder":
                    await sessao.comando_simples(
                        f"RESPONDER {msg['rodada']} {msg['alternativa']}", "responder")
                else:
                    await sessao.enviar({"tipo": "erro", "codigo": "comando_desconhecido"})
            except (json.JSONDecodeError, KeyError, ValueError):
                await sessao.enviar({"tipo": "erro", "codigo": "mensagem_invalida"})
    except ConnectionError as e:
        # o servidor caiu: avisa o navegador antes de fechar
        try:
            await sessao.enviar({"tipo": "erro", "codigo": str(e)})
        except websockets.ConnectionClosed:
            pass
    except websockets.ConnectionClosed:
        pass
    finally:
        sessao.fechar()


async def main():
    """Sobe o servidor WebSocket que o navegador usa."""
    async with websockets.serve(atender, HOST_PONTE, PORTA_PONTE):
        print(f"Ponte rodando em ws://{HOST_PONTE}:{PORTA_PONTE}")
        await asyncio.Future()  # roda para sempre


if __name__ == "__main__":
    asyncio.run(main())
