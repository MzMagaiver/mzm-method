# A Linguagem de Intenção e Contrato (Gramática MZ-M)

A Gramática MZ-M define a estrutura e a sintaxe da Linguagem de Intenção e Contrato, a linguagem formal que utilizamos para modelar a lógica de negócio do seu sistema. Esta linguagem é baseada no CUE, uma linguagem de configuração open source poderosa para definir, validar e gerar estruturas de dados.

Embora a Gramática MZ-M utilize a sintaxe do CUE, ela foca em expressar **conceitos de lógica de negócio**: Entidades, Regras, Intenções, Contexto e Geometria Causal.

A especificação formal completa da gramática está definida no arquivo [mzm_grammar_schema.cue](grammar/mzm_grammar_schema.cue) no repositório. Este documento fornece uma visão de alto nível e exemplos.

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
Vamos explorar cada uma das seções principais:

Entidades
A seção entities: define as Entidades de Verdade do seu domínio. São os conceitos que possuem significado intrínseco e regras invariantes que sempre devem ser verdadeiras para que um objeto dessa entidade seja considerado válido.

Cada entidade conforma ao schema #Entidade.

Fragmento do código

// Exemplo da seção 'entities' (do Exemplo 1)

entities: {
  Usuario: #Entidade & {
    description: "Representa um usuário do sistema com suas propriedades básicas."
    // Regras Invariantes: O que um Usuario VÁLIDO DEVE ser.
    invariants: [
      { rule: "common.email_valido", params: { value: "email" } }, // Valida formato do campo 'email'
      { rule: "common.string_min_length", params: { value: "senhaHash", min: 8 } }, // Valida tamanho do campo 'senhaHash'
      { rule: "status_usuario_valido", params: { status: "status" } } // Valida o campo 'status'
    ]
  }
  // ... outras entidades ...
}
A seção invariants lista as aplicações de regras (#RegraAplicada) que devem ser verdadeiras para a entidade.

Regras
A seção rules: define as Regras Reutilizáveis do seu domínio. São verificações atômicas e puras que podem ser aplicadas em diferentes contextos (como invariantes, pré/pós-condições, ou condições causais).

Cada regra conforma ao schema #Regra.

Fragmento do código

// Exemplo da seção 'rules' (do Exemplo 1)

rules: {
  status_usuario_valido: #Regra & {
    description: "Verifica se o status do usuário é 'ativo', 'inativo' ou 'bloqueado'."
    params_schema: { status: string } // Define os parâmetros que esta regra aceita.
    requires_context: [] // Lista itens de contexto que a implementação desta regra precisa.
    implementation_ref: { // Referência para o código real que executa a regra.
      python: "domain.usuario.rules.is_status_valido"
      // ... outras linguagens ...
    }
  }
  // ... outras regras ...
}
As Regras são o lugar onde a lógica atômica é definida uma única vez e depois reutilizada.

Contexto
A seção context: declara os Itens de Contexto Vivo que podem ser necessários durante a execução da lógica modelada (em Regras ou nas condições when_context da causalidade). Estes itens representam o estado do ambiente de runtime (usuário logado, configurações do sistema, acesso a serviços externos).

Cada item de contexto conforma ao schema #ContextItem.

Fragmento do código

// Exemplo da seção 'context' (do Exemplo 2)

context: {
  usuario_repository: #ContextItem & {
    description: "Serviço ou repositório para acessar dados de usuários existentes."
    source_ref: "service.database.user_repo" // Como obter este item em runtime.
  }
  // ... outros itens de contexto ...
}
O source_ref indica ao Kernel de Runtime (Etapa 3.x) como obter o valor deste item de contexto em tempo de execução.

Intenções
A seção intentions: define os Propósitos Verificáveis do seu sistema. Uma Intenção representa uma operação que o sistema pode realizar (Ex: Registrar Usuário, Processar Pedido, Enviar Notificação). Cada Intenção tem um Contrato (pré e pós-condições baseadas em Regras) e define sua Ação Primária e os Efeitos Causais de seu sucesso ou falha.

Cada intenção conforma ao schema #Intencao.

Fragmento do código

// Exemplo da seção 'intentions' (do Exemplo 2)

intentions: {
  LoginUsuario: #Intencao & {
    description: "Permite que um usuário faça login no sistema."

    // Input esperado para a Intenção de Login.
    input_schema: {
      email: string @tag(format: "email")
      senha: string
    }

    // Output em caso de sucesso (Ex: token de sessão, dados básicos do usuário logado).
    output_schema: {
       token: string
       user_id: string
       // ...
    }

    // Contratos: O que deve ser verdade ANTES de tentar logar, e DEPOIS de logar com sucesso.
    contracts: {
      pre_conditions: [
        // O usuário deve existir (regra depende do contexto do repositório).
        { rule: "usuario_existe_e_nao_bloqueado", params: { email: "input.email" } }, // Regra composta ou que depende de um lookup no contexto
        { rule: "senha_correta_para_usuario_contexto", params: { senhaFornecida: "input.senha" } } // Regra que usa senha do input e usuário do contexto
      ]
      post_conditions: [
        // Após a ação primária, deve existir um token de sessão válido no output.
        { rule: "common.string_nao_vazio", params: { value: "output.token" } }, // Regra comum de não vazio.
        // O usuário associado ao token deve estar marcado como logado (poderia ser uma regra de estado ou contexto).
      ]
    }

    // Ação Primária: A lógica real de tentar autenticar, gerar token, etc.
    // Esta referência aponta para o código manual do desenvolvedor.
    primary_action_ref: "domain.usuario.actions.authenticate_and_generate_token" // Caminho para o código

    // O que acontece na geometria causal se a Intenção for bem-sucedida.
    on_success_cause: [
      // Dispara um evento significativo "LoginDeUsuarioBemSucedido".
      { event_trigger: "LoginDeUsuarioBemSucedido", payload: { user_id: "output.user_id", email: "input.email" } } // Passa dados relevantes no payload.
    ]

    // O que acontece na geometria causal se as pré-condições falharem.
    // Ex: Pode disparar um evento de falha para logging ou alertas.
    on_failure_cause: [
       { event_trigger: "LoginDeUsuarioFalhou", payload: { email: "input.email", reason: "contract_violation" } }
    ]
  }
}
As Intenções modelam as operações de forma verificável e clara, separando a validação (Contratos) e o fluxo (Causalidade) da lógica de implementação (primary_action_ref).

Geometria Causal
A seção causal_geometry: define a Dinâmica e o Fluxo de Eventos do sistema. Ela descreve como eventos significativos levam a outros efeitos (disparar intenções, mudar estado, executar efeitos diretos) sob certas condições de contexto.

Inclui a declaração de Eventos (events:), Estados (states:) e as Relações Causais (relations:).

Fragmento do código

// Exemplo da seção 'causal_geometry' (do Exemplo 3)

causal_geometry: {
  events: {
    LoginDeUsuarioBemSucedido: #Evento & {
      description: "Disparado quando um usuário faz login com sucesso."
      payload_schema: { user_id: string, email: string @tag(format: "email") } // Dados que o evento carrega.
    }
    // ... outros eventos ...
  }

  states: {
    Usuario: { // Estados da Entidade Usuario
       Logado: #Estado & { description: "Usuário autenticado." },
       Deslogado: #Estado & { description: "Usuário não autenticado." }
    }
    // ... outros estados de entidades ou do sistema ...
  }

  relations: [
    // Relação Causal: Reage ao evento LoginDeUsuarioBemSucedido
    {
      on_event: "usuario.LoginDeUsuarioBemSucedido" // Evento que dispara.

      // Condição de Contexto (when_context): Deve ser verdadeira para ativar esta relação.
      when_context: {
         notificacoes_email_ativas: { rule: "notificacoes_email_ativas", params: {} }, // Regra checa contexto de notificação
         eh_primeiro_login_usuario: { rule: "eh_primeiro_login_usuario", params: {} } // Regra checa contexto de primeiro login
      }

      // Efeitos (cause): O que acontece se a condição when_context for verdadeira.
      cause: [
        { intention_trigger: "EnviarEmailBoasVindas", params: { email: "event.payload.email" } } // Dispara outra Intenção.
        // ... outros efeitos (mudança de estado, efeito direto) ...
      ]
    }
    // ... outras relações causais ...
  ]
}
A Geometria Causal modela o fluxo dinâmico e as reações do sistema, tornando o comportamento emergente explícito e rastreável.

Schemas Auxiliares (#RegraAplicada, #CausalEfeito)
Estes schemas definem a estrutura de elementos que são usados dentro das seções principais, como a aplicação de uma regra em um contrato (#RegraAplicada) ou um efeito causado em uma relação causal (#CausalEfeito). Eles garantem a consistência interna do modelo.

A especificação completa no mzm_grammar_schema.cue define estes schemas em detalhe.

Anterior: Introdução >> | Próximo: Ferramentas Essenciais >>
