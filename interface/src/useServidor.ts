// Hook que conversa com a ponte.py por WebSocket e guarda o estado do jogo.
// Faz na interface web o papel que o cliente.py faz no terminal.

import { useCallback, useEffect, useRef, useState } from "react"
import type {
  ItemPlacar, MensagemEnviada, MensagemRecebida, Pergunta, Resultado,
} from "./types"

const URL_PONTE = `ws://${location.hostname}:8765`   // mesma máquina que serve a página

// Texto mostrado na tela para cada código de erro
export const MENSAGENS_ERRO: Record<string, string> = {
  servidor_indisponivel: "Não foi possível conectar ao servidor. Confira o IP.",
  servidor_desconectado: "O servidor caiu.",
  conexao_perdida: "A conexão com a ponte foi perdida.",
  ponte_indisponivel: "A ponte (ponte.py) não está rodando.",
  partida_em_andamento: "A partida já começou.",
  poucos_jogadores: "São necessários pelo menos 3 jogadores.",
  nao_organizador: "Só o organizador pode iniciar.",
  ja_iniciada: "A partida já foi iniciada.",
  resposta_duplicada: "Você já respondeu esta rodada.",
  rodada_encerrada: "A rodada já terminou.",
  mensagem_invalida: "Mensagem inválida.",
}

// Tudo que as telas precisam saber sobre a partida
export interface Estado {
  entrou: boolean
  nome: string
  organizador: boolean
  iniciada: boolean
  pergunta: Pergunta | null
  escolhida: number | null   // alternativa enviada (1 a 4) na rodada atual
  resultado: Resultado | null
  placar: ItemPlacar[]
  fim: { vencedores: string[] } | null
  erro: string | null
}

// Estado antes de entrar na partida
const inicial: Estado = {
  entrou: false, nome: "", organizador: false, iniciada: false,
  pergunta: null, escolhida: null, resultado: null, placar: [],
  fim: null, erro: null,
}

export function useServidor() {
  const ws = useRef<WebSocket | null>(null)              // conexão com a ponte
  const ultimaEscolha = useRef<number | null>(null)      // alternativa enviada, esperando o OK
  const [estado, setEstado] = useState<Estado>(inicial)

  // Fecha a conexão com a ponte
  const fechar = useCallback(() => {
    const atual = ws.current
    ws.current = null
    atual?.close()
  }, [])

  // fecha o WebSocket ao desmontar
  useEffect(() => fechar, [fechar])

  // Envia uma mensagem JSON para a ponte
  const enviar = useCallback((msg: MensagemEnviada) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(msg))
    }
  }, [])

  // Atualiza o estado conforme a mensagem que chegou da ponte
  const tratar = useCallback((msg: MensagemRecebida) => {
    switch (msg.tipo) {
      case "entrou":
        setEstado(e => ({ ...e, entrou: true, organizador: msg.organizador, erro: null }))
        break
      case "pergunta":
        ultimaEscolha.current = null
        setEstado(e => ({
          ...e, iniciada: true, pergunta: msg, escolhida: null,
          resultado: null, erro: null,
        }))
        break
      case "resultado":
        setEstado(e => ({
          ...e, iniciada: true, resultado: msg, placar: msg.placar,
          pergunta: null, erro: null,
        }))
        break
      case "fim":
        setEstado(e => ({
          ...e, iniciada: true, placar: msg.placar, pergunta: null,
          fim: { vencedores: msg.vencedores },
        }))
        break
      case "ok":
        // o servidor aceitou a resposta: só agora ela é marcada como enviada
        if (msg.acao === "responder") {
          setEstado(e => ({ ...e, escolhida: ultimaEscolha.current, erro: null }))
        }
        break
      case "erro":
        // sem servidor não há jogo: volta para a tela de entrada
        if (msg.codigo === "servidor_indisponivel" || msg.codigo === "servidor_desconectado") {
          fechar()
          setEstado({ ...inicial, erro: msg.codigo })
        } else {
          setEstado(e => {
            // ERRO no ENTRAR (ainda sem cadastro): volta para a tela inicial
            if (!e.entrou) { fechar(); return { ...inicial, erro: msg.codigo } }
            return { ...e, erro: msg.codigo }
          })
        }
        break
    }
  }, [fechar])

  // Abre o WebSocket e pede para entrar na partida
  const conectar = useCallback((ip: string, nome: string) => {
    fechar()
    setEstado({ ...inicial, nome })
    const socket = new WebSocket(URL_PONTE)
    ws.current = socket
    socket.onopen = () => enviar({ tipo: "entrar", ip, nome })
    socket.onmessage = ev => tratar(JSON.parse(ev.data) as MensagemRecebida)
    // "ws.current === socket" ignora eventos de uma conexão antiga já descartada
    socket.onerror = () => {
      if (ws.current === socket) {
        ws.current = null
        setEstado({ ...inicial, erro: "ponte_indisponivel" })
      }
    }
    socket.onclose = () => {
      if (ws.current === socket) {
        ws.current = null
        setEstado(e => ({ ...inicial, erro: e.erro ?? "conexao_perdida" }))
      }
    }
  }, [enviar, fechar, tratar])

  // Organizador: começa a partida
  const iniciar = useCallback(() => enviar({ tipo: "iniciar" }), [enviar])

  // Envia a alternativa escolhida na rodada
  const responder = useCallback((rodada: number, alternativa: 1 | 2 | 3 | 4) => {
    ultimaEscolha.current = alternativa
    enviar({ tipo: "responder", rodada, alternativa })
  }, [enviar])

  // Sai da partida e volta para a tela de entrada
  const sair = useCallback(() => {
    fechar()
    setEstado(inicial)
  }, [fechar])

  return { estado, conectar, iniciar, responder, sair }
}
