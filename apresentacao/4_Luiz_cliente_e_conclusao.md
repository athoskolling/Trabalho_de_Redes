# Parte 4 — Luiz: Cliente e conclusão

**Arquivo:** `cliente.py` — **Tempo: ~2,5 min** — leia o texto abaixo do jeito que está.

---

Obrigado, Murilo. Eu apresento o cliente, que é o programa que o jogador usa.

Quando o cliente inicia, ele pede o endereço IP do servidor e o nome do jogador, e conecta por TCP na porta 5000. Depois, ele cria um socket UDP e deixa o sistema escolher uma porta livre. Isso permite abrir vários clientes no mesmo computador, cada um com a sua porta. Essa porta é enviada ao servidor no comando ENTRAR, para que o servidor saiba para onde mandar os avisos. O cliente também mantém o seu próprio arquivo de log, com o mesmo formato do log do servidor.

O cliente trabalha com duas threads. Uma lê o que o jogador digita no teclado. A outra fica escutando os avisos UDP. Assim, a digitação nunca fica travada esperando um aviso.

A parte mais interessante é o que o cliente faz quando chega um aviso, porque ele reage sozinho. Quando chega o aviso de rodada aberta, ele pede a pergunta oficial ao servidor por TCP e mostra na tela, com as alternativas a, b, c e d. Quando chega o aviso de rodada encerrada, ele pede o resultado daquela rodada. E quando chega o aviso de fim de jogo, ele pede o placar final. Isso mostra bem a divisão do projeto: o UDP avisa que algo aconteceu, e o TCP entrega a informação confiável.

Para facilitar para o jogador, ele não precisa digitar o comando completo. Basta digitar a letra da alternativa, a, b, c ou d, e o cliente converte para o formato do protocolo, com o número da rodada e a alternativa. O servidor não precisa saber dessa facilidade. Como as duas threads usam o mesmo socket TCP, o envio dos comandos é protegido por um lock, para que cada comando receba a sua própria resposta e uma thread não leia a resposta da outra.

Digitando a palavra sair, o jogador encerra o programa.

Para concluir: o projeto usa TCP para dados confiáveis, UDP para avisos rápidos, threads para atender vários jogadores ao mesmo tempo, locks para evitar conflitos e logs para acompanhar tudo o que acontece. Obrigado pela atenção, e ficamos à disposição para perguntas.
