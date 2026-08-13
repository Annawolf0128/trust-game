# Trust as Reinvestable Social Capital — oTree Implementation

An oTree implementation of a two-stage trust game studying how
mean-preserving payoff noise and reinvestment opportunities shape repeated
trust, persistence, and collapse.

## Overview

Participants first complete a one-shot strategy-method elicitation and are then
rematched into fixed Part 2 pairs. Within each Part 2 pair, **Player 1 (A)** is
the *truster* and **Player 2 (B)** is the *trustee*.

- **Stage 1** — every participant states (i) a proposer transfer from 0 to 10 and
  (ii) a responder return for each possible positive transfer. A zero transfer
  mechanically implies a zero return. One random match and one
  random payoff role make the elicitation consequential.
- **Stage 2** — a repeated trust game with a **random stopping rule** and a
  **2×2 between-pairs design**.

Before Stage 2, participants are randomly divided into Player 1 and Player 2
roles and randomly paired. The 12 pairs in an official 24-person session are
then randomly assigned to the four treatment cells, with exactly three pairs in
each cell. Part 1 choices are stored as pre-treatment covariates but do not
affect roles, partners, or treatment assignment.

Each round of the trust game: A receives an endowment of **10 points**, sends some
amount to B, the amount sent is **multiplied by 3** on the way to B, B then chooses
how much to return, and the rest is kept.

Part 1 and Part 2 use the same conversion rate: **USD 0.50 per point**. Participants also receive a fixed **USD 5.00 show-up fee**.

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

- factor **1.0** with probability **0.6**
- factor **0** with probability **0.2**
- factor **2** with probability **0.2**

(mean = 1, so the noise is mean-preserving). A sees only the **amount that
reaches them** — never B's intended return nor the noise factor. A low realized
return is therefore genuinely ambiguous between betrayal and bad luck. This
attribution ambiguity sits on the truster (A) by design, which is what the
relationship-memory and collapse hypotheses depend on. After each noisy result,
only A reports a concise belief about B's chosen return.

The adjustment affects **A's payoff only**. B's payoff is always the full
multiplied amount received minus B's chosen return; the computer neither adds to
nor subtracts from B's payoff.

### Random stopping

Stage 2 runs a **minimum of 5 rounds**, then stops after each round with
probability **0.20** (an indefinite-horizon / random-stopping design). The
24-round hard cap reduces the expected Part 2 length only slightly, from 9 to
approximately 8.94 rounds. oTree
requires a hard round ceiling; it is set to **24 Stage 2 rounds**, at which the
probability of reaching the ceiling is under 5%, so the realized length stays close
to the intended geometric distribution. Total `NUM_ROUNDS = 1 + 24 = 25`.

### Per-round belief elicitation

Beliefs are elicited *after* the strategic choices are fixed but *before* realized
returns are revealed, so realized payoffs cannot contaminate the report:

- A reports a belief about **B's intended return** (on the send screen).
- B reports a belief about **A's transfer** (on the return screen).

## Project structure

The project contains three oTree apps:

- **`trust_reinvestment`** — the full experiment (Stage 1 + Stage 2 + survey). This
  is the app real participants play.
- **`preview_part2`** — a single-player walkthrough of Part 2 (the shared animated
  instructions, send/return decisions, both results screens) plus the final-survey
  transition and survey. No partner,
  no waiting. Used to review the participant-facing text of one or all cells. It
  reuses the real `trust_reinvestment` templates, so the text is always identical
  to the official session.
- **`preview_part1`** — a single-player click-through of the Part 1 strategy
  method (intro, rules, quiz, proposer choice, responder schedule, and both
  possible payoff-role results). No partner or waiting.

## Sessions

The session configurations in `settings.py`:

### Official data-collection session

- **`official`** — *"OFFICIAL — 24 participants, four balanced blocks"*,
  **24 participants**. After the one-shot Stage 1 elicitation, roles and partners
  are randomized to form 12 pairs. Every treatment cell receives exactly three
  randomly assigned pairs.

### Eight-participant pilot session

- **`pilot_8`** — *"PILOT — 8 participants, one pair per block"*,
  **8 participants**. Random roles and partners form four pairs; each of the
  four Part 2 treatment cells receives exactly one pair. The participant flow
  is otherwise identical to the official session.

### Trial sessions (one forced cell each)

Two-participant sessions that force a single 2×2 cell, for piloting one cell at a
time with a real pair:

- **`trial_no_reinvestment_no_noise`** — forced `no_reinvestment` + `no_noise`.
- **`trial_no_reinvestment_noise`** — forced `no_reinvestment` + `noise`.
- **`trial_reinvestment_no_noise`** — forced `reinvestment` + `no_noise`.
- **`trial_reinvestment_noise`** — forced `reinvestment` + `noise`.

### Fast role-test sessions

Eight one-participant sessions cross the four Part 2 cells with Player 1 and
Player 2. A simulated counterpart supplies the other player's decision, so no
second browser or wait page is required. Their names begin with `test_`, for
example `test_no_reinvestment_no_noise_player1` and
`test_reinvestment_noise_player2`.

## Run locally

You need **Python 3.9–3.11** installed first (oTree 5.x does not support Python
3.12 or newer). Clone the repository and move into the project folder — the one
that contains `settings.py`. After cloning, that folder is simply `trust-game`
(`settings.py` sits at its top level). Every command below is run from inside it.

```bash
git clone https://github.com/Annawolf0128/trust-game.git
cd trust-game
```

Create a virtual environment, install the dependencies, and start the server:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
otree devserver
```

Then open `http://localhost:8000` and pick a session from the list above. The
database (`db.sqlite3`) is created automatically on first launch; if you ever
hit a database error, run `otree resetdb` once and then `otree devserver` again.
Press `Ctrl+C` to stop the server.

The oTree admin interface is the experiment-control website: use it to create
sessions, open participant links, monitor each participant's current page in
real time, inspect submitted fields, and export the final data. The default
local login is `admin`; set `OTREE_ADMIN_PASSWORD` before any production run.
Because this revision adds responder fields for transfers 6–10, an existing
development database created under the older schema must be backed up and then
recreated with `otree resetdb`. Do not reset a database containing data that has
not already been exported.

To run the automated bot tests for a config:

```bash
otree test official
otree test preview_reinvestment_noise 1
otree test ai_agent_trust_cycle 8 --export
```
