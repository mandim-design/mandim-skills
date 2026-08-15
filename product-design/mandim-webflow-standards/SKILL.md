---
name: Mandim Webflow Standards
description: Apply Mandim coding standards to Webflow projects using Client-First naming conventions. Use this skill whenever the user is writing, reviewing, refactoring, or generating HTML, CSS, or JavaScript for a Webflow project. Trigger on any mention of Webflow, Client-First, Finsweet, component classes, utility classes, is- prefix, section naming, CSS class naming, JS modules, GSAP animations, or any request to clean up, review, generate, or organize frontend code. Also trigger when the user pastes HTML/CSS/JS and asks for feedback, improvements, or to make it consistent with their style. Always use this skill before writing any frontend code for this user — even if the request seems simple.
---

# Mandim Webflow Standards

This skill enforces consistent code patterns for Webflow projects following the **Mandim Standards** system, built on top of the **Client-First** naming convention by Finsweet.

When working with the user's code:
1. **Read** → Summarize structure and identify pattern violations
2. **Audit** → Check against naming, HTML, and JS rules (`.claude/rules/`) and the checklists below
3. **Refactor/Generate** → Apply all conventions consistently

For detailed reference on any section, read the relevant file in `references/`.

**Naming and code-level conventions (CSS/Client-First, HTML structure, JS standards, GSAP) now live in `.claude/rules/css.md`, `html.md`, and `js.md` in the project's starter template — they load automatically by file type instead of depending on this skill being triggered. This skill covers the workflow and the delivery gate.**

---

## Loading strategy (still relevant beyond naming)

- Defer non-critical JS: `<script src="..." defer>`
- Async for independent scripts (analytics): `async`
- Inline critical CSS in `<head>`
- Preload critical fonts and stylesheets
- Performance targets (Core Web Vitals) live in the project's `CLAUDE.md`

---

## Accessibility Checklist

- [ ] Skip link: `<a href="#main-content" class="skip-link">`
- [ ] All images have meaningful `alt` text
- [ ] Forms: `<label for>` tied to every input
- [ ] Buttons: `aria-expanded`, `aria-controls`, `aria-label` where needed
- [ ] Focus states visible via `:focus-visible`
- [ ] ARIA live regions for dynamic content

---

## Pre-Launch Quality Gate

Before delivering any code, verify:
- [ ] All classes follow Client-First naming (underscore = component, no underscore = utility)
- [ ] No jQuery, no `var`
- [ ] JS comments in English
- [ ] One `<h1>`, semantic structure
- [ ] Images: `alt`, `width`, `height`, correct loading strategy
- [ ] GSAP respects `prefers-reduced-motion`
- [ ] Non-critical JS deferred/async
- [ ] LCP image has `fetchpriority="high"`

---

## Detailed Reference Files

For more examples and edge cases, read these files as needed:

- `references/class-naming.md` — Full Client-First class naming guide with examples
- `references/master-patterns.md` — Complete Mandim Standards master checklist
