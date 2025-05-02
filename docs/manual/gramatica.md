# A Linguagem de Intenção e Contrato (Gramática MZ-M)

A Gramática MZ-M define a estrutura e a sintaxe da Linguagem de Intenção e Contrato, a linguagem formal que utilizamos para modelar a lógica de negócio do seu sistema. Esta linguagem é baseada no CUE, uma linguagem de configuração open source poderosa para definir, validar e gerar estruturas de dados.

Embora a Gramática MZ-M utilize a sintaxe do CUE, ela foca em expressar **conceitos de lógica de negócio**: Entidades, Regras, Intenções, Contexto e Geometria Causal.

A especificação formal completa da gramática está definida no arquivo [mzm_grammar_schema.cue](/grammar/mzm_grammar_schema.cue) no repositório. Este documento fornece uma visão de alto nível e exemplos.

## Estrutura de um Arquivo MZ-M (.mzm)

Um arquivo MZ-M (`.mzm`) tipicamente define um domínio ou um módulo específico do seu sistema. Sua estrutura de alto nível é definida pelo schema `#MZMRoot` e inclui:

```cue
// Exemplo da estrutura básica de um arquivo .mzm

mzm_version: "1.0" // Versão da gramática utilizada
domain: "nome_do_seu_dominio" // Ex: "usuario", "pedido"

// Importa definições de outros arquivos .mzm ou repositórios comuns
imports: {
  // alias: "caminho/ou/uri"
  common: "repo://mzm-common-rules-repo/v1"
}

// Seções principais do modelo:
entities: {
  // Definições de Entidades
}

rules: {
  // Definições de Regras
}

context: {
  // Declarações de Itens de Contexto
}

intentions: {
  // Definições de Intenções
}

causal_geometry: {
  // Definições da Geometria Causal (eventos, estados, relações)
}
