# Academic Presentation Style Catalog

This catalog exists because "academic presentation" is not one style. A journal
editorial briefing, a 45-minute seminar, and a 15-minute conference slot reward
different densities, different type scales, and different tones — and picking
the wrong one is a common reason technically sound decks land flat. Use this
file at **Step 0** of the main skill, before any slide is drafted.

The six styles below share the base design system in `SKILL.md` Step 3
(white background, Arial/Calibri/Helvetica, left-aligned body text, ≥0.5"
margins). What changes across styles is: type scale, layout density, exhibit
count per slide, color usage, and the specific behaviors that are off-limits
for that audience. Nothing below authorizes going under the accessibility
floor already set in `content_guidelines.md` §8 (20 pt body minimum, 24 pt+
titles) — every style's type ladder in this file is at or above that floor,
and where a style needs a *smaller* caption size than the general floor
allows, this file says so explicitly and explains why it is still readable.

---

## How to choose: three questions, then narrow to ≤3 candidates

Ask the presenter these three questions before opening any style section below.
Do not guess the answers — a journal-editorial deck built for a thesis defense
timeline (or vice versa) fails in ways that are expensive to fix after the
slides exist.

1. **Audience** — Who is in the room? (Editors/reviewers deciding on a
   manuscript · a thesis committee with veto power · a subfield seminar
   audience of specialists · a broad conference session with mixed background
   · students · a poster-session passerby you're talking to for 3 minutes)
2. **Duration** — How long do you actually have on the clock, including Q&A?
   (5–8 min · 15 min · 45+ min · untimed but conversational)
3. **Occasion** — Is this a decision-making meeting (they will vote, revise,
   or grade), a discovery meeting (they're hearing this for the first time),
   or a support meeting (a poster, a teaching aid) where the slides are not
   the main event?

Map the answers to candidates with this table, then pick at most three and
compare before committing to one:

| Answer pattern | Top candidate | Also consider | Rule out |
|---|---|---|---|
| Editors/reviewers, any duration, decision meeting | journal-editorial | seminar-45min (if it's a long invited talk to the same crowd) | conference-15min, teaching |
| Thesis committee, 45–90 min, decision meeting (defense) | thesis-defense | journal-editorial (borrow its evidence-first tone) | conference-15min, poster-session-talk |
| Specialist subfield audience, 45 min, discovery | seminar-45min | thesis-defense (borrow its depth) | poster-session-talk |
| Mixed conference session, 12–18 min, discovery | conference-15min | seminar-45min (if you have 30+ min) | thesis-defense, teaching |
| Students, variable duration, support meeting | teaching | conference-15min (borrow its pacing discipline) | journal-editorial |
| Standing at a poster, 2–5 min per visitor, support meeting | poster-session-talk | teaching (borrow its plain-language habit) | journal-editorial, thesis-defense |

**Comparison pass (do this before finalizing):** for your ≤3 candidates, read
their "when to use" and "explicit no-gos" side by side. If two candidates both
seem to fit, the discriminating question is usually duration and whether the
room can push back (decision meetings need more robustness-check real estate;
discovery meetings need more motivation real estate). Converge on one style
and state the choice back to the user in one sentence before building slides.

---

## 1. journal-editorial

**When to use:** Presenting a manuscript, R&R response, or working paper
directly to journal editors, associate editors, or a review panel — the
audience's job is to decide accept/reject/revise, not to be entertained.
Also use for internal "pre-submission murder board" rehearsals aimed at the
same standard. Assume every claim will be challenged in real time.

**Type ladder (pt):**

| Element | Size | Rationale |
|---|---|---|
| Title | 26 | Matches SKILL.md floor; editors read fast, don't need larger |
| Section header | 20 | Minimum in content_guidelines.md §2 |
| Body | 20 | Accessibility floor — never go below this even under pressure to fit a robustness table |
| Caption / method footnote | 13 | At the muted-caption floor (12–14 pt) set in content_guidelines.md §5; used for sample/estimator footnotes, not for content the audience must read to follow the argument |

**Layout grid:** Single column for argument slides; two-column (finding left
5.5", robustness/mechanism right 3.5") for any slide pairing a headline result
with its immediate defense. Margin 0.5" minimum, same as base system.
Whitespace ratio: keep body text to ≤60% of the content area — the rest is
room for the inevitable "but what about—" annotation you'll add live.

**Density rules:** Maximum 30 words of body text per slide (stricter than the
40-word base rule — editors are reading the paper too, the slide should not
duplicate it). Maximum 1 exhibit per slide, but every results slide must have
a **paired robustness pointer** ("Robust to X, Y → Appendix C") visible in the
caption row, because the first question is almost always about robustness.

**Color:** Okabe–Ito subset — black (`#000000`) for all text and axes, blue
(`#0072B2`) as the single accent for the focal estimate/series, vermillion
(`#D55E00`) reserved only for flagging a result that failed a robustness
check (use sparingly, and only if such a result is being shown deliberately).
No third color. This is stricter than the base 3-color allowance because
editorial audiences read color choices as claims of importance — extra colors
invite "why is this highlighted" questions you don't want.

**Explicit no-gos:**
- No adjectives of self-assessment ("novel," "robust," "rigorous," "important")
  in titles or bullets — state the finding and let the evidence carry it.
- No teaser slides ("we will show that...") — lead with the actual number.
- No hiding a null or contrary result in the appendix without a pointer slide
  in the main deck; editors interpret an unexplained gap as evasion.
- No stacked bar/line combo charts with more than 2 series — editors will
  spend their question budget parsing the chart instead of the argument.

推測（reasoning, not measured）：一般編輯／審稿委員會的耐心閾值低於研討會聽眾，
故本節密度規則刻意比 conference-15min 更嚴格；若編輯部另有既定簡報格式（例如
期刊自己的 R&R 說明會模板），以該格式為準，本節僅為預設值。

---

## 2. thesis-defense

**When to use:** The oral defense itself (as opposed to a committee-only
progress check, which should be lighter). Audience is your committee — they
have read the thesis, have specific concerns already in mind, and are also
partly evaluating your command of the material live.

**Type ladder (pt):**

| Element | Size | Rationale |
|---|---|---|
| Title | 28 | Upper end of base range — defenses run in bigger rooms than lab meetings |
| Section header | 22 | Upper end of base range, matches multi-chapter navigation needs |
| Body | 20 | Floor; defenses run 45–90 min, fatigue makes smaller text costly |
| Caption | 14 | Upper end of caption range — committee members are often the room's oldest readers and sit farther from the screen than in a seminar |

**Layout grid:** Single column dominates (defenses are narrative, chapter by
chapter). Reserve two-column (evidence left / committee's-likely-objection
right) for the 2–3 slides you know will be contested. Include a persistent
breadcrumb bar (per `slide_patterns.md` §9) mapping to thesis chapters —
committees jump between "which chapter is this" mentally and the bar answers
it without you saying so.

**Density rules:** ≤40 words/slide (base rule applies as-is; defenses are
long enough that stricter limits would starve necessary chapter transitions).
Maximum 1 exhibit per slide in the main body; the appendix may carry as many
pre-built rebuttal slides as anticipated questions warrant — this is the one
style where a large, well-labeled appendix is expected, not a fallback.

**Color:** Full Okabe–Ito palette permitted across chapters IF the deck maps
one accent per chapter/study for navigation (e.g., blue `#0072B2` for Study 1,
vermillion `#D55E00` for Study 2, bluish green `#009E73` for Study 3) — this
is a legitimate use of multiple colors because it aids wayfinding across a
long, multi-chapter narrative, unlike decoration. Default single accent
(`#0072B2`) if the thesis is a single unified study.

**Explicit no-gos:**
- No slide that assumes the committee remembers a claim from 20 minutes
  earlier without a one-line callback — defenses are long, don't rely on
  short-term recall.
- No unlabeled "Study 2" section dividers — always restate how it connects to
  the overall dissertation argument, not just the study's own topic.
- No skipping the limitations slide — committees will ask about it whether or
  not it is shown, and showing it first signals command of the material.

---

## 3. seminar-45min

**When to use:** Department seminar, invited talk, brown-bag to a specialist
subfield audience who has not read your paper but knows the literature.
Discovery-oriented: audience is meeting the argument for the first time and
has 45 minutes (often 35 talk + 10 discussion, confirm locally).

**Type ladder (pt):**

| Element | Size | Rationale |
|---|---|---|
| Title | 26 | Base default |
| Section header | 22 | Base default |
| Body | 20 | Floor |
| Caption | 13 | Base default |

**Layout grid:** Figure-left/interpretation-right for all results slides (per
`content_guidelines.md` §3). Use section dividers (per `slide_patterns.md`
§8) every 6–8 slides — 45 minutes is long enough that the audience needs
re-orientation checkpoints the way conference talks don't.

**Density rules:** ≤40 words/slide. Up to 2 exhibits on a single
"landscape of results" slide is acceptable ONLY at the transition into the
results section (a summary table/forest plot orienting what's coming), never
for two individual findings — those still get one slide each.

**Color:** Base 3-color default (black `#000000` body/axes, blue `#0072B2`
accent, one emphasis color from vermillion `#D55E00` or bluish green
`#009E73` for a single contrastive result, e.g., treatment vs. control).

**Explicit no-gos:**
- No skipping the literature-gap slide — a specialist audience will judge
  positioning within the literature as carefully as the result itself.
- No going past 38 minutes of talk time even if content remains — seminar
  culture treats overrun as disrespecting the discussion slot.
- No live-reading of dense theory slides word-for-word — specialists will
  disengage; paraphrase and point.

---

## 4. conference-15min

**When to use:** Standard conference paper session slot (10–18 min depending
on venue; treat 15 as the anchor and scale proportionally). Audience is mixed
background, time-boxed by a chair, often deciding in real time whether to
attend your poster/follow up afterward.

**Type ladder (pt):**

| Element | Size | Rationale |
|---|---|---|
| Title | 26 | Base default; do not shrink to fit more text — cut text instead |
| Section header | 20 | Floor of base range — short talks need minimal internal signposting |
| Body | 20 | Floor |
| Caption | 13 | Base default |

**Layout grid:** Single exhibit, figure-left/text-right, identical to base
system — no room in 15 minutes for two-column theory slides. No breadcrumb
bar (`slide_patterns.md` §9 recommends it only for >15 min talks; at this
length it consumes vertical space the content needs more).

**Density rules:** ≤30 words/slide (stricter than base — every second counts
and dense slides are the single most common reason 15-minute talks run over).
Exactly 1 exhibit per slide, no exceptions, no "landscape" slide like the
seminar style gets — there is no time for a scene-setting exhibit.
Slide budget: 12–14 content slides per `content_guidelines.md` §7 — treat
this as a hard ceiling, not a target.

**Color:** Base 3-color default (black `#000000`, blue `#0072B2` accent,
vermillion `#D55E00` for a single highlighted callout box per
`slide_patterns.md` §5's "↑ 28% for Q1" pattern).

**Explicit no-gos:**
- No methods slide longer than 1 slide — identification strategy gets one
  slide, full assumptions go to appendix per `content_guidelines.md` §6.
- No "outline" slide listing agenda items — at 15 minutes it's wasted time;
  go straight to motivation.
- No result presented without its annotation already on the chart — there is
  no time to narrate a bare chart into meaning.

---

## 5. teaching

**When to use:** Lecturing this material to students (undergraduate,
master's, or PhD coursework), lab-meeting tutorials, or method walkthroughs
aimed at people learning the technique, not judging the contribution.

**Type ladder (pt):**

| Element | Size | Rationale |
|---|---|---|
| Title | 26 | Base default |
| Section header | 22 | Base default; used more often here as worked examples are chunked into sub-steps |
| Body | 22 | Above floor — classrooms are frequently larger/deeper than seminar rooms and students are less forgiving of small text than specialists focused on content |
| Caption | 14 | Upper end of range — citations here often need to double as "go read this" pointers students will actually act on, so keep them legible |

**Layout grid:** Sequential/step-by-step single column is default (teaching
is inherently linear — "first this happens, then that"). Worked examples may
use a persistent "given / step / result" three-row template repeated across
several slides for consistency, which is an explicit exception to the "one
exhibit per slide" rule below.

**Density rules:** ≤50 words/slide (loosened from the 40-word base — teaching
slides often carry a formula plus its verbal gloss, and asking students to
split derivations across extra slides breaks continuity). Up to 2 small
exhibits per slide permitted for step-by-step derivations (e.g., before/after
a transformation) — this is the one style where the base "one exhibit" rule
is relaxed, because the pedagogical point is the transition between the two.

**Color:** Base 3-color default, but color may additionally be used as a
*consistent semantic code across the whole course* (e.g., blue `#0072B2`
always denotes "given," vermillion `#D55E00` always denotes "what we're
solving for") — this repeated-meaning use is pedagogically motivated and
distinct from decoration.

**Explicit no-gos:**
- No skipping intermediate algebra/derivation steps "for time" — the entire
  point of a teaching deck is showing the steps; compressing them defeats
  the format (cut scope elsewhere, e.g., fewer worked examples, not fewer
  steps within one).
- No unexplained jargon on first use — define every term, even ones that
  would be assumed knowledge in seminar-45min or conference-15min.
- No dense proofs presented without a worked numerical example alongside.

---

## 6. poster-session-talk

**When to use:** The small set of speaking-aid slides (typically 3–6) you
show on a laptop or tablet standing next to your printed poster, for the
~2–5 minutes you get with an interested passerby. This is **not** the poster
itself — see the dedicated poster skill for that large-format single-page
artifact. This style exists because presenters increasingly carry a QR-linked
tablet deck as a leave-behind/talk-through aid alongside the physical poster.

**Type ladder (pt):**

| Element | Size | Rationale |
|---|---|---|
| Title | 24 | Base floor — viewed close-up on a laptop/tablet, not projected, so the room-visibility rationale for larger titles doesn't apply, but the content_guidelines.md floor still holds |
| Section header | 20 | Floor |
| Body | 20 | Floor — even though viewing distance is short, keep the standard floor so the same deck could be projected on a monitor at the booth without re-editing |
| Caption | 13 | Base default |

**Layout grid:** Single column, single big idea per slide — this is the most
compressed style in the catalog. Treat each slide as answering exactly one
of: "what did you do," "what did you find," "why does it matter." No
two-column layouts — you'll be pointing at the screen while talking, and
split attention across columns fights that.

**Density rules:** ≤20 words/slide — the strictest in this catalog, because
the slide is a prop for a live conversation, not a stand-alone document (the
printed poster already serves the stand-alone/self-sufficient role from
`content_guidelines.md` §3). Maximum 1 exhibit per slide, and it should be
the *same* exhibit as the corresponding poster panel — do not introduce new
figures the passerby can't also see on the poster, or you'll create confusion
about which artifact is authoritative.

**Color:** Match the poster's own palette exactly (pull the accent color
already chosen for the printed poster) rather than defaulting to
`#0072B2` — visual consistency between the two artifacts a visitor is looking
at side by side matters more here than anywhere else in this catalog.

**Explicit no-gos:**
- No slide count above 6 — if you need more, you are trying to give the full
  talk, not a conversation aid.
- No content that contradicts or duplicates-with-variation the poster's
  numbers — any numeric discrepancy between poster and tablet deck reads as
  a data-integrity problem to a sharp visitor.
- No small multiples or dense tables — a visitor standing at a booth will not
  parse a 4x4 grid of mini-charts; save that for the poster itself.

---

## Chinese-language font discipline (中文字型紀律)

This section applies to all six styles above whenever the deck is delivered
in Chinese, or is bilingual (中英夾雜), which is common in Taiwanese business-school seminar
and defense contexts even when the paper itself is written in English.

- **標題與內文中文**：一律使用標楷體（DFKai-SB）。這是本 repo 家族一貫的字型紀律
  （與 docx／research-framework-figure 等技能的規則一致），不因簡報用途而例外。
- **英文與數字**：一律使用 Times New Roman，即使鑲嵌在中文句子中的英文詞彙、
  變數名稱、統計量（t 值、p 值）與年份也一樣——不要為了「視覺一致」而把它們
  也套成標楷體，中英文分流是規則本身，不是妥協。
- **圖表座標軸與圖例（axis labels / legends）**：同樣分流——軸上的中文說明用
  標楷體，數值刻度與英文變數名用 Times New Roman。若圖表工具（如
  `management-figure` 產出的 matplotlib 圖）无法在同一物件內混排两种字型，
  誠實標註「本圖座標軸為英文，中文說明另以文字框補充」，不要假裝已經套用。
- **字型缺漏時的誠實原則**：比照 `research-framework-figure` 的既有慣例——
  若執行環境沒有安裝標楷體，明確告知使用者「本機缺少 DFKai-SB，已改用退回
  字型 ___，請在有標楷體的機器上重新產生／重新開啟後另存」，不要靜默替換
  卻不說明。
- 本節不覆蓋 SKILL.md Step 3「單一無襯線字體」的英文技能預設——那條規則
  管的是**純英文簡報**的西文字體選擇（Arial/Calibri/Helvetica 三選一），
  與本節管的**中文段落字型**是兩個不衝突的維度：同一份簡報可以是「英文
  用 Arial 或 Times New Roman、中文用標楷體」的組合，取決於場合是否需要
  中文（例如 teaching 或 thesis-defense 若以中文授課／口試，本節適用；
  journal-editorial 面向國際期刊編輯則通常全英文，本節不適用）。
