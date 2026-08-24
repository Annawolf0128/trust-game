from os import environ

SESSION_CONFIG_DEFAULTS = dict(
    # Parts 1 and 2 use the same exchange rate.
    real_world_currency_per_point=0.10,
    participation_fee=10.00,
    doc="Two-person allocation task",
)

SESSION_CONFIGS = [
    # Official session: 24 participants are assigned random roles and random
    # partners, forming 12 pairs. The pairs are then randomized across the four
    # Part 2 cells with exactly 3 pairs per cell. Part 1 choices are retained as
    # analysis covariates but never affect roles, matches, or cell assignment.
    dict(
        name="official",
        display_name="OFFICIAL — 24 participants, four balanced blocks",
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
    dict(
        name="trial_no_reinvestment_no_noise",
        display_name="Trial Cell: No reinvestment, no noise",
        num_demo_participants=2,
        app_sequence=["trust_reinvestment"],
        forced_treatment="no_reinvestment",
        forced_noise="no_noise",
    ),
    dict(
        name="trial_no_reinvestment_noise",
        display_name="Trial Cell: No reinvestment, noise",
        num_demo_participants=2,
        app_sequence=["trust_reinvestment"],
        forced_treatment="no_reinvestment",
        forced_noise="noise",
    ),
    dict(
        name="trial_reinvestment_no_noise",
        display_name="Trial Cell: Reinvestment, no noise",
        num_demo_participants=2,
        app_sequence=["trust_reinvestment"],
        forced_treatment="reinvestment",
        forced_noise="no_noise",
    ),
    dict(
        name="trial_reinvestment_noise",
        display_name="Trial Cell: Reinvestment, noise",
        num_demo_participants=2,
        app_sequence=["trust_reinvestment"],
        forced_treatment="reinvestment",
        forced_noise="noise",
    ),
    # Fast, single-participant full-flow tests. Each path starts in Part 1,
    # then continues into its specified Part 2 cell and role. Counterpart
    # decisions are simulated so these paths never wait for another browser.
    *[
        dict(
            name=f"test_{treatment}_{noise}_player{role}",
            display_name=(
                f"TEST — {'Reinvestment' if treatment == 'reinvestment' else 'No reinvestment'}, "
                f"{'noise' if noise == 'noise' else 'no noise'}, Player {role}"
            ),
            num_demo_participants=1,
            app_sequence=["preview_part1", "preview_part2"],
            preview_treatment=treatment,
            preview_noise=noise,
            preview_role=role,
            fast_role_test=True,
        )
        for treatment, noise in [
            ("no_reinvestment", "no_noise"),
            ("no_reinvestment", "noise"),
            ("reinvestment", "no_noise"),
            ("reinvestment", "noise"),
        ]
        for role in [1, 2]
    ],
]

LANGUAGE_CODE = "en"
REAL_WORLD_CURRENCY_CODE = "CNY"
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
