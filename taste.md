# PlateLab — Design & Style Reference

A living document capturing the visual language and design principles used in this project, for reuse in future builds.

---

## Design Principles

### 1. Visual-first, data-second
The main draw is the image — license plates, maps, photos. Lead with visuals; let text support them. Thumbnails appear in tooltips before the user even opens a panel. Data fills in around the image, never competes with it.

### 2. Terminal aesthetic
Everything is monospace. The app feels like a well-designed CLI or developer tool in a browser. This is intentional — it signals precision and makes structured data (plate format codes, dimensions, ISO identifiers) feel native rather than forced into a sans-serif world.

### 3. Dark-mode first
The default is dark. The map feels like a night-mode satellite view; the accent colors pop against a near-black canvas. Light mode is an inversion, not the primary target. Design and test in dark first.

### 4. Accent-driven color system
One accent color drives all interactive states: hover fills on the map, panel borders, section titles, footer link hovers, the status dot, tooltip top borders. The accent is swappable (green, blue, red, orange, white, black) via a single CSS custom property. Never hardcode interactive color — always use `var(--accent)`.

### 5. Progressive disclosure
The user's first touch is the map. Hovering shows a tooltip. Clicking opens a panel. Each layer reveals more detail. Don't front-load information — make the user pull it naturally.

### 6. Zero fluff
No shadow layers for depth, no gradients for backgrounds, no decorative icons. Separation comes from 1px borders and subtle background differences. Only add visual complexity if it carries meaning.

### 7. Minimal chrome, maximal content
The nav is one line. The footer is one line. Everything else is content. The map and panel get all the space.

### 8. No external JS dependencies
Vanilla JS only. The app must work with a single HTTP server. No bundler, no framework, no build step. This keeps the architecture simple and the page load fast.

---

## Typography

**Typeface:** JetBrains Mono (Google Fonts), with fallbacks: `'SF Mono', Monaco, Inconsolata, 'Fira Code', monospace`

All text is monospace. No serif, no sans-serif, no mixing families except within code/format display elements (which also use monospace stacks).

### Scale

| Use | Size | Weight | Transform | Tracking |
|---|---|---|---|---|
| Logo | `0.85em` | 700 | uppercase | `0.08em` |
| Nav tabs | `0.7em` | 600 | uppercase | `0.06em` |
| Status bar | `0.65em` | 400 | uppercase | `0.05em` |
| Footer | `0.6em` | 400 | — | `0.03em` |
| Panel country name | `24px` | 700 | uppercase | `0.08em` |
| Panel section title | `14px` | 700 | uppercase | `0.12em` |
| Panel field label | `10px` | 600 | uppercase | `0.08em` |
| Panel field value | `13px` | 400 | — | — |
| Format pattern display | `20px` | 700 | — | `0.15em` |
| Tooltip country name | `12px` | 600 | uppercase | `0.05em` |
| Forbidden/code tags | `11–12px` | 600 | — | — |

**Rule:** Labels are always uppercase with tracked spacing. Values are mixed-case and relaxed. This creates a clear label/value hierarchy without color.

---

## Color System

### Dark mode (default)

| Token | Value | Use |
|---|---|---|
| `body background` | `#0a0a0a` | Page background |
| `main background` | `#0a0f0d` | Map canvas (slight green tint) |
| `nav/footer background` | `#141414` | Chrome surfaces |
| `body color` | `#e8e8e8` | Primary text |
| `muted text` | `#888888` | Status bar, metadata |
| `dimmed text` | `#666666` | Footer, placeholders |
| `border` | `#2a2a2a` | Dividers, element borders |
| `border light` | `#333333` | Buttons, tags, panels |
| `panel background` | `rgba(10,10,10,0.95)` | Slide-in panel, tooltip |
| `tag/chip background` | `rgba(255,255,255,0.06)` | Code tags, list items |

### Light mode (`body.light`)

| Token | Value | Use |
|---|---|---|
| `body background` | `#f5f5f5` | Page background |
| `nav/footer/main` | `#ffffff` | Chrome surfaces |
| `body color` | `#1a1a1a` | Primary text |
| `border` | `#dddddd` | Dividers |
| `border element` | `#cccccc` | Buttons, tags |
| `muted text` | `#888888` | Labels |
| `panel background` | `rgba(255,255,255,0.95)` | Slide-in panel |
| `tag background` | `rgba(0,0,0,0.04)` | Code tags, list items |

### Accent palettes

Each accent defines four tokens:

```
--accent            primary fill / active states
--accent-stroke     border paired with --accent fill
--accent-light      light-mode primary (darker, readable on white)
--accent-light-dark light-mode border / title (darkest)
```

Plus two map tokens that tint the SVG land masses:

```
--land-dark / --land-dark-stroke   dark mode country fill
--land-light / --land-light-stroke light mode country fill
```

| Name | `--accent` | `--land-dark` |
|---|---|---|
| green (default) | `#44ff88` | `#0f3028` |
| blue | `#44aaff` | `#0f2030` |
| red | `#ff5566` | `#300f14` |
| orange | `#ffaa44` | `#302010` |
| white | `#ffffff` | `#1a1a1a` |
| black | `#000000` | `#0a0a0a` |

---

## Spacing & Layout

- **Base unit:** 4px
- **Content padding:** `28px` inside panels, `24px` in nav/footer
- **Small gaps:** `4px`, `6px`, `8px` for tight groupings
- **Section spacing:** `20px` top margin + `16px` padding-top per panel section
- **Field spacing:** `10px` between fields, `3px` between label and value

The layout is always `flex-direction: column` on body, with `flex: 1` on `<main>` to fill remaining height. The map is `position: absolute; inset: 0` inside a relative container.

---

## Borders & Radius

| Context | Radius |
|---|---|
| Most elements (buttons, tags, inputs) | `4px` |
| Panels, workbench panels | `8px` |
| Plate images inside panel | `4px` |
| Wiki button | `6px` |
| Accent dots | `50%` (circles) |

Borders are always 1px (`#2a2a2a` dark / `#ccc` light) except:
- Country panel: `2px solid var(--accent)` — this is the primary accent border in the UI
- Tooltip top edge: `2px solid var(--accent)` — the only colored border on the tooltip
- Map country paths: `stroke-width: 0.5`

---

## Interactive States & Transitions

All hover transitions are `0.15s ease`. Structural animations (panel slide-in, tab indicator) are `0.25–0.3s ease`.

| Element | Default | Hover / Active |
|---|---|---|
| Country on map | `var(--land-dark)` fill | `var(--accent)` fill |
| Map control buttons | `#888` icon color | `var(--accent)` icon color |
| Footer links | `#888888` | `var(--accent)` |
| Panel wiki button | `rgba(255,255,255,0.06)` bg | `rgba(255,255,255,0.12)` bg + accent border |
| Nav tab | `#777` text | `#ccc` (hover) / `#e8e8e8` (active) |
| Accent dots | normal | `scale(1.25)` |

Theme toggle uses a globally applied `body.theme-transition` class (applied for 300ms) that enables smooth property transitions across all elements simultaneously, then removes itself.

---

## Key Components

### Nav
One row: logo left, tabs center-right, theme toggle far-right. The active tab indicator is an absolutely positioned `<div>` that slides between tabs via `transform: translateX`. No underlines, no borders on tabs — just the indicator background and text color change.

### Tooltip
Appears on hover (desktop) or first tap (mobile). Dark frosted glass (`rgba(10,10,10,0.95)`), 1px border on all sides, 2px accent border on top only. Contains: country name (accent color, uppercase), plate image (max 160px wide), or "No plate data" in muted text.

### Country Panel
Slides in from the left (`translateX` from off-screen). Floats inside the map container with 12px inset, not inside the document flow. Width is `min(480px, 45% - 24px)`. On mobile it takes full width minus 24px. Has a 2px accent-colored border all around. Content: country name, plate image, then sections separated by 1px `#2a2a2a` dividers.

### Panel sections
Each section has: a title (uppercase, accent color, 14px bold, 0.12em tracking), followed by fields. Each field stacks label (`10px`, `#777`, uppercase) above value (`13px`, `#ccc`). The format pattern gets a special display: large monospace box with `0.15em` letter spacing, dark background, centered.

### Code/tag chips
Inline monospace elements with `rgba(255,255,255,0.06)` background and `1px solid #333` border. Used for plate codes, forbidden combinations, any short structured string that needs to stand out.

### Status dot
A 6px circle in `var(--accent)` color with a `pulse-dot` animation (opacity 1 → 0.4 → 1 over 2s). Appears in the nav status area.

### Accent drawer
Slides out horizontally from a button using `max-width: 0 → 120px` + opacity transition. Color swatches are 16px circles that scale to 1.25× on hover, with a white border when active.

---

## Motion

| Animation | Duration | Easing |
|---|---|---|
| Hover states (colors, backgrounds) | `0.15s` | `ease` |
| Tab indicator slide | `0.25s` | `ease` |
| Accent drawer open/close | `0.25s` | `ease` |
| Panel slide in/out | `0.3s` | `ease` |
| Theme transition | `0.3s` | `ease` |
| Status dot pulse | `2s` | `ease-in-out` |
| View fade | `0.2s` | `ease` |

No spring physics, no cubic-bezier curves. Everything uses `ease` or `ease-in-out`. Keep motion short and purposeful.

---

## Mobile

Breakpoint: `max-width: 768px`

- Touch targets minimum `44px × 44px` (map controls, close button, accent dots scale up)
- Panel fills full width minus 24px margin (12px each side)
- Two-tap interaction: first tap = tooltip, second tap = open panel
- `touch-action: none` on map container for custom gesture handling
- Pinch-to-zoom and single-finger pan via touch event handlers
- `user-scalable=no` in viewport meta (map manages its own zoom)

---

## Architecture Constraints (that affect design)

- **Single file.** All CSS and JS are inline in `index.html`. No external stylesheets.
- **No build step.** What you write is what ships. No PostCSS, no Sass.
- **CSS custom properties** are the entire theming system. Accent and mode switches happen by changing `data-accent` attribute and `body.light` class, nothing else.
- **LocalStorage** persists `theme` and `accent` preferences.
- Plate images are the only assets — all other UI is pure CSS/HTML.
