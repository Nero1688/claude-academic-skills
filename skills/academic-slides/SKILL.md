---
name: academic-slides
description: Create Beamer-inspired academic HTML presentations from scratch or by converting PowerPoint files. Use when the user wants to build slides for a conference talk, lecture, seminar, or thesis defense. Supports theorem environments, KaTeX equations, algorithm pseudocode, and citations. Helps academics discover their preferred visual theme through Beamer-style previews rather than abstract choices.
---

# Academic Slides Skill

Create zero-dependency, Beamer-inspired HTML presentations that run entirely in the browser. This skill helps academics and researchers build professional presentations with proper theorem environments, equation rendering via KaTeX, and structured frame navigation. Users discover their preferred theme through visual exploration ("show, don't tell"), then the skill generates production-quality frame decks.

## Core Philosophy

1. **Zero Build Dependencies** -- Single HTML files with inline CSS/JS. KaTeX loaded via CDN for equations. No npm, no build tools.
2. **Show, Don't Tell** -- People don't know what they want until they see it. Generate visual theme previews for academic users.
3. **Academic Authenticity** -- Beamer-inspired structure, Computer Modern typography, proper theorem environments. Not PowerPoint-with-serif-fonts.
4. **Production Quality** -- Accessible, responsive, well-commented code.
5. **Viewport Fitting (CRITICAL)** -- Every frame MUST fit exactly within the viewport. No scrolling within frames, ever. This is non-negotiable.

---

## CRITICAL: Viewport Fitting Requirements

**This section is mandatory for ALL presentations. Every frame must be fully visible without scrolling on any screen size.**

### The Golden Rule

```text
Each frame = exactly one viewport height (100vh/100dvh)
Content overflows? -> Split into multiple frames or reduce content
Never scroll within a frame.
```

### Content Density Limits

To guarantee viewport fitting, enforce these limits per frame:

| Frame Type | Maximum Content |
|------------|-----------------|
| Title Frame | 1 title + 1 subtitle + author/institute/date block |
| Content Frame | 1 heading + 4-5 bullet points OR 1 heading + 2 short paragraphs |
| Theorem/Proof Frame | 1 theorem box (max 4 lines) + 1 proof sketch (max 5 lines) |
| Equation Frame | 1 heading + 1-3 display equations with optional annotation |
| Algorithm Frame | 1 heading + max 12 lines of pseudocode |
| Definition Frame | 1 heading + 1-2 definition boxes (max 3 lines each) |
| Citation/References Frame | 1 heading + max 8 reference entries |
| Section Divider Frame | 1 section number + 1 section title + optional outline |

**If content exceeds these limits -> Split into multiple frames**


### CSS 架構與溢版防治(已拆出)

撰寫任何 slide HTML/CSS 前,讀 `references/css-architecture.md`:必用的 CSS 骨架、溢版防治檢查清單、內容塞不下時的處理順序、視口貼合測試法。上方的 Golden Rule 與密度上限是鐵律,細節與程式碼全在該檔。

## Phase 0: Detect Mode

First, determine what the user wants:

**Mode A: New Academic Presentation**
- User wants to create slides from scratch for a talk, lecture, or defense
- Proceed to Phase 0.5 (Essential Content Questions), then Phase 1 (Content Discovery)

**Mode B: PPT/PDF/Paper Conversion**
- User has an existing PowerPoint, PDF, or paper URL to convert to web slides
- Proceed to Phase 4 (Content Extraction), then Phase 0.5, then Phase 1P (Paper Focus Discovery)

**Mode C: Existing Presentation Enhancement**
- User has an HTML presentation and wants to improve it
- Read the existing file, understand the structure, then enhance

### Fast-Path Detection

If the user's initial message specifies enough to skip format questions (e.g., topic, approximate length, and/or theme name are all present), you MAY skip the format-mechanical questions in Phase 1 (purpose, length, content types, field). However, you MUST still run Phase 0.5 (Essential Content Questions) before generating. **No presentation should ever be generated without asking the Phase 0.5 questions.**

**Examples of fast-path triggers:**
- "/academic-slides 10-slide lecture on dynamic programming using Metropolis"
- "/academic-slides conference talk on our ICML paper, Berlin theme"
- "Make 15 slides about transformer attention for my lab meeting"

In all of these cases, format is clear from context but content quality questions have not been answered. Proceed to Phase 0.5.

---

## Phase 0.5: Essential Content Questions (MANDATORY)

**These questions MUST be asked before generating any presentation, regardless of mode or how much information the user provided in their initial message.** They cannot be inferred from topic or theme -- they require the user's judgment. Ask all 3 in a single AskUserQuestion call.

### Why These Questions Matter

A presentation on "transformer attention" for a room of NLP researchers looks completely different from one for undergraduate CS students. A talk where the takeaway is "our method is 3x faster" structures differently from one where the takeaway is "this theoretical framework unifies prior work." These questions determine content strategy, not just format.

### The Questions (Single AskUserQuestion Call)

**Question 1: Audience**
- Header: "Audience"
- Question: "Who is your audience?"
- Options:
  - "Domain experts" -- They know the field well; skip basics, focus on contributions and technical details
  - "Technical but not specialist" -- They have technical background but are not in your exact subfield
  - "Students / newcomers" -- They need context, definitions, and motivation before results
  - "Mixed / general academic" -- Varies widely; balance accessibility with depth

**Question 2: Key Takeaway**
- Header: "Takeaway"
- Question: "If the audience remembers ONE thing from your talk, what should it be?"
- Options:
  - "A specific result" -- A theorem, benchmark, or experimental finding (will ask you to state it)
  - "A new method or technique" -- How to do something they could not do before
  - "A conceptual framework" -- A way of thinking about a problem or connecting ideas
  - "A problem or open question" -- Motivating future work or collaboration

**Question 3: Narrative Arc**
- Header: "Structure"
- Question: "How should the presentation flow?"
- Options:
  - "Problem -> Solution -> Results" -- Classic research talk structure
  - "Background -> Our Work -> Impact" -- Contextualizes contribution in the field
  - "Survey / Comparison" -- Review multiple approaches, compare trade-offs
  - "Build-up / Tutorial" -- Teach concepts progressively, layer by layer

### Follow-Up: Key Result Statement

If the user chose "A specific result" as their takeaway, follow up immediately:

"Please state the key result in one sentence. This will be featured prominently in the slides."

Store the user's response as the KEY_RESULT to place on a dedicated frame and echo in the conclusion frame.

### How Answers Shape Content

**Audience -> Depth calibration:**
- "Domain experts" -> Skip introductory definitions, assume notation familiarity, spend frames on technical details and proofs, include comparison with prior work
- "Technical but not specialist" -> Include 1-2 frames of background/notation, explain key terms on first use, focus on intuition before formalism
- "Students / newcomers" -> Lead with motivation and examples, define all notation, use progressive disclosure heavily, include recap frames
- "Mixed / general academic" -> Start accessible (motivation, big picture), add depth progressively, mark technical deep-dives as optional

**Takeaway -> Emphasis strategy:**
- "A specific result" -> Build the entire talk toward stating and supporting this result. Place it on a dedicated frame and repeat in conclusion.
- "A new method or technique" -> Motivate the problem, then spend most frames on the method with worked examples. Include a summary frame with key steps.
- "A conceptual framework" -> Start with the fragmented view (what existed before), then reveal the unifying framework. Use comparison frames.
- "A problem or open question" -> Build evidence for why the problem matters, show what has been tried, end with the open question and potential directions.

**Narrative Arc -> Frame sequencing:**
- "Problem -> Solution -> Results" -> Title, Motivation/Problem (1-2 frames), Prior Work (1 frame), Our Approach (2-3 frames), Results (2-3 frames), Conclusion
- "Background -> Our Work -> Impact" -> Title, Background (2-3 frames), Our Contribution (3-4 frames), Validation (1-2 frames), Impact/Future Work, Conclusion
- "Survey / Comparison" -> Title, Overview/Taxonomy, Approach A, Approach B, Approach C, Comparison Table, Takeaways, Open Problems
- "Build-up / Tutorial" -> Title, Prerequisites, Concept 1, Concept 2, Concept 3, Putting It Together, Examples, Summary

---

## Phase 1: Content Discovery (New Presentations -- Full Interactive Mode)

**Prerequisite:** Phase 0.5 (Essential Content Questions) has already been completed.

If the user is on the fast path (topic, length, and theme all known from initial message), skip this phase entirely -- Phase 0.5 has already captured what matters for quality. Proceed to Phase 2 (Style Discovery) or Phase 3 (Generate) as appropriate.

For full interactive mode, ask the remaining format-detail questions via AskUserQuestion:

### Step 1.1: Presentation Context

**Question 1: Purpose**
- Header: "Purpose"
- Question: "What is this presentation for?"
- Options:
  - "Conference talk" -- Presenting research at a conference (ICML, NeurIPS, STOC, etc.)
  - "Lecture/Course" -- Teaching a class, course lecture, or tutorial
  - "Seminar/Workshop" -- Lab meeting, reading group, or invited talk
  - "Thesis Defense" -- Master's or doctoral thesis/dissertation defense

**Question 2: Length**
- Header: "Length"
- Question: "Approximately how many frames?"
- Options:
  - "Short (5-10)" -- Lightning talk, brief seminar
  - "Medium (10-20)" -- Standard conference talk
  - "Long (20+)" -- Full lecture, thesis defense

**Question 3: Content Readiness**
- Header: "Content"
- Question: "Do you have the content ready, or do you need help structuring it?"
- Options:
  - "I have all content ready" -- Just need to design the presentation
  - "I have rough notes" -- Need help organizing into frames
  - "I have a topic only" -- Need help creating the full outline

**Question 4: Academic Content Types**
- Header: "Content Types"
- Question: "What types of academic content will your presentation include?"
- multiSelect: true
- Options:
  - "Theorems/Proofs/Lemmas" -- Formal mathematical statements and their proofs
  - "Equations/Derivations" -- Display math, inline equations, step-by-step derivations
  - "Algorithms/Pseudocode" -- Algorithm descriptions, pseudocode blocks
  - "Citations/References" -- Bibliography entries, paper references

**Question 5: Field**
- Header: "Field"
- Question: "What academic field is this for?"
- Options:
  - "Mathematics/Statistics" -- Pure math, applied math, probability, statistics
  - "Computer Science/Engineering" -- Systems, ML, theory, hardware
  - "Natural Sciences" -- Physics, chemistry, biology
  - "Humanities/Social Sciences" -- Economics, linguistics, philosophy

If user has content, ask them to share it (text, bullet points, paper draft, etc.).

---

## Phase 1P: Paper Focus Discovery (Paper/URL Conversion Only)

**This phase runs AFTER content extraction (Phase 4) and AFTER Phase 0.5, but BEFORE theme selection and generation.** It is specific to Mode B when the source is a research paper (PDF, arXiv URL, or paper file).

After extracting and summarizing the paper content, ask via AskUserQuestion:

### Step 1P.1: Focus and Coverage

**Question 1: Paper Focus**
- Header: "Focus"
- Question: "Which aspects of the paper should the slides emphasize?"
- multiSelect: true
- Options:
  - "Main results / theorems" -- The core contribution and its formal statement
  - "Method / approach" -- How the technique works, algorithm details
  - "Experiments / evaluation" -- Benchmarks, comparisons, ablations
  - "Motivation / problem setup" -- Why this problem matters, background context

**Question 2: Depth vs. Breadth**
- Header: "Coverage"
- Question: "How should the paper content be presented?"
- Options:
  - "Deep dive on key results" -- Focus 70% of frames on 1-2 main contributions, skip minor details
  - "Balanced overview" -- Cover all sections roughly equally
  - "Highlight reel" -- One frame per major point, emphasize the story arc
  - "Extended with discussion" -- Include interpretation, limitations, and connections to other work

**Question 3: What to Skip** (optional -- only ask if the paper is long or has many sections)
- Header: "Skip"
- Question: "Is there anything in the paper you want to skip or minimize?"
- Options:
  - "Related work section" -- Will handle comparisons verbally
  - "Proofs and derivations" -- Just state results, skip formal proofs
  - "Experimental details" -- Show headline numbers only, skip methodology
  - "Nothing -- include everything relevant"

### Content Directives for Paper Conversion

Based on answers, apply these rules during generation:

- **"Main results"** selected -> Dedicate 30-40% of frames to stating, illustrating, and supporting the main theorems/results. Create a dedicated "Main Result" frame with the theorem statement prominently displayed.
- **"Method"** selected -> Include algorithm/pseudocode frames, step-by-step breakdowns. Use progressive disclosure for multi-step methods.
- **"Experiments"** selected -> Create comparison tables, result highlight frames. Use two-column layouts for method-vs-baseline comparisons.
- **"Motivation"** selected -> Lead with 2-3 problem motivation frames before any results.
- **"Deep dive"** -> Allocate most frames to the selected focus areas. Other sections get at most 1 frame each.
- **"Highlight reel"** -> Maximum 1 frame per section, focus on the narrative throughline.
- **"Related work" skipped** -> Omit or compress to a single "Prior Work" frame with 3-4 key references.
- **"Proofs" skipped** -> State theorems without proof. Add "Proof: see paper" annotation.

---

## Phase 2: Style Discovery (Visual Exploration)

**CRITICAL: This is the "show, don't tell" phase.**

Most people can't articulate design preferences in words. Instead of asking "do you want Madrid or Metropolis?", we generate mini-previews and let them react.

### How Users Choose Presets

Users can select a theme in **two ways**:

**Option A: Guided Discovery (Default)**
- User answers mood questions
- Skill generates 3 preview files based on their answers
- User views previews in browser and picks their favorite
- This is best for users who do not have a specific style in mind

**Option B: Direct Selection**
- If user already knows what they want, they can request a theme by name
- Example: "Use the Madrid theme" or "I want something like Metropolis"
- Skip to Phase 3 immediately

**Available Themes:**

| Preset | Vibe | Best For |
|--------|------|----------|
| Madrid | Classic Beamer, blue bars | Conference talks, general academic |
| Berlin | Sidebar navigation, structured | Course lectures, structured talks |
| Copenhagen | Clean minimal header | Seminars, workshops |
| Warsaw | Bold gradient bars | Keynotes, plenary talks |
| Metropolis | Modern sans-serif | CS/tech conferences |
| Classic Serif | Traditional LaTeX look | Mathematics, formal proofs |
| Cambridge | University formal, green+gold | Thesis defense, formal events |
| Lecture Notes | Warm, pedagogical | Teaching, tutorials |
| Technical Report | Engineering/CS style | Technical presentations |
| Thesis Defense | Formal, institution-branded | Thesis/dissertation defense |
| Seminar | Informal, relaxed | Lab meetings, reading groups |
| Journal Article | Paper-style layout | Research presentations |

### Step 2.0: Style Path Selection

First, ask how the user wants to choose their theme:

**Question: Style Selection Method**
- Header: "Theme"
- Question: "How would you like to choose your presentation theme?"
- Options:
  - "Show me options" -- Generate 3 previews based on my needs (recommended for most users)
  - "I know what I want" -- Let me pick from the theme list directly

**If "Show me options"** -> Continue to Step 2.1 (Mood Selection)

**If "I know what I want"** -> Show theme picker:

**Question: Pick a Theme**
- Header: "Theme"
- Question: "Which theme would you like to use?"
- Options:
  - "Madrid" -- Classic Beamer with blue bars, the standard academic look
  - "Berlin" -- Sidebar navigation for structured, multi-section talks
  - "Copenhagen" -- Clean minimal header, good for focused seminars
  - "Warsaw" -- Bold gradient bars for keynotes and plenary talks
  - "Metropolis" -- Modern sans-serif for CS and tech conferences
  - "Classic Serif" -- Traditional LaTeX look for mathematics and formal proofs
  - "Cambridge" -- University formal with green and gold accents
  - "Lecture Notes" -- Warm and pedagogical for teaching
  - "Technical Report" -- Engineering and CS style
  - "Thesis Defense" -- Formal, institution-branded
  - "Seminar" -- Informal and relaxed for lab meetings
  - "Journal Article" -- Paper-style layout for research talks

(If user picks one, skip to Phase 3.)

### Step 2.1: Mood Selection (Guided Discovery)

**Question 1: Feeling**
- Header: "Tone"
- Question: "What tone should your presentation convey?"
- Options:
  - "Authoritative/Rigorous" -- Formal, precise, mathematically grounded
  - "Clear/Pedagogical" -- Approachable, well-structured, easy to follow
  - "Modern/Minimal" -- Clean, contemporary, distraction-free
  - "Classic/Traditional" -- Timeless, scholarly, university-style
- multiSelect: true (can choose up to 2)

**Mood-to-Theme Mapping:**

| Mood | Theme Options |
|------|---------------|
| Authoritative/Rigorous | Madrid, Warsaw, Classic Serif, Thesis Defense |
| Clear/Pedagogical | Berlin, Copenhagen, Lecture Notes |
| Modern/Minimal | Metropolis, Technical Report, Seminar |
| Classic/Traditional | Cambridge, Classic Serif, Journal Article |

### Step 2.2: Generate Theme Previews

Based on their mood selection, generate **3 distinct theme previews** as mini HTML files in a temporary directory. Each preview should be a single title frame showing:

- Typography (font choices, heading/body hierarchy)
- Color palette (background, header/footer chrome, accent colors)
- Frame structure (header bar, footer bar, content area)
- Theorem environment styling (a sample theorem box)
- Overall academic feel

**IMPORTANT: Every preview must feel academically authentic:**
- Use Computer Modern or Source Serif 4 as primary fonts
- Include header/footer chrome (short title, section title, frame number)
- Show a sample theorem or definition box
- Include a sample inline equation rendered with KaTeX
- Muted, professional color palettes (no neon, no gradients for decoration)

### Step 2.3: Present Previews

Create the previews in: `.claude-design/frame-previews/`

```text
.claude-design/frame-previews/
    style-a.html   # First theme option
    style-b.html   # Second theme option
    style-c.html   # Third theme option
```

Each preview file should be:
- Self-contained (inline CSS/JS, KaTeX via CDN)
- A single title frame plus one content frame with a theorem box
- Showing the header/footer chrome style
- Around 80-120 lines, not a full presentation

Present to user:
```text
I have created 3 theme previews for you to compare:

**Theme A: [Name]** -- [1 sentence description]
**Theme B: [Name]** -- [1 sentence description]
**Theme C: [Name]** -- [1 sentence description]

Open each file to see them in action:
- .claude-design/frame-previews/style-a.html
- .claude-design/frame-previews/style-b.html
- .claude-design/frame-previews/style-c.html

Take a look and tell me:
1. Which theme resonates most?
2. What do you like about it?
3. Anything you would change?
```

Then use AskUserQuestion:

**Question: Pick Your Theme**
- Header: "Theme"
- Question: "Which theme preview do you prefer?"
- Options:
  - "Theme A: [Name]" -- [Brief description]
  - "Theme B: [Name]" -- [Brief description]
  - "Theme C: [Name]" -- [Brief description]
  - "Mix elements" -- Combine aspects from different themes

If "Mix elements", ask for specifics.

---

## Phase 3: Generate Presentation

Now generate the full presentation based on:
- **Content quality directives** from Phase 0.5 (audience, takeaway, narrative arc)
- Content details from Phase 1 (or inferred from fast-path)
- Paper focus from Phase 1P (if Mode B)
- Theme from Phase 2

### Content Generation Rules

**Apply audience calibration throughout:**
- For "domain experts": no introductory definitions, assume standard notation, include technical depth
- For "students/newcomers": define all terms, use examples before formalism, include recap frames
- For "mixed": start accessible, deepen progressively

**Structure frames according to narrative arc:**
- Follow the frame sequencing template from Phase 0.5 based on the user's chosen arc
- The KEY_RESULT (if provided) gets its own dedicated frame AND is echoed in the conclusion

**For paper conversions, apply focus directives:**
- Allocate frames according to the coverage choice from Phase 1P
- Skip sections the user marked as skippable
- When "deep dive" was chosen, spend 70% of frames on the focus areas

### File Structure

For single presentations:
```text
presentation.html    # Self-contained presentation
assets/              # Images, if any
```

For projects with multiple presentations:
```text
[presentation-name].html
[presentation-name]-assets/
```

### HTML 骨架、JavaScript 功能與程式碼品質(已拆出)

產生簡報檔時,讀 `references/html-architecture.md`:完整 HTML 範本(含鍵盤導覽、進度列、簡報者模式)、必備 JS 功能清單、程式碼品質要求。照該檔範本組裝,不要憑記憶重寫骨架。

## Phase 4: PPT Conversion(已拆出)

使用者提供 .pptx 要轉成 HTML 簡報時,讀 `references/ppt-conversion.md`:內容抽取→結構確認→主題選擇→生成→品質檢核的完整流程。

## Phase 5: Delivery

### Final Output

When the presentation is complete:

1. **Clean up temporary files**
   - Delete `.claude-design/frame-previews/` if it exists

2. **Open the presentation**
   - Use `open [filename].html` to launch in browser

3. **Provide summary**
```text
Your presentation is ready.

File: [filename].html
Theme: [Theme Name]
Frames: [count]
Equations: KaTeX rendering enabled

Navigation:
- Arrow keys or Space to advance (including progressive disclosure steps)
- Page Up / Page Down for frame-level navigation
- Home / End to jump to first or last frame
- Scroll and swipe also work
- Frame counter displayed in footer

To customize:
- Colors and fonts: Edit the :root CSS variables at the top of the file
- Theorem styles: Modify .theorem-box, .definition-box, .proof-box variables
- Header/footer chrome: Change --header-bg, --header-fg, --footer-bg, --footer-fg
- Equations: Use $...$ for inline and $$...$$ for display math (KaTeX syntax)

Would you like me to make any adjustments?
```

---


## 樣式對照與動畫模式(已拆出)

選擇語氣風格(正式/現代/溫暖/技術密集)對應的視覺效果,與進場動畫、progressive disclosure(Beamer \pause 等效)、reduced-motion 模式,讀 `references/style-and-animation.md`。

## 疑難排解與示範流程(已拆出)

遇到常見問題(溢版、字型、跑版)或想看四種完整互動流程範例,讀 `references/troubleshooting-and-examples.md`。

