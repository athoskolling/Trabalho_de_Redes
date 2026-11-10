import { useEffect, useState } from "react"
import Alternativa from "../componentes/Alternativa"
import BarraProgresso from "../componentes/BarraProgresso"
import { MENSAGENS_ERRO, type Estado } from "../useServidor"

const TOTAL_RODADAS = 10
const LETRAS = ["A", "B", "C", "D"]

interface Props {
  estado: Estado
  onIniciar: () => void
  onResponder: (rodada: number, alternativa: 1 | 2 | 3 | 4) => void
  onSair: () => void
}

// Contagem regressiva local: começa no tempo que o servidor informou e desce 1 por segundo
function Contagem({ segundos }: { segundos: number }) {
  const [restante, setRestante] = useState(segundos)
  useEffect(() => {
    const t = setInterval(() => setRestante(r => Math.max(0, r - 1)), 1000)
    return () => clearInterval(t)   // para o relógio quando o componente sai da tela
  }, [])
  return <span className="tempo">{restante}s</span>
}

// Tela do jogo: sala de espera, pergunta, resultado da rodada e placar final
export default function Pergunta({ estado, onIniciar, onResponder, onSair }: Props) {
  const { pergunta, resultado, fim, placar, nome, organizador, iniciada, erro, escolhida } = estado
  // a seleção local vale só para a rodada em que foi feita
  const [selecao, setSelecao] = useState<{ rodada: number; alt: number } | null>(null)
  const marcada = selecao && selecao.rodada === pergunta?.rodada ? selecao.alt : null

  const meusPontos = placar.find(p => p.nome === nome)?.pontos ?? 0
  const rodada = pergunta?.rodada ?? resultado?.rodada ?? 0
  const mensagem = erro ? (MENSAGENS_ERRO[erro] ?? erro) : null

  return (
    <>
      <div className="topo">
        <strong>Quiz · Redes</strong>
        <span>{fim ? "Fim de jogo" : `Rodada ${rodada} de ${TOTAL_RODADAS}`}</span>
      </div>
      <BarraProgresso atual={fim ? TOTAL_RODADAS : rodada} total={TOTAL_RODADAS} />

      <div className="card">
        {/* rodada aberta: pergunta, alternativas e botão Responder */}
        {pergunta && (
          <>
            <p className="rotulo">Pergunta {pergunta.rodada}</p>
            <h2>{pergunta.texto}</h2>
            {pergunta.alternativas.map((texto, i) => {
              const n = i + 1
              // depois de enviada, a resposta não pode mais ser trocada
              const enviada = escolhida !== null
              const alvo = enviada ? escolhida : marcada
              return (
                <Alternativa key={n} letra={LETRAS[i]} texto={texto}
                  estado={alvo === n ? "selecionada" : undefined}
                  desabilitada={enviada}
                  onClick={() => setSelecao({ rodada: pergunta.rodada, alt: n })} />
              )
            })}
            <div className="rodape">
              <span>Pontuação: {meusPontos} · Tempo: <Contagem key={pergunta.rodada} segundos={pergunta.segundos} /></span>
              <button className="botao" disabled={marcada === null || escolhida !== null}
                onClick={() => marcada && onResponder(pergunta.rodada, marcada as 1 | 2 | 3 | 4)}>
                {escolhida !== null ? "Enviada ✓" : "Responder →"}
              </button>
            </div>
          </>
        )}

        {/* rodada encerrada: resposta correta e placar */}
        {!pergunta && resultado && !fim && (
          <>
            <p className="rotulo">Resultado da rodada {resultado.rodada}</p>
            <h2>Resposta correta: {LETRAS[resultado.correta - 1]}</h2>
            <p>
              {resultado.acertaram.length
                ? `Acertaram: ${resultado.acertaram.join(", ")}`
                : "Ninguém acertou."}
            </p>
            <Placar placar={resultado.placar} nome={nome} />
            <p className="espera">Aguardando a próxima rodada…</p>
          </>
        )}

        {/* fim de jogo: vencedores e placar final */}
        {fim && (
          <>
            <p className="rotulo">Fim de jogo</p>
            <h2>{fim.vencedores.length > 1 ? "Vencedores" : "Vencedor"}: {fim.vencedores.join(", ")}</h2>
            <Placar placar={placar} nome={nome} />
            <div className="rodape"><span /><button className="botao" onClick={onSair}>Sair</button></div>
          </>
        )}

        {/* antes do início: só o organizador vê o botão Iniciar */}
        {!iniciada && !pergunta && (
          <>
            <p className="rotulo">Sala de espera</p>
            <h2>Olá, {nome}!</h2>
            {organizador ? (
              <>
                <p>Você é o organizador. Com pelo menos 3 jogadores conectados, inicie a partida.</p>
                <button className="botao" onClick={onIniciar}>Iniciar partida</button>
              </>
            ) : (
              <p className="espera">Aguardando o organizador iniciar a partida…</p>
            )}
          </>
        )}

        {mensagem && <p className="msg">{mensagem}</p>}
      </div>
    </>
  )
}

// Lista de pontuação, do maior para o menor, destacando o próprio jogador
function Placar({ placar, nome }: { placar: { nome: string; pontos: number }[]; nome: string }) {
  const ordenado = [...placar].sort((a, b) => b.pontos - a.pontos)
  return (
    <ul className="placar">
      {ordenado.map(p => (
        <li key={p.nome} className={p.nome === nome ? "eu" : ""}>
          <span>{p.nome}</span><span>{p.pontos}</span>
        </li>
      ))}
    </ul>
  )
}
