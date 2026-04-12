# Design System Specification: Greek A2 Education

## 1. Overview & Creative North Star
The "Creative North Star" for this design system is **The Hellenic Luminary**. 

The goal is to move beyond the "flat app" aesthetic common in mobile webviews and instead create an experience that feels like a premium, nocturnal study guide. We break the template-driven look by using **High-Contrast Chromatic Depth**: pairing deep, abyssal navy surfaces with high-energy, solar-inspired accents. 

To achieve a signature look, this system utilizes **Intentional Asymmetry** and **Tonal Layering**. We avoid the traditional "box-inside-a-box" layout. Instead, we treat the UI as a collection of glowing, floating artifacts that guide the user through their language journey. 

---

## 2. Colors: Chromatic Depth & The "No-Line" Rule
This palette is designed for high-end legibility and emotional resonance. The primary color is not just a highlight; it is the "light source" of the application.

### Core Tokens
*   **Primary (The Light):** `#fdd828` – Used for progression, success states, and primary actions.
*   **Surface (The Abyssal):** `#0b0d1a` – The foundational canvas.
*   **Secondary (The Shadow):** `#caccf7` – Used for secondary metadata and icons.

### The "No-Line" Rule
Explicitly prohibit 1px solid borders for sectioning. Structural boundaries must be defined solely through background color shifts or tonal transitions.
*   **The Layering Hierarchy:**
    *   **Surface (Base):** `#0b0d1a`
    *   **Surface Container Low:** `#101221` (Background for large sections)
    *   **Surface Container High:** `#1c1e30` (Interactive cards)
    *   **Surface Container Highest:** `#222537` (Active states or nested highlights)

### The "Glass & Gradient" Rule
To elevate the experience, use **Glassmorphism** for floating navigation and top bars.
*   **Backdrop Blur:** `12px - 20px`
*   **Transparency:** Use `surface_bright` at 60-80% opacity.
*   **Signature Textures:** Apply a subtle linear gradient to main CTAs from `primary` (#fdd828) to `primary_container` (#eeca12) at 135 degrees. This provides a tactile "glow" rather than a flat fill.

---

## 3. Typography: Editorial Authority
We use **Plus Jakarta Sans** for its geometric clarity and modern, open apertures, which mirror the clarity needed when learning a new alphabet.

*   **Display (Editorial Moments):** `display-lg` (3.5rem) should be used sparingly for achievement milestones (e.g., "Level Up").
*   **Headlines (Navigation):** `headline-sm` (1.5rem) is the standard for screen titles. Use `on_surface` with a slightly tighter letter-spacing (-0.02em) for an authoritative feel.
*   **Titles (Information Architecture):** `title-md` (1.125rem) is used for card headings.
*   **Body (Instructional):** `body-md` (0.875rem) is optimized for readability.
*   **Labels (The "Glossary" Look):** `label-sm` (0.6875rem) in ALL CAPS with `+0.05em` tracking for metadata like "STREAK" or "WORDS".

---

## 4. Elevation & Depth: Tonal Layering
This system rejects traditional drop shadows in favor of **Ambient Presence**.

*   **The Layering Principle:** Place a `surface_container_highest` card on a `surface` background to create a soft, natural lift. Depth is a result of color value, not artificial shadows.
*   **Ambient Shadows:** When a card must "float" (e.g., a modal or floating action button), use a diffuse shadow:
    *   **Blur:** `24px`
    *   **Opacity:** 8%
    *   **Color:** `#000000` (Never use pure black if the background is tinted; ensure the shadow feels like a occlusion of the navy background).
*   **The Ghost Border:** If a border is required for accessibility (e.g., in an input field), use `outline_variant` (#454756) at **20% opacity**. 100% opaque borders are strictly forbidden.

---

## 5. Components: Gamified Modernism

### Buttons
*   **Primary:** High-gloss gradient (`primary` to `primary_container`), `9999px` (Full) or `1.5rem` (md) radius. No border. Text in `on_primary` (#5b4c00).
*   **Secondary:** `surface_variant` background with `primary` text. No border.

### Cards (The "Hellenic" Card)
*   **Radius:** `xl` (3rem) or `lg` (2rem).
*   **Content:** No dividers. Use 24px vertical white space to separate groups.
*   **Nested Cards:** Use `surface_container_highest` inside a `surface_container_low` parent.

### Progress Indicators
*   **The Halo:** Circular progress indicators should use `primary` for the active path and `surface_variant` for the track.
*   **Linear:** Use a `24px` (full) rounded track. The active bar should have a subtle glow (Shadow: `0px 0px 8px primary`).

### Input Fields
*   **Style:** Minimalist. No background fill. A "Ghost Border" bottom-only or a very subtle `surface_container_high` background with `md` (1.5rem) corners.

---

## 6. Do’s and Don’ts

### Do:
*   **Do** use `primary` (#fdd828) as a focal point for the eye. It should represent "energy" and "progress."
*   **Do** embrace negative space. Mobile webviews often feel cluttered; give elements 24px-32px of breathing room.
*   **Do** use `plusJakartaSans` for all Greek characters to maintain a clean, modern aesthetic.
*   **Do** use "Full" rounded corners (9999px) for buttons to emphasize the gamified, friendly nature of the app.

### Don't:
*   **Don't** use 1px solid dividers to separate content. Use background color shifts.
*   **Don't** use pure white (#ffffff) for body text. Use `on_surface` (#eae9fd) to reduce eye strain in the dark navy environment.
*   **Don't** use sharp corners. The minimum radius for any container is `sm` (0.5rem), but the preference is `md` (1.5rem) or higher.
*   **Don't** use high-contrast drop shadows. They break the "Glass & Glow" aesthetic of the navy environment.