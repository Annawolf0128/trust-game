# Trust as Reinvestable Social Capital — oTree Experiment

This repository contains the current oTree implementation of a two-part trust
game studying whether trust persists, collapses after adverse outcomes, and is
shaped by payoff noise and opportunities to reuse accumulated earnings. The
participant interface is in English; a fully Chinese counterpart lives in the
separate repository `Annawolf0128/trust_game_China` (experiment logic identical,
interface language only).

## Quick start after downloading

Open a fresh Terminal tab before entering the commands below. If the current
Terminal is already running another local server and does not show a normal
prompt such as `rabbit@... %`, press **Control+C** to stop that process, or press
**Command+T** to open a new Terminal tab. GitHub CLI login (`gh auth login`) is
not required to run this experiment.

First enter `cd ` with a trailing space, drag the downloaded repository folder
from the Desktop into the Terminal window, and press Return. Alternatively, if
the downloaded folder is named `trust-game-main`, run:

```bash
cd /Users/rabbit/Desktop/trust-game-main
```

For the first run, execute these commands one at a time:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
otree devserver
```

When the server starts, open <http://localhost:8000>. The default local admin
credentials are `admin` / `admin`. Stop the server with **Control+C**.

For later runs from the same downloaded folder, only the following commands
are needed:

```bash
source .venv/bin/activate
otree devserver
```

## Current design at a glance

| Parameter | Current value |
|---|---:|
| Currency | SGD |
| Player 1 endowment | 10 points per round |
| Transfer multiplier | 3 |
| Point conversion rate | S$0.05 per point in both parts |
| Show-up fee | S$10.00 |
| Part 2 length (what participants are told) | at least 4 rounds, then a 25% stopping chance after every round, hard cap 6 |
| Part 2 length (what actually runs) | exactly 5 rounds in every session |
| Noise factors | ×0 with 20%, ×1 with 60%, ×2 with 20% |

**On the round-length discrepancy.** The instructions truthfully describe a
random stopping rule (minimum 4 rounds, 25% stop hazard afterwards, cap 6), but
every session is currently set to run exactly 5 rounds via a session-wide
`fixed_stage2_rounds = 5` default in `settings.py`. This is a deliberate design
choice: participants believe the length is uncertain while the realized length
is held constant across sessions. Treat this as a benign deception when
preparing IRB / ethics materials. Removing the `fixed_stage2_rounds` default
restores a genuinely random draw governed by `STAGE2_MIN_ROUNDS = 4`,
`STAGE2_STOP_PROBABILITY = 0.25`, and `STAGE2_MAX_ROUNDS = 6`.

The interface uses animated HTML instruction pages: instruction lines are
revealed sequentially, while decision, quiz, waiting, result, survey, and
completion pages share the same visual system. Player 1 is styled blue and
Player 2 orange consistently across pages.

## Part 1: one-shot strategy-method trust game

Every participant first learns the rules, passes an understanding test, and
makes payoff-relevant decisions for both possible roles:

1. As **Player 1**, the participant chooses one whole-number transfer from 0 to
   10 points.
2. As **Player 2**, the participant specifies a whole-number return for every
   possible positive transfer from Player 1. A zero transfer implies a zero
   return.
3. After all decisions are submitted, the computer randomly assigns each
   participant to Player 1 or Player 2 and randomly matches one Player 1 with
   one Player 2.
4. The assigned role, the matched pair's submitted decisions, and the standard
   trust-game payoff formulas determine Part 1 earnings.

If Player 1 sends `s` and Player 2 returns `r`:

- Player 1 payoff: `10 - s + r`
- Player 2 payoff: `3s - r`

Part 1 earnings are recorded separately and are never added to the accumulated
Part 2 account. Part 1 decisions are retained as pre-treatment covariates, but
they do not affect role assignment, matching, or treatment assignment.

## Transition and randomization into Part 2

The payoff-relevant Part 1 role and partner remain unchanged throughout Part 2.
After pairs have been formed, each pair is assigned to one of the four Part 2
cells **cyclically**: pair 1 → cell 1, pair 2 → cell 2, pair 3 → cell 3, pair 4
→ cell 4, pair 5 → cell 1 again, and so on. This keeps the cells as balanced as
possible at any (even) session size, and does not stratify on Part 1 behavior.

## Part 2: repeated trust game

Each Part 2 round retains the Part 1 roles and partner:

1. Player 1 receives a 10-point current-round endowment.
2. Player 1 chooses a whole-number amount to send.
3. Player 2 receives three times the amount Player 1 sent.
4. Player 2 chooses a whole-number amount to return (from 0 up to the amount
   received). If Player 2 received 0, the return is automatically 0 and the
   input is skipped.
5. The round payoffs are added to each participant's accumulated Part 2 account.

Player 2's round payoff is always the amount received minus the amount Player 2
chose to return. Player 1's round payoff is the unused current-round endowment
plus the amount that reaches Player 1 after any computer adjustment. Each round's
result page shows only the viewer's own payoff and accumulated account; in noise
cells, Player 2's result additionally shows the amount that reached Player 1.

### The 2×2 between-pair design

| Dimension | Control level | Treatment level |
|---|---|---|
| Accumulated-account use | `no_reinvestment`: Player 1 can send at most the current 10-point endowment | `reinvestment`: Player 1 can send up to the current 10-point endowment plus the accumulated Part 2 balance |
| Return noise | `no_noise`: Player 1 receives exactly Player 2's chosen return | `noise`: the computer applies a mean-preserving adjustment (the *random multiplier*) to the return before it reaches Player 1 |

This produces four cells:

1. no reinvestment × no noise
2. no reinvestment × noise
3. reinvestment × no noise
4. reinvestment × noise

In reinvestment cells, Player 1 enters a single total send amount. The program
uses the current-round endowment first and draws only any remainder from the
accumulated Part 2 account. The interface deliberately avoids asking
participants to allocate separate amounts from two labelled sources.

### Return-noise mechanism

Noise is applied only after Player 2 chooses a return. The interface calls the
factor the **random multiplier** (`realized return = chosen return × random
multiplier`):

- 20% probability: Player 1 receives 0 points, regardless of Player 2's choice (`×0`)
- 60% probability: exactly the chosen return reaches Player 1 (`×1`)
- 20% probability: twice the chosen return reaches Player 1 (`×2`)

The expected multiplier is 1, so the noise is mean-preserving. During the
decision, Player 1 sees only the realized amount that arrived, not Player 2's
chosen return or the multiplier; at each round's result page Player 2 can see
the amount that reached Player 1. The adjustment changes only Player 1's
realized return and payoff; it never changes Player 2's payoff.

### Accumulated Part 2 account

Both players begin Part 2 with an account balance of zero. After every round,
the participant's round earnings are added to this account. In reinvestment
cells, any points Player 1 sends above the current 10-point endowment are first
deducted from Player 1's account. A small jar badge in the top-right corner
shows the live account balance on every Part 2 page. The final Part 2 account
balance is the Part 2 point payoff.

### Belief elicitation

Beliefs are collected before the relevant partner decision is revealed:

- Player 1 reports a belief about how much Player 2 will return.
- Player 2 reports a belief about how much Player 1 will send, before
  multiplication.

In noise cells, after seeing the realized amount, Player 1 also reports a belief
about Player 2's chosen return.

### Random stopping (as presented)

Participants are told Part 2 lasts at least 4 rounds and that, from round 4 on,
the game ends with a 25% chance after every round. See the discrepancy note
above: every session currently runs exactly 5 rounds.

## Payment

Both Part 1 and Part 2 use the same configured conversion rate of S$0.05 per
point. Final payment is:

`S$10.00 show-up fee + Part 1 points × 0.05 + Part 2 points × 0.05`

The final participant page reports the Part 1 payoff, accumulated Part 2 payoff,
decision payment, show-up fee, and total payment. Participants are instructed to
remain seated and quiet until the experimenter dismisses them.

## Post-experiment survey

The final survey collects gender, age, a general risk-preference item, two
generalized-trust items, and a self-assessed trustworthiness item (all on 1–7
scales). It then asks one role-specific question about the matched partner:
Player 1 rates how trustworthy Player 2's behavior was; Player 2 rates how
trusting Player 1's behavior was.

## oTree apps

- `trust_reinvestment` — the full paired experiment used by every session
  configuration below.

## Session configurations

All session configurations are defined in `settings.py`.

| Session | Participants | Pair allocation | Notes |
|---|---:|---|---|
| `official` | any even number (default 24) | random pairs, cells assigned cyclically | full four-cell run; balances at any size |
| `pilot_8` | 8 | 4 random pairs, cyclic cells | compact pilot |
| `test_no_reinvestment_no_noise` | 2 | one forced cell | two-person cell trial |
| `test_no_reinvestment_noise` | 2 | one forced cell | two-person cell trial |
| `test_reinvestment_no_noise` | 2 | one forced cell | two-person cell trial |
| `test_reinvestment_noise` | 2 | one forced cell | two-person cell trial |
| `all24_no_reinvestment_no_noise` | 24 | all pairs in one cell | single-treatment full room |
| `all24_no_reinvestment_noise` | 24 | all pairs in one cell | single-treatment full room |
| `all24_reinvestment_no_noise` | 24 | all pairs in one cell | single-treatment full room |
| `all24_reinvestment_noise` | 24 | all pairs in one cell | single-treatment full room |

The four `test_*` configurations are identical to `official` except that each
runs exactly two participants (one pair) with its treatment cell forced, so a
single reviewer can inspect any cell end-to-end. Every session inherits the
`fixed_stage2_rounds = 5` default.

## Participant flow

The full paired experiment proceeds through:

1. Welcome and payment information
2. Part 1 title and execution explanation
3. Part 1 animated rules
4. Part 1 understanding test with question-specific feedback and rule review
5. Decisions for Player 1 and Player 2
6. Wait for the matched participant and Part 1 result
7. Part 2 title, fixed-role/partner reminder, and cell-specific animated rules
8. Part 2 understanding test with question-specific feedback and rule review
9. Repeated round title, belief/decision pages, partner wait pages, and results
10. Continue/end outcome after each eligible round
11. Post-experiment survey
12. Final point and SGD payment summary

## Run locally

Use Python 3.9–3.11 with the oTree version pinned in `requirements.txt`.

```bash
git clone https://github.com/Annawolf0128/trust-game.git
cd trust-game
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
otree devserver
```

For classroom / lab sessions, run in production mode (hides the debug panel and
binds all interfaces) and set a real admin password:

```bash
otree resetdb                       # clear old sessions first
OTREE_PRODUCTION=1 OTREE_ADMIN_PASSWORD=your_password otree prodserver 8000
```

Open `http://localhost:8000`, sign in to the oTree admin interface, and create
the required session. The local default admin login is `admin` / `admin`; set a
strong `OTREE_ADMIN_PASSWORD` and `OTREE_SECRET_KEY` before deployment. Never
reset a production database before exporting its data.

## Automated checks

```bash
otree test official
otree test pilot_8
otree test test_reinvestment_noise
```

The official bot test exercises a full four-cell run; the two-person tests are
useful for reviewing individual cell paths.

## Production notes

- Use the `decision_lab` room or generated participant links to assign stations.
  Participants enter a name on the first page, which is written to
  `participant.label` and shown on the admin Payments page for settlement.
- Any even number of participants can start an `official` session (under or over
  24); pairs continue to fill the four cells cyclically.
- Monitor participant progress and wait pages through the oTree admin screen.
- Export session data before any schema migration or database reset.
- Temporary browser captures, local databases (including SQLite WAL files),
  virtual environments, and logs are intentionally excluded from Git.
