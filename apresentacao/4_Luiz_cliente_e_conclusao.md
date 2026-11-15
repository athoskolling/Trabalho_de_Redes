# Parte 4 — Luiz: Cliente e conclusão

**Arquivo:** `cliente.py` — **Tempo: até 2,5 min**

## Fala

Obrigado, Murilo. Eu apresento o **cliente**, que é o programa que o jogador usa.

Ao iniciar, ele pede o **IP do servidor** e o **nome** do jogador, e conecta por TCP na porta 5000. Depois cria um socket **UDP com porta 0**, o que faz o sistema escolher uma porta livre. Isso permite abrir vários clientes no mesmo computador. Essa porta é enviada ao servidor no comando `ENTRAR`.

Cada cliente também tem o seu **arquivo de log**, com a mesma estrutura do log do servidor.

Sobre as funções:

- A `ler_resposta` faz o mesmo que o servidor: lê do TCP com buffer até completar uma linha.
- A `enviar` manda um comando e devolve a resposta. Ela usa um **lock**, porque duas threads usam o mesmo socket TCP, a do teclado e a dos avisos. Sem o lock, uma poderia ler a resposta da outra.
- A `traduzir_comando` é uma facilidade pro jogador. Em vez de `RESPONDER 1 3`, ele digita só **a, b, c ou d**, e o cliente converte para o formato do protocolo. O servidor não precisa mudar.
- A `mostrar_resposta` formata a pergunta na tela, com as alternativas a), b), c) e d) e o tempo restante.

A parte mais interessante é a `escutar_udp`, que roda em **uma thread separada** para não travar a digitação. Quando chega um aviso, o cliente reage sozinho:

- `RODADA_ABERTA`: pede a **PERGUNTA** oficial por TCP e mostra na tela.
- `RODADA_ENCERRADA`: pede o **RESULTADO** da rodada.
- `FIM_JOGO`: pede o **PLACAR** final.

Isso mostra bem a divisão do projeto. O **UDP avisa** que algo aconteceu e o **TCP entrega a informação confiável**.

Por fim, o laço principal lê o que o jogador digita, traduz o comando, envia e mostra a resposta. Digitando `sair`, o cliente fecha a conexão.

Para concluir: o projeto combina **TCP e UDP**, **threads**, **locks** para evitar condições de corrida e um **protocolo de texto** simples, tudo com log completo dos eventos. Obrigado, ficamos à disposição para perguntas.
