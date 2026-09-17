---
name: interface-review
description: Reviews an interface as one system — accessibility, layout, writing, typography, and UI polish — and consolidates everything into a single prioritized verdict with file-and-line evidence. Use whenever the user wants a screen, flow, feature, component, or repository reviewed for interface quality; asks whether something is accessible, keyboard-navigable, or WCAG-compliant; wants focus rings, hit areas, spacing, hierarchy, microcopy, error messages, empty states, type scale, line length, border radius, shadows, icons, or animations checked; or asks "does this feel off?", "review this UI", "audit this screen", "revê esta interface". Also use before a design handoff or release, and when the user asks to implement the findings afterwards.
---

# Interface Review

A strong interface is not five independent audits stapled together. Position and spacing carry hierarchy before a word is read, the words themselves do the explaining, type makes them legible, and polish is what makes the result feel deliberate rather than assembled. Review the whole experience, then consolidate into one prioritized verdict.

When reviewing, slow the interface down. Walk it as a keyboard-only user first — every flow must complete without a mouse. Read the page instead of scanning the code: squint to check the hierarchy holds, read one full paragraph for comfort, resize the viewport to catch bad wrapping and truncation at real content lengths. Replay motion at 10% speed in the browser's Animations panel and walk every state: hover, focus, active, loading, empty. What feels off at 10% speed is what's subtly wrong at full speed.

**Match the project's styling system.** Before writing any fix, check how the codebase styles things and express every change in that system: Tailwind utilities in a Tailwind project, plain declarations in CSS, CSS Modules, styled-components or StyleX. Preserve the project's component library, tokens, and density, and its established motion language except where a principle below prescribes an exact interaction pattern. Never introduce a second styling approach just to apply a fix.

Treat numeric values as starting points for interfaces without an established density or spacing system. Preserve deliberate platform chrome, compact professional tools, and project tokens when they remain usable under hit-area, zoom, localization, and viewport stress tests.

Color notation, palette construction, and gamut are out of scope; this skill measures and reports contrast but does not repaint the project.

## Reference files

Load these only when a finding touches their subject:

| File | Covers |
| --- | --- |
| `references/surfaces.md` | Concentric border radius, optical alignment, shadows vs. borders, image outlines |
| `references/animations.md` | Interruptible transitions, enter/exit staging, contextual icon animations, scale on press |
| `references/icons.md` | Stroke weight, `currentColor` states, outline vs. fill, render size, RTL mirroring |
| `references/performance.md` | Transition specificity, `will-change` and GPU compositing |

## How to run a review

### Resolve scope and mode first

Infer the screen, flow, feature, or repository scope from the request and current workspace. State the resolved scope in the output. Use `full` when no mode is supplied.

| Mode | Coverage | Finding cap |
| --- | --- | --- |
| `quick` | Primary user path and highest-traffic states; report only `HIGH` and `MEDIUM` issues | 5 |
| `full` | Entire requested scope across all five domains, including empty, loading, error, and narrow-width states when present | 15 |

If the requested scope is too large to inspect credibly, narrow it to the highest-traffic complete flow and state the boundary. Never imply uninspected surfaces were reviewed.

### Recon before judgment

Identify the framework, styling system, component library, design tokens, supported viewports, and available preview or test commands. For copy, inspect nearby interface text, the product's terminology, localization conventions, and any voice or content style guide before proposing a change.

Check `package.json` or the page's loaded scripts for a smooth-scroll or scroll-animation library — Lenis, Locomotive, GSAP ScrollTrigger, Framer's `useScroll`. If one is present, read the next section before touching the page.

### Walking a scroll-driven page

On a page that hijacks or drives animation from scroll, the usual tools lie to you. Establish the ground rules before you file anything:

- **Programmatic scrolling is not user scrolling.** Once Lenis or Locomotive is installed, `window.scrollTo` and `element.scrollIntoView` fight the library's own loop: the page lands somewhere you did not ask for, or reports the right `scrollY` while painting a different frame. Drive the page with real wheel events and real clicks on real links. If you must jump, jump and then wait for the position to hold steady across two reads before you believe it.
- **A blank capture is not a blank page.** After an instant jump, a screenshot can beat the compositor: the DOM reports the section in place, full opacity, correct colors, and the image still comes back empty. Before filing anything from a blank frame, re-capture after the scroll settles and confirm the same emptiness twice. A screenshot that disagrees with a DOM read is a capture artifact until proven otherwise — this is the single most productive false lead on these pages.
- **Distinguish a resting state from a transit state.** A pinned sequence puts the user in control of the timeline, so every position is one they can stop at. A gap that only exists mid-scroll is not a finding; a gap that survives once inertia stops is.
- **Pinning breaks the mapping from scroll offset to content.** A pin spacer means the element at scroll position N is not the element at document offset N. Verify anchor links and deep links by loading each one cold, not by jumping in an already-scrolled page.
- **Deep links and find-in-page bypass the triggers.** Load every in-page anchor as a fresh navigation and confirm the target section renders in its finished state, not its pre-animation one.
- **The theme may repaint as it scrolls.** A script that swaps CSS variables per section means contrast, focus rings, and image outlines each have as many states as the page has themes. Measure them all.
- **Motion preference is a JS concern here, not a CSS one.** A CSS `@media (prefers-reduced-motion: reduce)` block does not reach a GSAP timeline or a Lenis instance. Grep the scripts for `prefers-reduced-motion`; if nothing reads it, the preference is unimplemented no matter how many CSS rules mention it.

### Review in this order

Foundational failures must not be hidden by polish:

1. Accessibility
2. Layout
3. Writing
4. Typography
5. UI polish

When two domains appear to cover the same issue, assign it to the one that owns the underlying rule and mention secondary effects in the **Why** cell. Report it once.

### Require evidence

Every finding cites `path/to/file:line` and shows the current implementation. If the review artifact has no source files, cite the exact screen and component. Do not report a code-level finding from visual appearance alone, or a visual finding from source code alone when runtime behavior determines the result.

### Review without mutating by default

Treat a review request as read-only. Do not edit source code unless the user also asks to implement the findings. When implementation is requested, preserve the consolidated report as the change scope and re-run the relevant verification afterward.

## Accessibility

Accessibility is not a compliance checkbox bolted on at the end; it is the floor for interface craft. Most of it is free if you use the platform: native elements ship with keyboard support, real labels announce themselves, and a visible focus ring is one CSS rule. When unsure, prefer the platform default over a custom rebuild, and remove ARIA rather than add it.

### 1. Native Elements First

The first rule of ARIA: don't use ARIA when a native element exists. `<button>` for actions, `<a href>` for navigation (it must support Cmd/Ctrl/middle-click), never `<div onClick>`. No ARIA is better than bad ARIA.

### 2. Visible Focus Rings

Style `:focus-visible`, not bare `:focus`, so keyboard users get a ring and mouse users usually don't. Prefer the browser's unmodified focus indicator. If the design needs a custom ring, use a project focus token or another explicit color and verify the complete indicator against every adjacent color it crosses; `currentColor` is acceptable only after the same check. Use at least a `2px` solid perimeter or an equivalent visible area. Never use `outline: none` without a verified replacement, and preserve system colors in forced-colors mode.

### 3. Full Keyboard Support

Every pointer interaction needs a keyboard path, following the ARIA APG patterns: Escape closes overlays, arrow keys move within composite widgets (tabs, menus, listboxes), Tab moves between widgets, Enter and Space activate. Only `tabindex="0"` (join the natural tab order) and `tabindex="-1"` (programmatic focus), never positive values, which break the natural order. Composite widgets use roving tabindex: the active item is `0`, all others `-1`.

### 4. Trap and Restore Focus

Modals set `inert` on the background content, move focus inside on open, and return focus to the trigger on close. Add `overscroll-behavior: contain` so background content doesn't scroll.

### 5. Minimum Hit Area

WCAG 2.5.8's Level AA baseline is a 24×24 CSS-pixel target or one of its defined spacing, equivalent-control, inline, user-agent, or essential exceptions. For easier activation, aim for 44×44px in touch contexts and 40×40px in desktop interfaces when density permits. Extend with a pseudo-element if the visible element should stay smaller. Never let extended hit areas overlap.

### 6. Label and Type Every Control

Every input gets a `<label for>` or wrapping `<label>`; a placeholder is never a label, and label and control share one hit target: no dead zones between a checkbox and its text. Add `autocomplete` with a meaningful `name`, and the correct `type` and `inputmode` for the keyboard. Never block paste; users paste passwords and one-time codes.

### 7. Accessible Names Everywhere

Icon-only buttons need a descriptive `aria-label`. Visible label text must appear in the accessible name. Decorative elements get `aria-hidden="true"`, never on a focusable element.

### 8. Don't Rely on Color Alone

Status needs a redundant cue: icon, text, or underline alongside the color. Determine which WCAG contrast requirement applies from the content and state, then measure the rendered foreground/background pair. When contrast fails, report the pair and the requirement it misses; do not change the project's colors unless asked.

**Measure what the eye receives, not what the declaration says.** A `color` value read on its own is not the rendered pair. Before computing a ratio, fold in every ancestor `opacity` down to the element, composite the result over the nearest ancestor with a real background, and only then measure. Text at `opacity: 0.6` is the most common way a failing pair hides from an audit: the declared ink passes, the painted ink does not. The same care applies to text over gradients, images, and video — measure the worst pixel region the text crosses, not an average.

```js
// Effective color = declared color composited over the backdrop by the opacity chain
function effectiveOpacity(el) {
  let e = el, op = 1;
  while (e && e !== document.documentElement) { op *= parseFloat(getComputedStyle(e).opacity); e = e.parentElement; }
  return op;
}
// effective = fg.map((v, i) => v * op + bg[i] * (1 - op))
```

On a page that repaints itself as it scrolls — a theme that inverts, a section that swaps its palette — measure once per theme, not once per page. A pair that passes in the light state can fail in the dark one.

### 9. Honor prefers-reduced-motion

Wrap motion in `@media (prefers-reduced-motion: no-preference)` so it is opt-in. Under reduced motion, replace slides and scales with opacity crossfades; kill parallax and autoplay entirely. Independent of the preference: autoplaying media needs a visible pause control, and toasts carrying actions or errors stay until dismissed.

## Layout

Layout communicates before a single word is read: position, spacing, and alignment carry hierarchy on their own, and generous space beats decoration. A good layout also survives stress: resize it, translate it, mirror it for RTL, and it should still hold together.

### 1. Group with Space, Not Lines

Negative space is the primary grouping tool; background shapes second; separator lines last, only where space alone can't carry the structure. The gap between groups must be at least 2× the gap within a group (`8px` intra-group → `16px`+ inter-group), or the grouping reads as noise.

### 2. Keep Controls Distinct from Content

Interactive elements must look interactive: a background shape, a border, or a consistent placement zone. Never style a control identically to adjacent static text.

### 3. Align to Shared Edges

Pick alignment edges and stick to them; every stray edge reads as noise. Use one project spacing step for each level of subordination (`16px` is a useful default). Use logical properties (`padding-inline-start`, `margin-inline-end`) for direction-dependent layout; reserve physical left/right for genuinely physical geometry.

### 4. Order by Importance

The most important content sits near the top and the leading edge; reading order flows top-to-bottom, leading-to-trailing. Think in leading/trailing, not left/right.

### 5. Breathing Room Between Targets

Without an established density system, start with `12px` between adjacent bordered or filled controls and `24px` of clearance around borderless text- and icon-only controls. Compact layouts may use less when the hit areas above do not overlap and the controls remain visually distinct.

### 6. Hold Structure Until It Breaks

Breakpoints come from the content, not device presets. Keep the expanded layout as long as it genuinely fits and collapse late; prefer container queries for component-level adaptation. Test the smallest and largest sizes first.

### 7. Plan for Growth and Clipping

Plan for substantial and language-dependent string growth rather than relying on a universal percentage: no fixed widths or heights on text containers, and let rows wrap. Never park critical actions where resizing or scrolling clips them; keep them reachable in the normal flow or stable chrome appropriate to the product.

## Writing

Clear and brief beats clever, consistency beats variety, and the best error message is the interaction redesigned so the error can't happen. Preserve intentional brand character when it remains clear and appropriate to the stakes: treat a difference from generic plain language as a finding only when it creates inconsistency, ambiguity, translation risk, or an inappropriate tone.

### 1. One Voice, Flexible Tone

The product has one voice, established by its existing system rather than invented during a local edit. Keep terms consistent: if it's "Archive" in the menu, it isn't "Move to storage" in the toast. Tone flexes with the stakes:

| Context | Tone |
| --- | --- |
| Success, onboarding, empty states | Warm, can be light |
| Routine actions, settings | Neutral, minimal |
| Errors, destructive confirmations | Calm, plain, zero playfulness |
| Data loss, security | Serious, explicit |

### 2. Plain Words Over Clever Ones

Choose easily understood words and delete every word that isn't needed. No idioms, colloquialisms, or humor that won't translate. Skip unnecessary gender: "Subscribers can post recipes", not "each subscriber can post his or her recipes". Match the input device: "tap" on touch, "click" with a pointer, "select" when both are possible. Never build sentences by concatenating fragments around variables (`"You have " + n + " new messages"`); word order changes per language, so use full templated strings with proper pluralization.

### 3. Verb-First Buttons

Button labels start with a verb naming the specific action: "Send", "Save draft", "Delete project". Never "OK!", "Let's go!", or bare "Yes"/"No" on consequential actions. Confirmation buttons repeat the consequence so the dialog is answerable without reading the body: "Delete this project?" offers `Delete project` and `Cancel`, not `Yes` and `No`.

### 4. Links Describe Their Destination

Link text makes sense out of context; screen-reader users navigate by a list of the page's links. "Read the billing docs", never "Click here" (which also fails the device-verb rule on touch), and never a bare "Learn more" when several appear on one page. Suffix each: "Learn more about exports".

### 5. One Capitalization Policy

Pick title case or sentence case per element type (all buttons, all headings) and apply it consistently; sentence case is the safer default: calmer, no per-word case rules, localizes cleanly. "Save Changes" beside "Discard changes" reads as sloppiness.

### 6. Errors Say How to Fix, Next to Where It Broke

An error is an instruction, adjacent to the failing field:

| Bad | Good |
| --- | --- |
| That password is too short | Choose a password with at least 8 characters |
| Invalid name | Use only letters for your name |
| Oops! Something went wrong. | Unable to save. Check your connection and try again. |

No blame, no "oops", no exclamation marks. Phrase hints positively ("Use only letters", not "Don't use numbers or symbols") and show them before the mistake, not after. If the same error keeps firing for many users, redesign the interaction instead of rewording it.

### 7. Empty States Point Forward

An empty state says what this place is and how to fill it, with one clear next action:

```html
<!-- Bad: a shrug -->
<p>No results.</p>

<!-- Good: orientation plus a next step -->
<p class="font-medium">No projects yet</p>
<p class="text-sm text-zinc-500">Projects keep your tasks and files together.</p>
<button class="mt-4">Create a project</button>
```

Search and filter empty states name the query and offer an exit: "No results for 'quarterly'. Clear filters". Never park crucial persistent information in an empty state; it disappears the moment content exists.

## Typography

Good typography is mostly restraint. A sensible scale, comfortable spacing and enough contrast beat any clever effect. A label, a table cell, a marketing headline and an article paragraph should not share one set of rules.

### 1. Fewer Fonts, Sizes and Weights

Rarely use more than three fonts. Weight and size define hierarchy, but overusing them hurts readability quickly. Pair for contrast, not similarity: a serif headline with a sans body reads as deliberate, two near-identical sans-serifs read as a mistake. Below `18px`, stay at weight `400`+; weights under `300` are display-only (`28px`+), they disappear at text sizes.

### 2. Use a Type Scale with Semantic Names

Define a small set of sizes and deviate from it as little as possible. Hard-coded sizes without a system break down at scale. For solo projects, default names like `text-sm` work fine as long as the usage rules are clear. On a team, name sizes by use (`text-body-sm`), not by size, so the rules stay consistent.

### 3. Heading Sizes Descend with Level

Within a coherent page hierarchy, map heading levels to descending steps of the type scale: a visually subordinate heading should not accidentally overpower its parent. Adjacent levels may share a size toward the small end of the scale as long as weight or spacing keeps them distinct. Pick semantic heading elements per the Accessibility principles above; this section controls only their visual treatment.

### 4. Line-Height by Role

Headings tighter, around `1.1`. Body copy `1.5` to `1.6`. Prefer unitless values so line-height scales with the font size; fixed values like `24px` do not. Tight line-height is for short text: anything that wraps to three or more lines needs at least `1.4`, even in height-constrained rows.

### 5. Cap the Measure

Long lines make it hard for the eye to find the next line. Cap long-form text around 60–75 characters per line. Any unit works: `65ch` measures characters directly, and a pixel or rem cap is just as good: at a `16px` body size the range lands roughly between `560px` and `680px` depending on the font, so Tailwind's `max-w-xl` or `max-w-2xl` fit. What matters is that a cap exists and the resulting line length sits in range.

### 6. Wrap Deliberately

`text-wrap: balance` distributes text evenly across lines: use it on headings. `text-wrap: pretty` avoids leaving a single short word on the final line: use it on descriptions. Skip both in long-form text: browsers ignore `balance` past a few lines anyway, and evening out a whole paragraph wastes space and makes it harder to read. `overflow-wrap: break-word` where long words, links or IDs could escape the container. `white-space: nowrap` on labels and badges where a line break looks broken.

### 7. Tabular Numbers on Changing Values

Digits have different widths by default, so timers, counters and prices shift layout as they update. Apply `font-variant-numeric: tabular-nums` to any value that changes.

### 8. Truncate Without Losing Content

Single line: `text-overflow: ellipsis` with `overflow: hidden` and `white-space: nowrap`. Multiple lines: `line-clamp`. Truncation hides content, so if the missing text matters, keep the full value reachable in a tooltip or expanded view.

### 9. Inputs at 16px on Mobile

iOS Safari zooms the whole page when an input's text is smaller than `16px`. Keep input text at `16px` on mobile viewports (`text-base sm:text-sm`). Avoid the `maximum-scale=1` viewport meta: Safari ignores it for pinch zoom, but every other browser honors it and blocks zooming, which fails WCAG.

## UI polish

Great interfaces rarely come from a single thing. It's usually a collection of small details that compound into a great experience. This section assumes an animation belongs; deciding whether it belongs at all, and what it costs the user at its trigger frequency, is a separate question worth asking before reaching for the recipes below.

### 1. Concentric Border Radius

Outer radius = inner radius + padding. Mismatched radii on nested elements is the most common thing that makes interfaces feel off. See `references/surfaces.md`.

### 2. Optical Over Geometric Alignment

When geometric centering looks off, align optically. Buttons with icons, play triangles, and asymmetric icons all need manual adjustment. See `references/surfaces.md`.

### 3. Shadows for Elevation, Borders for Structure

For buttons, cards, and containers whose border exists only to create depth, prefer layered transparent `box-shadow` values. Keep borders that communicate structure or state: dividers, layout separators, and selected or focus states. See `references/surfaces.md`.

### 4. Interruptible Animations

Use CSS transitions for interactive state changes: they can be interrupted mid-animation. Reserve keyframes for staged sequences that run once. See `references/animations.md`.

### 5. Split and Stagger Enter Animations

For an infrequent staged entrance where sequence helps communicate hierarchy, break content into semantic chunks and stagger them by ~100ms instead of animating one container. Confirm the entrance is infrequent enough to earn a stagger; anything the user triggers often should not stagger at all.

### 6. Subtle Exit Animations

Use a small fixed `translateY` instead of full height. Exits should be softer than enters. Use `ease-out` for both enter and exit transitions.

### 7. Contextual Icon Animations

Animate icons with `opacity`, `scale`, and `blur` instead of toggling visibility. Use exactly these values: scale from `0.25` to `1`, opacity from `0` to `1`, blur from `4px` to `0px`. If the project has `motion` or `framer-motion` in `package.json`, match that package's import path (or the established nearby imports when both exist) and use `transition: { type: "spring", duration: 0.3, bounce: 0 }`; bounce must always be `0`. If no motion library is installed, keep both icons in the DOM (one absolute-positioned) and cross-fade with CSS transitions using `cubic-bezier(0.2, 0, 0, 1)`; this gives both enter and exit animations without any dependency. See `references/animations.md`.

### 8. Image Outlines

Add a subtle `1px` outline with low opacity to images for consistent depth. The color must be pure black in light mode (`oklch(0 0 0 / 0.1)`) and pure white in dark mode (`oklch(1 0 0 / 0.1)`), never a near-black like slate, zinc, or any tinted neutral. A tinted outline picks up the surface color underneath it and reads as dirt on the image edge.

### 9. Scale on Press

A subtle `scale(0.96)` on click gives buttons tactile feedback. Always use `0.96`. Never use a value smaller than `0.95`: anything below feels exaggerated. Add a `static` prop to disable it when motion would be distracting.

### 10. Skip Animation on Page Load

Use `initial={false}` on `AnimatePresence` to prevent enter animations on first render. Verify it doesn't break intentional entrance animations.

### 11. Never Use `transition: all`

Always specify exact properties: `transition-property: scale, opacity`. Tailwind's `transition-transform` covers `transform, translate, scale, rotate`. See `references/performance.md`.

### 12. Use `will-change` Sparingly

Only for `transform`, `opacity`, `filter`, the properties the GPU can composite. Never use `will-change: all`. Only add when you notice first-frame stutter.

### 13. Match Icon Stroke to Text Weight

An icon next to text carries the text's optical weight: `1.5px` stroke beside regular (400) text, `2px` beside semibold (600). One stroke weight per icon set; never mix libraries on one surface. See `references/icons.md`.

### 14. One SVG, Recolored per State

Icons use `currentColor` and get their states (hover, selected, disabled) from CSS color and opacity, never from separate assets. Outline variant is the default; fill variant marks the active state.

### UI polish: common mistakes

| Mistake | Fix |
| --- | --- |
| Same border radius on closely nested parent and child | Calculate `outerRadius = innerRadius + padding` |
| Icons look off-center | Adjust optically with padding or fix SVG directly |
| Border used only to fake elevation | Use layered `box-shadow` with transparency; keep structural and state borders |
| Jarring staged entrance or contextual exit | Stagger infrequent entrances and keep context-preserving exits subtle |
| Stateful icon or toggle animates its default state on page load | Add `initial={false}` to that `AnimatePresence`; preserve intentional page entrances |
| `transition: all` on elements | Specify exact properties |
| First-frame animation stutter | Add `will-change: transform` (sparingly) |
| Hairline icon beside bold text | Match the stroke width to the text weight |
| Separate icon assets per state | One `currentColor` SVG, states via CSS |
| Filled icons everywhere | Outline as default, fill only for the active state |

## Review Output Format

Always use the following sections.

### Scope and Coverage

State the mode, exact scope, stack and styling conventions, and any review boundary. Then show coverage:

| Domain | Evidence inspected | Result |
| --- | --- | --- |
| Accessibility | Files, components, states, or checks | Findings count or `Clear` |

Include all five domains. `Clear` means inspected with no actionable finding; `Not reviewed` must explain why.

### Findings

Use one table ordered by severity, then reach and leverage:

| # | Severity | Domain | Location | Before | After | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | HIGH | Accessibility | `src/Dialog.tsx:42` | `<button><XIcon /></button>` | Add `aria-label="Close"` and hide the icon from the accessibility tree | The icon-only control has no accessible name |

Severity is one shared scale:

- `HIGH`: blocks a task, misleads the user, hides content or controls, causes data-loss risk, or creates a repeated systemic failure.
- `MEDIUM`: meaningfully harms comprehension, efficiency, adaptability, or consistency.
- `LOW`: isolated polish with limited task impact. Include only in `full` mode.

Within a severity, rank by reach and leverage. A token or shared-component fix outranks the same symptom in one leaf component.

Each row is one root cause: list every confirmed location in the same row rather than producing a row per occurrence. Respect the mode's finding cap, and never pad the report to reach it. If there are no findings, omit the table and state "No actionable interface findings."

### Considered but Rejected

Record candidates considered but deliberately rejected. A candidate is rejected when the principle above permits the current implementation, evidence is insufficient, the project convention is intentional, or the proposed change would add complexity without user benefit.

Include 1–3 candidates in `quick` mode and 2–5 in `full` mode:

| Location | Candidate | Rejected because |
| --- | --- | --- |
| `src/Card.tsx:28` | Increase the shadow | Existing depth matches the shared surface token; changing one card would reduce consistency |

These are real candidates inspected during the review, not invented filler. If the scope genuinely contains fewer borderline candidates, include the ones that exist and say so.

### Verification

Run safe, relevant checks available in the project. Inspect the rendered interface when runtime behavior or visual judgment matters. List each check or interaction, the exact command or steps, and the observed result. Separate checks that passed from checks marked **Not verified**; never convert a verification gap into a finding.

### Verdict

End with exactly one:

- `Block` — one or more `HIGH` findings remain.
- `Needs changes` — only `MEDIUM` or `LOW` findings remain.
- `Approve` — no actionable findings remain and the claimed coverage was verified.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| `outline: none` to remove the focus ring | Style `:focus-visible` instead; mouse clicks won't show it |
| `<div onClick>` for a button or link | `<button>` for actions, `<a href>` for navigation |
| Placeholder used as the only label | Add a visible `<label for>`; placeholders disappear on input |
| Positive `tabindex` to fix focus order | Fix the DOM order; only use `0` and `-1` |
| `aria-hidden="true"` on a focusable element | Remove it or make the element non-focusable |
| Submit disabled until the form is valid | Keep it enabled; validate on submit and focus the first error |
| Separator line where spacing would do | Remove the line, double the gap between groups |
| `margin-left` / `padding-right` in a localizable layout | `margin-inline-start` / `padding-inline-end` |
| Breakpoints at 768/1024 because they're the defaults | Break where the content actually stops fitting |
| Fixed-width text container sized to one language | `max-width` + wrapping; test pseudo-localization and representative locales |
| `OK` / `Yes` confirming a destructive dialog | Repeat the consequence: "Delete project" |
| "Click here" or bare "Learn more" link | Describe the destination: "Read the billing docs" |
| "Oops! Something went wrong." | Say what to do, next to the failing field |
| "Save Changes" beside "Discard changes" | One capitalization policy per element type |
| Hard-coded one-off font sizes | Use the type scale |
| `line-height: 24px` on scalable text | Unitless value (`1.5`) |
| Full-width paragraphs | Cap around 60–75 characters per line |
| Numbers cause layout shift | `tabular-nums` |
| Truncated text with no way to read it | Tooltip or expanded view for the full value |
| Inputs below `16px` zoom on iOS | `text-base sm:text-sm` |
| Six disconnected domain reports | Consolidate into one ranked findings table |
| Visual claim inferred only from source | Inspect the rendered state or mark it not verified |
| Review silently edits code | Stay read-only unless implementation was requested |
| "Approve" with pending actionable findings | Use `Needs changes` or `Block` |
