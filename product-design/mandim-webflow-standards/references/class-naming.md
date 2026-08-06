# Client-First Class Naming — Full Reference

This is the detailed naming guide behind the summary in `SKILL.md`. Read this when auditing an unfamiliar file, resolving an edge case, or generating a new component from scratch.

The whole system rests on one distinction: **does the underscore appear or not?**

- No underscore → **utility class** — reusable, single-purpose, no component context (`padding-large`, `text-color-primary`).
- Underscore → **component class** — scoped to one component, not meant to be reused elsewhere (`card_image`, `nav_link`).

If a class name doesn't make it obvious which one it is at a glance, it's wrong.

---

## Utility classes

Pattern: `[property]-[descriptor]-[value]`

Utilities describe *what they do*, never *where they're used*. They should be freely reusable across every component on the site.

### Spacing
```
padding-global
padding-section-small / -medium / -large / -xlarge
margin-bottom-small / -medium / -large
```

### Layout & sizing
```
container-small / -medium / -large / -full
display-none
display-block
position-relative
```

### Typography
```
text-size-tiny / -small / -regular / -large / -xlarge
text-weight-regular / -medium / -bold
text-color-primary / -secondary / -inverse
text-align-center
```

### Images
```
image-cover       ← object-fit: cover, fills the box
image-contain     ← object-fit: contain, fits inside the box
image-radius-small / -medium / -full
```

### Rules
- Full words only — never `sm`, `lg`, `btn`, `col`, `txt`.
- One utility = one CSS concern. Don't bundle unrelated properties into a single utility class.
- If you're tempted to write `hero-padding-large`, stop — that's scoping a utility to a component, which defeats the point. Use `padding-section-large` and let the component class handle anything hero-specific.

---

## Component classes

Pattern: `[component]_[element]`

Component classes describe *structure within one component*. They are never reused outside that component's context — if two components need the same visual treatment, that's a utility class, not a shared component class.

### Standard component skeleton
```
.card_component   ← root wrapper; always ends in _component
.card_wrapper     ← optional inner wrapper (e.g. for a link covering the whole card)
.card_content     ← text/content grouping
.card_image       ← media element
.card_title
.card_description
.card_button
.card_item        ← repeated child inside a list/grid (e.g. .card_item inside .card_list)
```

### Naming the root
Always suffix the root element with `_component`: `hero_component`, `testimonial_component`, `pricing-card_component`. This makes the component boundary unambiguous when scanning the Navigator or a stylesheet.

### Nested components
When a component contains another distinct component (not just a structural child), give the nested one its own `_component` root rather than treating it as an element of the parent:
```
.team-grid_component
  .team-grid_list
    .team-card_component   ← own component, not .team-grid_card
      .team-card_image
      .team-card_name
```

### Rules
- ❌ Never reuse a component class outside its component (`.card_button` styled once, used only inside `.card_component`).
- ❌ Never mix a utility pattern into a component name (`.card_padding-large` is wrong — use a utility class alongside it: `class="card_content padding-large"`).
- ✅ Component classes can and should be combined with utility classes on the same element: `class="card_title text-size-large text-color-primary"`.

---

## Combo / state classes (`is-`)

Pattern: `[base-class] is-[variant]`

`is-` classes always sit on top of an existing base class (utility or component) and toggle a variant or state. They are never used standalone because they carry no styling on their own outside their combo context.

```html
<div class="button is-primary">Primary</div>
<div class="button is-secondary is-disabled">Secondary, disabled</div>
<div class="nav_link is-active">Current page</div>
<div class="section_header is-home">Home page variant</div>
```

Common `is-` variants: `is-active`, `is-disabled`, `is-open`, `is-selected`, `is-current`, `is-home`, `is-dark`, `is-hidden`.

### Rules
- ❌ `<div class="is-active">` alone — meaningless without a base class.
- ✅ Style `is-` classes in Webflow using the combo-class workflow (select base class, add combo), never as an independent class in the Style panel.

---

## Page structure classes

These are fixed, non-negotiable class names — they exist so any Mandim-standard project has the same skeleton, regardless of which components live inside it.

```
.page-wrapper           ← single root wrapper, one per page
.main-wrapper            ← wraps <main>, holds all page content
.section_[name]          ← one per <section>, named for content (section_hero, section_pricing, section_faq)
.padding-global           ← left/right padding, applied inside every full-bleed section
.padding-section-[size]   ← top/bottom spacing, applied to the section wrapper
.container-[size]         ← centers and caps content width inside a section
```

### Section anatomy
```html
<section class="section_pricing">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">
        <!-- section content / component here -->
      </div>
    </div>
  </div>
</section>
```
This nesting order (`section_[name]` → `padding-global` → `container-[size]` → `padding-section-[size]`) is the standard wrap order — keep it consistent so every section behaves the same way when global padding or container width changes.

---

## Collection lists & CMS-bound components (Webflow-specific)

- The CMS Collection List wrapper gets the component's `_list` class: `.team-card_list`.
- Each Collection Item gets the component's `_item` class: `.team-card_item` — this is the class that becomes the repeating component root inside the list.
- Never style the Webflow-generated `.w-dyn-item` / `.w-dyn-list` classes directly — always add a Client-First class alongside them.
- Empty states use a dedicated class, not a bare div: `.team-card_empty-state`.

---

## Common naming mistakes to flag in review

| Wrong | Right | Why |
|---|---|---|
| `.btn-primary` | `.button is-primary` | Abbreviation + missing combo pattern |
| `.heroSection` | `.section_hero` | camelCase, and doesn't follow `section_[name]` |
| `.card__title` (BEM double underscore) | `.card_title` | Client-First uses a single underscore, not BEM |
| `.cardTitle` | `.card_title` | camelCase not allowed anywhere in class names |
| `.card_component.padding-large` (padding baked into component class) | `.card_content` + `.padding-large` as separate classes | Utilities must stay reusable and separate |
| `.is-card-active` | `.card_component is-active` | `is-` is always a suffix combo, not a prefix on its own compound name |
| `.txt-lg` | `.text-size-large` | No abbreviations, ever |
