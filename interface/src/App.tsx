import Entrar from "./telas/Entrar"
import Pergunta from "./telas/Pergunta"
import { useServidor } from "./useServidor"

// Componente principal: escolhe qual tela mostrar
export default function App() {
  const { estado, conectar, iniciar, responder, sair } = useServidor()

  // enquanto o servidor não respondeu OK ao ENTRAR, fica na tela de entrada
  if (!estado.entrou) {
    return <Entrar erro={estado.erro} onEntrar={conectar} />
  }
  return <Pergunta estado={estado} onIniciar={iniciar} onResponder={responder} onSair={sair} />
}
