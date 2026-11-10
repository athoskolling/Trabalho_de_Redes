export type MensagemEnviada =
  | { tipo: "entrar"; ip: string; nome: string }
  | { tipo: "iniciar" }
  | { tipo: "responder"; rodada: number; alternativa: 1 | 2 | 3 | 4 }

export interface ItemPlacar {
  nome: string
  pontos: number
}

export interface Pergunta {
  rodada: number
  texto: string
  alternativas: string[]
  segundos: number
}

export interface Resultado {
  rodada: number
  correta: number
  acertaram: string[]
  placar: ItemPlacar[]
}

export type MensagemRecebida =
  | { tipo: "entrou"; id: number; organizador: boolean }
  | ({ tipo: "pergunta" } & Pergunta)
  | ({ tipo: "resultado" } & Resultado)
  | { tipo: "fim"; placar: ItemPlacar[]; vencedores: string[] }
  | { tipo: "erro"; codigo: string }
  | { tipo: "ok"; acao: "iniciar" | "responder" }
