# Argument-Force Check (Structural Layer) — English Academic Writing

## What this file is for

Word-level de-AI-ing (deleting `delve`, `pivotal`, `In today's rapidly evolving
landscape`) **only cleans the surface**. What makes a reviewer write
*"the contribution is thin"* is the **structural layer**: the sentences are
grammatical, the vocabulary is clean, and the argument still carries no weight.

There is evidence behind this. Work such as StoryScope (2025), comparing human
and LLM text, found that LLM output **clusters systematically in the most
predictable range** — word choice, sentence construction, and rhetorical moves
all default to the safe option, with a markedly narrower rarity distribution
than human writing; and that **each model carries its own stylistic fingerprint**.

⚠️ **Two caveats, or this file will be misapplied**:

1. **That research studied fiction, not empirical papers.** Its markers of
   "human-ness" (moral ambiguity, non-linear time, narrative rarity) are
   **anti-requirements** for an empirical paper, which should be clear, linear,
   and reproducible. Only one thing transfers: **AI defaults to the costless,
   uncommitted, predictable move** — and in academic writing that is simply
   called *weak argumentation*.

2. **The goal here is not to evade AI detectors.** Detectors have high false-
   positive rates and break with each model release; optimising against them is
   backwards. Every item below is **a defect worth fixing even if AI did not
   exist**. Text reading more like a human is the side effect, not the target.

---

## Eight checkable structural signals

Each gives: **how to spot it**, **why it is a defect**, **how to fix**,
**when not to touch it**.

### 1. Antithesis inflation

**Spot it**: `not merely X, but Y` / `It is not X; rather, it is Y` /
`This is less about X than about Y`, recurring. More than 2–3 in a paper is a flag.

**Why it is a defect**: it manufactures **a straw opponent nobody can trace**.
"Our focus is not ownership share, but control configuration" — who ever
claimed it was ownership share? Without a citation, X exists only to make Y
look insightful. A reviewer will ask whom you are arguing against.

**Fix** — pick one:
- **Name X**: "Claessens et al. (2000) measure family influence by cash-flow
  rights; we use control rights, because pyramidal structures cause the former
  to understate effective control." (straw man → real literature dialogue)
- **Drop the antithesis** and simply assert Y.

**Don't touch it when**: a genuine, cited disagreement exists. The test is
whether X has a **traceable holder**.

---

### 2. The rule-of-three reflex

**Spot it**: lists are almost always three items, and the third is visibly
thinner. "We contribute to the family-firm literature, the governance
literature, and to emerging-market research."

**Why it is a defect**: item count should be set by **evidence, not cadence**.
The padded third item is exactly what a reviewer will interrogate — and when it
collapses, it takes the credibility of the first two with it.

**Fix**: cut to what holds. Two solid contributions beat three with one hollow.
If there genuinely are three, make the third **as specific as the first two**.

**Don't touch it when**: three dimensions come from your framework or your three
actual hypotheses.

---

### 3. Uniform paragraph weight

**Spot it**: every paragraph in a section runs 5–7 sentences.

**Why it is a defect**: length **signals importance**. Giving your core
contribution the same space as a control-variable description tells the reader
you cannot tell them apart either.

**Fix**: identify the single most important claim and let its paragraph be
**visibly the longest and most detailed**; compress secondary material into a
sentence or fold it elsewhere. Allow a two-sentence paragraph — brevity
emphasises.

---

### 4. Symmetric hedging (both sides, no verdict)

**Spot it**: `On one hand … on the other hand …`, or `While some scholars
argue … others contend …`, given equal weight, then the section ends
**without a judgment**.

**Why it is a defect**: this is the most serious item. **No position, no
contribution.** Listing a disagreement is a review; saying which side holds —
or why your setting favours one — is research. Stopping at the symmetry
outsources your job to the reader.

**Fix**: the pair **must** be closed:
"The divergence reflects sample context: X studies dispersed-ownership European
firms, whereas control concentration among Taiwanese family firms is
substantially higher; we therefore expect the latter effect to dominate."

**Don't touch it when**: the Limitations section admits you cannot separate two
mechanisms. That is honesty, not hedging — provided you say **why** you cannot
(see item 5).

---

### 5. Costless claims

**Spot it**: nothing in the paper costs the author anything. Limitations read
`future research could expand the sample` / `additional countries could be
included` — boilerplate that fits any paper.

**Why it is a defect**: generic limitations are no limitations. An experienced
reviewer reads them as *"the author does not know where the weakness is"* — and
then goes looking, usually finding something worse.

**Fix**: at least one limitation must follow this shape —
**specific threat + why it resists correction + what you did + residual risk**.
> "We proxy ESG performance with TESG scores, but the score itself may load on
> firm size (larger firms have more disclosure resources), creating common
> variance with the dependent variable. Adding size controls and re-estimating
> on within-industry ranks (Table 6) leaves the sign unchanged but shrinks the
> coefficient by roughly a third; size-driven measurement error therefore
> cannot be fully excluded."

Naming your weakest link is a strong writer's move, not an admission of defeat.

---

### 6. Literature review as a roll call

**Spot it**: `A (2020) finds …. B (2021) shows …. C (2022) argues ….`
One study per sentence, **no relational connective** between them.

**Why it is a defect**: that is a **stack of abstracts**, not a review. The value
of a review lies in the relationships — extension, divergence, contradiction —
and in where the gap sits.

**Fix**: every cluster needs a **relational sentence**:
"A and B both report a positive association, but both sample dispersed-ownership
firms; C finds the effect vanishes under family control, suggesting the
association is conditional on control structure — which is where we intervene."

---

### 7. Missing mechanism

**Spot it**: "X affects Y" with no **channel** stated.
"Family control affects ESG disclosure." — through what?

**Why it is a defect**: a hypothesis without a mechanism is a description of
correlation, not a theoretical contribution. "So what / why" is the single most
common reviewer question.

**Fix**: hypothesis statements need a **verb chain**:
"Family controlling owners derive socioemotional wealth from family reputation;
reputational exposure makes them **more likely** to disclose ESG information to
pre-empt external scrutiny. H1 therefore predicts a positive association."
Test the mechanism if the data allow (mediation, subsample splits); if not, say
so explicitly rather than leaving the gap silent.

---

### 8. Every paragraph opens with a perfect topic sentence

**Spot it**: paragraph one-liners are uniformly textbook-standard claim sentences.

**Why it is a defect**: minor, but it reads mechanical. The more substantive
point: **some paragraphs are more persuasive with evidence first and the claim
last** — especially counter-intuitive findings, where a reader who meets the
claim up front starts resisting before seeing the support.

**Fix**: convert 2–3 paragraphs to evidence-first, claim-last. Don't convert all
of them; consistency is not itself a fault.

---

## How to use this

Run the **word layer first** (SKILL.md stage 3), **then this table**.
Report structural findings as a **separate block**, because the remediation cost
differs: word-layer issues can be rewritten directly, whereas most structural
items — especially 4, 5, and 7 — **require the author to supply substance**.
Do not write that substance for them; doing so would fabricate research
findings and breach this skill's honesty constraints.

Grade each hit:
- **Author must supply content**: items 4, 5, 7 (no position / no specific
  limitation / no mechanism)
- **Can be rewritten here**: items 1, 2, 6, 8 (sentence-level restructuring)
- **Flag only**: item 3 (paragraph weighting is the author's editorial call)

last_verified: 2026-08-29
