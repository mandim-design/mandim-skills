---
name: figma-to-storybook
description: Reads a Figma Design System file end-to-end using the Figma Desktop Bridge MCP and builds a pixel-accurate Storybook — tokens, components, stories, dark mode — all mapped 1-to-1 from the DS with no guessing.
---

# Figma → Storybook

## Purpose

Takes any Figma Design System URL and produces a fully working Storybook component library that is pixel-accurate to the Figma file. Every token, dimension, shadow, variant and state is read directly from Figma using the Desktop Bridge MCP — nothing is guessed or taken from training data.

## When to Use

- Bootstrapping a component library from an existing Figma DS
- Auditing whether a codebase matches its Figma source of truth
- Generating a living Storybook from a DS that has no code implementation yet
- Demoing design-to-code automation end-to-end

## Stack Assumptions

Next.js 15 (App Router) · TypeScript · Tailwind v4 (CSS-first, `@theme inline`) · shadcn/ui · `@base-ui/react` primitives · `class-variance-authority` · Storybook 8 (`@storybook/nextjs-vite`)

---

## The Live Connection Chain (non-negotiable)

Every value in the system must trace back to a single source of truth: `globals.css`.

```
globals.css  ──▶  CSS variables (:root / .dark)
                      │
                      ▼
              Tailwind @theme inline
              (--color-*, --radius-*, etc.)
                      │
                      ├──▶  components/ui/*.tsx   (Tailwind classes → CSS vars)
                      │              │
                      │              ▼
                      │     stories/*.stories.tsx  (import components, no raw colors)
                      │              │
                      │              ▼
                      │     Flow stories / Foundations  (composed from components)
                      │
                      └──▶  Foundations.stories.tsx  (reads vars live via getComputedStyle)
```

**Changing one token in `globals.css` must update every component, story, and Foundations swatch simultaneously — with zero other file edits.**

---

## Zero Hardcoded Values — Absolute Rule

**No hardcoded hex, rgb, hsl, or color literal is ever allowed in:**
- `components/ui/*.tsx`
- `stories/*.stories.tsx`
- Any inline `style={{ color: '...' }}` in stories or components

The only place hex values may appear is inside `:root` and `.dark` blocks in `globals.css`, annotated with the Figma variable name.

**Enforcement grep — run before declaring done:**
```bash
grep -rn '#[0-9a-fA-F]\{3,6\}' components/ui/ stories/ --include="*.tsx"
# Must return zero matches (comments excluded)
```

Every color must be expressed as one of:
- A Tailwind utility that maps to a CSS variable: `bg-primary`, `text-muted-foreground`, `border-border`
- A CSS variable reference: `var(--primary)`, `color-mix(in srgb, var(--primary) 30%, transparent)`
- An opacity modifier on a semantic class: `bg-primary/30`, `text-foreground/60`
- A Tailwind arbitrary value referencing a CSS variable: `bg-[var(--primary-hover)]`

---

## Workflow

### Phase 1 — Discover the file structure

Use the Figma Desktop Bridge MCP. Do not guess or use training-data values.

1. Call `figma_get_file_data` — identify every page and its purpose.
2. Call `figma_get_variables` (all collections, `resolveAliases: true`) — record the exact resolved value AND alias chain for every variable. Identify the semantic layer vs. primitive palettes, and all modes (light/dark, brand themes).
3. Call `figma_get_styles` and `figma_get_text_styles` — capture all named text, color, and effect styles.
4. Call `figma_search_components` — list every published component grouped by page.
5. `figma_take_screenshot` of every component page for visual reference.

Do not proceed until you have a complete inventory of all pages, all variable collections fully resolved, and all component node IDs.

---

### Phase 2 — Deep-read every component

For each component or component set, call `figma_get_component_for_development_deep`. Extract and record:

| Property | What to capture |
|---|---|
| Dimensions | h, w, padding (T/R/B/L), gap, border-radius, border-width |
| Typography | font-family, size, weight, line-height, letter-spacing, transform |
| Colors | every fill + stroke → resolved hex + **Semantic variable alias** |
| Effects | every shadow layer → type, x, y, blur, spread, color, opacity |
| States | default, hover, pressed, focus, disabled, loading, error, selected |
| Variants | every component-set property and every value it accepts |
| Token bindings | every Semantic variable the component references |

For every color, record the **Semantic variable name**, not the raw hex. The hex goes only in `globals.css`. The component always uses the Semantic variable.

Do not proceed until all measurements are recorded for every component.

---

### Phase 3 — Map tokens to shadcn CSS variables

**Step 1 — Automatic mapping.** Walk every Semantic variable and map to the shadcn token it corresponds to:

`background` · `foreground` · `card` · `card-foreground` · `popover` · `popover-foreground` · `primary` · `primary-foreground` · `secondary` · `secondary-foreground` · `muted` · `muted-foreground` · `accent` · `accent-foreground` · `destructive` · `border` · `input` · `ring` · `ring-offset` · `radius` · `chart-1…N` · `sidebar` and all `sidebar-*` sub-tokens.

**Step 2 — Extended token mapping.** For every Semantic variable with no shadcn equivalent, create a custom CSS property using the Figma variable name slugified to kebab-case (e.g. `base/primary-hover` → `--primary-hover`). This covers: all state tokens, status tokens, border variants, icon/muted tiers.

**Step 3 — Effect tokens.** For every unique shadow, create a named CSS custom property (e.g. `--shadow-button-primary`) preserving every layer exactly.

**Step 4 — Resolve placeholders.** If any Semantic variable resolves to an unexpected value, trace its alias chain through the Primitive collections or inspect the component node. Never leave a placeholder.

---

### Phase 4 — Write `globals.css`

```css
@import "tailwindcss";
@import "tw-animate-css";
@import "shadcn/tailwind.css";

@custom-variant dark (&:is(.dark *));

@theme inline {
  /* var() references only — no hex values here */
  /* Font, radius scale, --color-* for every token */
}

:root {
  /* Every resolved token — light mode
     --token: #HEX; /* Figma variable name · primitive alias */
  /* Shadow tokens, chart tokens, sidebar tokens */
}

.dark { /* dark mode overrides */ }

@layer base { ... }
```

Rules:
- Hex values only in `:root`/`.dark` blocks, annotated with Figma variable name + alias
- Every CSS variable used anywhere must be defined here
- `@theme inline` contains only `var()` references — never hex

---

### Phase 5 — Implement components

Create `components/ui/<name>.tsx` for each component.

- Use the matching `@base-ui/react` primitive as the wrapper if one exists.
- Use CVA for variant + state styling.
- Every dimension from Phase 2 measurements — no guessing.
- **Every color is a Tailwind class backed by a CSS variable — zero hardcoded hex.**
- Every shadow references a CSS variable — no inline values.
- Every Figma variant maps to a CVA variant option.
- Every interactive state implemented via Tailwind state modifiers.
- JSDoc comment block at the top: DS variant → CVA key + key measurements.

**Color mapping reference — always prefer semantic classes:**

| Need | Use (not hex) |
|---|---|
| Brand fill | `bg-primary` |
| Brand text on brand fill | `text-primary-foreground` |
| Lighter/accent fill | `bg-accent` |
| Dimmed surface | `bg-muted` |
| Dimmed text | `text-muted-foreground` |
| Page/shell background | `bg-secondary` or `bg-background` |
| Border | `border-border` |
| Input border | `border-input` |
| Focus ring | `ring-ring` / `ring-2 ring-primary/30` |
| Tinted opacity | `bg-primary/30`, `text-foreground/60` |
| State token | `bg-[var(--primary-hover)]` |

---

### Phase 6 — Write Storybook stories

Create `stories/<ComponentName>.stories.tsx` for every component:

- **Playground** — interactive controls for all variant/size props.
- **Per-variant** — one static story per Figma component-set variant, named to match Figma exactly.
- **AllStates** — matrix of every variant × every interactive state.
- **Docs table** — Markdown table: DS variant name → CVA key → key measurements.
- Width-constrained wrappers matching the Figma canvas width.
- **Zero hardcoded hex in story files.** Use component imports; never recreate component styles inline.

---

### Phase 6b — Foundations story (live, CSS-variable-driven)

Create `stories/Foundations.stories.tsx`. **This story must read every color live from CSS variables at render time using `getComputedStyle`.** No hardcoded hex anywhere.

#### Required pattern — `useCSSVar` hook

```tsx
'use client'

import { useEffect, useState } from 'react'

/** Reads a CSS custom property from :root at render time. Always reflects globals.css. */
function useCSSVar(name: string): string {
  const [value, setValue] = useState('')
  useEffect(() => {
    const resolved = getComputedStyle(document.documentElement)
      .getPropertyValue(name)
      .trim()
    setValue(resolved || '(not set)')
  }, [name])
  return value
}
```

#### Required pattern — `Swatch` component

```tsx
function Swatch({ label, cssVar }: { label: string; cssVar: string }) {
  const resolved = useCSSVar(cssVar)   // live resolved hex — updates when globals.css changes
  return (
    <div className="flex flex-col gap-1.5">
      {/* background uses var() directly — live, no hardcoding */}
      <div
        className="h-14 w-full rounded-lg border border-border shadow-sm"
        style={{ background: `var(${cssVar})` }}
      />
      <div>
        <p className="text-xs font-medium text-foreground">{label}</p>
        <p className="font-mono text-[10px] text-muted-foreground">{cssVar}</p>
        <p className="font-mono text-[10px] text-muted-foreground/60">{resolved}</p>
      </div>
    </div>
  )
}
```

#### Required sections in the Colors story

Pass **only** CSS variable names — never hex strings:

```tsx
// ✅ Correct
{ label: 'primary', cssVar: '--primary' }

// ❌ Wrong — hardcoded, breaks on rebrand
{ name: 'primary', value: '#3E2AA6' }
```

Group swatches by: Core · Primary & States · Secondary & Surface · Accent · Border & Input · Sidebar · Destructive · Status · Chart Palette.

Every token defined in `globals.css` must appear in exactly one group. If you add a new token to `globals.css`, add it to the Foundations story too.

#### Why this matters

When `globals.css` changes (rebrand, theme switch, dark mode):
- Components update because they use Tailwind classes → CSS variables ✓
- Foundations updates because swatches use `var(--token)` and `getComputedStyle` ✓
- Flows update because they use components ✓

If the Foundations story has **any** hardcoded hex, it becomes stale on the first rebrand and lies to the viewer about what the system looks like.

---

### Phase 7 — Font setup for Storybook

`next/font` only runs in the Next.js layout — Storybook bypasses it.

1. Install the font npm package (or use a CDN `@import`).
2. Create `.storybook/fonts.css` with `@font-face` declarations and `--font-*` CSS variables in `:root`.
3. Import `fonts.css` **before** `globals.css` in `.storybook/preview.ts`.
4. In the `preview.ts` decorator: toggle `dark` class on `<html>`, add `antialiased`, set `lang` attribute.

---

### Phase 8 — Verify

1. Run Storybook build. Fix every error before continuing.
2. Screenshot each story and compare against the Phase 1 Figma screenshots:
   - Dimensions · Colors · Typography · Shadows · All states
3. For any discrepancy: re-read from Figma, fix, rebuild, re-screenshot. Repeat until pixel-accurate.
4. **Rebrand test:** change `--primary` in `globals.css` to a completely different color (e.g. a red). Reload Storybook. Verify that:
   - Every button, badge, input ring, stepper, sidebar accent all changed
   - The Foundations swatches reflect the new color
   - Zero components still show the old color
   Revert the change after the test.
5. Final checklist:
   - [ ] Every Semantic variable present in `globals.css`
   - [ ] Every CSS variable referenced in code is defined in `globals.css`
   - [ ] `grep -rn '#[0-9a-fA-F]\{3,6\}' components/ui/ stories/` returns zero matches
   - [ ] Foundations story uses `useCSSVar` hook + `var(--token)` backgrounds — no hex strings
   - [ ] Every Figma variant has a corresponding story
   - [ ] Storybook builds with zero errors and zero warnings
   - [ ] Rebrand test passed

---

## Do Not

- Write any code before Phase 1 and Phase 2 are fully complete
- Use training-data color values, sizes, or shadow values
- Leave any CSS variable undefined or any token unmapped
- Hardcode hex values in component or story files — the only legal hex location is `:root`/`.dark` in `globals.css`
- Use `style={{ color: '#...' }}` or `style={{ background: '#...' }}` anywhere in components or stories
- Write Foundations swatches as `{ name: 'primary', value: '#...' }` — always `{ label: '...', cssVar: '--...' }`
