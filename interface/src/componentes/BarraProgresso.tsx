interface Props {
  atual: number
  total: number
}

export default function BarraProgresso({ atual, total }: Props) {
  return (
    <div className="barra">
      <div style={{ width: `${(atual / total) * 100}%` }} />
    </div>
  )
}
