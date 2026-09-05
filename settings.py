from os import environ

SESSION_CONFIG_DEFAULTS = dict(
    # Parts 1 and 2 use the same exchange rate.
    real_world_currency_per_point=0.05,
    participation_fee=10.00,
    # Every session actually runs exactly 5 Part 2 rounds. The interface still
    # describes the random stopping rule (min 4, 25% per round); this default
    # overrides the draw session-wide.
    fixed_stage2_rounds=5,
    doc="Two-person allocation task",
)

SESSION_CONFIGS = [
    # Official session: any EVEN number of participants can start (under or
    # over 24). Random roles and random partners form pairs; pairs are assigned
    # to the four Part 2 cells cyclically (pair 1 -> cell 1, ..., pair 5 ->
    # cell 1 again), so cells stay as balanced as possible at any size.
    dict(
        name="official",
        display_name="OFFICIAL — any even headcount, cyclic blocks (default 24)",
        num_demo_participants=24,
        app_sequence=["trust_reinvestment"],
    ),
    # Small complete session: 8 participants form 4 random pairs, with exactly
    # one pair assigned to each Part 2 treatment cell.
    dict(
        name="pilot_8",
        display_name="PILOT — 8 participants, one pair per block",
        num_demo_participants=8,
        app_sequence=["trust_reinvestment"],
        # Override the session-level 4-7 round draw: this compact pilot always
        # ends after its fifth Part 2 round (instructions stay truthful: they
        # only say the computer decides the number of rounds).
        fixed_stage2_rounds=5,
    ),
    # TEST sessions: identical to the official configuration (same app, same
    # exchange rate/fee, same session-level 4-7 round draw), except each session
    # has exactly 2 participants who are paired together, with the Part 2 cell
    # forced so every block can be inspected directly.
    *[
        dict(
            name=f"test_{treatment}_{noise}",
            display_name=(
                f"TEST — {'Reinvestment' if treatment == 'reinvestment' else 'No reinvestment'}, "
                f"{'noise' if noise == 'noise' else 'no noise'} (2 participants, one pair)"
            ),
            num_demo_participants=2,
            app_sequence=["trust_reinvestment"],
            forced_treatment=treatment,
            forced_noise=noise,
        )
        for treatment, noise in [
            ("no_reinvestment", "no_noise"),
            ("no_reinvestment", "noise"),
            ("reinvestment", "no_noise"),
            ("reinvestment", "noise"),
        ]
    ],
    # Full-room single-cell sessions: 24 participants (12 pairs), every pair
    # forced into the same Part 2 cell.
    *[
        dict(
            name=f"all24_{treatment}_{noise}",
            display_name=(
                f"ALL-24 — {'Reinvestment' if treatment == 'reinvestment' else 'No reinvestment'}, "
                f"{'noise' if noise == 'noise' else 'no noise'} (24 participants, one block)"
            ),
            num_demo_participants=24,
            app_sequence=["trust_reinvestment"],
            forced_treatment=treatment,
            forced_noise=noise,
        )
        for treatment, noise in [
            ("no_reinvestment", "no_noise"),
            ("no_reinvestment", "noise"),
            ("reinvestment", "no_noise"),
            ("reinvestment", "noise"),
        ]
    ],
]

LANGUAGE_CODE = "en"
REAL_WORLD_CURRENCY_CODE = "SGD"
USE_POINTS = True

ROOMS = [
    dict(
        name="decision_lab",
        display_name="Decision Lab",
        # Drop-in room: no participant_label_file. Identity is collected on the
        # first experiment page instead and written to participant.label.
    )
]

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD", "admin")
SECRET_KEY = environ.get("OTREE_SECRET_KEY", "dev-secret-key")

INSTALLED_APPS = ["otree"]
