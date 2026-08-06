---
name: Mandim Webflow Standards
description: Apply Mandim coding standards to Webflow projects using Client-First naming conventions. Use this skill whenever the user is writing, reviewing, refactoring, or generating HTML, CSS, or JavaScript for a Webflow project. Trigger on any mention of Webflow, Client-First, Finsweet, component classes, utility classes, is- prefix, section naming, CSS class naming, JS modules, GSAP animations, or any request to clean up, review, generate, or organize frontend code. Also trigger when the user pastes HTML/CSS/JS and asks for feedback, improvements, or to make it consistent with their style. Always use this skill before writing any frontend code for this user — even if the request seems simple.
---

# Mandim Webflow Standards

This skill enforces consistent code patterns for Webflow projects following the **Mandim Standards** system, built on top of the **Client-First** naming convention by Finsweet.

When working with the user's code:
1. **Read** → Summarize structure and identify pattern violations
2. **Audit** → Check against naming, HTML, JS, and performance rules below
3. **Refactor/Generate** → Apply all conventions consistently

For detailed reference on any section, read the relevant file in `references/`.

---

## CSS Class Naming (Client-First)

### Utility Classes — no underscore
Pattern: `[property]-[descriptor]-[value]`
- Never abbreviate. Full descriptive words only.
- Examples: `padding-global`, `padding-section-large`, `text-size-large`, `text-color-primary`, `display-none`, `container-medium`

### Custom Component Classes — always underscore
Pattern: `[component]_[element]`
- The underscore is what distinguishes component classes from utility classes.
- Examples: `card_component`, `card_image`, `nav_link`, `footer_column`, `hero_content`

### Combo / State Classes — `is-` prefix
Pattern: `[base-class] is-[variant]`
- Always added ON TOP of a base class, never standalone.
- Examples: `button is-primary`, `section_header is-home`, `nav_link is-active`

### Page Structure Classes (always use these)
```
.page-wrapper
.main-wrapper
.section_[name]         ← anchors + Navigator panel organization
.padding-global         ← universal left/right padding
.padding-section-[size] ← universal top/bottom section spacing
.container-[size]       ← max-width content container
```

### Component Template
```
.[name]_component   ← main wrapper
.[name]_wrapper
.[name]_content
.[name]_item
.[name]_image
.[name]_button
```

### Key Rules
- ❌ No abbreviations (`btn`, `txt`, `col`) — always spell it out
- ❌ No camelCase in class names
- ❌ No `is-` classes used standalone
- ✅ Lowercase with hyphens for utilities, underscore for components

For the full naming guide — grids, forms, CMS collection lists, and common mistakes — read `references/class-naming.md`.

---

## HTML Structure

- Use semantic HTML5: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`
- One `<h1>` per page. Logical heading hierarchy (h1 → h2 → h3).
- All interactive elements must be keyboard accessible.
- `<a href>` for navigation. `<button type="button">` for actions.

### Landmark template
```html
<div class="page-wrapper">
  <header class="header_component" role="banner">
    <nav class="nav_component" role="navigation" aria-label="Primary">
    </nav>
  </header>
  <main class="main-wrapper" role="main" id="main-content">
  </main>
  <footer class="footer_component" role="contentinfo">
  </footer>
</div>
```

### Images
- Always include `alt`, `width`, `height`
- LCP/hero images: `fetchpriority="high" decoding="async"` — NO `loading="lazy"`
- All other images: `loading="lazy" decoding="async"`
- Use `<picture>` with WebP/AVIF sources for performance-critical images
- Class patterns: `image-cover` (fills), `image-contain` (fits), `image-radius-[size]`, `image-radius-full`

---

## JavaScript Standards

- ES6+ only: `const`/`let`, never `var`
- No jQuery — vanilla JS only
- All comments in **English**
- Module pattern: one feature per file, exported as named functions

### Module structure
```js
// feature.js — export named init function
export const initFeatureName = () => {
  const el = document.querySelector('.component_element');
  // logic
};

// main.js — import and call on DOMContentLoaded
import { initFeatureName } from './feature.js';
document.addEventListener('DOMContentLoaded', () => {
  initFeatureName();
});
```

### DOM & events
- `querySelector` / `querySelectorAll` — no jQuery
- `addEventListener('scroll', fn, { passive: true })` for scroll/touch
- Debounce resize/scroll handlers (250ms)
- Throttle frequent events
- Use `data-` attributes for JS hooks, not CSS classes

### Comments pattern (JSDoc for functions)
```js
/**
 * Short description of what this does
 * @param {string} param - What it is
 */
const myFunction = (param) => {
  // Inline comments explaining non-obvious logic
};
```

---

## GSAP Animations

- Load from CDN with `defer`
- Only animate GPU-accelerated properties: `x`, `y`, `scale`, `rotation`, `opacity`
- ❌ Never animate `width`, `height`, `margin`, `padding` (causes reflow)
- Always check `prefers-reduced-motion`

```js
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!prefersReducedMotion) {
  gsap.from('.element', { opacity: 0, y: 30, duration: 0.6, ease: 'power2.out' });
} else {
  gsap.set('.element', { opacity: 1, y: 0 });
}
```

---

## Performance Targets (Core Web Vitals)

| Metric | Target |
|--------|--------|
| LCP    | < 2.5s |
| INP    | < 200ms |
| CLS    | < 0.1 |
| TTFB   | < 200ms |
| DOM nodes | < 1,500 |
| DOM depth | < 32 |

- Defer non-critical JS: `<script src="..." defer>`
- Async for independent scripts (analytics): `async`
- Inline critical CSS in `<head>`
- Preload critical fonts and stylesheets

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
