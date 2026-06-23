from os import environ

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.10,
    participation_fee=0.00,
    doc="Two-person allocation task",
)

SESSION_CONFIGS = [
    # Official session: every session contains all four 2x2 cells. 24
    # participants (12 pairs) are paired on arrival and play Stage 1; at the
    # start of Stage 2 the 12 pairs are split 3-per-cell, stratified by Stage 1
    # relationship quality (see assign_stage2_treatments). Running every cell in
    # every session keeps session orthogonal to treatment instead of confounded
    # with it.
    dict(
        name="official",
        display_name="Official: 12 pairs, all four cells",
        num_demo_participants=24,
        app_sequence=["trust_reinvestment"],
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
    # Preview only: single player, no Part 1, no waiting, no partner. One session
    # per 2x2 cell -- walk both roles through that cell's Part 2 instructions,
    # send/return decision screens, both results screens, then the survey.
    dict(
        name="preview_no_reinvestment_no_noise",
        display_name="Preview: Part 2 (No reinvestment, no noise) + survey",
        num_demo_participants=1,
        app_sequence=["preview_part2"],
        preview_treatment="no_reinvestment",
        preview_noise="no_noise",
    ),
    dict(
        name="preview_no_reinvestment_noise",
        display_name="Preview: Part 2 (No reinvestment, noise) + survey",
        num_demo_participants=1,
        app_sequence=["preview_part2"],
        preview_treatment="no_reinvestment",
        preview_noise="noise",
    ),
    dict(
        name="preview_reinvestment_no_noise",
        display_name="Preview: Part 2 (Reinvestment, no noise) + survey",
        num_demo_participants=1,
        app_sequence=["preview_part2"],
        preview_treatment="reinvestment",
        preview_noise="no_noise",
    ),
    dict(
        name="preview_reinvestment_noise",
        display_name="Preview: Part 2 (Reinvestment, noise) + survey",
        num_demo_participants=1,
        app_sequence=["preview_part2"],
        preview_treatment="reinvestment",
        preview_noise="noise",
    ),
    # Preview only: single player, no partner, no waiting. Click straight through
    # every Part 1 page (intro, role, rules, quizzes, send/return, results).
    dict(
        name="preview_part1",
        display_name="Preview: Part 1 pages (no play-through)",
        num_demo_participants=1,
        app_sequence=["preview_part1"],
    ),
]

LANGUAGE_CODE = "en"
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = True

ROOMS = [
    dict(
        name="decision_lab",
        display_name="Decision Lab",
    )
]

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD", "admin")
SECRET_KEY = environ.get("OTREE_SECRET_KEY", "dev-secret-key")

INSTALLED_APPS = ["otree"]
