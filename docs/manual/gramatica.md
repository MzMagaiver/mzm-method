A Gramática MZ-M
A Gramática MZ-M, baseada em CUE, é a linguagem formal para descrever a lógica de negócio. Seu objetivo é expressar a intenção e o contrato dos sistemas com clareza e de forma verificável, separando a lógica da implementação técnica.

Estrutura
Modelos MZ-M (.mzm) usam sintaxe CUE e incluem seções como:

entities: Define entidades e seus invariantes.

intents: Descreve operações do sistema.

contracts: Especifica pré/pós-condições para intenções.

rules: Define lógica reutilizável.

events: Modela resultados de intenções.

causality: Mapeia relações entre intenções e eventos.

Schema da Gramática
Um schema CUE define formalmente a gramática, permitindo validação de arquivos .mzm.

Baixar o Schema da Gramática MZ-M

Nota: Link relativo navega um nível acima (../) para a pasta grammar/.

Conceitos Chave
Entidades e Invariantes: Modele conceitos de negócio com condições que devem ser sempre verdadeiras. Exemplo:

{{ include "examples/usuario_invariants.mzm" }}

Intenções e Contratos: Descreva operações e suas condições (pré/pós). Exemplo:

{{ include "examples/usuario_login.mzm" }}

Regras Reutilizáveis: Encapsule lógica comum para consistência.

Causalidade e Eventos: Descreva resultados de intenções para rastreabilidade semântica. Exemplo:

{{ include "examples/usuario_causalidade.mzm" }}

Próximos Passos
Explore mais sobre Ferramentas Essenciais, Runtime e Rastreabilidade e a A Visão Completa no manual.

Entender a gramática é crucial para
