# CSS Architecture & Viewport Fitting(自 SKILL.md 拆出,內容原樣)

### Required CSS Architecture

Every presentation MUST include this base CSS for viewport fitting:

```css
/* ===========================================
   VIEWPORT FITTING: MANDATORY BASE STYLES
   These styles MUST be included in every presentation.
   They ensure frames fit exactly in the viewport.
   =========================================== */

/* 1. Lock html/body to viewport */
html, body {
    height: 100%;
    overflow-x: hidden;
}

html {
    scroll-snap-type: y mandatory;
    scroll-behavior: smooth;
}

/* 2. Each frame = exact viewport height */
.frame {
    width: 100vw;
    height: 100vh;
    height: 100dvh; /* Dynamic viewport height for mobile browsers */
    overflow: hidden; /* CRITICAL: Prevent ANY overflow */
    scroll-snap-align: start;
    display: flex;
    flex-direction: column;
    position: relative;
}

/* 3. Content container with flex for centering */
.frame-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    max-height: 100%;
    overflow: hidden; /* Double-protection against overflow */
    padding: var(--frame-padding);
}

/* 4. ALL typography uses clamp() for responsive scaling */
:root {
    /* Titles scale from mobile to desktop */
    --title-size: clamp(1.5rem, 5vw, 3.5rem);
    --h2-size: clamp(1.25rem, 3.5vw, 2.25rem);
    --h3-size: clamp(1rem, 2.5vw, 1.75rem);

    /* Body text */
    --body-size: clamp(0.75rem, 1.5vw, 1.125rem);
    --small-size: clamp(0.65rem, 1vw, 0.875rem);

    /* Spacing scales with viewport */
    --frame-padding: clamp(1rem, 4vw, 4rem);
    --content-gap: clamp(0.5rem, 2vw, 2rem);
    --element-gap: clamp(0.25rem, 1vw, 1rem);

    /* Frame chrome */
    --chrome-height-top: clamp(2.5rem, 5vh, 3.5rem);
    --chrome-height-bottom: clamp(1.5rem, 3vh, 2.5rem);
}

/* 5. Theorem/definition/proof boxes use viewport-relative max sizes */
.theorem-box, .definition-box, .example-box, .lemma-box, .corollary-box {
    border-left: 4px solid var(--theorem-border);
    background: var(--theorem-bg);
    padding: clamp(0.5rem, 1.5vw, 1rem) clamp(0.75rem, 2vw, 1.5rem);
    margin: clamp(0.25rem, 0.5vw, 0.5rem) 0;
    max-height: min(40vh, 350px);
    overflow: hidden;
}

.theorem-box .env-title, .definition-box .env-title {
    font-weight: 700;
    font-size: var(--body-size);
    color: var(--theorem-border);
    margin-bottom: clamp(0.2rem, 0.5vw, 0.5rem);
}

.proof-box {
    border-left: 2px solid var(--proof-border);
    background: var(--proof-bg);
    padding: clamp(0.4rem, 1vw, 0.75rem) clamp(0.75rem, 2vw, 1.5rem);
    font-style: italic;
}

.proof-box::after {
    content: '\25A1'; /* QED square */
    float: right;
    font-style: normal;
}

.algorithm-box {
    border: 1px solid var(--theorem-border);
    background: var(--proof-bg);
    padding: clamp(0.5rem, 1.5vw, 1rem);
    font-family: var(--font-mono);
    font-size: var(--small-size);
    line-height: 1.6;
}

/* 6. Lists auto-scale with viewport */
.item-list, .enum-list {
    gap: clamp(0.4rem, 1vh, 1rem);
}

.item-list li, .enum-list li {
    font-size: var(--body-size);
    line-height: 1.4;
}

/* 7. Columns adapt to available space */
.columns {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr));
    gap: clamp(0.5rem, 1.5vw, 1rem);
}

/* 8. Images constrained to viewport */
img, .image-container {
    max-width: 100%;
    max-height: min(50vh, 400px);
    object-fit: contain;
}

/* ===========================================
   RESPONSIVE BREAKPOINTS
   Aggressive scaling for smaller viewports
   =========================================== */

/* Short viewports (< 700px height) */
@media (max-height: 700px) {
    :root {
        --frame-padding: clamp(0.75rem, 3vw, 2rem);
        --content-gap: clamp(0.4rem, 1.5vw, 1rem);
        --title-size: clamp(1.25rem, 4.5vw, 2.5rem);
        --h2-size: clamp(1rem, 3vw, 1.75rem);
    }
}

/* Very short viewports (< 600px height) */
@media (max-height: 600px) {
    :root {
        --frame-padding: clamp(0.5rem, 2.5vw, 1.5rem);
        --content-gap: clamp(0.3rem, 1vw, 0.75rem);
        --title-size: clamp(1.1rem, 4vw, 2rem);
        --body-size: clamp(0.7rem, 1.2vw, 0.95rem);
    }

    /* Hide non-essential elements */
    .frame-nav, .keyboard-hint, .decorative {
        display: none;
    }
}

/* Extremely short (landscape phones, < 500px height) */
@media (max-height: 500px) {
    :root {
        --frame-padding: clamp(0.4rem, 2vw, 1rem);
        --title-size: clamp(1rem, 3.5vw, 1.5rem);
        --h2-size: clamp(0.9rem, 2.5vw, 1.25rem);
        --body-size: clamp(0.65rem, 1vw, 0.85rem);
    }
}

/* Narrow viewports (< 600px width) */
@media (max-width: 600px) {
    :root {
        --title-size: clamp(1.25rem, 7vw, 2.5rem);
    }

    /* Stack columns vertically */
    .columns {
        grid-template-columns: 1fr;
    }
}

/* ===========================================
   REDUCED MOTION
   Respect user preferences
   =========================================== */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.2s !important;
    }

    html {
        scroll-behavior: auto;
    }
}
```

### Overflow Prevention Checklist

Before generating any presentation, mentally verify:

1. Every `.frame` has `height: 100vh; height: 100dvh; overflow: hidden;`
2. All font sizes use `clamp(min, preferred, max)`
3. All spacing uses `clamp()` or viewport units
4. Content containers have `max-height` constraints
5. Images have `max-height: min(50vh, 400px)` or similar
6. Columns use `auto-fit` with `minmax()` for responsive layout
7. Breakpoints exist for heights: 700px, 600px, 500px
8. No fixed pixel heights on content elements
9. Content per frame respects density limits
10. Theorem/proof boxes have `max-height` constraints

### When Content Does Not Fit

If you find yourself with too much content:

**DO:**
- Split into multiple frames
- Reduce bullet points (max 4-5 per frame)
- Shorten text (aim for 1-2 lines per bullet)
- Break long proofs across "Proof (cont.)" frames
- Create a "continued" frame

**DO NOT:**
- Reduce font size below readable limits
- Remove padding/spacing entirely
- Allow any scrolling
- Cram content to fit

### Testing Viewport Fit

After generating, recommend the user test at these sizes:
- Desktop: 1920x1080, 1440x900, 1280x720
- Tablet: 1024x768, 768x1024 (portrait)
- Mobile: 375x667, 414x896
- Landscape phone: 667x375, 896x414

---

