# Arquivo: tools/linter/mzm_linter.py
#
# Linter de Intenções MZ-M (MVP Conceitual)
#
# Este script demonstra as funcionalidades básicas de validação do Método MZ-M:
# 1. Parsing e Validação de Gramática usando o schema CUE.
# 2. Validação de Referências Cruzadas (elementos declarados e usados).
# 3. Validações de Consistência Básica (ex: parâmetros de regras vs schema).
#
# Requer a biblioteca 'python-cue' (pip install python-cue)

import cue
import sys
import os
import typing # Para type hints

# --- Configuração ---
# Caminho para o arquivo de schema da gramática MZ-M
# Assume que mzm_grammar_schema.cue está em <raiz_do_repo>/grammar/mzm_grammar_schema.cue
# Ajuste o caminho conforme a estrutura do seu repositório.
# Se este script for executado da raiz do repo, o caminho seria:
SCHEMA_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "grammar", "mzm_grammar_schema.cue")
# Se for executado da pasta tools/linter, o caminho seria:
# SCHEMA_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "grammar", "mzm_grammar_schema.cue") # Este está correto assumindo execução da pasta linter

# --- Funções Auxiliares ---
class MzmValidationError:
    """Classe para representar um erro ou aviso de validação MZ-M."""
    def __init__(self, message: str, severity: typing.Literal['error', 'warning'] = 'error', position: str = "N/A"):
        self.message = message
        self.severity = severity
        self.position = position # Ex: "arquivo.mzm:linha:coluna"

    def __str__(self):
        return f"[{self.severity.upper()}] {self.position}: {self.message}"

# Funções para adicionar erros e avisos com posição CUE
def add_error(errors_list: list[MzmValidationError], msg: str, value: cue.Value):
     """Adiciona um erro com a posição do valor CUE."""
     try:
         # Tenta obter a posição do valor CUE
         position = value.position()
         position_str = str(position) if position else "N/A"
     except Exception:
         position_str = "N/A"
     errors_list.append(MzmValidationError(msg, severity='error', position=position_str))

def add_warning(warnings_list: list[MzmValidationError], msg: str, value: cue.Value):
     """Adiciona um aviso com a posição do valor CUE."""
     try:
         position = value.position()
         position_str = str(position) if position else "N/A"
     except Exception:
         position_str = "N/A"
     warnings_list.append(MzmValidationError(msg, severity='warning', position=position_str))


# --- Parte 1: Parsing e Validação de Gramática ---
def load_mzm_schema(schema_file_path: str) -> cue.Value:
    """Carrega o schema formal da gramática MZ-M a partir de um arquivo CUE."""
    try:
        schema_value = cue.load(schema_file_path)
        # Procura pela definição raiz #MZMRoot dentro do schema
        mzm_root_schema = schema_value.lookup("#MZMRoot")
        if not mzm_root_schema.exists():
             raise ValueError("A definição '#MZMRoot' não foi encontrada no schema MZ-M.")
        return mzm_root_schema
    except Exception as e:
        print(f"Erro fatal ao carregar ou processar o schema MZ-M '{schema_file_path}': {e}", file=sys.stderr)
        sys.exit(1)

def validate_grammar_and_parse(mzm_file_path: str, mzm_schema_value: cue.Value) -> tuple[cue.Value | None, list[MzmValidationError]]:
    """
    Carrega um arquivo .mzm, valida sua gramática usando o schema CUE,
    e retorna o valor CUE parseado ou None em caso de erro.
    Retorna também uma lista de erros encontrados durante esta fase.
    """
    errors: list[MzmValidationError] = []
    parsed_value: cue.Value | None = None

    # print(f"Validando estrutura e gramática de '{mzm_file_path}'...") # Comentado para saída mais limpa no MVP

    try:
        # 1. Carrega o arquivo .mzm
        # O cue.load já faz o parsing básico e pode lançar exceções de sintaxe CUE inválida
        input_value = cue.load(mzm_file_path)

        # 2. Unifica o valor do arquivo de entrada com o schema da gramática.
        # Esta é a validação estrutural e de tipos básicos feita pelo CUE.
        # Se a estrutura não conformar com #MZMRoot, a unificação falha.
        # Também valida restrições CUE como @>=1, @minitems, etc.
        unified_value = input_value.unify(mzm_schema_value)

        # 3. Valida a unificação. Força a avaliação completa e captura erros CUE definidos com '_error'.
        unified_value.validate()

        # print(f"Estrutura e gramática de '{mzm_file_path}' validadas com sucesso pelo CUE.") # Comentado
        parsed_value = unified_value # Retorna o valor unificado e validado

    except Exception as e:
        # CUE levanta exceções com detalhes dos erros de validação/unificação
        # Tentativa mais robusta de extrair posição do erro CUE
        error_message = str(e)
        position_str = "N/A"

        # A string de erro do cue pode ter o formato "path/to/file:line:col: message"
        # Tenta parsear a primeira linha da mensagem de erro
        first_line_error = error_message.splitlines()[0]
        parts = first_line_error.split(':', 3) # Divide em no máximo 4 partes

        if len(parts) >= 3 and os.path.exists(parts[0].strip()): # Verifica se a primeira parte parece um arquivo existente
             file_path = parts[0].strip()
             line = parts[1].strip()
             col = parts[2].strip()
             position_str = f"{file_path}:{line}:{col}"
             # O restante da mensagem é a descrição do erro CUE
             error_description = parts[3].strip() if len(parts) > 3 else "Erro de validação CUE."
             errors.append(MzmValidationError(f"Erro CUE: {error_description}", severity='error', position=position_str))
        else:
             # Se o formato não for o esperado ou o path não existir, apenas loga a mensagem completa.
             errors.append(MzmValidationError(f"Erro de parsing ou validação de gramática CUE: {error_message}", severity='error', position="N/A"))

        # Se houve erros de gramática CUE, o parsed_value pode não estar completo ou ser utilizável para as próximas fases.
        # Retornamos None para indicar que as próximas validações não devem ocorrer.
        return None, errors


    return parsed_value, errors


# --- Parte 2: Validação de Referências Cruzadas ---
def index_declared_elements(mzm_model_value: cue.Value) -> dict[str, dict[str, cue.Value]]:
    """
    Constrói um índice de todos os elementos declarados no modelo MZ-M validado.
    Opera no valor CUE parseado e validado contra o schema.
    Ignora elementos de imports nesta versão simples do indexador.
    Retorna um dicionário mapeando tipo_elemento -> nome_elemento -> valor_cue.
    Ex: { "entity": {"Usuario": <cue.Value do Usuario>}, "rule": {...} }
    """
    declared: dict[str, dict[str, cue.Value]] = {
        "entity": {}, "rule": {}, "context": {}, "intention": {},
        "event": {}, "state": {}, "direct_effect": {} # 'direct_effect' não tem uma seção de declaração formal no schema MVP, é mais um placeholder
    }

    root_fields = mzm_model_value

    # Indexar seções principais usando o conhecimento do schema #MZMRoot
    sections_to_index = ["entities", "rules", "context", "intentions"]
    for section_name in sections_to_index:
        if root_fields.lookup(section_name).exists():
            # .items() para iterar sobre chaves e valores de um objeto CUE
            element_type = section_name.rstrip('s') # entity, rule, context, intention
            # Use .items() no valor resolvido (unificado e validado)
            for name, value in root_fields.lookup(section_name).items():
                 declared[element_type][name] = value

    # Geometria Causal (Eventos e Estados)
    if root_fields.lookup("causal_geometry").exists():
         cg_value = root_fields.lookup("causal_geometry")
         if cg_value.lookup("events").exists():
             for name, value in cg_value.lookup("events").items():
                 declared["event"][name] = value
         if cg_value.lookup("states").exists():
              for entity_state_group_name, state_group_value in cg_value.lookup("states").items():
                   # CUE garante que state_group_value é um objeto conformando a { [string]: #Estado }
                   # Indexamos os estados aninhados sob o nome do grupo (entidade ou "Sistema")
                   if entity_state_group_name not in declared["state"]:
                       declared["state"][entity_state_group_name] = {}
                   for state_name, state_value in state_group_value.items():
                        declared["state"][entity_state_group_name][state_name] = state_value


    # TODO: Adicionar indexação de imports. Itens importados também são "declarados" do ponto de vista do modelo que importa.
    # Isso exigiria um mecanismo para carregar e indexar arquivos .mzm importados. Complexo para o Linter MVP.

    return declared

def validate_cross_references(mzm_model_value: cue.Value, declared_elements: dict[str, dict[str, cue.Value]]) -> list[MzmValidationError]:
    """
    Valida as referências cruzadas no modelo MZ-M carregado.
    Opera no valor CUE parseado e validado contra o schema.
    Retorna uma lista de erros encontrados.
    """
    errors: list[MzmValidationError] = []

    root_fields = mzm_model_value

    # --- Validar Referências onde #RegraAplicada é usada ---
    # Verifica se a 'rule' referenciada existe.
    # Verifica se itens em 'requires_context' dentro da aplicação da regra existem em 'context'.
    def validate_applied_rule_refs(applied_rule_value: cue.Value, source_description: str):
        rule_name_val = applied_rule_value.lookup("rule")
        if rule_name_val.exists():
             rule_name = rule_name_val.value
             # Verifica se a regra declarada localmente OU importada (se imports fossem indexados) existe.
             if not declared_elements.get("rule", {}).get(rule_name):
                 add_error(errors, f"Regra '{rule_name}' referenciada em {source_description} não encontrada nos elementos declarados.", rule_name_val)

        # Valida 'requires_context' dentro da #RegraAplicada (se definido)
        if applied_rule_value.lookup("requires_context").exists():
             for context_item_name_val in applied_rule_value.lookup("requires_context").value:
                  if context_item_name_val.exists() and not declared_elements.get("context", {}).get(context_item_name_val.value):
                       add_error(errors, f"Item de Contexto '{context_item_name_val.value}' requerido por uma Regra Aplicada em {source_description} não encontrado na seção 'context'.", context_item_name_val)


    # Aplicar validação de #RegraAplicada onde ela é usada:
    if root_fields.lookup("entities").exists():
        for entity_name, entity_value in root_fields.lookup("entities").items():
            if entity_value.lookup("invariants").exists():
                for i, invariant_applied_rule in enumerate(entity_value.lookup("invariants").value):
                    validate_applied_rule_refs(invariant_applied_rule, f"Entidade '{entity_name}' (invariants[{i}])")

    if root_fields.lookup("intentions").exists():
        for intention_name, intention_value in root_fields.lookup("intentions").items():
            if intention_value.lookup("contracts").exists():
                contracts_value = intention_value.lookup("contracts")
                for contract_list_name in ["pre_conditions", "post_conditions"]:
                    if contracts_value.lookup(contract_list_name).exists():
                         for i, applied_rule in enumerate(contracts_value.lookup(contract_list_name).value):
                             validate_applied_rule_refs(applied_rule, f"Intenção '{intention_name}' ({contract_list_name}[{i}])")

    # --- Validar Referências em Regras ---
    # Verifica se itens em 'requires_context' na definição da Regra existem em 'context'.
    if root_fields.lookup("rules").exists():
        for rule_name, rule_value in root_fields.lookup("rules").items():
            if rule_value.lookup("requires_context").exists():
                for context_item_name_val in rule_value.lookup("requires_context").value:
                    if context_item_name_val.exists() and not declared_elements.get("context", {}).get(context_item_name_val.value):
                         add_error(errors, f"Item de Contexto '{context_item_name_val.value}' requerido pela Regra '{rule_name}' (definição) não encontrado na seção 'context'.", context_item_name_val)
            # TODO: Validar 'implementation_ref's? Requer um catálogo de implementações disponíveis, fora do escopo do Linter MVP.

    # --- Validar Referências em Intenções ---
    if root_fields.lookup("intentions").exists():
        for intention_name, intention_value in root_fields.lookup("intentions").items():
            # Validar 'primary_action_ref' - apenas verifica se o formato é string não vazio (já feito pelo schema)
            # Uma validação mais profunda checaria se a referência existe em um catálogo de ações primárias disponíveis. Fora do escopo do MVP.
            primary_action_ref_val = intention_value.lookup("primary_action_ref")
            # Opcional: Se o formato esperasse "Intencao:NomeIntencao", poderíamos validar a referência a outra intenção.
            # Exemplo: if primary_action_ref_val.value.startswith("Intencao:"): ... validate reference to intention ...

            # Validar Efeitos Causais disparados pela Intenção (#CausalEfeito)
            for causal_list_name in ["on_success_cause", "on_failure_cause"]:
                if intention_value.lookup(causal_list_name).exists():
                     for i, causal_effect in enumerate(intention_value.lookup(causal_list_name).value):
                         # Passar a descrição da fonte para o reporte de erro
                         validate_causal_effect_references(causal_effect, declared_elements, errors, f"Intenção '{intention_name}' -> {causal_list_name}[{i}]")


    # --- Validar Referências em Geometria Causal ---
    if root_fields.lookup("causal_geometry").exists():
        cg_value = root_fields.lookup("causal_geometry")
        # Validar referências em Relações Causais
        if cg_value.lookup("relations").exists():
            for i, relation_value in enumerate(cg_value.lookup("relations").value):
                # Evento disparador (on_event)
                on_event_name_val = relation_value.lookup("on_event")
                if on_event_name_val.exists():
                     event_name = on_event_name_val.value
                     if not declared_elements.get("event", {}).get(event_name):
                          add_error(errors, f"Evento '{event_name}' na Relação Causal [{i}] (on_event) não encontrado nos elementos declarados.", on_event_name_val)

                # Condições de Contexto (when_context) -> referenciam Regras e Itens de Contexto
                if relation_value.lookup("when_context").exists():
                     # Valida referências de Regras e Itens de Contexto dentro da estrutura aninhada de when_context
                     validate_when_context_references(relation_value.lookup("when_context"), declared_elements, errors, f"Relação Causal [{i}] (when_context)")


                # Efeitos Causados (cause) -> referenciam #CausalEfeito
                if relation_value.lookup("cause").exists():
                    for j, caused_effect in enumerate(relation_value.lookup("cause").value):
                         validate_causal_effect_references(caused_effect, declared_elements, errors, f"Relação Causal [{i}]->cause[{j}]")


    # --- Validar Referências em Estados ---
    if root_fields.lookup("causal_geometry.states").exists():
        for entity_state_group_name, state_group_value in root_fields.lookup("causal_geometry.states").items():
             # Valida entity_ref em grupos de estado que não sejam "Sistema"
             if entity_state_group_name != "Sistema" and state_group_value.lookup("entity_ref").exists():
                 entity_ref_val = state_group_value.lookup("entity_ref")
                 if entity_ref_val.exists() and not declared_elements.get("entity", {}).get(entity_ref_val.value):
                      add_error(errors, f"Entidade '{entity_ref_val.value}' referenciada no grupo de Estados '{entity_state_group_name}' (entity_ref) não encontrada nos elementos declarados.", entity_ref_val)

    return errors

# Função auxiliar para validar referências dentro de um #CausalEfeito
def validate_causal_effect_references(causal_effect_value: cue.Value, declared_elements: dict[str, dict[str, cue.Value]], errors: list[MzmValidationError], source_description: str):
     """Valida referências dentro de um #CausalEfeito."""

     # Verifica qual tipo de efeito está presente e valida a referência
     if causal_effect_value.lookup("event_trigger").exists():
          event_name_val = causal_effect_value.lookup("event_trigger")
          if event_name_val.exists() and not declared_elements.get("event", {}).get(event_name_val.value):
               add_error(errors, f"Evento '{event_name_val.value}' disparado por {source_description} não encontrado nos elementos declarados.", event_name_val)

     elif causal_effect_value.lookup("state_transition").exists():
          transition_str_val = causal_effect_value.lookup("state_transition")
          if transition_str_val.exists():
              transition_str = transition_str_val.value
              # Formato esperado: "Entidade.Estado -> 'NomeEstado'" ou "Sistema.Estado -> 'NomeEstado'"
              parts = transition_str.split("->")
              if len(parts) == 2:
                   entity_state_part = parts[0].strip()
                   target_state_str_raw = parts[1].strip()
                   # Remover aspas simples ou duplas do nome do estado destino
                   target_state_name = target_state_str_raw.strip("'\"")


                   if "." in entity_state_part:
                        # Transição de estado de Entidade
                        entity_name = entity_state_part.split(".")[0]
                        state_group_name = entity_name # O grupo de estados é nomeado pela entidade
                        # Validar a existência da Entidade (opcional, mas boa prática)
                        # if not declared_elements.get("entity", {}).get(entity_name):
                        #     add_error(errors, f"Entidade '{entity_name}' referenciada na transição de estado '{transition_str}' por {source_description} não encontrada nos elementos declarados.", transition_str_val)
                        # Validar a existência do Estado destino PARA ESSE GRUPO (Entidade)
                        if not declared_elements.get("state", {}).get(state_group_name, {}).get(target_state_name):
                             add_error(errors, f"Estado destino '{target_state_name}' para a Entidade '{entity_name}' na transição de estado '{transition_str}' por {source_description} não encontrado nos estados declarados para '{entity_name}'.", transition_str_val)

                   elif entity_state_part == "Sistema":
                        # Transição de estado de Sistema
                        state_group_name = "Sistema" # O grupo de estados do sistema é nomeado "Sistema"
                        # Validar a existência do Estado destino PARA O SISTEMA
                        if not declared_elements.get("state", {}).get(state_group_name, {}).get(target_state_name):
                             add_error(errors, f"Estado destino '{target_state_name}' para o Sistema na transição de estado '{transition_str}' por {source_description} não encontrado nos estados declarados para 'Sistema'.", transition_str_val)
                   else:
                       add_error(errors, f"Formato inválido para parte da Entidade/Sistema na transição de estado '{transition_str}'. Esperado 'Entidade.Estado' ou 'Sistema.Estado'.", transition_str_val)
              else:
                  add_error(errors, f"Formato inválido para transição de estado '{transition_str}'. Esperado '... -> ...'.", transition_str_val)

     elif causal_effect_value.lookup("intention_trigger").exists():
          intention_name_val = causal_effect_value.lookup("intention_trigger")
          if intention_name_val.exists() and not declared_elements.get("intention", {}).get(intention_name_val.value):
               add_error(errors, f"Intenção '{intention_name_val.value}' disparada por {source_description} não encontrada nos elementos declarados.", intention_name_val)

     elif causal_effect_value.lookup("effect").exists():
          effect_name_val = causal_effect_value.lookup("effect")
          # TODO: Para validar 'effect', precisaríamos de uma lista de efeitos diretos configurados ou declarados (talvez em outra seção?).
          # Por agora, a validação @>=1 do CUE já garante que não está vazio.
          # Adicionar aviso/erro se um efeito direto não declarado é usado?
          pass


# Função auxiliar para validar referências de Regras e Contexto dentro de um valor CUE (usado em when_context)
def validate_when_context_references(when_context_value: cue.Value, declared_elements: dict[str, dict[str, cue.Value]], errors: list[MzmValidationError], source_description: str):
    """
    Percorre a estrutura aninhada de um when_context e valida referências a Regras e Itens de Contexto.
    Assume que a estrutura do when_context usa chaves que são nomes de itens de contexto e valores
    que são #RegraAplicada ou estruturas aninhadas.
    """
    if when_context_value.kind() == cue.Kind.STRUCT:
        for key, field in when_context_value.items():
            # A chave pode ser um nome de item de contexto ou um operador lógico ('e', 'ou', etc.) se a gramática suportar
            # Assumindo para o MVP que as chaves são nomes de itens de contexto ou operadores.
            # Se a chave é um nome de item de contexto, validamos sua existência.
            # Se a chave for um operador lógico, recursamos nos valores.

            # Simplificação para o MVP: Validamos apenas as referências a #RegraAplicada e Itens de Contexto
            # contidos DENTRO da estrutura do when_context.
            # Precisamos descer na estrutura.

            if field.kind() == cue.Kind.STRUCT:
                 # Verifica se este struct parece uma #RegraAplicada {rule: ..., params: ...}
                 if field.lookup("rule").exists():
                     # Parece uma #RegraAplicada. Valida as referências DENTRO dela.
                     validate_applied_rule_refs(field, source_description + f" -> when_context item '{key}'")
                 else:
                     # Estrutura aninhada. Recurva.
                     validate_when_context_references(field, declared_elements, errors, source_description)
            elif field.kind() == cue.Kind.LIST:
                 # Lista (pode ser para lógica OR, se a gramática suportar)
                 for i, item in enumerate(field.value):
                      validate_when_context_references(item, declared_elements, errors, source_description + f" -> when_context list item [{i}]")
            # else: É um valor primitivo, não esperamos referências aqui no when_context.


# --- Parte 3: Validações de Consistência Básica ---
def validate_basic_consistency(mzm_model_value: cue.Value, declared_elements: dict[str, dict[str, cue.Value]]) -> tuple[list[MzmValidationError], list[MzmValidationError]]:
    """
    Realiza validações básicas de consistência semântica no modelo MZ-M validado.
    Assume que o modelo passou pela validação de gramática e referências.
    Retorna listas de erros e avisos encontrados.
    """
    errors: list[MzmValidationError] = []
    warnings: list[MzmValidationError] = []

    # --- Validações Aplicadas a Regras Aplicadas (#RegraAplicada) e Efeitos Causais (#CausalEfeito) ---
    # Verifica se params/payload fornecidos batem com o schema esperado do destino (Regra, Intenção, Evento).
    def validate_payload_params_against_schema(provided_value_cue: cue.Value, expected_schema_cue: cue.Value, errors_list: list[MzmValidationError], source_description: str, schema_source_description: str):
        """Tenta unificar o valor fornecido com o schema esperado e reporta erros."""
        if not provided_value_cue.exists():
            # Não há nada para validar se não foram fornecidos params/payload
            # Opcional: Adicionar aviso se o schema esperado existe mas nada foi fornecido?
            # warnings_list.append(MzmValidationError(f"Schema esperado para {schema_source_description}, mas nenhuns dados fornecidos em {source_description}.", severity='warning', position=str(expected_schema_cue.position())))
            return

        if not expected_schema_cue.exists():
             # Não há schema esperado para validar contra. Isso pode ser um aviso dependendo da regra/evento/intenção.
             # warnings_list.append(MzmValidationError(f"Dados fornecidos em {source_description}, mas nenhum {schema_source_description} definido.", severity='warning', position=str(provided_value_cue.position())))
             return # Nada para validar se não há schema

        try:
            # Tenta unificar os dados fornecidos com o schema esperado.
            # Se não bater (tipos, estrutura, restrições), o CUE lança um erro.
            provided_value_cue.unify(expected_schema_cue).validate()
        except Exception as e:
            # Capturar erros CUE da unificação/validação
            error_message = str(e)
            # Tenta extrair posição do erro dentro do provided_value_cue
            position_str = "N/A"
            try:
                # CUE 0.8+ tenta incluir a posição no erro, mas pode variar
                 if hasattr(e, 'pos') and e.pos:
                     position_str = str(e.pos)
                 # Outras tentativas de parsear a string de erro CUE se 'pos' não estiver disponível ou for None
                 elif hasattr(e, 'message') and ':' in e.message:
                      parts = e.message.split(':', 3)
                      if len(parts) >= 3 and os.path.exists(parts[0].strip()):
                           position_str = f"{parts[0].strip()}:{parts[1].strip()}:{parts[2].strip()}"

            except Exception:
                 pass # Se a extração de posição falhar, usa "N/A"

            msg = f"Dados fornecidos em {source_description} não correspondem ao {schema_source_description}: {error_message}"
            errors_list.append(MzmValidationError(msg, severity='error', position=position_str))


    # Validar params onde #RegraAplicada é usada (Invariantes, Contratos, when_context)
    def apply_rule_params_validation(applied_rule_value: cue.Value, declared_elements: dict[str, dict[str, cue.Value]], errors_list: list[MzmValidationError], source_description: str):
         rule_name_val = applied_rule_value.lookup("rule")
         if not rule_name_val.exists(): return # Já reportado como erro de referência

         rule_name = rule_name_val.value
         provided_params_val = applied_rule_value.lookup("params") # O valor CUE dos parâmetros fornecidos na aplicação da regra

         referenced_rule_value = declared_elements.get("rule", {}).get(rule_name) # Já validado que existe em referências

         if referenced_rule_value and referenced_rule_value.lookup("params_schema").exists():
              expected_params_schema_value = referenced_rule_value.lookup("params_schema")
              validate_payload_params_against_schema(provided_params_val, expected_params_schema_value, errors_list, source_description + " (params)", f"params_schema da Regra '{rule_name}'")
         # Opcional: Aviso se 'params' é fornecido mas a regra não tem 'params_schema' ou vice-versa.


    # Aplicar validação de parâmetros de Regra Aplicada onde ela é usada:
    if root_fields.lookup("entities").exists():
        for entity_name, entity_value in root_fields.lookup("entities").items():
            if entity_value.lookup("invariants").exists():
                for i, invariant_applied_rule in enumerate(entity_value.lookup("invariants").value):
                    apply_rule_params_validation(invariant_applied_rule, declared_elements, errors, f"Entidade '{entity_name}' (invariants[{i}])")

    if root_fields.lookup("intentions").exists():
        for intention_name, intention_value in root_fields.lookup("intentions").items():
            if intention_value.lookup("contracts").exists():
                contracts_value = intention_value.lookup("contracts")
                for contract_list_name in ["pre_conditions", "post_conditions"]:
                    if contracts_value.lookup(contract_list_name).exists():
                         for i, applied_rule in enumerate(contracts_value.lookup(contract_list_name).value):
                             apply_rule_params_validation(applied_rule, declared_elements, errors, f"Intenção '{intention_name}' ({contract_list_name}[{i}])")

            # Validação de params/payload para efeitos causais disparados pela Intenção
            for causal_list_name in ["on_success_cause", "on_failure_cause"]:
                 if intention_value.lookup(causal_list_name).exists():
                      for i, causal_effect in enumerate(intention_value.lookup(causal_list_name).value):
                           validate_causal_effect_payload_params_consistency(causal_effect, declared_elements, errors, f"Intenção '{intention_name}' -> {causal_list_name}[{i}]")

    # Validar params/payload para efeitos causais dentro de Relações Causais
    if root_fields.lookup("causal_geometry.relations").exists():
        for i, relation_value in enumerate(root_fields.lookup("causal_geometry.relations").value):
            if relation_value.lookup("cause").exists():
                for j, caused_effect in enumerate(relation_value.lookup("cause").value):
                     validate_causal_effect_payload_params_consistency(caused_effect, declared_elements, errors, f"Relação Causal [{i}]->cause[{j}]")

            # TODO: Validação de params de regras dentro de 'when_context'.
            # Requer percorrer a estrutura do when_context e chamar apply_rule_params_validation para cada regra encontrada.
            # validate_when_context_params_consistency(relation_value.lookup("when_context"), declared_elements, errors, f"Relação Causal [{i}] (when_context)")


    # --- Outras Validações de Consistência Geral e Avisos ---

    # Aviso: Entidade sem invariantes (pode ser Entidade de Valor, mas suspeito no geral)
    if root_fields.lookup("entities").exists():
        for entity_name, entity_value in root_fields.lookup("entities").items():
            if not entity_value.lookup("invariants").exists() or len(entity_value.lookup("invariants").value) == 0:
                 add_warning(warnings, f"Entidade '{entity_name}' não possui regras invariantes definidas. Considere adicionar regras que definem a validade intrínseca deste conceito.", entity_value)

    # Aviso: Regra declarada nunca usada (pode ser regra comum no repositório, mas no projeto local é suspeito)
    # Exigiria percorrer todo o modelo para ver onde cada regra é referenciada. Complexo para o Linter MVP.

    # Aviso: Intenção sem contratos (pode ser intencional, mas suspeito)
    if root_fields.lookup("intentions").exists():
        for intention_name, intention_value in root_fields.lookup("intentions").items():
            contracts_exist = intention_value.lookup("contracts.pre_conditions").exists() or intention_value.lookup("contracts.post_conditions").exists()
            if not contracts_exist:
                 add_warning(warnings, f"Intenção '{intention_name}' não possui pré-condições ou pós-condições definidas. Considere adicionar contratos para definir seu comportamento esperado.", intention_value)

    # Aviso: Evento declarado nunca disparado
    # Exigiria percorrer Intenções (on_success_cause, on_failure_cause) e Relações Causais (event_trigger em cause)
    # e comparar com a lista de eventos declarados. Complexo para o Linter MVP.

    # Aviso: Estado declarado nunca usado em transição
    # Exigiria percorrer Relações Causais (state_transition em cause). Complexo para o Linter MVP.


    return errors, warnings

# Função auxiliar para validar payload/params de efeitos causais contra o schema do destino.
def validate_causal_effect_payload_params_consistency(causal_effect_value: cue.Value, declared_elements: dict[str, dict[str, cue.Value]], errors_list: list[MzmValidationError], source_description: str):
    """Valida payload/params de efeitos causais contra o schema do destino (Evento ou Intenção)."""

    # Validar payload para Eventos disparados
    if causal_effect_value.lookup("event_trigger").exists():
        event_name_val = causal_effect_value.lookup("event_trigger")
        if event_name_val.exists():
            event_name = event_name_val.value
            event_value = declared_elements.get("event", {}).get(event_name)
            provided_payload_val = causal_effect_value.lookup("payload")

            if event_value and event_value.lookup("payload_schema").exists(): # Validar se há evento e schema no evento
                 expected_payload_schema = event_value.lookup("payload_schema")
                 validate_payload_params_against_schema(provided_payload_val, expected_payload_schema, errors_list, source_description + " (payload)", f"payload_schema do Evento '{event_name}'")
            # else: Aviso se payload fornecido mas schema do evento não existe? Aviso se schema existe mas payload não fornecido?

    # Validar params para Intenções disparadas
    elif causal_effect_value.lookup("intention_trigger").exists():
        intention_name_val = causal_effect_value.lookup("intention_trigger")
        if intention_name_val.exists():
            intention_name = intention_name_val.value
            intention_value = declared_elements.get("intention", {}).get(intention_name)
            provided_params_val = causal_effect_value.lookup("params") # Intenção espera input via 'params' em causalidade

            if intention_value and intention_value.lookup("input_schema").exists(): # Validar se há Intenção e input_schema nela
                 expected_input_schema = intention_value.lookup("input_schema")
                 validate_payload_params_against_schema(provided_params_val, expected_input_schema, errors_list, source_description + " (params)", f"input_schema da Intenção '{intention_name}'")
            # else: Aviso se params fornecido mas input_schema da intenção não existe? Aviso se input_schema existe mas params não fornecido?

    # TODO: Validação para 'effect' - se houver schemas esperados para efeitos diretos.


# Função auxiliar para validar params de regras dentro de when_context
# Este é mais complexo pois o when_context tem estrutura arbitrária.
# Precisa percorrer a estrutura e encontrar todas as aplicações de regra.
# Implementação conceitual (recursiva):
def validate_when_context_params_consistency(when_context_value: cue.Value, declared_elements: dict[str, dict[str, cue.Value]], errors_list: list[MzmValidationError], source_description: str):
    """
    Percorre a estrutura aninhada de um when_context e valida os params de #RegraAplicada encontrados.
    """
    if not when_context_value.exists():
        return

    if when_context_value.kind() == cue.Kind.STRUCT:
        for key, field in when_context_value.items():
             current_source = source_description + f" -> '{key}'"
             if field.kind() == cue.Kind.STRUCT:
                  # Verifica se o struct é uma #RegraAplicada
                  if field.lookup("rule").exists() and field.lookup("params").exists(): # Assume que #RegraAplicada tem rule e params
                      apply_rule_params_validation(field, declared_elements, errors_list, current_source)
                  else:
                      # É um struct aninhado, recursa
                      validate_when_context_params_consistency(field, declared_elements, errors_list, current_source)
             elif field.kind() == cue.Kind.LIST:
                  # É uma lista, recursa em cada item
                  for i, item in enumerate(field.value):
                       validate_when_context_params_consistency(item, declared_elements, errors_list, source_description + f" -> list[{i}]")
            # else: Ignora outros tipos de valores primitivos ou outros tipos não esperados no when_context


# --- Função principal para executar o linter completo (MVP) ---
# Esta função seria chamada pelo script principal do Linter CLI.
# No Playground, seria chamada pelo backend da API /validate.
def lint_mzm_model(mzm_file_path: str, mzm_schema_value: cue.Value) -> tuple[list[MzmValidationError], list[MzmValidationError], cue.Value | None]:
    """
    Executa o processo completo de linting para um arquivo MZ-M.
    Retorna listas de erros e avisos, e o valor CUE parseado/validado (ou None).
    """
    all_errors: list[MzmValidationError] = []
    all_warnings: list[MzmValidationError] = []
    mzm_model_value: cue.Value | None = None

    # 1. Parsing e Validação de Gramática
    parsed_value, grammar_errors = validate_grammar_and_parse(mzm_file_path, mzm_schema_value)
    all_errors.extend(grammar_errors)

    # Procede com as próximas validações SOMENTE se a validação de gramática CUE passou sem erros que impedem parsing completo
    if parsed_value is not None and not grammar_errors:
        mzm_model_value = parsed_value # O valor parseado e validado gramaticalmente está disponível

        # 2. Indexar elementos declarados (necessário para referências e consistência)
        # Este passo opera no modelo que passou na gramática.
        declared_elements = index_declared_elements(mzm_model_value)

        # 3. Validar referências cruzadas
        reference_errors = validate_cross_references(mzm_model_value, declared_elements)
        all_errors.extend(reference_errors)

        # 4. Validar consistência básica (params/payload vs schemas, avisos)
        # Só valida consistência básica se não houver erros de referência que possam mascarar problemas.
        # Poderíamos rodar mesmo com erros de referência, mas a saída pode ser confusa.
        if not reference_errors:
            consistency_errors, consistency_warnings = validate_basic_consistency(mzm_model_value, declared_elements)
            all_errors.extend(consistency_errors)
            all_warnings.extend(consistency_warnings)
        else:
             # print("Pulando validação de consistência básica devido a erros de referência.") # Comentado para MVP

    # else: Se houveram erros de gramática impeditivos, as próximas fases não rodaram.

    return all_errors, all_warnings, mzm_model_value


# --- Script CLI principal para demonstração do MVP ---
# Permite executar o linter a partir da linha de comando.
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python mzm_linter.py <caminho_para_arquivo.mzm>")
        sys.exit(1)

    mzm_file = sys.argv[1]

    # 1. Carregar o schema da gramática MZ-M (fatal se falhar)
    # Assume que o script é executado de tools/linter/
    # Ajuste o SCHEMA_FILE_PATH no topo do arquivo se a localização for diferente.
    mzm_schema = load_mzm_schema(SCHEMA_FILE_PATH)

    # 2. Executar o processo de linting completo
    errors, warnings, validated_model_value = lint_mzm_model(mzm_file, mzm_schema)


    # --- Relatório Final ---
    if errors or warnings:
        print("\n--- Relatório de Validação MZ-M ---", file=sys.stderr)
        for error in errors:
            print(error, file=sys.stderr)
        for warning in warnings:
            print(warning, file=sys.stderr)
        print("------------------------------------", file=sys.stderr)

        if errors:
            print(f"\nValidação para '{mzm_file}' FALHOU com {len(errors)} erros e {len(warnings)} avisos.")
            sys.exit(1) # Sair com código de erro se houver erros
        else:
             print(f"\nValidação para '{mzm_file}' CONCLUÍDA com {len(warnings)} avisos.")
             sys.exit(0) # Sair com sucesso se houver apenas avisos

    else:
        print(f"\n--- Linter MZ-M (MVP) Concluído Com Sucesso para '{mzm_file}' ---")
        print("O arquivo MZ-M é válido de acordo com as verificações do Linter MVP.")
        # Em um fluxo real, validated_model_value seria passado para o Tradutor ou Verificador Semântico.
        sys.exit(0) # Sair com sucesso
