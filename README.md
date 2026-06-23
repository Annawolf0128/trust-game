# Trust as Reinvestable Social Capital — oTree Implementation

An oTree implementation of a two-stage trust game studying **trust as reinvestable
social capital**, with relationship history, mean-preserving payoff noise, and a
reinvestment treatment.

## Overview

Participants are matched into **fixed pairs** for the whole experiment. Within a
pair, **Player 1 (A)** is the *truster* and **Player 2 (B)** is the *trustee*.

- **Stage 1** — 3 rounds of a standard, fully transparent trust game. This builds
  a measured **relationship history** that is used only as a state variable for
  stratified randomization and later analysis. It is *not* a participant-facing
  treatment.
- **Stage 2** — a repeated trust game with a **random stopping rule** and a
  **2×2 between-pairs design**.

Each round of the trust game: A receives an endowment of **10 points**, sends some
amount to B, the amount sent is **multiplied by 3** on the way to B, B then chooses
how much to return, and the rest is kept.

### The 2×2 Stage 2 design

Two treatment dimensions are randomized at the pair level:

| Dimension | Levels |
|-----------|--------|
| **Reinvestment** | `no_reinvestment` (accumulated earnings cannot be used in the current relationship) / `reinvestment` (A can allocate accumulated earnings back to the same matched B) |
| **Payoff noise** | `no_noise` (A receives exactly what B returns) / `noise` (a mean-preserving computer adjustment is applied to B's return) |

This gives four cells: `no_reinvestment × no_noise`, `no_reinvestment × noise`,
`reinvestment × no_noise`, `reinvestment × noise`.

### Noise channel (important)

Under `noise`, the mean-preserving multiplicative adjustment falls on the amount
**B returns to A**, on its way back to A. B receives the full multiplied transfer
with **no** adjustment, chooses a return, and the computer then scales that return
by a factor:

- factor **1.0** with probability **0.8**
- factor **0.5** with probability **0.1**
- factor **1.5** with probability **0.1**

(mean = 1, so the noise is mean-preserving). A sees only the **final amount that
reaches them** — never B's intended return nor the noise factor. A low realized
return is therefore genuinely ambiguous between betrayal and bad luck. This
attribution ambiguity sits on the truster (A) by design, which is what the
relationship-memory and collapse hypotheses depend on. Only A is asked to report a
**signal attribution** after results, and only under noise.

### Random stopping

Stage 2 runs a **minimum of 5 rounds**, then stops after each round with
probability **0.15** (an indefinite-horizon / random-stopping design). oTree
requires a hard round ceiling; it is set to **24 Stage 2 rounds**, at which the
probability of reaching the ceiling is under 5%, so the realized length stays close
to the intended geometric distribution. Total `NUM_ROUNDS = 3 + 24 = 27`.

### Per-round belief elicitation

Beliefs are elicited *after* the strategic choices are fixed but *before* realized
returns are revealed, so realized payoffs cannot contaminate the report:

- A reports a belief about **B's intended return** (on the send screen).
- B reports a belief about **A's transfer** (on the return screen).

## Project structure

The project contains three oTree apps:

- **`trust_reinvestment`** — the full experiment (Stage 1 + Stage 2 + survey). This
  is the app real participants play.
- **`preview_part2`** — a single-player walkthrough of Stage 2 (Part 2 instruction
  pages, send/return decisions, both results screens) plus the survey. No partner,
  no waiting. Used to review the participant-facing text of one or all cells. It
  reuses the real `trust_reinvestment` templates, so the text is always identical
  to the official session.
- **`preview_part1`** — a single-player click-through of every Part 1 page (intro,
  role assignment, rules, quizzes, send/return, results). Used to review Part 1
  text. No partner, no waiting.

## Sessions

The session configurations in `settings.py`:

### Official data-collection session

- **`official`** — *"Official: 12 pairs, all four cells"*, **24 participants**.
  This is the session used to collect real data. 24 participants are paired on
  arrival (12 pairs) and play Stage 1. At the start of Stage 2, the 12 pairs are
  split **3 per cell**, **stratified by Stage 1 relationship quality**: pairs are
  ranked by relationship quality and assigned in blocks of four, so each cell draws
  one pair from each quality band. Running **every cell in every session** keeps the
  session factor orthogonal to treatment — any session-level effect (subject pool,
  time of day, lab conditions) is balanced across treatments instead of confounded
  with them. Because each cell gets only 3 pairs per session, adequate power
  requires accumulating across multiple sessions.

### Trial sessions (one forced cell each)

Two-participant sessions that force a single 2×2 cell, for piloting one cell at a
time with a real pair:

- **`trial_no_reinvestment_no_noise`** — forced `no_reinvestment` + `no_noise`.
- **`trial_no_reinvestment_noise`** — forced `no_reinvestment` + `noise`.
- **`trial_reinvestment_no_noise`** — forced `reinvestment` + `no_noise`.
- **`trial_reinvestment_noise`** — forced `reinvestment` + `noise`.

### Preview sessions (single player, no partner)

One-participant sessions to review participant-facing text without running a full
pair. Each walks both roles through one cell's Part 2 instructions, the send/return
decision screens, both results screens, and the survey:

- **`preview_no_reinvestment_no_noise`**
- **`preview_no_reinvestment_noise`**
- **`preview_reinvestment_no_noise`**
- **`preview_reinvestment_noise`**

And for Part 1:

- **`preview_part1`** — *"Preview: Part 1 pages (no play-through)"*, one participant,
  clicks straight through every Part 1 page.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
otree devserver
```

Then open `http://localhost:8000` and pick a session from the list above.

To run the automated bot tests for a config:

```bash
otree test official 24
otree test preview_reinvestment_noise 1
```
