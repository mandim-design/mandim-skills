# mandim-skills

A collection of [Claude Skills](https://www.anthropic.com/news/skills) — reusable, self-contained expert playbooks that give Claude a specific role, standard, and workflow for a recurring type of task.

Each skill lives in its own folder as `<skill-name>/SKILL.md`, following Anthropic's skill format, and can be dropped straight into a Claude Skills directory or plugin.

## Categories

### 🧭 Business Strategy
High-level strategic thinking: research, growth, prioritization, and validation.

| Skill | Description |
|---|---|
| [ai-research-analyst](business-strategy/ai-research-analyst/SKILL.md) | Executive-level market research, competitor analysis, and strategic intelligence grounded in cited sources. |
| [business-growth-consultant](business-strategy/business-growth-consultant/SKILL.md) | Diagnoses the real constraint on growth and finds the highest-leverage moves for revenue, profit, and retention. |
| [ceo-advisor](business-strategy/ceo-advisor/SKILL.md) | Acts as a CEO coach who pressure-tests plans, challenges assumptions, and helps prioritize ruthlessly. |
| [saas-idea-validator](business-strategy/saas-idea-validator/SKILL.md) | Brutally honest evaluation of SaaS/startup ideas across market, competition, monetization, and defensibility. |

### 📣 Marketing & Content
Turning strategy into audience-facing content, campaigns, and copy.

| Skill | Description |
|---|---|
| [chief-content-officer](marketing-content/chief-content-officer/SKILL.md) | Strategic content planning and production tied to business outcomes, not vanity metrics. |
| [landing-page-cro-expert](marketing-content/landing-page-cro-expert/SKILL.md) | Audits and rewrites landing/sales pages using conversion-rate-optimization principles. |
| [marketing-campaign-planner](marketing-content/marketing-campaign-planner/SKILL.md) | Designs coordinated multi-channel campaigns and product launches around one clear story. |
| [newsletter-writer](marketing-content/newsletter-writer/SKILL.md) | Writes newsletters and marketing emails built to educate, engage, and convert. |
| [youtube-producer](marketing-content/youtube-producer/SKILL.md) | Plans, packages, and scripts long-form YouTube videos for retention and channel growth. |

### 🎨 Product & Design
Evaluating and building the product experience itself.

| Skill | Description |
|---|---|
| [figma-to-storybook](product-design/figma-to-storybook/SKILL.md) | Reads a Figma Design System via the Desktop Bridge MCP and builds a pixel-accurate Storybook. |
| [ux-product-auditor](product-design/ux-product-auditor/SKILL.md) | Senior-level UX, CRO, and product-strategy audits tied to business outcomes. |

### 🤖 AI Engineering
Building and tuning the AI systems and tooling themselves.

| Skill | Description |
|---|---|
| [ai-workflow-architect](ai-engineering/ai-workflow-architect/SKILL.md) | Designs AI systems, automations, and agent workflows using tools like Claude, MCP, and APIs. |
| [prompt-optimizer](ai-engineering/prompt-optimizer/SKILL.md) | Transforms rough ideas and weak prompts into production-quality prompts, using real technique. |
| [web-artifacts-builder](ai-engineering/web-artifacts-builder/SKILL.md) | Bootstraps and bundles web-based Claude Artifacts, including a shadcn/ui component set. |

### 🗂️ Productivity & Operations
Running the day-to-day: personal task management, planning, and execution.

| Skill | Description |
|---|---|
| [daily-ops-copilot](productivity-operations/daily-ops-copilot/SKILL.md) | A configurable Notion + Slack (+ optional Calendar) task and project command center — daily sweeps, capacity-aware planning, and sprint reviews. |

## License

MIT — see [LICENSE](LICENSE). The `web-artifacts-builder` skill bundles its own [Apache 2.0 license](ai-engineering/web-artifacts-builder/LICENSE.txt) from Anthropic, which applies to that folder specifically.

## Adding a new skill

1. Pick (or create) the category folder it belongs in.
2. Create `<category>/<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`) followed by the skill instructions.
3. Add supporting files (scripts, references, assets) alongside `SKILL.md` in the same folder.
4. Add a row to the relevant table above.
