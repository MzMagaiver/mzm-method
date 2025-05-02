// Arquivo: mzm_grammar_schema.cue
// Define o schema formal da Linguagem de Intenção e Contrato do Método MZ-M.

// Define a estrutura raiz esperada para um arquivo MZ-M (.mzm)
#MZMRoot: {
  // Versão da especificação da gramática MZ-M. Essencial para compatibilidade.
  mzm_version: string @>= "1.0" @tag(major: int, minor: int) // Ex: "1.0"

  // O nome do domínio ou módulo principal definido neste arquivo.
  domain: string @>= 1 @lowercase @trim // Exige nome não vazio, minúsculo e sem espaços no início/fim.

  // Declarações de importação de outras definições MZ-M (de outros arquivos ou repositórios).
  // A chave é um alias, o valor é a URI ou caminho do componente importado.
  imports?: { [string]: string @>= 1 } @tag(format: "uri-or-path") // Opcional.

  // Seções principais que contêm as definições dos elementos do modelo.
  // Cada seção é um mapa onde a chave é o nome do elemento definido.
  entities?:   { [string]: #Entidade }
  rules?:      { [string]: #Regra }
  context?:    { [string]: #ContextItem }
  intentions?: { [string]: #Intencao }
  causal_geometry?: #CausalGeometry // A Geometria Causal é um único objeto complexo, não um mapa de chaves.
}

// --- Schemas para os Elementos da Gramática ---
// Definimos a estrutura esperada para cada tipo de elemento MZ-M.

// Schema para uma Entidade de Verdade.
#Entidade: {
  description: string @>= 1 // Descrição clara da entidade.
  invariants?: [...#SchemasAuxiliares.#RegraAplicada] // Lista opcional de Regras Invariantes aplicadas.
  // Nota: Campos de dados da Entidade (como 'email', 'senha') não são definidos diretamente aqui,
  // mas inferidos dos 'params_schema' das Regras Invariantes e Contratos de Intenção,
  // ou definidos em um schema 'fields' opcional futuro na Entidade.
}

// Schema para uma Regra Reutilizável.
#Regra: {
  description: string @>= 1 // Descrição clara da regra.
  // Schema CUE que define a estrutura e os tipos dos parâmetros que esta regra ACEITA.
  // O Linter/Motor valida que quem usa a regra fornece parâmetros que batem com este schema.
  params_schema: { [string]: _ } // Permite qualquer estrutura aninhada de parâmetros.

  // Lista opcional de nomes de Itens de Contexto necessários para executar esta regra.
  // O Linter/Motor valida que estes itens estão declarados na seção 'context' ou imports.
  requires_context?: [...string @>= 1] @minitems(1) // Se presente, a lista não pode ser vazia.

  // Referências para as implementações reais desta regra em código.
  // A chave é o nome da linguagem/plataforma, o valor é o caminho da implementação.
  // Ex: { python: "mzmlib.validators.string.is_email", java: "com.mylib.EmailValidator.isValid" }
  implementation_ref: { [string]: string @>= 1 }

  // Restrição CUE: A regra deve ter pelo menos uma implementação referenciada.
  if len(implementation_ref) == 0 {
      _error: "Uma regra deve ter pelo menos uma implementação_ref definida."
  }
}

// Schema para um Item de Contexto Vivo.
#ContextItem: {
  description: string @>= 1 // Descrição clara do item de contexto.
  // Referência para o mecanismo em runtime que fornece este dado (Ex: "context.session.user", "config.featureFlags").
  source_ref: string @>= 1 @tag(format: "context-source-uri")

  // Schema CUE opcional que define a estrutura e os tipos do dado retornado por este item de contexto.
  // O Linter/Motor pode usar isso para validar o uso do contexto em Regras/Causalidade.
  schema?: _ // Pode ser qualquer schema CUE válido.
}

// Schema para uma Intenção (Propósito Verificável).
#Intencao: {
  description: string @>= 1 // Descrição clara da Intenção.

  // Schema CUE que define a estrutura e os tipos dos dados de entrada para esta Intenção.
  input_schema?: { [string]: _ } // Opcional se a Intenção não recebe input direto.

  // Schema CUE que define a estrutura e os tipos dos dados de saída em caso de sucesso.
  output_schema?: { [string]: _ } // Opcional se a Intenção não retorna dados.

  // Contratos: Regras que definem as condições que governam a execução da Intenção.
  contracts: {
    pre_conditions?: [...#SchemasAuxiliares.#RegraAplicada] // Lista opcional de Regras que devem ser verdadeiras ANTES.
    post_conditions?: [...#SchemasAuxiliares.#RegraAplicada] // Lista opcional de Regras que devem ser verdadeiras DEPOIS do sucesso.
  }

  // Referência para a lógica primária que executa a Intenção SE as pré-condições passarem.
  // Pode ser código manual, uma chamada a outra Intenção, etc.
  primary_action_ref: string @>= 1 @tag(format: "primary-action-ref")

  // Como esta Intenção se conecta à Geometria Causal ao ser executada.
  on_success_cause?: [...#SchemasAuxiliares.#CausalEfeito] // Lista opcional de Efeitos causados pelo sucesso.
  on_failure_cause?: [...#SchemasAuxiliares.#CausalEfeito] // Lista opcional de Efeitos causados pela falha de pré-condição.
}

// Schema para a Geometria Causal (Dinâmica e Fluxo).
#CausalGeometry: {
  // Declara os tipos de Eventos Significativos que podem ocorrer no sistema.
  // Cada evento tem um nome único e opcionalmente um schema para seu payload.
  events?: { [string]: #Evento }

  // Declara os Estados qualitativos que as Entidades ou o Sistema podem ter.
  // Organizados por nome da Entidade ou "Sistema".
  states?: { [string]: { [string]: #Estado } }

  // Lista de Relações Causais concretas (ON Event WHEN Context CAUSE Effects).
  // Define as regras de como eventos levam a efeitos sob certas condições.
  relations?: [...#RelacaoCausal]
}

// Schema para um Tipo de Evento.
#Evento: {
  description: string @>= 1 // Descrição clara do Evento.
  // Schema CUE opcional que define a estrutura e os tipos dos dados que este evento carrega.
  payload_schema?: { [string]: _ } // Pode ser qualquer schema CUE válido.
}

// Schema para um Tipo de Estado.
#Estado: {
  description: string @>= 1 // Descrição clara do Estado.
  // Opcional: Referência à Entidade que possui este estado (Ex: "Usuario").
  // Útil para validar transições de estado.
  entity_ref?: string @>= 1 @tag(format: "entity-name")
}

// Schema para uma Relação Causal (ON Event WHEN Context CAUSE Effects).
#RelacaoCausal: {
  // O nome do Evento que dispara esta relação causal.
  // O Linter/Motor valida que este evento está declarado em 'causal_geometry.events' ou imports.
  on_event: string @>= 1 @tag(format: "event-name")

  // Condições de Contexto que devem ser verdadeiras para que esta relação causal seja ativada.
  // A estrutura interna { [string]: _ } permite definir condições baseadas em itens de contexto.
  // Ex: { usuario_logado.role: "admin", estado_sistema: "operacional" }
  // O Linter/Motor valida que os nomes de itens de contexto usados aqui estão declarados.
  when_context?: { [string]: _ }

  // A lista de Efeitos que esta relação causal provoca quando ativada.
  cause: [...#SchemasAuxiliares.#CausalEfeito] @minitems(1) // Pelo menos um efeito deve ser causado.
}

// --- Schemas Auxiliares (Usados em outras definições) ---
// Agrupados para organização.
#SchemasAuxiliares: {
    // Schema para a aplicação de uma Regra em um contrato ou invariante.
    #RegraAplicada: {
        rule: string @>= 1 @tag(format: "rule-name") // Nome da regra referenciada.
        // Parâmetros específicos para esta aplicação da regra.
        // O Linter/Motor valida que a estrutura e tipos dos parâmetros batem com o params_schema da regra referenciada.
        params?: { [string]: _ }
        // Contexto específico necessário para esta APLICAÇÃO de regra (opcional).
        // Se definido, adiciona requisitos de contexto além dos declarados na regra em si.
        requires_context?: [...string @>= 1] @minitems(1) @tag(format: "context-item-name")
         // Validação semântica (feita no código do Linter/Motor):
         // - A regra 'rule' existe em 'rules' ou imports? (Feito na validação de referências)
         // - Os 'params' fornecidos correspondem ao 'params_schema' da regra referenciada? (Feito na validação de consistência básica)
         // - Os itens em 'requires_context' existem em 'context' ou imports? (Feito na validação de referências)
    }
     // Schema para um Efeito causado por uma Intenção ou Relação Causal.
     #CausalEfeito: {
        // Tipos de Efeitos (apenas um deve ser presente)
        event_trigger?: string @>= 1 @tag(format: "event-name") // Dispara um Evento declarado.
        state_transition?: string @>= 1 @tag(format: "state-transition-string") // Ex: "Usuario.Estado -> 'Ativo'". O Linter/Motor valida o formato e a existência da Entidade/Estado.
        intention_trigger?: string @>= 1 @tag(format: "intention-name") // Dispara outra Intenção declarada.
        effect?: string @>= 1 @tag(format: "direct-effect-name") // Referência a uma ação direta/serviço (logging, notificação, etc.). O Linter/Motor valida que esta referência existe e está configurada.

        // Dados associados ao efeito (Ex: payload para evento, input para intenção disparada).
        // Pode referenciar dados do evento que disparou a relação causal ("event.payload.xyz")
        // ou do output da intenção ("output.abc").
        payload?: { [string]: _ } // Pode ser qualquer estrutura de dados.

        // Parâmetros adicionais para intenções ou efeitos disparados.
        params?: { [string]: _ } // Pode ser qualquer estrutura de dados.

        // Restrição CUE: Deve ter exatamente um tipo de efeito disparador.
        if len([ for x in [event_trigger, state_transition, intention_trigger, effect] if x != null ]) != 1 {
             _error: "Um efeito causal deve especificar exatamente um de: event_trigger, state_transition, intention_trigger, ou effect."
        }

         // Validação semântica (feita no código do Linter/Motor):
         // - Referências (event_trigger, intention_trigger, effect) existem? (Feito na validação de referências)
         // - Payload/params batem com schemas/expectativas do destino? (Feito na validação de consistência básica)
     }
    // ... outros schemas auxiliares podem ser adicionados conforme necessário ...
}

// A raiz do arquivo MZ-M deve estar em conformidade com #MZMRoot
// Isso é validado pela engine CUE quando #MZMRoot é unificado com o conteúdo do arquivo.
#MZMRoot: _ 
