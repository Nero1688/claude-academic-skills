# HTML Architecture, JavaScript Features & Code Quality(自 SKILL.md 拆出,內容原樣)

### HTML Architecture

Follow this structure for all presentations:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Presentation Title</title>

    <!-- Academic Fonts — 釘死版本 + SRI(子資源完整性)；CDN 內容若被竄改，瀏覽器會拒絕載入 -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/computer-modern@0.1.2/cmu-serif.css"
        integrity="sha384-bmXwZFPTzbsTyqOUN+esSEAvRmtdAGP8q+IH0WCmlP6Y5TwLwS7PWaZWX6ylJujF"
        crossorigin="anonymous" referrerpolicy="no-referrer">
    <!-- OR Google Fonts alternative
         ⚠️ 隱私提醒：Google Fonts 的 CSS 為動態產生，無法加 SRI，且載入時會把觀眾 IP 送給 Google。
         隱私敏感或離線(氣隙)場合，請刪掉下面這行、只用上面的 Computer-Modern，或把字型檔自帶進專案。 -->
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap">

    <!-- KaTeX for equation rendering — 釘死 0.16.47 + SRI -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.47/dist/katex.min.css"
        integrity="sha384-nH0MfJ44wi1dd7w6jinlyBgljjS8EJAh2JBoRad8a3VDw2K69vfaaqm4WnR+gXtA"
        crossorigin="anonymous" referrerpolicy="no-referrer">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.47/dist/katex.min.js"
        integrity="sha384-CwjPRVHTvLiMBFjEoij+QZViMV5rhTOIp7CJzl24JEqpRDA1sJFHVXXLURktbYYp"
        crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.47/dist/contrib/auto-render.min.js"
        integrity="sha384-bjyGPfbij8/NDKJhSGZNP/khQVgtHUE5exjm4Ydllo42FwIgYsdLO2lXGmRBf5Mz"
        crossorigin="anonymous" referrerpolicy="no-referrer"
        onload="renderMathInElement(document.body, {delimiters: [{left: '$$', right: '$$', display: true},{left: '$', right: '$', display: false}]});"></script>

    <style>
        /* ===========================================
           CSS CUSTOM PROPERTIES (THEME)
           Easy to modify: change these to change the whole look.
           =========================================== */
        :root {
            /* Typography */
            --font-heading: 'CMU Serif', 'Source Serif 4', Georgia, serif;
            --font-body: 'CMU Serif', 'Source Serif 4', Georgia, serif;
            --font-mono: 'CMU Typewriter Text', 'Source Code Pro', 'Courier New', monospace;

            /* Frame Chrome */
            --header-bg: #2c3e50;
            --header-fg: #ffffff;
            --footer-bg: #2c3e50;
            --footer-fg: #ffffff;

            /* Environment Colors */
            --theorem-bg: #e8f4f8;
            --theorem-border: #2980b9;
            --definition-bg: #fdf2e9;
            --definition-border: #e67e22;
            --proof-bg: #f9f9f9;
            --proof-border: #95a5a6;
            --example-bg: #eafaf1;
            --example-border: #27ae60;
            --alert-bg: #fdedec;
            --alert-border: #e74c3c;

            /* Viewport fitting vars (must use clamp) */
            --title-size: clamp(1.5rem, 5vw, 3.5rem);
            --h2-size: clamp(1.25rem, 3.5vw, 2.25rem);
            --body-size: clamp(0.75rem, 1.5vw, 1.125rem);
            --small-size: clamp(0.65rem, 1vw, 0.875rem);
            --frame-padding: clamp(1rem, 4vw, 4rem);
            --content-gap: clamp(0.5rem, 2vw, 2rem);
            --h3-size: clamp(1rem, 2.5vw, 1.75rem);
            --element-gap: clamp(0.25rem, 1vw, 1rem);

            /* Frame chrome */
            --chrome-height-top: clamp(2.5rem, 5vh, 3.5rem);
            --chrome-height-bottom: clamp(1.5rem, 3vh, 2.5rem);

            /* Animation */
            --ease-subtle: ease-in-out;
            --duration-normal: 0.3s;
        }

        /* ===========================================
           BASE STYLES
           =========================================== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            scroll-behavior: smooth;
            scroll-snap-type: y mandatory;
            height: 100%;
        }

        body {
            font-family: var(--font-body);
            background: #ffffff;
            color: #2c3e50;
            overflow-x: hidden;
            height: 100%;
        }

        /* ===========================================
           FRAME CONTAINER
           CRITICAL: Each frame MUST fit exactly in viewport.
           - Use height: 100vh (NOT min-height).
           - Use overflow: hidden to prevent scroll.
           - Content must scale with clamp() values.
           =========================================== */
        .frame {
            width: 100vw;
            height: 100vh; /* Exact viewport height, no scrolling. */
            height: 100dvh; /* Dynamic viewport height for mobile. */
            scroll-snap-align: start;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden; /* Prevent any content overflow. */
        }

        /* Content wrapper that prevents overflow. */
        .frame-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            max-height: 100%;
            overflow: hidden;
            padding: var(--frame-padding);
            padding-top: calc(var(--chrome-height-top) + var(--frame-padding));
            padding-bottom: calc(var(--chrome-height-bottom) + var(--frame-padding));
        }

        /* ===========================================
           FRAME HEADER AND FOOTER (Beamer-style chrome)
           =========================================== */
        .frame-header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--chrome-height-top);
            background: var(--header-bg);
            color: var(--header-fg);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 var(--frame-padding);
            font-size: var(--small-size);
            z-index: 100;
        }

        .frame-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: var(--chrome-height-bottom);
            background: var(--footer-bg);
            color: var(--footer-fg);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 var(--frame-padding);
            font-size: var(--small-size);
            z-index: 100;
        }

        /* ===========================================
           TITLE FRAME
           =========================================== */
        .title-frame .frame-content {
            text-align: center;
            align-items: center;
        }

        .title-frame h1 {
            font-family: var(--font-heading);
            font-size: var(--title-size);
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: var(--content-gap);
        }

        .title-frame .subtitle {
            font-size: var(--h2-size);
            color: var(--theorem-border);
            margin-bottom: var(--content-gap);
        }

        .author-block {
            font-size: var(--body-size);
            line-height: 1.6;
        }

        .author-block .author {
            font-weight: 600;
        }

        .author-block .institute {
            font-style: italic;
        }

        /* ===========================================
           SECTION DIVIDER FRAME
           =========================================== */
        .section-frame .frame-content {
            text-align: center;
            align-items: center;
        }

        .section-frame .section-number {
            font-size: var(--title-size);
            font-weight: 700;
            color: var(--theorem-border);
            opacity: 0.3;
        }

        /* ===========================================
           THEOREM ENVIRONMENTS
           Beamer-style environments for formal content.
           =========================================== */
        .theorem-box, .definition-box, .example-box, .lemma-box, .corollary-box {
            border-left: 4px solid var(--theorem-border);
            background: var(--theorem-bg);
            padding: clamp(0.5rem, 1.5vw, 1rem) clamp(0.75rem, 2vw, 1.5rem);
            margin: clamp(0.25rem, 0.5vw, 0.5rem) 0;
            max-height: min(40vh, 350px);
            overflow: hidden;
        }

        .definition-box {
            border-left-color: var(--definition-border);
            background: var(--definition-bg);
        }

        .example-box {
            border-left-color: var(--example-border);
            background: var(--example-bg);
        }

        .theorem-box .env-title,
        .definition-box .env-title,
        .example-box .env-title,
        .lemma-box .env-title,
        .corollary-box .env-title {
            font-weight: 700;
            font-size: var(--body-size);
            color: var(--theorem-border);
            margin-bottom: clamp(0.2rem, 0.5vw, 0.5rem);
        }

        .definition-box .env-title {
            color: var(--definition-border);
        }

        .example-box .env-title {
            color: var(--example-border);
        }

        .proof-box {
            border-left: 2px solid var(--proof-border);
            background: var(--proof-bg);
            padding: clamp(0.4rem, 1vw, 0.75rem) clamp(0.75rem, 2vw, 1.5rem);
            font-style: italic;
            margin: clamp(0.25rem, 0.5vw, 0.5rem) 0;
        }

        .proof-box::after {
            content: '\25A1'; /* QED square. */
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
            margin: clamp(0.25rem, 0.5vw, 0.5rem) 0;
        }

        /* ===========================================
           EQUATION BLOCK
           For centered display equations with annotations.
           =========================================== */
        .equation-block {
            text-align: center;
            margin: var(--content-gap) 0;
            font-size: clamp(1rem, 2vw, 1.5rem);
        }

        /* ===========================================
           CITATION BLOCK
           For reference lists.
           =========================================== */
        .citation-block {
            font-size: var(--small-size);
            line-height: 1.5;
            padding-left: 2em;
            text-indent: -2em;
        }

        .citation-block p {
            margin-bottom: clamp(0.15rem, 0.3vw, 0.3rem);
        }

        /* ===========================================
           COLUMNS (replaces .grid)
           Multi-column layouts for side-by-side content.
           =========================================== */
        .columns {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr));
            gap: clamp(0.5rem, 1.5vw, 1rem);
        }

        .columns.two-col {
            grid-template-columns: 1fr 1fr;
        }

        .columns.three-col {
            grid-template-columns: 1fr 1fr 1fr;
        }

        /* ===========================================
           ITEM LIST AND ENUM LIST
           =========================================== */
        .item-list {
            list-style: none;
            padding: 0;
        }

        .item-list li {
            font-size: var(--body-size);
            line-height: 1.4;
            padding-left: 1.5em;
            position: relative;
            margin-bottom: clamp(0.2rem, 0.5vw, 0.5rem);
        }

        .item-list li::before {
            content: '\25B8'; /* Small right triangle, similar to Beamer. */
            position: absolute;
            left: 0;
            color: var(--theorem-border);
            font-weight: bold;
        }

        .enum-list {
            padding-left: 1.5em;
        }

        .enum-list li {
            font-size: var(--body-size);
            line-height: 1.4;
            margin-bottom: clamp(0.2rem, 0.5vw, 0.5rem);
        }

        /* ===========================================
           RESPONSIVE BREAKPOINTS
           Adjust content for different screen sizes.
           =========================================== */
        @media (max-height: 700px) {
            :root {
                --frame-padding: clamp(0.75rem, 3vw, 2rem);
                --content-gap: clamp(0.4rem, 1.5vw, 1rem);
                --title-size: clamp(1.25rem, 4.5vw, 2.5rem);
                --h2-size: clamp(1rem, 3vw, 1.75rem);
            }
        }

        @media (max-height: 600px) {
            :root {
                --frame-padding: clamp(0.5rem, 2.5vw, 1.5rem);
                --content-gap: clamp(0.3rem, 1vw, 0.75rem);
                --title-size: clamp(1.1rem, 4vw, 2rem);
                --body-size: clamp(0.7rem, 1.2vw, 0.95rem);
            }

            .frame-nav, .keyboard-hint, .decorative {
                display: none;
            }
        }

        @media (max-height: 500px) and (orientation: landscape) {
            :root {
                --title-size: clamp(1rem, 3.5vw, 1.5rem);
                --frame-padding: clamp(0.4rem, 2vw, 1rem);
            }
        }

        @media (max-width: 600px) {
            :root {
                --title-size: clamp(1.25rem, 7vw, 2.5rem);
            }

            .columns {
                grid-template-columns: 1fr;
            }
        }

        /* ===========================================
           ANIMATIONS
           Subtle fade only. Academic presentations
           do not need flashy entrance effects.
           =========================================== */
        .reveal {
            opacity: 0;
            transition: opacity var(--duration-normal) var(--ease-subtle);
        }

        .frame.visible .reveal {
            opacity: 1;
        }

        /* Stagger children subtly. */
        .reveal:nth-child(1) { transition-delay: 0.05s; }
        .reveal:nth-child(2) { transition-delay: 0.1s; }
        .reveal:nth-child(3) { transition-delay: 0.15s; }
        .reveal:nth-child(4) { transition-delay: 0.2s; }

        /* ===========================================
           PROGRESSIVE DISCLOSURE (Beamer \pause equivalent)
           Elements with data-pause="N" are hidden until
           the user advances to pause step N.
           =========================================== */
        [data-pause] {
            opacity: 0;
            transition: opacity var(--duration-normal) var(--ease-subtle);
        }

        [data-pause].paused-visible {
            opacity: 1;
        }

        /* ===========================================
           REDUCED MOTION
           Respect user preferences.
           =========================================== */
        @media (prefers-reduced-motion: reduce) {
            .reveal {
                transition: opacity 0.2s ease;
            }

            html {
                scroll-behavior: auto;
            }
        }

        /* ... more theme-specific styles ... */
    </style>
</head>
<body>
    <!-- Frame Header (Beamer-style) -->
    <header class="frame-header">
        <span class="short-title">Paper Title</span>
        <span class="section-title">Current Section</span>
    </header>

    <!-- Frames -->
    <section class="frame title-frame">
        <div class="frame-content">
            <h1 class="reveal">Presentation Title</h1>
            <p class="reveal subtitle">Subtitle or Conference Name</p>
            <div class="author-block reveal">
                <p class="author">Author Name</p>
                <p class="institute">University / Institution</p>
                <p class="date">Conference, Date</p>
            </div>
        </div>
    </section>

    <section class="frame section-frame">
        <div class="frame-content">
            <span class="section-number">1</span>
            <h2>Section Title</h2>
        </div>
    </section>

    <section class="frame">
        <div class="frame-content">
            <h2 class="reveal">Frame Title</h2>
            <div class="theorem-box reveal" data-pause="1">
                <span class="env-title">Theorem 1 (Main Result)</span>
                <p>The theorem statement using $inline math$ and display:</p>
                <p>$$\int_a^b f(x)\,dx = F(b) - F(a)$$</p>
            </div>
            <div class="proof-box reveal" data-pause="2">
                <span class="env-title">Proof.</span>
                <p>By the fundamental theorem of calculus...</p>
            </div>
        </div>
    </section>

    <!-- More frames... -->

    <!-- Frame Footer -->
    <footer class="frame-footer">
        <span class="author-short">A. Name</span>
        <span class="title-short">Short Title</span>
        <span class="frame-number"></span>
    </footer>

    <script>
        /* ===========================================
           ACADEMIC PRESENTATION CONTROLLER
           Handles frame navigation, progressive disclosure
           (pause), animations, and keyboard/touch input.
           =========================================== */

        class AcademicPresentation {
            constructor() {
                this.frames = document.querySelectorAll('.frame');
                this.currentFrame = 0;
                this.currentPause = 0;
                this.init();
            }

            init() {
                this.setupNavigation();
                this.setupIntersectionObserver();
                this.setupProgressiveDisclosure();
                this.updateFrameCounter();
                this.showFrame(0);
            }

            /* ----- Navigation ----- */

            setupNavigation() {
                /* Keyboard: arrows, space, page up/down. */
                document.addEventListener('keydown', (e) => {
                    switch(e.key) {
                        case 'ArrowRight':
                        case 'ArrowDown':
                        case ' ':
                        case 'PageDown':
                            e.preventDefault();
                            this.next();
                            break;
                        case 'ArrowLeft':
                        case 'ArrowUp':
                        case 'PageUp':
                            e.preventDefault();
                            this.prev();
                            break;
                        case 'Home':
                            e.preventDefault();
                            this.goToFrame(0);
                            break;
                        case 'End':
                            e.preventDefault();
                            this.goToFrame(this.frames.length - 1);
                            break;
                    }
                });

                /* Touch/swipe support. */
                let touchStartY = 0;
                document.addEventListener('touchstart', (e) => {
                    touchStartY = e.touches[0].clientY;
                });
                document.addEventListener('touchend', (e) => {
                    const deltaY = touchStartY - e.changedTouches[0].clientY;
                    if (Math.abs(deltaY) > 50) {
                        deltaY > 0 ? this.next() : this.prev();
                    }
                });

                /* Mouse wheel. */
                let wheelTimeout;
                document.addEventListener('wheel', (e) => {
                    e.preventDefault();
                    clearTimeout(wheelTimeout);
                    const delta = e.deltaY;
                    wheelTimeout = setTimeout(() => {
                        delta > 0 ? this.next() : this.prev();
                    }, 50);
                }, { passive: false });
            }

            /* ----- Frame Display ----- */

            next() {
                /* Advance pause first, then next frame. */
                if (this.advancePause()) return;
                if (this.currentFrame < this.frames.length - 1) {
                    this.showFrame(this.currentFrame + 1);
                }
            }

            prev() {
                if (this.currentFrame > 0) {
                    this.showFrame(this.currentFrame - 1);
                }
            }

            goToFrame(index) {
                this.showFrame(index);
            }

            showFrame(index) {
                /* Reset pause state on the frame being left.
                   Design choice: backward navigation resets to step 0,
                   matching Beamer's default \pause behavior. */
                const leaving = this.frames[this.currentFrame];
                if (leaving) {
                    leaving.querySelectorAll('[data-pause]').forEach(el =>
                        el.classList.remove('paused-visible'));
                }
                this.currentFrame = index;
                this.currentPause = 0;
                this.frames[index].scrollIntoView({ behavior: 'smooth' });
                this.updateFrameCounter();
            }

            /* ----- Progressive Disclosure (\pause) ----- */

            setupProgressiveDisclosure() {
                this.frames.forEach(frame => {
                    frame.querySelectorAll('[data-pause]').forEach(el => {
                        el.classList.remove('paused-visible');
                    });
                });
            }

            advancePause() {
                const frame = this.frames[this.currentFrame];
                const pauseElements = frame.querySelectorAll('[data-pause]');
                const nextPause = this.currentPause + 1;
                let found = false;

                pauseElements.forEach(el => {
                    if (parseInt(el.dataset.pause) === nextPause) {
                        el.classList.add('paused-visible');
                        found = true;
                    }
                });

                if (found) {
                    this.currentPause = nextPause;
                    return true; /* Consumed the advance. */
                }
                return false; /* No more pauses, advance frame. */
            }

            /* ----- Intersection Observer ----- */

            setupIntersectionObserver() {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('visible');
                        }
                    });
                }, { threshold: 0.5 });

                this.frames.forEach(frame => observer.observe(frame));
            }

            /* ----- Frame Counter ----- */

            updateFrameCounter() {
                const counter = document.querySelector('.frame-number');
                if (counter) {
                    counter.textContent = `${this.currentFrame + 1} / ${this.frames.length}`;
                }
            }
        }

        /* Initialize presentation. */
        new AcademicPresentation();
    </script>
</body>
</html>
```

### Required JavaScript Features

Every presentation should include:

1. **AcademicPresentation Class** -- Main controller
   - Keyboard navigation (arrows, space, page up/down, home/end)
   - Touch/swipe support
   - Mouse wheel navigation
   - Progress indicator (frame counter "X / Y" in footer)

2. **Intersection Observer** -- For scroll-triggered animations
   - Add `.visible` class when frames enter viewport
   - Trigger CSS fade-in efficiently

3. **Progressive Disclosure** -- Beamer `\pause` equivalent
   - Elements with `data-pause="N"` are hidden initially
   - Each "next" press reveals the next pause group before advancing the frame
   - Allows step-by-step theorem proofs, equation derivations, algorithm walkthroughs

4. **Frame Counter** -- "Frame X of Y" display in the footer

### Code Quality Requirements

**Comments:**
Every section should have clear comments explaining:
- What it does
- Why it exists
- How to modify it

```javascript
/* ===========================================
   PROGRESSIVE DISCLOSURE
   Implements Beamer's \pause command for HTML.
   - Elements with data-pause="N" are hidden initially.
   - Pressing next reveals pause group N before advancing.
   - This allows step-by-step reveals within a single frame.
   =========================================== */
```

**Accessibility:**
- Semantic HTML (`<section>`, `<nav>`, `<header>`, `<footer>`)
- Keyboard navigation works
- ARIA labels where needed
- Reduced motion support

```css
@media (prefers-reduced-motion: reduce) {
    .reveal {
        transition: opacity 0.2s ease;
    }
}
```

**Responsive and Viewport Fitting (CRITICAL):**

**See the "CRITICAL: Viewport Fitting Requirements" section above for complete CSS and guidelines.**

Quick reference:
- Every `.frame` must have `height: 100vh; height: 100dvh; overflow: hidden;`
- All typography and spacing must use `clamp()`
- Respect content density limits (max 4-5 bullets, max 4-line theorems, etc.)
- Include breakpoints for heights: 700px, 600px, 500px
- When content does not fit -> split into multiple frames, never scroll

---

