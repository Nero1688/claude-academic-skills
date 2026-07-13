# Troubleshooting & Example Session Flows(自 SKILL.md 拆出,內容原樣)

## Troubleshooting

### Common Issues

**KaTeX equations not rendering:**
- Verify the KaTeX CDN scripts are loaded (check `<head>` for katex.min.js and auto-render.min.js)
- Ensure the `onload` attribute on auto-render.min.js calls `renderMathInElement`
- Check delimiter configuration: `$...$` for inline, `$$...$$` for display
- Escape special characters in HTML (use `&amp;` for `&` inside equations if needed)

**Computer Modern fonts not loading:**
- Check that the CDN link to computer-modern CSS is present and accessible
- Ensure the font-family fallback chain includes Source Serif 4 and Georgia
- Test with the browser's network inspector to confirm the CSS file loads

**Theorem box overflow:**
- Verify `max-height: min(40vh, 350px)` is set on the theorem box
- Reduce theorem statement length (max 4 lines)
- Split long proofs across multiple frames with "Proof (cont.)" headings

**Frame numbering incorrect:**
- Check that `updateFrameCounter()` is called on navigation events
- Verify the `.frame-number` element exists in the footer
- Ensure `this.frames` selects all `.frame` elements correctly

**Progressive disclosure (pause) not working:**
- Verify `data-pause="N"` attributes are on the correct elements (N = 1, 2, 3, ...)
- Check that `advancePause()` is called before frame advance in `next()`
- Ensure `.paused-visible` class is being added to revealed elements

**Speaker notes display issues:**
- Speaker notes are stored as HTML comments: `<!-- NOTES: ... -->`
- For a dedicated speaker view, open browser developer tools to read comments
- Alternatively, generate a separate `-notes.html` file with notes visible

**Header/footer not appearing on all frames:**
- The header and footer are global elements outside individual frames
- They use `position: fixed` to stay visible across all frames
- Ensure they have `z-index: 100` above frame content

---

## Example Session Flows

### Conference Talk (Full Interactive)

1. User: "I need slides for my ICML 2026 talk on attention mechanisms"
2. **Phase 0.5:** Skill asks essential questions -- audience (domain experts), takeaway (a specific result: "our attention converges in O(sqrt(d))"), narrative arc (Problem -> Solution -> Results)
3. Phase 1: Skill asks remaining format questions -- purpose (Conference talk), length (Medium 10-20), content types (Theorems, Equations), field (Computer Science)
4. User shares their paper abstract and key results
5. Phase 2: Skill asks about desired tone (Modern/Minimal)
6. Skill generates 3 theme previews (Metropolis, Technical Report, Copenhagen)
7. User picks Theme A (Metropolis), asks for darker header bars
8. Skill generates presentation structured as Problem->Solution->Results, calibrated for domain experts, with the convergence theorem on a dedicated frame
9. Final presentation delivered

### Fast-Path (Theme + Topic in Args)

1. User: "/academic-slides 10-slide lecture on dynamic programming using Lecture Notes"
2. Skill detects fast path: length=10, purpose=lecture, theme=Lecture Notes, topic=dynamic programming
3. **Phase 0.5 (still mandatory):** Skill asks -- audience (students/newcomers), takeaway (a new method/technique), narrative arc (build-up/tutorial)
4. Skill generates 10-frame presentation using Lecture Notes theme, structured as a progressive tutorial, calibrated for students with definitions and examples before formalism
5. Final presentation delivered

### Paper-to-Slides (URL Provided)

1. User: "/academic-slides convert this paper to slides: https://eprint.iacr.org/2025/236"
2. Skill fetches and extracts paper content
3. **Phase 0.5:** Skill asks -- audience (technical but not specialist), takeaway (a specific result), narrative arc (background -> our work -> impact)
4. **Phase 1P:** Skill asks paper-specific questions -- focus (main results + method), coverage (deep dive on key results), skip (proofs and derivations)
5. Phase 2: Skill asks about theme preference
6. Skill generates presentation focused on main results and method, skipping proofs, calibrated for a technically literate but non-specialist audience
7. Final presentation delivered

### PPT Conversion

1. User: "Convert my research paper PPT to web slides"
2. Skill extracts content and images from PPT, flags detected equation objects
3. Skill confirms extracted content with user
4. **Phase 0.5:** Skill asks essential content questions (audience, takeaway, arc)
5. Skill asks about desired tone/theme
6. User picks a theme
7. Skill generates HTML presentation with preserved assets, equations converted to KaTeX, and content structured according to the chosen narrative arc
8. Final presentation delivered
