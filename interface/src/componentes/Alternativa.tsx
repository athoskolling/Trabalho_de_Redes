interface Props {
  letra: string
  texto: string
  estado?: "selecionada" | "correta" | "errada"
  desabilitada?: boolean
  onClick?: () => void
}

// Botão de uma alternativa: letra dentro do círculo e o texto ao lado
export default function Alternativa({ letra, texto, estado, desabilitada, onClick }: Props) {
  return (
    // o estado vira uma classe CSS, que muda a cor do botão
    <button className={`alternativa ${estado ?? ""}`} disabled={desabilitada} onClick={onClick}>
      <span className="letra">{letra}</span>
      {texto}
    </button>
  )
}
