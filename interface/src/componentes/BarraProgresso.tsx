interface Props {
  atual: number
  total: number
}

// Barra de progresso: mostra em que rodada o jogo está
export default function BarraProgresso({ atual, total }: Props) {
  return (
    <div className="barra">
      {/* a largura da parte preenchida é a porcentagem de rodadas já abertas */}
      <div style={{ width: `${(atual / total) * 100}%` }} />
    </div>
  )
}
