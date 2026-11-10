import { useState } from "react"
import { MENSAGENS_ERRO } from "../useServidor"

interface Props {
  erro: string | null
  onEntrar: (ip: string, nome: string) => void
}

// Tela inicial: pede o IP do servidor e o nome do jogador
export default function Entrar({ erro, onEntrar }: Props) {
  const [ip, setIp] = useState("127.0.0.1")
  const [nome, setNome] = useState("")
  const [aviso, setAviso] = useState<string | null>(null)   // erro de preenchimento do formulário

  // Confere os campos antes de conectar
  function enviar(e: React.FormEvent) {
    e.preventDefault()   // impede o navegador de recarregar a página
    const n = nome.trim()
    if (!n) return setAviso("Digite um nome.")
    // estes caracteres são separadores do protocolo e quebrariam o placar
    if (/[,:|]/.test(n)) return setAviso('O nome não pode ter os caracteres , : |')
    if (!ip.trim()) return setAviso("Digite o IP do servidor.")
    setAviso(null)
    onEntrar(ip.trim(), n)
  }

  // erro do formulário tem prioridade sobre o erro vindo do servidor
  const mensagem = aviso ?? (erro ? (MENSAGENS_ERRO[erro] ?? erro) : null)

  return (
    <>
      <div className="topo"><strong>Quiz · Redes</strong></div>
      <form className="card" onSubmit={enviar}>
        <p className="rotulo">Entrar na partida</p>
        <h1>Quiz de Redes</h1>
        <label className="campo">IP do servidor
          <input value={ip} onChange={e => setIp(e.target.value)} />
        </label>
        <label className="campo">Seu nome
          <input value={nome} onChange={e => setNome(e.target.value)} autoFocus maxLength={30} />
        </label>
        <button className="botao" type="submit">Entrar</button>
        {mensagem && <p className="msg">{mensagem}</p>}
      </form>
    </>
  )
}
