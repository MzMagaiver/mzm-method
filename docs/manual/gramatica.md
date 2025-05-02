📘 Gramática MZ-M
A Gramática MZ-M, baseada em CUE, é a linguagem formal para descrever a lógica de negócio dos sistemas. Seu objetivo é expressar a intenção e o contrato dos sistemas com clareza e de forma verificável, separando a lógica da implementação técnica.

📚 Estrutura
Modelos MZ-M (.mzm) utilizam sintaxe do CUE e são organizados em seções principais:

entities: Define entidades e seus invariantes (regras sempre verdadeiras).

intents: Descreve operações ou intenções do sistema.

contracts: Especifica pré-condições e pós-condições das intenções.

rules: Define lógica reutilizável para manter consistência.

events: Modela os resultados das intenções.

causality: Mapeia relações causais entre intenções e eventos.

🧩 Schema da Gramática
Um arquivo schema CUE formaliza a gramática da linguagem MZ-M, permitindo a validação dos arquivos .mzm com precisão.

📥 Baixar Schema da Gramática MZ-M

Nota: o link acima é relativo e navega um nível acima para acessar a pasta grammar/.

🔑 Conceitos Chave
✅ Entidades e Invariantes
Modele conceitos de negócio com condições que devem ser sempre verdadeiras.

📄 Exemplo:

cue
Copiar
Editar
{{ include "examples/usuario_invariants.mzm" }}
🧠 Intenções e Contratos
Descreva operações do sistema, suas condições de entrada (pré) e resultados esperados (pós).

📄 Exemplo:

cue
Copiar
Editar
{{ include "examples/usuario_login.mzm" }}
♻️ Regras Reutilizáveis
Encapsule lógica comum em rules para garantir consistência entre diferentes partes do modelo.

🔗 Causalidade e Eventos
Descreva os resultados gerados por intenções para rastreabilidade semântica do sistema.

📄 Exemplo:

cue
Copiar
Editar
{{ include "examples/usuario_causalidade.mzm" }}
🧭 Próximos Passos
Explore mais:

Ferramentas Essenciais

Runtime

Rastreabilidade

A Visão Completa

Entender a gramática é crucial para garantir consistência, rastreabilidade e clareza na modelagem dos sistemas baseados em MZ-M.
