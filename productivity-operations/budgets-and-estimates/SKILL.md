---
name: budgets-and-estimates
description: >
  Criação de orçamentos personalizados para clientes de Amanda Lemos Mandim (Product Designer & Webflow Developer, Porto).
  Use este skill sempre que o utilizador pedir para criar, calcular, estimar ou gerar um orçamento, proposta comercial,
  estimativa de horas ou investimento para projetos de UX/UI Design e/ou desenvolvimento Webflow.
  Trigger em frases como: "cria um orçamento", "quanto custa", "estimativa de horas", "proposta para cliente",
  "orçamento para site", "calcular horas", "orçamento Webflow", "budget for client", "quote for project".
  Sempre usar este skill antes de responder a qualquer pedido de orçamento ou estimativa de projeto.
---

# Orçamentos — Amanda Lemos Mandim

## Perfil
- **Nome:** Amanda Lemos Mandim
- **Função:** Product Designer & Webflow Developer
- **Localização:** Porto, Portugal (fuso UTC+0/UTC+1)
- **Taxa hora:** €35/h
- **Idioma:** Responde no idioma do utilizador (PT ou EN), deteção automática

---

## Processo Standard de Orçamentação

### 1. Recolher informações do projeto
Antes de gerar o orçamento, perguntar (se não fornecido):
- Nome do cliente / empresa
- Tipo de projeto (Landing Page, Site institucional, Produto digital, etc.)
- Escopo: quais fases são necessárias (Design, Dev, ou ambos)
- Número de páginas ou telas
- Necessidade de CMS?
- Animações GSAP? (sim/não/complexidade)
- Prazo pretendido pelo cliente
- Observações especiais ou exclusões

### 2. Calcular horas por fase
Ver tabela de referência em `references/horas-referencia.md`.

**Regra do buffer:** Sempre adicionar +10% ao total de horas para gestão, alinhamentos, QA e revisões internas.

**Regra das animações GSAP:** Se houver animações GSAP, adicionar +20% a +30% do tempo total das animações para afinação e performance.

### 3. Calcular investimento
- Usar **valor médio do range** de horas para o cenário base
- Apresentar também o range (mínimo e máximo) como referência
- Fórmula: `horas × €35 = investimento`

### 4. Estrutura do orçamento

Apresentar sempre com:

| Campo | Conteúdo |
|-------|----------|
| **Fase** | Nome da fase (Discovery, UX/UI, Dev, QA, Handoff) |
| **Task** | Descrição específica da task |
| **Horas (range)** | Ex: 4–8h |
| **Horas (estimado)** | Valor médio usado para cálculo |
| **Valor (€)** | horas estimadas × €35 |

**Rodapé do orçamento:**
- Total de horas estimadas
- Investimento total (range mínimo – máximo e valor base)
- 2 rodadas de revisão incluídas
- Revisões adicionais: orçamentadas separadamente (não mencionar valor/hora)
- Pagamento: 50% na assinatura + 50% na entrega
- Validade do orçamento: 30 dias
- Prazo estimado de execução (baseado nas horas e fuso de Portugal continental)

### 5. Premissas e exclusões
Incluir sempre uma secção de premissas claras, por exemplo:
- Fornecimento de conteúdos (textos, imagens) pelo cliente
- Hospedagem Webflow não incluída (plano do cliente)
- Domínio e configurações DNS não incluídos
- Integrações de terceiros não incluídas (salvo menção explícita)
- Copy/redação não incluída

---

## Formatos de entrega

### Artifact HTML interativo (formato principal)

**SEMPRE usar o template oficial como base:** `assets/orcamento-template.html`.

Não recriar o HTML do zero. O fluxo é:
1. Ler o ficheiro `assets/orcamento-template.html` (template completo com CSS, layout, header, footer e logo SVG inline).
2. Preencher os placeholders (`[—]`, `[X]`, `[REF]`, `[DATA]`, `[Nome do Cliente]`, `[TÍTULO DO PROJETO]`, etc.) com os dados calculados para o projeto.
3. Adaptar as fases e tasks dentro de `<!-- 02 FASES -->` ao escopo real do projeto (adicionar, remover ou renomear conforme necessário, mantendo a estrutura `.phase > .phase-header + .task-list`).
4. Renderizar com `show_widget` para apresentar o orçamento como artifact interativo na conversa.

**Secção RESUMO DO PROJETO (overview grid)** — sempre 6 células, nesta ordem:

| Posição | Label | Conteúdo |
|---------|-------|----------|
| 1 | Cliente | Nome do cliente ou empresa |
| 2 | Tipo de projeto | Ex: Landing Page, Site institucional, Produto digital |
| 3 | Prazo | Ex: 4–6 semanas |
| 4 | Horas estimadas | Total de horas do projeto (sem ranges, valor único arredondado) |
| 5 | Investimento | €X (valor base) |
| 6 | Revisões incluídas | Ex: 2 rodadas por fase |

**Regras visuais do template (não alterar):**
- Tipografia: `Roboto Mono` via Google Fonts
- Fundo `#fafafa`, texto e bordas `#1d1d1d`
- Labels de secção com prefixo `↳ ` e bullet `●` à direita
- Fases identificadas por `(A)` `(B)` `(C)`…
- Logo SVG MANDIM já está inline no header e footer
- **NUNCA mostrar ranges de horas** — nem por task, nem por fase, nem no total. Sem `range [X]–[X]h` em lado nenhum do orçamento.
- **NUNCA mostrar o valor hora (€35/h ou qualquer taxa horária)** ao cliente — nem no total, nem nas condições, nem em revisões. O cliente vê apenas o investimento total fechado.
- **Horas visíveis ao cliente:** apenas o total na overview ("Horas estimadas") e o total estimado por fase no cabeçalho de cada fase (ex: `~[X]h estimadas`). Sem horas por task individual.
- **Nunca mostrar valor monetário por task** — só o investimento total no `total-block` e na overview

### Documento Word/PDF
- Consultar skill `docx` ou `pdf` para geração do ficheiro
- Usar cabeçalho: "Amanda Lemos Mandim — Proposta Comercial"

### Planilha Excel
- Consultar skill `xlsx` para geração do ficheiro
- Incluir aba de cálculo e aba de resumo

---

## Referência rápida de horas
Ver ficheiro completo: `references/horas-referencia.md`

Resumo rápido:
- Landing Page completa (UI + Dev): ~24–35h base
- Site institucional 5–8 pág (UI + Dev): ~55–105h base
- Site com CMS complexo (UX+UI+Dev): ~100–190h base

---

## Assets de marca

Os ficheiros de marca estão em `assets/`:

- **`assets/orcamento-template.html`** — template oficial HTML do orçamento. Sempre usar como base.
- **`assets/mandim_logo.svg`** — logótipo vetorial MANDIM (ficheiro autónomo, caso seja necessário fora do template). O template já inclui o logo SVG inline.

### Identidade visual (sempre aplicar)

```css
--color--border: #1d1d1d;
--color--text:   #1d1d1d;
--color--background: #fafafa;
--color--muted:  #6a6a6a;
--color--light:  #b0b0b0;
--color--surface: #f2f2f0;
font-family: 'Roboto Mono', monospace;
```

- Fundo off-white `#fafafa`, texto e bordas `#1d1d1d`
- Tipografia exclusivamente **Roboto Mono** (Google Fonts)
- Layout editorial minimalista: `↳ SECÇÃO`, bullet `●`, índices `(A)` `(B)` `(C)`
- Localização: **Porto, Portugal** (mantida no footer do template)
- **Cálculos de horas são internos.** O cliente vê: total de horas na overview e horas estimadas por fase (sem ranges). Nunca vê horas por task individual nem ranges de horas.

---

## Tom e linguagem
- Profissional mas próximo
- Transparente sobre o que está incluído e excluído
- Sempre apresentar o orçamento como uma **proposta de valor**, não só uma lista de preços
- Se o cliente mencionar orçamento apertado, sugerir uma versão reduzida do escopo (MVP)
