# 📘 SIVEAUTO – Documentação Técnica do Projeto

> **Entrega 1: Planeamento, Modelação e Arquitetura**
>
> * **Projeto:** SIVEAUTO (Sistema de Cotação de Veículos e Auditoria Técnica)
> * **Desenvolvedor:** Gabriel H. S. Oliveira
> * **Data da Entrega:** 10 de Fevereiro de 2026
> * **Versão:** 1.0.0 (Estrutura Inicial)
> * **Jira:** https://ghso.atlassian.net/jira/software/projects/PS/summary

---

## 1. Visão Geral e Objetivos
O **SIVEAUTO** é uma solução de software desenvolvida para automatizar a consulta, recolha e auditoria de preços de veículos no mercado nacional. O sistema integra uma interface pública de consulta com um painel administrativo seguro.

### 🎯 Objetivos do Sistema
1.  **Consulta Pública:** Fornecer uma ferramenta performante para consulta de preço médio (Base FIPE e Mercado).
2.  **Gestão de Cotações:** Permitir o registo de preços reais encontrados em lojas parceiras por pesquisadores.
3.  **Auditoria e Compliance:** Garantir a imutabilidade dos registos de busca e alterações de preço para fins de auditoria.

---

## 2. Arquitetura da Solução

### 🛠️ Stack Tecnológica
A seleção tecnológica visa a manutenibilidade e a rapidez de desenvolvimento (Rapid Application Development).

| Componente | Tecnologia | Justificação Técnica |
| :--- | :--- | :--- |
| **Backend/Core** | Python 3.12+ |
| **Frontend** | Streamlit |
| **Base de Dados** | SQLite |
| **QA / Testes** | Pytest |
| **Análise** | Pandas |

### 📂 Estrutura de Diretórios
O projeto segue o padrão MVC (Model-View-Controller) adaptado:
* `/src/controllers`: Regras de negócio, validação de dados e controlo de fluxo.
* `/src/models`: Definição das classes de dados e ORM.
* `/src/views`: Interfaces de utilizador (Páginas do Streamlit).
* `/tests`: Bateria de testes automatizados (Unitários e Integração).

---

## 3. Artefatos de Modelação (Entrega Visual)
Esta secção documenta a concretização das tarefas de modelação (**Jira PS-5** e **PS-8**).

### 3.1 Fluxos de Processo (User Flows)
Mapeamento da jornada do utilizador e das rotas do sistema.

* **Fluxo do Utilizador (Consulta Pública):**
  Jornada de pesquisa anónima, seleção de veículo e visualização de resultados.
  ![Fluxo do Utilizador](Fluxo_user.jpg)

* **Fluxo Administrativo (Gestão):**
  Processos de login, gestão de lojas parceiras e aprovação de cotações.
  ![Fluxo Administrativo](Fluxo_admin.jpg)

### 3.2 Modelo de Dados (DER)
Estrutura relacional normalizada do banco de dados SQLite.
![DER UML](DER_UML.jpg)

**Dicionário de Dados Resumido:**
* `USUARIOS`: Credenciais e perfis (`admin`, `pesquisador`).
* `VEICULOS`: Catálogo de referência importado da Tabela FIPE.
* `LOJAS`: Parceiros comerciais (Status: Pendente/Aprovada/Rejeitada).
* `COTACOES`: Tabela transacional com preços coletados e data.
* `LOGS`: Tabela de auditoria para registo de todas as operações de busca.

### 3.3 Diagrama de Classes
Arquitetura de código orientada a objetos, separando Entidades e Controladores.
![Diagrama de Classes](Diagrama_de_classes.jpg)

---

## 4. Regras de Negócio e Requisitos (TDD)
Critérios de aceitação implementados conforme a **Documentação Técnica (TDD)**:

1.  **Hierarquia de Acesso:**
    * Apenas utilizadores com perfil `ADMIN` podem cadastrar, aprovar ou inativar lojas.
    * Utilizadores `PESQUISADOR` têm permissão exclusiva para inserir novas cotações de preços.

2.  **Validação de Dados (Data Integrity):**
    * O sistema deve rejeitar a inserção de cotações com valores negativos ou iguais a zero.
    * **Alerta de Desvio:** O sistema deve marcar automaticamente (flag) cotações que apresentem um desvio superior a **20%** em relação à média FIPE.

3.  **Auditoria:**
    * É estritamente proibida a exclusão física de registos de histórico (Logs). Deve ser aplicado *Soft Delete* ou imutabilidade total.

---

## 5. Dicionário de Dados (Detalhado)

Especificação técnica das tabelas do banco de dados SQLite (`siveaut.db`), incluindo tipos de dados e restrições de integridade.

### 5.1. Tabela: `usuarios`
Responsável pelo controle de acesso e perfis de segurança.
| Coluna | Tipo (SQLite) | Obrigatório | Descrição |
| :--- | :--- | :---: | :--- |
| `id` | INTEGER | **Sim** | Chave Primária (PK). Autoincremental. |
| `nome` | TEXT | **Sim** | Nome completo do usuário. |
| `email` | TEXT | **Sim** | Identificador único para login (Unique). |
| `senha_hash` | TEXT | **Sim** | Senha criptografada (nunca salvar em texto plano). |
| `perfil` | TEXT | **Sim** | Define permissões: `'ADMIN'` ou `'PESQUISADOR'`. |
| `data_criacao` | DATETIME | Não | Data de cadastro do usuário. |

### 5.2. Tabela: `veiculos`
Catálogo de referência (baseado na Tabela FIPE) para padronizar as coletas.
| Coluna | Tipo (SQLite) | Obrigatório | Descrição |
| :--- | :--- | :---: | :--- |
| `id` | INTEGER | **Sim** | Chave Primária (PK). Código FIPE ou interno. |
| `marca` | TEXT | **Sim** | Fabricante (ex: Fiat, Honda). |
| `modelo` | TEXT | **Sim** | Nome do modelo (ex: Uno Mille 1.0). |
| `ano` | INTEGER | **Sim** | Ano de fabricação do veículo. |
| `preco_referencia`| REAL | Não | Preço médio oficial (FIPE) para comparação. |

### 5.3. Tabela: `lojas`
Estabelecimentos parceiros onde as coletas de preço são realizadas.
| Coluna | Tipo (SQLite) | Obrigatório | Descrição |
| :--- | :--- | :---: | :--- |
| `id` | INTEGER | **Sim** | Chave Primária (PK). |
| `nome` | TEXT | **Sim** | Nome fantasia da loja. |
| `endereco` | TEXT | Não | Localização física. |
| `situacao` | TEXT | **Sim** | Status do cadastro: `'PENDENTE'`, `'APROVADA'`, `'REJEITADA'`. |

### 5.4. Tabela: `cotacoes` (Transacional)
Tabela Fato que registra o preço coletado em campo.
| Coluna | Tipo (SQLite) | Obrigatório | Descrição |
| :--- | :--- | :---: | :--- |
| `id` | INTEGER | **Sim** | Chave Primária (PK). |
| `valor` | REAL | **Sim** | Preço encontrado na loja (R$). |
| `data_registro` | DATETIME | **Sim** | Data e hora exata da coleta. |
| `id_usuario` | INTEGER | **Sim** | FK -> Tabela `usuarios` (Quem coletou). |
| `id_veiculo` | INTEGER | **Sim** | FK -> Tabela `veiculos` (Qual carro). |
| `id_loja` | INTEGER | **Sim** | FK -> Tabela `lojas` (Onde). |

### 5.5. Tabela: `logs_busca` (Auditoria)
Histórico imutável de consultas públicas realizadas no sistema.
| Coluna | Tipo (SQLite) | Obrigatório | Descrição |
| :--- | :--- | :---: | :--- |
| `id` | INTEGER | **Sim** | Chave Primária (PK). |
| `termo_busca` | TEXT | **Sim** | O que foi pesquisado (ex: "Fiat Uno"). |
| `data_hora` | DATETIME | **Sim** | Carimbo de tempo da ação. |
| `ip_origem` | TEXT | Não | Endereço IP do solicitante (para segurança). |