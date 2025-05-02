# Runtime e Rastreabilidade Semântica

## Executando a Lógica Modelada

O código gerado pelo [Tradutor MZ-M → Código](#tradutor-mz-m--código) não contém toda a lógica de negócio; ele contém a **estrutura e a orquestração** da lógica definida no seu modelo `.mzm`. A lógica de implementação real reside no código manual do desenvolvedor (as `implementation_ref`s e `primary_action_ref`s).

Para que o código gerado execute a lógica modelada, ele interage com um **Kernel de Runtime MZ-M Mínimo**. Este kernel é uma pequena biblioteca ou conjunto de funções que encapsula a lógica central para a execução de operações modeladas em MZ-M. Ele é chamado pelo código gerado e fornece uma interface padronizada para serviços essenciais em tempo de execução:

* **Gerenciamento de Contexto:** Torna o [Contexto Vivo](#contexto) (dados do ambiente de runtime) acessível para as regras e ações primárias.
* **Execução de Regras:** Fornece uma forma padronizada de chamar as implementações reais das [Regras](#regras), passando os dados e o contexto necessários.
* **Disparo de Eventos:** Encaminha [Eventos](#eventos) disparados (pelo código gerado das Intenções ou Efeitos Causais) para os [Handlers de Geometria Causal](#geometria-causal) correspondentes.
* **Rastreamento Semântico:** Captura o fluxo da execução da lógica modelada.

O código gerado chama as funções deste Kernel para realizar as operações definidas no modelo. Por exemplo, em vez de o código gerado saber *como* executar uma regra, ele chama `mzm_runtime.rules.run_rule("nome_da_regra", ...)` no Kernel.

## Rastreabilidade Semântica: Entendendo o "Por Quê"

Um dos pilares mais poderosos do Método MZ-M é a [Rastreabilidade Semântica](#rastreabilidade-semantica). Ela resolve o problema de entender *por que* o sistema se comportou de uma certa maneira, especialmente quando algo inesperado acontece.

Como isso funciona? O Kernel de Runtime, em conjunto com o código gerado, registra a execução da lógica modelada em um formato estruturado chamado **Traço Semântico**.

**O Que é um Traço Semântico?**

Um Traço Semântico é uma sequência cronológica de **Eventos Lógicos** que ocorreram durante a execução de uma operação (Ex: uma Intenção, um fluxo causal). Ele não registra apenas chamadas de funções técnicas, mas sim a **narrativa da lógica de negócio**:

* Intenção "LoginUsuario" iniciada com input X.
* Regra de pré-condição "usuario_existe" avaliada com resultado TRUE e motivo Y.
* Regra de pré-condição "senha_correta" avaliada com resultado FALSE e motivo "Senha Incorreta".
* Intenção "LoginUsuario" falhou nas pré-condições.
* Evento "LoginDeUsuarioFalhou" disparado com payload Z.
* Relação Causal \[0] ON "LoginDeUsuarioFalhou" verificada.
* Condição `when_context` da Relação Causal \[0] avaliada com resultado TRUE/FALSE.
* ... e assim por diante ...

Cada evento no traço pode incluir detalhes relevantes, como os parâmetros usados em uma regra, o resultado de uma condição de contexto, ou o payload de um evento disparado.

## Benefícios da Rastreabilidade Semântica

* **Debugging Revolucionário:** Entenda a causa raiz de um bug lógico rapidamente, seguindo o fluxo exato da lógica modelada. Veja quais regras falharam, quais condições de contexto não foram atendidas.
* **Auditoria e Conformidade:** Tenha um registro verificável de como as decisões lógicas foram tomadas para cada operação.
* **Observabilidade de Negócio:** Monitore o sistema a partir de uma perspectiva de lógica de negócio, não apenas técnica.
* **Análise de Comportamento:** Analise traços agregados para entender padrões de uso, gargalos lógicos ou falhas comuns no sistema real (alimenta a [Metacognição](#metacognicão-e-evolucão-assistida)).

## Integração com o Ambiente (Adaptadores e Middleware)

Para que a execução MZ-M aconteça dentro de um framework, precisamos de componentes que atuam como a "interface" entre o mundo externo/técnico e o núcleo de runtime:

* **Adaptadores para Frameworks:** Mapeiam entradas do framework (requisições HTTP, mensagens de fila) para chamadas a [Intenções](#intenções) MZ-M, e mapeiam a saída da Intenção de volta para a resposta do framework.
* **Middleware de Contexto:** No pipeline de processamento do framework, ele coleta dados do ambiente (sessão, requisição, configs) e monta o [Contexto Vivo](#contexto), disponibilizando-o para o Kernel de Runtime.

Em conjunto, o Kernel de Runtime, Adaptadores e Middleware permitem que a lógica modelada execute, utilize o contexto do ambiente, interaja com código manual e gere traços semânticos, tudo dentro da arquitetura existente do seu sistema.

---

[Anterior: Ferramentas Essenciais >>](/manual/ferramentas/) | [Próximo: A Visão Completa: Metacognição e Ecossistema >>](/manual/visao-completa/)
