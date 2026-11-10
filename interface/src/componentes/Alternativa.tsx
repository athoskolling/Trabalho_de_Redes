interface Props {
  letra: string
  texto: string
  estado?: "selecionada" | "correta" | "errada"
  desabilitada?: boolean
  onClick?: () => void
}

export default function Alternativa({ letra, texto, estado, desabilitada, onClick }: Props) {
  return (
    <button className={`alternativa ${estado ?? ""}`} disabled={desabilitada} onClick={onClick}>
      <span className="letra">{letra}</span>
      {texto}
    </button>
  )
}
