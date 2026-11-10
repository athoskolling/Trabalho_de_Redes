// Formato das mensagens JSON trocadas entre o navegador e a ponte.py

// Navegador -> ponte
export type MensagemEnviada =
  | { tipo: "entrar"; ip: string; nome: string }
  | { tipo: "iniciar" }
  | { tipo: "responder"; rodada: number; alternativa: 1 | 2 | 3 | 4 }

// Uma linha do placar
export interface ItemPlacar {
  nome: string
  pontos: number
}

// Pergunta da rodada aberta (a resposta correta nunca vem junto)
export interface Pergunta {
  rodada: number
  texto: string
  alternativas: string[]
  segundos: number   // tempo restante da rodada
}

// Resultado de uma rodada encerrada
export interface Resultado {
  rodada: number
  correta: number      // alternativa certa (1 a 4)
  acertaram: string[]  // nomes de quem acertou
  placar: ItemPlacar[]
}

// Ponte -> navegador
export type MensagemRecebida =
  | { tipo: "entrou"; id: number; organizador: boolean }
  | ({ tipo: "pergunta" } & Pergunta)
  | ({ tipo: "resultado" } & Resultado)
  | { tipo: "fim"; placar: ItemPlacar[]; vencedores: string[] }
  | { tipo: "erro"; codigo: string }
  | { tipo: "ok"; acao: "iniciar" | "responder" }
