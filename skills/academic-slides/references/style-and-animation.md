# Style Reference & Animation Patterns(自 SKILL.md 拆出,內容原樣)

## Style Reference: Tone-to-Effect Mapping

Use this guide to match visual treatment to intended tone:

### Formal / Traditional
- Serif fonts (Computer Modern, Source Serif 4)
- Muted, institutional colors (navy, burgundy, forest green)
- Structured header/footer chrome with bars
- Generous whitespace, precise alignment
- Best themes: Madrid, Warsaw, Cambridge, Thesis Defense

### Modern / Clean
- Sans-serif fonts (Source Sans 3, Inter for body only)
- High contrast, minimal decoration
- Thin or absent header/footer bars
- Generous whitespace, content-focused
- Best themes: Metropolis, Technical Report

### Warm / Pedagogical
- Serif or rounded sans-serif fonts
- Warmer palette (cream backgrounds, warm grays, soft blues)
- Approachable, larger font sizes
- Visible structure aids (section numbers, outlines)
- Best themes: Lecture Notes, Seminar, Copenhagen

### Dense / Technical
- Compact spacing, smaller base font
- Monospace accents for code and algorithms
- Equation-heavy layouts, multi-column support
- Structured environments (theorem, definition, algorithm boxes)
- Best themes: Berlin, Classic Serif, Journal Article

---

## Animation Patterns Reference

Academic presentations use restrained, purposeful animation. The only entrance effect is a subtle fade.

### Entrance Animation

```css
/* Subtle fade -- the only entrance animation for academic use. */
.reveal {
    opacity: 0;
    transition: opacity 0.3s ease-in-out;
}

.frame.visible .reveal {
    opacity: 1;
}

/* Stagger children subtly. */
.reveal:nth-child(1) { transition-delay: 0.05s; }
.reveal:nth-child(2) { transition-delay: 0.1s; }
.reveal:nth-child(3) { transition-delay: 0.15s; }
.reveal:nth-child(4) { transition-delay: 0.2s; }
```

### Progressive Disclosure (Beamer \pause)

```css
/* Elements hidden until their pause step is reached. */
[data-pause] {
    opacity: 0;
    transition: opacity 0.3s ease-in-out;
}

[data-pause].paused-visible {
    opacity: 1;
}
```

### Reduced Motion

```css
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

**Do not use any of the following in academic presentations:**
- Scale, slide, or blur entrance animations
- Gradient mesh or noise texture backgrounds
- Grid pattern overlays
- 3D tilt or parallax effects
- Custom cursor with trail
- Particle system backgrounds
- Magnetic buttons or hover effects
- Counter animations

---

