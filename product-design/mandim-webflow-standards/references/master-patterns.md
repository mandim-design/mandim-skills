# Mandim Standards — Master Pattern Checklist

The complete checklist behind `SKILL.md`'s summary. Walk through this top to bottom on any full audit; jump to a section directly when reviewing one concern.

---

## 1. HTML structure

### Semantic skeleton
- `<header>` / `<nav>` / `<main>` / `<section>` / `<article>` / `<aside>` / `<footer>` — never a `<div>` where a semantic tag fits.
- Exactly one `<h1>` per page, and heading levels never skip (no `h2` straight to `h4`).
- Every `<section>` should be independently meaningful — if it's just a layout wrapper with no distinct content, it's not a `<section>`.

### Landmarks
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
- `role="banner"` / `role="navigation"` / `role="main"` / `role="contentinfo"` are redundant with the semantic tags for most browsers but keep them — Webflow's exported markup and some older AT combinations benefit from the explicit role.
- `id="main-content"` exists specifically as the skip-link target.

### Links vs. buttons
- `<a href="...">` for anything that navigates (including same-page anchors and Webflow CMS links).
- `<button type="button">` for anything that triggers JS behavior without navigating (toggles, modals, accordions). Never a `<div onclick>`.
- Never use `<a href="#">` as a fake button — it breaks keyboard behavior (Enter fires, Space scrolls) and pollutes browser history.

### Forms
- Every input has a real `<label for="id">`, not a placeholder standing in for a label.
- Group related fields with `<fieldset>` / `<legend>` (e.g. radio groups).
- Required fields: `aria-required="true"` plus a visible indicator, not color alone.
- Client-side validation errors are announced via `aria-live="polite"` regions tied to the field with `aria-describedby`.

### Images
- `alt`, `width`, `height` on every `<img>` — width/height (or `aspect-ratio`) prevent CLS even before the image loads.
- LCP/hero image: `fetchpriority="high" decoding="async"`, **no** `loading="lazy"` (lazy-loading the LCP element delays it).
- Every other image: `loading="lazy" decoding="async"`.
- Purely decorative images: `alt=""` (empty, not omitted) so screen readers skip them.
- Performance-critical images (hero, above-the-fold): `<picture>` with AVIF/WebP sources and a JPEG/PNG fallback.
- Class patterns: `image-cover`, `image-contain`, `image-radius-[size]`, `image-radius-full`.

---

## 2. JavaScript

### Language baseline
- ES6+: `const`/`let` only, arrow functions where they read cleaner, template literals over string concatenation.
- No jQuery, no legacy Webflow-exported jQuery snippets left in `<head>`/`<body>` embeds — replace them with vanilla JS during any refactor.
- All comments in English, regardless of the surrounding copy's language.

### Module pattern
One feature per file, exported as a named function, wired up centrally:
```js
// accordion.js
export const initAccordion = () => {
  const triggers = document.querySelectorAll('[data-accordion-trigger]');
  triggers.forEach((trigger) => {
    trigger.addEventListener('click', () => {
      const expanded = trigger.getAttribute('aria-expanded') === 'true';
      trigger.setAttribute('aria-expanded', String(!expanded));
    });
  });
};

// main.js
import { initAccordion } from './accordion.js';
import { initFeatureName } from './feature.js';

document.addEventListener('DOMContentLoaded', () => {
  initAccordion();
  initFeatureName();
});
```
- Never leave feature logic loose in `main.js` — it should only import and call `init*` functions.
- Each `init*` function should be safe to call even if its target elements don't exist on the current page (`querySelectorAll` on zero matches is a no-op — don't hard-fail).

### DOM & events
- `querySelector` / `querySelectorAll`, never jQuery selectors or `$()`.
- Scroll/touch listeners: `{ passive: true }` unless the handler needs `preventDefault()`.
- Debounce resize/scroll handlers at ~250ms; throttle high-frequency events (e.g. `mousemove`-driven effects) instead of debouncing when continuous feedback matters.
- JS hooks live in `data-*` attributes (`data-modal-trigger`), never in CSS classes — this keeps styling and behavior decoupled so a class rename never silently breaks a script.

### Documentation
JSDoc on every exported function:
```js
/**
 * Opens the modal matching the given data-modal-id.
 * @param {string} modalId - Value of the target [data-modal-id] attribute.
 */
export const openModal = (modalId) => {
  const modal = document.querySelector(`[data-modal-id="${modalId}"]`);
  if (!modal) return;
  modal.setAttribute('aria-hidden', 'false');
};
```
Inline comments only where the *why* isn't obvious from the code (a browser quirk being worked around, a non-obvious ordering requirement) — not restating what the line already says.

---

## 3. GSAP animation

- Load GSAP (and plugins) from CDN with `defer` so it never blocks first paint.
- GPU-accelerated properties only: `x`, `y`, `scale`, `rotation`, `opacity`. Never animate `width`, `height`, `top`, `left`, `margin`, `padding` — these trigger layout reflow every frame.
- Always branch on `prefers-reduced-motion` and provide a static end-state fallback, not just a shorter/faster animation:
```js
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!prefersReducedMotion) {
  gsap.from('.element', { opacity: 0, y: 30, duration: 0.6, ease: 'power2.out' });
} else {
  gsap.set('.element', { opacity: 1, y: 0 });
}
```
- ScrollTrigger instances: kill and re-create on breakpoint changes where the animation's start/end points depend on layout that shifts between mobile and desktop, rather than letting stale trigger positions accumulate.
- Keep animation timelines in their own module (`animations.js`), separate from interaction logic (`accordion.js`, `modal.js`).

---

## 4. Performance (Core Web Vitals)

| Metric | Target | Primary levers |
|--------|--------|-----------------|
| LCP | < 2.5s | `fetchpriority="high"` on the LCP image, preload critical fonts, avoid render-blocking JS above the fold |
| INP | < 200ms | Keep JS handlers short, debounce/throttle, avoid layout thrashing (reading `offsetHeight` in a loop, etc.) |
| CLS | < 0.1 | `width`/`height` or `aspect-ratio` on all media, reserve space for embeds/ads, avoid injecting content above existing content after load |
| TTFB | < 200ms | Mostly a hosting/CDN concern in Webflow — flag if consistently missed, but it's outside code-level fixes |
| DOM nodes | < 1,500 | Flatten unnecessary wrapper divs; Webflow's nested-div tendency is the usual culprit |
| DOM depth | < 32 | Same — audit deeply nested component wraps |

- Non-critical JS: `defer`. Independent third-party scripts (analytics, chat widgets): `async`.
- Inline critical above-the-fold CSS in `<head>` when the page has a heavy custom stylesheet; otherwise Webflow's own CSS pipeline handles this.
- `<link rel="preload">` for the LCP image/font and any web font used in the hero.

---

## 5. Accessibility

- Skip link as the first focusable element: `<a href="#main-content" class="skip-link">Skip to content</a>`, visually hidden until focused.
- Every image has meaningful `alt` text (or `alt=""` if decorative) — never a filename or "image".
- Every form input has a `<label for>`; placeholder text is never a substitute for a label.
- Interactive components expose state via ARIA: `aria-expanded` on accordion/dropdown triggers, `aria-controls` pointing at the controlled element's `id`, `aria-label` on icon-only buttons.
- Visible focus states via `:focus-visible` — never `outline: none` without a replacement focus style.
- Dynamic content changes (form errors, live-updated counters, toast notifications) live inside `aria-live="polite"` (or `"assertive"` for urgent errors) regions.
- Color is never the only signal for state (error fields, active nav links) — pair it with an icon, text, or shape change.

---

## 6. Pre-launch quality gate

Run through this immediately before delivering or shipping any code:

- [ ] All classes follow Client-First naming — underscore = component, no underscore = utility, `is-` always a combo
- [ ] No jQuery anywhere, no `var`
- [ ] JS comments in English; exported functions have JSDoc
- [ ] Exactly one `<h1>`; heading hierarchy has no skipped levels; semantic landmarks used throughout
- [ ] All images: `alt`, `width`/`height`, correct `loading`/`fetchpriority`
- [ ] GSAP animations respect `prefers-reduced-motion` and only touch GPU-safe properties
- [ ] Non-critical JS is `defer`/`async`; nothing render-blocking above the fold
- [ ] LCP image has `fetchpriority="high"` and is not lazy-loaded
- [ ] Forms: labeled inputs, `aria-required`, live-region error announcements
- [ ] Focus states visible on every interactive element
- [ ] DOM node/depth counts checked on component-heavy pages
