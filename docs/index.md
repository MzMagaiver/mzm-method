# Método MZ-M: Modelagem Zen de Sistemas

Bem-vindo à documentação oficial do Método MZ-M (Modelagem Zen de Sistemas).

O Método MZ-M é uma abordagem inovadora para a modelagem de sistemas complexos, focada na clareza, rastreabilidade e na representação precisa da intenção e causalidade dos processos. Utilizando uma gramática simples e poderosa baseada em CUE, o MZ-M permite descrever sistemas de forma declarativa, facilitando a compreensão, a manutenção e a evolução.

## O Que Você Encontrará Aqui

Esta documentação foi estruturada para guiá-lo desde os conceitos fundamentais do Método MZ-M até exemplos práticos e detalhes técnicos. Explore as seções:

* **Manual do Arquiteto Zen:** Entenda a filosofia por trás do MZ-M, aprenda sobre a gramática, as ferramentas e como o método se encaixa no ciclo de vida de um sistema.
* **Exemplos:** Veja o MZ-M em ação com exemplos de modelos que ilustram diferentes aspectos da gramática e suas aplicações.
* **Playground Online:** Experimente a gramática MZ-M diretamente no seu navegador (link será disponibilizado em breve).
* **Repositório GitHub:** Acesse o código-fonte, contribua e acompanhe o desenvolvimento do Método MZ-M.

## Comece Agora

Recomendamos que você comece lendo a [Introdução ao Manual do Arquiteto Zen](manual/introducao.md) para ter uma visão geral do Método MZ-M.

Você também pode [Baixar o Schema da Gramática MZ-M](grammar/mzm_grammar_schema.cue) para referência.

## Exemplos Rápidos

Veja abaixo um snippet de um modelo MZ-M que demonstra a declaração de invariantes:

```mzm
{{ include "examples/usuario_invariants.mzm" }}

E um exemplo mostrando a intenção e contrato de uma operação:

{{ include "examples/usuario_login.mzm" }}

Contribuição
O Método MZ-M é um projeto de código aberto e sua contribuição é muito bem-vinda! Se você tiver ideias, sugestões, encontrar um bug ou quiser ajudar a melhorar a documentação,
