# Config template

This file ships empty (placeholders only). Fill in every `{{LIKE_THIS}}` with real values from your own Notion workspace and Slack team before this skill can act. Nothing in `SKILL.md` or `routines.md` should ever guess an ID — if a value below is still a placeholder, stop and ask the user to fill it in rather than improvising one.

## Identity & language

- User's name: `{{USER_NAME}}`
- Notion user ID (used as Assignee / Owner): `{{NOTION_USER_ID}}`
- Slack user ID: `{{SLACK_USER_ID}}`
- Working language for task names / Notion content: `{{TASK_LANGUAGE}}` (e.g. English)
- Spoken language for reports/conversation, if different: `{{REPORT_LANGUAGE}}`

## Notion data sources

Fill one row per database this skill should touch. Not every workspace needs all of these — delete rows that don't apply, but don't invent IDs for the ones that do.

| Purpose | Data source ID | Title property | Template ID (always apply on create) |
|---|---|---|---|
| Work tasks | `{{WORK_TASKS_DS_ID}}` | `{{WORK_TASKS_TITLE_PROP}}` | `{{WORK_TASK_TEMPLATE_ID}}` |
| Personal tasks | `{{PERSONAL_TASKS_DS_ID}}` | `{{PERSONAL_TASKS_TITLE_PROP}}` | `{{PERSONAL_TASK_TEMPLATE_ID}}` (if separate) |
| Projects | `{{PROJECTS_DS_ID}}` | `{{PROJECTS_TITLE_PROP}}` | `{{PROJECT_TEMPLATE_ID}}` |
| Sprints — track 1 | `{{SPRINTS_1_DS_ID}}` | `{{SPRINTS_1_TITLE_PROP}}` | — |
| Sprints — track 2 (if you run two, e.g. work vs. personal) | `{{SPRINTS_2_DS_ID}}` | `{{SPRINTS_2_TITLE_PROP}}` | — |
| Clients (optional relation) | `{{CLIENTS_DS_ID}}` | — | — |
| Components (optional relation) | `{{COMPONENTS_DS_ID}}` | — | — |

> **Template rule:** every new task/project is created with its template applied via the `template_id` field on the create call, properties set alongside it. Never hand-build a page when a template exists.

### Task database schema

For each task database above, record:
- Status property name and values, e.g. `{{STATUS_PROP}}`: Not Started / In Progress / Done / Archived (use the **exact** values, including any emoji — Notion matches them literally).
- `Due` property name: `{{DUE_PROP}}`.
- `Priority` property name and values: `{{PRIORITY_PROP}}` (Low/Medium/High or your own scale).
- `Sprint` relation property name: `{{SPRINT_RELATION_PROP}}` — limit 1, always set on create/move.
- **`Source` property** (URL or rich text) — new, if it doesn't exist yet: `{{SOURCE_PROP}}`. Holds the originating Slack permalink. This is the exact-match dedupe key; without it, dedupe falls back to fuzzy title matching, which is worse.
- **`Estimate` property** (optional but recommended) — new, if it doesn't exist yet: `{{ESTIMATE_PROP}}`, either a number (hours) or a select (S/M/L). If you don't want to add this property, define a fallback heuristic instead, e.g. `S = 0.5h, M = 1.5h, L = 3h`, and size tasks by judgment.
- Project relation property name (work tasks only, if applicable): `{{PROJECT_RELATION_PROP}}`.
- Any other properties this skill should set or respect: `{{OTHER_PROPS}}`.

### Project database schema

- `Owner`, `Status` (+ values), `Priority`, `Dates` (range), `Summary`/description property, task relation property, plus any relations (`Client`, `Component`, `Blocked By` / `Is Blocking`). Record actual property names here: `{{PROJECT_SCHEMA_NOTES}}`.

## Sprints

- Current-sprint status value per track (e.g. track 1 = `{{SPRINT_1_CURRENT_VALUE}}`, track 2 = `{{SPRINT_2_CURRENT_VALUE}}`). Note if the two tracks use different languages/value sets for status — don't assume they match.
- "Ended" status values (safe to archive `Done` tasks from): `{{SPRINT_ENDED_VALUES}}`.
- "Next/upcoming" status values (where carry-over lands): `{{SPRINT_NEXT_VALUES}}`.
- Sprint cadence: `{{SPRINT_CADENCE}}` (e.g. weekly, Monday–Sunday).

### Sprint naming convention
Define the exact format sprint titles must follow, e.g. `Sprint DD/MM — DD/MM` (start–end date of the cadence period, em dash with spaces). Write your actual convention here: `{{SPRINT_NAMING_FORMAT}}`. Never leave a sprint titled with a placeholder like "New sprint" — if you see one, that's the fix-it signal in the weekly review. Leave the database's own blank template row(s) alone; only real sprint rows follow this rule.

## Ops State

A single Notion page (or a tiny database) this skill reads/writes to track cross-run state that doesn't belong on any task. Create it once, then record its ID here: `{{OPS_STATE_PAGE_ID}}`.

It needs to hold, at minimum:
- **Last swept timestamp per Slack source** — so the Daily Sweep knows the real gap instead of guessing a lookback window.
- **Reschedule counters per task** — a simple table (task ID/name → count), incremented every time that task's `Due` is pushed. Used to flag repeat-reschedule drift in the Daily Sweep report.

A plain Notion page with two child tables (or even a structured text block, if you'd rather not add a database) is enough — this doesn't need to be fancy, it needs to be read/written reliably.

## Slack

- Workspace: `{{SLACK_WORKSPACE_NAME}}`.
- Team/channel sources to sweep every run: `{{SLACK_CHANNELS}}` (list channel names/IDs).
- Any project-per-channel convention (e.g. a `#project-*` prefix) the sweep should auto-discover by paginating channel search, cross-referenced against the Projects database: `{{PROJECT_CHANNEL_CONVENTION}}`.
- Day-off / vacation signal: where the sweep should look to detect protected days if no calendar is connected, e.g. a specific DM or channel: `{{DAY_OFF_SIGNAL_SOURCE}}`.

> **Discovery reliability note:** channel search and `@mention` search can both return incomplete or empty results without erroring. Always fully paginate channel discovery (follow the cursor to exhaustion), and treat `@mention` search as a secondary cross-check only — never treat an empty result there as proof nothing is new.

## Calendar (optional)

- Calendar MCP connected: `{{CALENDAR_CONNECTED}}` (yes/no).
- Calendar ID to read for meeting load and out-of-office/vacation events: `{{CALENDAR_ID}}`.

## Capacity & prioritization

- Flat fallback target task-hours/day (used only when no calendar is connected, or as the baseline the calendar adjusts): `{{DAILY_CAPACITY_HOURS}}`. Note any day-of-week variation, e.g. weekends carrying more.
- Prioritization framework — score each open task on:
  1. **Priority** (stated importance — High > Medium > Low, or your own scale).
  2. **Due proximity** — overdue and due-today rank highest, then this week, then later.
  3. **Age** — how long it's been open/stale; old "In Progress" items get a nudge or a reset.
  4. **Effort vs. capacity** — fit the day to the target above; mix one chunky item with quick wins rather than stacking heavy tasks.
  5. Any custom tie-breakers: `{{CUSTOM_TIEBREAKERS}}` (e.g. business-hours-only tasks go on weekdays, anything blocking someone else jumps the queue).

## Recurring tasks (optional)

If you want a separate "standing chores/errands" source that gets pre-loaded into the real task databases ahead of each week (see `routines.md → Recurring task preload`), define it here rather than adding permanent recurring rows to the task databases themselves.

- Data source ID: `{{RECURRING_TASKS_DS_ID}}`. Title property: `{{RECURRING_TASKS_TITLE_PROP}}`.
- `Type` property (routes each row to the right destination database): `{{RECURRING_TYPE_PROP}}` — values matching your destination databases, e.g. Work / Personal.
- `Day` property (weekday the instance lands on): `{{RECURRING_DAY_PROP}}` — one value per weekday.
- `Priority` property: `{{RECURRING_PRIORITY_PROP}}`.
- `Cadence` property (how often a row actually gets instantiated — every run, or every Nth): `{{RECURRING_CADENCE_PROP}}`, and the exact values/windows each one means, e.g. `Weekly` = every run, `Biweekly` = skip if an instance exists within the last ~14 days.
- `Active` property (checkbox — unchecked rows are paused, not deleted): `{{RECURRING_ACTIVE_PROP}}`.
- Any other columns worth noting (e.g. `Notes`): `{{RECURRING_OTHER_PROPS}}`.
- Don't assume this source has the same properties as your task databases (e.g. a `Category` a task database has doesn't necessarily exist here, or vice versa) — read its actual live schema, don't carry assumptions from the task databases over.

## Saved views (optional)
List any pre-built Notion views this skill should point to instead of re-deriving them, e.g. a "Today" view (`Due = today`) or an "Overdue" view (grouped by status, since Notion's view DSL can't filter by a status *value* directly — group by status instead): `{{SAVED_VIEWS}}`.

## Known tool quirks
- Notion's view-DSL cannot filter by a Status *value* (only `IS EMPTY`/`IS NOT EMPTY`); it can filter by date and by other select properties. To separate done from open in a view, **group by Status** instead of filtering on it.
- Status values with an emoji (or any exact-string select value) must be passed **exactly**, emoji included.
- Date properties are typically set via expanded keys (e.g. `date:Due:start`, `date:Due:end`, `date:Due:is_datetime`) — check your Notion MCP's actual convention.
- Record any other quirks you hit here as you go: `{{OTHER_QUIRKS}}`.
