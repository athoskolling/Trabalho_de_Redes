import Entrar from "./telas/Entrar"
import Pergunta from "./telas/Pergunta"
import { useServidor } from "./useServidor"

export default function App() {
  const { estado, conectar, iniciar, responder, sair } = useServidor()

  if (!estado.entrou) {
    return <Entrar erro={estado.erro} onEntrar={conectar} />
  }
  return <Pergunta estado={estado} onIniciar={iniciar} onResponder={responder} onSair={sair} />
}
