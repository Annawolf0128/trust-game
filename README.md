# Trust as Reinvestable Social Capital — oTree Experiment

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

This repository contains the current oTree implementation of a two-part trust
game studying whether trust persists, collapses after adverse outcomes, and is
shaped by payoff noise and opportunities to reuse accumulated earnings.

## Current design at a glance

| Parameter | Current value |
|---|---:|
| Player 1 endowment | 10 points per round |
| Transfer multiplier | 3 |
| Point conversion rate | USD 0.50 per point in both parts |
| Show-up fee | USD 5.00 |
| Part 2 minimum length | 5 rounds |
| Continuation after Round 5 | 80% after each completed round |
| Stopping after Round 5 | 20% after each completed round |
| Part 2 hard ceiling | 24 rounds |
| Noise factors | ×0 with 20%, ×1 with 60%, ×2 with 20% |

The participant interface is in English and uses animated HTML instruction
pages. Instruction lines are revealed sequentially, while decision, quiz,
waiting, result, survey, and completion pages share the same visual system.

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
After pairs have been formed, each pair is randomly assigned to one of four
Part 2 cells. Assignment is balanced within the session:

- In `official`, 12 pairs are assigned with exactly 3 pairs per cell.
- In `pilot_8`, 4 pairs are assigned with exactly 1 pair per cell.

The assignment does not stratify on Part 1 behavior.

## Part 2: repeated trust game

Each Part 2 round retains the Part 1 roles and partner:

1. Player 1 receives a 10-point current-round endowment.
2. Player 1 chooses a whole-number amount to send.
3. Player 2 receives three times the amount Player 1 sent.
4. Player 2 chooses a whole-number amount to return.
5. The round payoffs are added to each participant's accumulated Part 2
   account.

Player 2's round payoff is always the amount received minus the amount Player 2
chose to return. Player 1's round payoff is the unused current-round endowment
plus the amount that reaches Player 1 after any computer adjustment.

### The 2×2 between-pair design

| Dimension | Control level | Treatment level |
|---|---|---|
| Accumulated-account use | `no_reinvestment`: Player 1 can send at most the current 10-point endowment | `reinvestment`: Player 1 can send up to the current 10-point endowment plus the accumulated Part 2 balance |
| Return noise | `no_noise`: Player 1 receives exactly Player 2's chosen return | `noise`: the computer applies a mean-preserving adjustment to the return before it reaches Player 1 |

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

Noise is applied only after Player 2 chooses a return:

- 20% probability: none of the returned points reach Player 1 (`×0`)
- 60% probability: exactly the chosen return reaches Player 1 (`×1`)
- 20% probability: twice the chosen return reaches Player 1 (`×2`)

The expected adjustment factor is 1, so the noise is mean-preserving. Player 1
sees only the realized amount that arrived, not Player 2's chosen return or the
computer factor. The adjustment changes only Player 1's realized return and
payoff; it never changes Player 2's payoff.

### Accumulated Part 2 account

Both players begin Part 2 with an account balance of zero. After every round,
the participant's round earnings are added to this account. In reinvestment
cells, any points Player 1 sends above the current 10-point endowment are first
deducted from Player 1's account. The final Part 2 account balance is the Part 2
point payoff.

### Belief elicitation

Beliefs are collected before the relevant partner decision is revealed:

- Player 1 reports a belief about how much Player 2 will return.
- Player 2 reports a belief about how much Player 1 sent, before multiplication.

In noise cells, after seeing the realized amount, Player 1 also reports a belief
about Player 2's chosen return. The earlier attribution-scale question has been
removed.

### Random stopping

Part 2 always lasts at least five rounds. After Round 5 and after every later
completed round, the interaction continues with probability 0.80 and ends with
probability 0.20. A 24-round oTree ceiling prevents an unbounded session; the
probability of reaching that ceiling is approximately `0.8^19 = 1.44%`.

The untruncated expected Part 2 length is 9 rounds. With the 24-round ceiling,
the expected length is approximately 8.94 rounds.

## Payment

Both Part 1 and Part 2 use the same configured conversion rate of USD 0.50 per
point. Final payment is:

`USD 5.00 show-up fee + Part 1 points × 0.50 + Part 2 points × 0.50`

The final participant page reports the Part 1 payoff, accumulated Part 2 payoff,
decision payment, show-up fee, and total payment. Participants are instructed to
remain seated and quiet until the experimenter dismisses them. An optional
short English excerpt from *Anna Karenina* is available on that page for early
finishers.

## oTree apps

- `trust_reinvestment` — the full paired experiment used by official, pilot,
  and two-person trial sessions.
- `preview_part1` — internal single-participant support app used by the fast
  role-test sessions to exercise the real Part 1 templates without waiting.
- `preview_part2` — internal single-participant support app used by the fast
  role-test sessions to exercise one Part 2 treatment/role path with a simulated
  counterpart.

There are no standalone participant-facing preview session configurations.

## Session configurations

All session configurations are defined in `settings.py`.

### Data collection and compact pilot

| Session | Participants | Pair allocation | Part 2 length |
|---|---:|---|---|
| `official` | 24 | 12 random pairs; exactly 3 pairs per cell | Minimum 5 rounds, then 80% continue / 20% stop; 24-round cap |
| `pilot_8` | 8 | 4 random pairs; exactly 1 pair per cell | Exactly 5 rounds; participant-facing instructions remain the same |

### Two-participant cell trials

These sessions use the full paired flow and force one treatment cell. They use
the official minimum-five-round random-stopping rule.

- `trial_no_reinvestment_no_noise`
- `trial_no_reinvestment_noise`
- `trial_reinvestment_no_noise`
- `trial_reinvestment_noise`

### Fast single-participant role tests

Eight configurations cross the four cells with Player 1 and Player 2. Each test
runs the full Part 1 instruction/quiz/decision flow, then one simulated Part 2
round, survey, and final payment page. Counterpart decisions are scripted, so
there are no wait pages requiring a second browser.

- `test_no_reinvestment_no_noise_player1`
- `test_no_reinvestment_no_noise_player2`
- `test_no_reinvestment_noise_player1`
- `test_no_reinvestment_noise_player2`
- `test_reinvestment_no_noise_player1`
- `test_reinvestment_no_noise_player2`
- `test_reinvestment_noise_player1`
- `test_reinvestment_noise_player2`

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
12. Final point and USD payment summary

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

Open `http://localhost:8000`, sign in to the oTree admin interface, and create
the required session. The local default admin login is `admin` / `admin`; set a
strong `OTREE_ADMIN_PASSWORD` and `OTREE_SECRET_KEY` before deployment.

The database is created automatically. If an old development database uses a
previous schema, export anything needed and then recreate it:

```bash
otree resetdb
```

Never reset a production database before exporting its data.

## Automated checks

Representative commands are:

```bash
otree test official
otree test pilot_8
otree test test_reinvestment_noise_player1
otree test test_no_reinvestment_noise_player2
```

The official bot test exercises all 24 participants and all four cells. The
pilot test verifies the balanced eight-person allocation and fixed five-round
ending. The fast tests are useful for reviewing individual role/cell paths.

## Production notes

- Use the `decision_lab` room or generated participant links to assign stations.
- Monitor participant progress and wait pages through the oTree admin screen.
- Keep the server clock, database, and exported payment records backed up.
- Export session data before any schema migration or database reset.
- Temporary browser captures, audit videos, local databases, and logs are
  intentionally excluded from Git.
