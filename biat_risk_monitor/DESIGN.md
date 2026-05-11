---
name: BIAT Risk Monitor
colors:
  surface: '#07122a'
  surface-dim: '#07122a'
  surface-bright: '#2f3952'
  surface-container-lowest: '#030d25'
  surface-container-low: '#101b33'
  surface-container: '#151f37'
  surface-container-high: '#1f2942'
  surface-container-highest: '#2a344e'
  on-surface: '#d9e2ff'
  on-surface-variant: '#bacac3'
  inverse-surface: '#d9e2ff'
  inverse-on-surface: '#263049'
  outline: '#85948e'
  outline-variant: '#3c4a45'
  surface-tint: '#38debb'
  primary: '#ffffff'
  on-primary: '#00382d'
  primary-container: '#5ffbd6'
  on-primary-container: '#00725e'
  inverse-primary: '#006b58'
  secondary: '#b6c6ed'
  on-secondary: '#20304f'
  secondary-container: '#374767'
  on-secondary-container: '#a5b5db'
  tertiary: '#ffffff'
  on-tertiary: '#393000'
  tertiary-container: '#fbe273'
  on-tertiary-container: '#756400'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#5ffbd6'
  primary-fixed-dim: '#38debb'
  on-primary-fixed: '#002019'
  on-primary-fixed-variant: '#005142'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#b6c6ed'
  on-secondary-fixed: '#091b39'
  on-secondary-fixed-variant: '#374767'
  tertiary-fixed: '#fbe273'
  tertiary-fixed-dim: '#dec65a'
  on-tertiary-fixed: '#211b00'
  on-tertiary-fixed-variant: '#534600'
  background: '#07122a'
  on-background: '#d9e2ff'
  surface-variant: '#2a344e'
typography:
  display-lg:
    fontFamily: Hanken Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-padding: 24px
  gutter: 16px
  stack-sm: 4px
  stack-md: 12px
  stack-lg: 32px
---

## Brand & Style
The design system for BIAT Risk Monitor is engineered for high-stakes enterprise financial surveillance. The aesthetic prioritizes authority, precision, and rapid cognitive processing. The brand personality is "Vigilant Professionalism"—a calm, structured environment that allows risk officers to identify anomalies instantly. 

The style utilizes a **Corporate Modern** foundation infused with **Glassmorphism** for layered data visualization. By using translucent surfaces and high-contrast accents, the UI creates a sense of depth and technical sophistication. This approach ensures that while the interface feels high-fidelity and futuristic, it remains grounded in the reliability required for a banking institution.

## Colors
The palette is built on a deep "Midnight Navy" foundation to reduce eye strain during extended monitoring sessions. 

- **Primary Accent:** "Banking Blue" (#64FFDA) is used sparingly for primary actions, focus states, and key data points. 
- **Surface Tiers:** Backgrounds use #0A192F, while interactive surfaces and containers use #112240. 
- **Functional Semantics:** Risk colors are saturated to ensure they "pop" against the dark background. "Critical" (#D32F2F) is reserved for immediate threats, while "Danger" (#FF5252) signifies high-risk trends.
- **Contrast:** Text and icons utilize a range of cool greys to maintain hierarchy without the harshness of pure white.

## Typography
Typography in this design system balances modern sans-serif readability with technical monospaced precision. 

- **Headlines:** Hanken Grotesk provides a sharp, contemporary look for high-level metrics and page titles.
- **Body:** Inter is used for its exceptional legibility in data-dense tables and descriptions.
- **Data Labels:** JetBrains Mono is employed for all numerical data, timestamps, and status tags to evoke a "live-feed" or technical monitor feel, ensuring digits are easy to compare vertically.

## Layout & Spacing
The design system utilizes a **12-column fluid grid** for the main dashboard content. 

- **Rhythm:** An 8px linear scale governs all spacing.
- **Desktop:** 24px margins and 16px gutters to provide enough "breathability" for dense financial data.
- **Sidebars:** The navigation sidebar is fixed at 280px to maximize the horizontal space for complex data tables and charts.
- **Mobile Adaptivity:** On mobile devices, the 12-column grid collapses to a single-column stack with 16px horizontal margins. Glassmorphism effects are reduced on mobile to maintain performance.

## Elevation & Depth
Elevation is expressed through **Tonal Layering** and **Subtle Glassmorphism** rather than traditional heavy shadows.

- **Level 0 (Background):** #0A192F (Flat).
- **Level 1 (Cards/Containers):** #112240 with a 1px border (#233554).
- **Level 2 (Modals/Popovers):** #112240 with a background-blur (20px) and 10% white opacity tint to create a "frosted" effect.
- **Interaction:** Hovering over a card should increase the border brightness (#64FFDA at 30% opacity) rather than adding a shadow, maintaining the "flat-high-tech" look.

## Shapes
The shape language of the design system is "Rounded" (Level 2). This softens the "clinical" nature of financial data, making the interface more approachable for daily use.

- **Standard Containers:** 0.5rem (8px) radius.
- **Large Cards/Dashboards:** 1rem (16px) radius.
- **Inputs & Buttons:** 0.5rem (8px) to match container harmony.
- **Status Pills:** Fully rounded (pill-shaped) to distinguish them from interactive buttons.

## Components
- **Buttons:** Primary buttons use a solid #64FFDA fill with dark text. Secondary buttons use a ghost style with a #64FFDA border. 
- **Risk Indicators:** Small circular "pips" or high-contrast pill-shaped tags (e.g., "CRITICAL") using the risk color palette.
- **Input Fields:** Darker than the surface (#0D1B2A) with a subtle 1px border. Focus state triggers a primary blue glow.
- **Data Tables:** Zebra-striping is avoided; instead, use thin #233554 horizontal dividers. Header rows should use `label-sm` typography in all-caps.
- **Cards:** Incorporate a subtle gradient from top-left to bottom-right (Primary Blue at 5% opacity to transparent) to suggest light source direction.
- **Charts:** Use a refined palette derived from the primary banking blue and risk colors. Line charts should use "glow" effects (neon-style) for the primary data path.