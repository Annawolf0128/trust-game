from otree.api import *
import random


doc = """
Dynamic two-person allocation task with account rules and random stopping after
a minimum second-stage length.
"""


class C(BaseConstants):
    NAME_IN_URL = "two_person_allocation"
    PLAYERS_PER_GROUP = 2

    # Part 1 is a one-shot strategy-method elicitation. Everyone states both a
    # proposer transfer and a complete responder return schedule before one
    # random role/match is used to determine Part 1 earnings.
    STAGE1_ROUNDS = 1
    STAGE2_MIN_ROUNDS = 5
    # Hard ceiling on Stage 2 length. With a 20% per-round stopping probability
    # after the minimum, a pair reaches round 24 with probability ~0.80**19 < 1.5%,
    # so this cap almost never binds and barely truncates the random-stopping
    # (geometric) distribution.
    STAGE2_MAX_ROUNDS = 24
    NUM_ROUNDS = STAGE1_ROUNDS + STAGE2_MAX_ROUNDS

    ENDOWMENT = cu(10)
    MULTIPLIER = 3
    STOPPING_PROBABILITY = 0.20

    NO_REINVESTMENT = "no_reinvestment"
    REINVESTMENT = "reinvestment"
    NO_NOISE = "no_noise"
    NOISE = "noise"
    TREATMENT_CHOICES = [
        [NO_REINVESTMENT, "No reinvestment"],
        [REINVESTMENT, "Reinvestment"],
    ]
    NOISE_CHOICES = [
        [NO_NOISE, "No noise"],
        [NOISE, "Noise"],
    ]

    # Mean-preserving return adjustment. The computer can remove the entire
    # return, leave it unchanged, or double it. This adjustment changes only
    # what reaches player 1; player 2's payoff always uses the chosen return.
    NOISE_FACTORS = [0, 1, 2]
    NOISE_WEIGHTS = [0.2, 0.6, 0.2]

    # Both parts use the same exchange rate.
    PART1_USD_PER_POINT = 0.50
    PART2_USD_PER_POINT = 0.50


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    treatment = models.StringField(choices=C.TREATMENT_CHOICES)
    noise_treatment = models.StringField(choices=C.NOISE_CHOICES, blank=True)
    treatment_cell = models.StringField(blank=True)
    pair_type = models.StringField(blank=True)
    stage2_should_continue = models.BooleanField(initial=True)


# Quiz choice sets. Defined at module level (not as Player class attributes),
# because oTree forbids list/dict class attributes on a model class.
MAX_SEND_CHOICES = [
    ["endowment_only", "Only your current-period endowment"],
    ["endowment_plus_account", "Your current-period endowment plus your accumulated account"],
    ["multiple", "Three times your current-period endowment"],
    ["unlimited", "Any amount, with no limit"],
]
MAX_SEND_CHOICES_P2 = [
    ["endowment_only", "Only player 1's current-period endowment"],
    ["endowment_plus_account", "Player 1's current-period endowment plus their accumulated account"],
    ["multiple", "Three times player 1's current-period endowment"],
    ["unlimited", "Any amount, with no limit"],
]
MULTIPLIER_CHOICES = [[2, "2"], [4, "4"], [8, "8"], [12, "12"]]
RETURN_SIX_CODE = 6
UNCERTAIN_RETURN_CODE = -1
REALIZED_RETURN_CHOICES = [
    [0, "0 points"],
    [6, "6 points"],
    [12, "12 points"],
    [-1, "0, 6, or 12 points"],
]


class Player(BasePlayer):
    role_label = models.StringField()

    stage = models.IntegerField()
    stage2_round = models.IntegerField(blank=True)

    # Part 1 strategy-method decisions. Player 1 may send any whole number
    # from 0 through the full 10-point endowment. A zero send implies a zero
    # return; for offers 1--10, Player 2 states a complete return schedule.
    part1_proposer_offer = models.CurrencyField(
        label="Suppose you are Player 1. How many points will you send?",
        choices=[[i, str(i)] for i in range(0, 11)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    part1_return_1 = models.CurrencyField(
        label="Return if Player 1 sends 1 point",
        choices=[[i, str(i)] for i in range(0, 4)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    part1_return_2 = models.CurrencyField(
        label="Return if Player 1 sends 2 points",
        choices=[[i, str(i)] for i in range(0, 7)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    part1_return_3 = models.CurrencyField(
        label="Return if Player 1 sends 3 points",
        choices=[[i, str(i)] for i in range(0, 10)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    part1_return_4 = models.CurrencyField(
        label="Return if Player 1 sends 4 points",
        choices=[[i, str(i)] for i in range(0, 13)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    part1_return_5 = models.CurrencyField(
        label="Return if Player 1 sends 5 points",
        choices=[[i, str(i)] for i in range(0, 16)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    part1_return_6 = models.CurrencyField(
        label="Return if Player 1 sends 6 points",
        choices=[[i, str(i)] for i in range(0, 19)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    part1_return_7 = models.CurrencyField(
        label="Return if Player 1 sends 7 points",
        choices=[[i, str(i)] for i in range(0, 22)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    part1_return_8 = models.CurrencyField(
        label="Return if Player 1 sends 8 points",
        choices=[[i, str(i)] for i in range(0, 25)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    part1_return_9 = models.CurrencyField(
        label="Return if Player 1 sends 9 points",
        choices=[[i, str(i)] for i in range(0, 28)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    part1_return_10 = models.CurrencyField(
        label="Return if Player 1 sends 10 points",
        choices=[[i, str(i)] for i in range(0, 31)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    part1_payoff_role = models.StringField(blank=True)
    part1_realized_offer = models.CurrencyField(initial=0)
    part1_realized_return = models.CurrencyField(initial=0)
    part1_truster_score = models.FloatField(blank=True)
    part1_trustee_score = models.FloatField(blank=True)
    behavior_type = models.StringField(blank=True)
    stage2_role = models.StringField(blank=True)
    matched_pair_type = models.StringField(blank=True)

    transfer = models.CurrencyField(label="Amount to send", min=0)
    amount_sent = models.CurrencyField(label="Whole number of points to send", min=0, blank=True)
    intended_return = models.CurrencyField(label="Whole number of points to return", min=0, blank=True)
    realized_return = models.CurrencyField(initial=0)
    noise_factor = models.FloatField(blank=True)

    safe_account_start = models.CurrencyField(initial=0)
    reinvestment = models.CurrencyField(
        label="Amount from Part 2 accumulated account to use this round",
        min=0,
        initial=0,
    )
    retained_amount = models.CurrencyField(initial=0)
    total_exposure = models.CurrencyField(initial=0)
    received_amount = models.CurrencyField(initial=0)

    round_payoff = models.CurrencyField(initial=0)

    belief_partner_intended_return = models.CurrencyField(
        label="What is your belief about how many points player 2 will choose to return this round?",
        min=0,
        blank=True,
    )
    belief_partner_transfer = models.CurrencyField(
        label="What is your belief about how many points player 1 sent this round, before multiplication?",
        min=0,
        blank=True,
    )
    belief_partner_return_post = models.CurrencyField(
        label="How many points do you believe Player 2 chose to return this round?",
        min=0,
        blank=True,
    )
    signal_attribution = models.IntegerField(
        label="To what extent did the amount that reached you reflect player 2's chosen return rather than the computer adjustment? (1 - entirely the computer adjustment, 10 - entirely player 2's choice)",
        choices=[[i, str(i)] for i in range(1, 11)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )

    gender = models.StringField(
        label="What is your gender?",
        choices=[
            ["female", "Female"],
            ["male", "Male"],
            ["non_binary", "Non-binary"],
            ["prefer_not", "Prefer not to say"],
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    age = models.IntegerField(
        label="What is your age in years?",
        choices=[[i, str(i)] for i in range(18, 101)],
        blank=True,
    )
    risk_preference = models.IntegerField(
        label="How willing are you to take risks in general? (1 - Not at all willing, 7 - Very willing)",
        choices=[[i, str(i)] for i in range(1, 8)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    trust_most_people = models.IntegerField(
        label="Generally speaking, would you say that most people can be trusted, or that you need to be very careful in dealing with people? (1 - Need to be very careful, 7 - Most people can be trusted)",
        choices=[[i, str(i)] for i in range(1, 8)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    trust_willingness = models.IntegerField(
        label="In general, how willing are you personally to trust other people? (1 - Not at all willing, 7 - Completely willing)",
        choices=[[i, str(i)] for i in range(1, 8)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    part1_quiz_p1_multiplied = models.IntegerField(
        label="1. How many points does Player 2 receive?",
        min=0,
        blank=True,
    )
    part1_quiz_p1_payoff = models.IntegerField(
        label="2. How many points does Player 1 earn?",
        min=0,
        blank=True,
    )
    part1_quiz_p2_received = models.IntegerField(
        label="If player 1 sends 4 points to you in Part 1, how many points do you receive?",
        min=0,
        blank=True,
    )
    part1_quiz_p2_payoff = models.IntegerField(
        label="3. How many points does Player 2 earn?",
        min=0,
        blank=True,
    )

    part2_quiz_p1_account = models.IntegerField(
        label="In your Part 2 rules, can you use points from your accumulated account in the current round?",
        choices=[
            [1, "Yes"],
            [0, "No"],
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    part2_quiz_p1_multiplier = models.IntegerField(
        label="If you send 4 points to player 2, how many points does player 2 receive?",
        choices=MULTIPLIER_CHOICES,
        widget=widgets.RadioSelect,
        blank=True,
    )
    part2_quiz_p1_realized_return = models.IntegerField(
        label="Which amount or amounts can reach you?",
        choices=REALIZED_RETURN_CHOICES,
        widget=widgets.RadioSelect,
        blank=True,
    )
    part2_quiz_p1_maxsend = models.StringField(
        label="What is the most you can send to player 2 in a round?",
        choices=MAX_SEND_CHOICES,
        widget=widgets.RadioSelect,
        blank=True,
    )
    part2_quiz_p2_account = models.IntegerField(
        label="In your Part 2 rules, can the points sent to you include points from player 1's accumulated account?",
        choices=[
            [1, "Yes"],
            [0, "No"],
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    part2_quiz_p2_multiplier = models.IntegerField(
        label="If player 1 sends 4 points to you, how many points do you receive?",
        choices=MULTIPLIER_CHOICES,
        widget=widgets.RadioSelect,
        blank=True,
    )
    part2_quiz_p2_realized_return = models.IntegerField(
        label="Which amount or amounts can reach player 1?",
        choices=REALIZED_RETURN_CHOICES,
        widget=widgets.RadioSelect,
        blank=True,
    )
    part2_quiz_p2_maxsend = models.StringField(
        label="What is the most player 1 can send to you in a round?",
        choices=MAX_SEND_CHOICES_P2,
        widget=widgets.RadioSelect,
        blank=True,
    )


def part2_quiz_p1_realized_return_label(player: Player):
    if has_noise_in_part2(player):
        return "Which amount or amounts can reach you after the computer adjustment?"
    return "How many points reach you?"


def part2_quiz_p2_realized_return_label(player: Player):
    if has_noise_in_part2(player):
        return "Which amount or amounts can reach Player 1 after the computer adjustment?"
    return "How many points reach Player 1?"


def part2_quiz_p1_realized_return_choices(player: Player):
    return REALIZED_RETURN_CHOICES


def part2_quiz_p2_realized_return_choices(player: Player):
    return REALIZED_RETURN_CHOICES


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        # Placeholder groups are needed while everyone completes both Part 1
        # strategies. The payoff match and role are randomized only after all
        # decisions arrive at Part1DecisionWait.
        subsession.group_randomly()
        for player in subsession.get_players():
            player.participant.vars["part1_account"] = 0
            player.participant.vars["part2_account"] = 0
    elif subsession.round_number == C.STAGE1_ROUNDS + 1:
        # Temporary grouping only. Stage2SetupWait rematches the full session
        # after all Part 1 choices are available.
        subsession.group_like_round(1)
    else:
        subsession.group_like_round(C.STAGE1_ROUNDS + 1)
    for group in subsession.get_groups():
        for player in group.get_players():
            player.role_label = "A" if player.id_in_group == 1 else "B"
            player.stage = 1 if subsession.round_number <= C.STAGE1_ROUNDS else 2
            if player.stage == 2:
                player.stage2_round = subsession.round_number - C.STAGE1_ROUNDS


def role(player: Player):
    return player.role_label


def is_player_a(player: Player):
    return player.id_in_group == 1


def is_player_b(player: Player):
    return player.id_in_group == 2


def stage2_round_number(player: Player):
    return player.round_number - C.STAGE1_ROUNDS


def current_stage(player: Player):
    return 1 if player.round_number <= C.STAGE1_ROUNDS else 2


def copy_stage2_state(group: Group):
    if group.round_number == C.STAGE1_ROUNDS + 1:
        return
    previous = group.in_round(group.round_number - 1)
    group.treatment = previous.treatment
    group.noise_treatment = previous.noise_treatment
    group.treatment_cell = previous.treatment_cell
    group.pair_type = previous.pair_type
    group.stage2_should_continue = previous.stage2_should_continue
    for player in group.get_players():
        previous_player = previous.get_player_by_id(player.id_in_group)
        player.stage2_role = previous_player.stage2_role
        player.behavior_type = previous_player.behavior_type
        player.part1_truster_score = previous_player.field_maybe_none("part1_truster_score")
        player.part1_trustee_score = previous_player.field_maybe_none("part1_trustee_score")
        player.matched_pair_type = previous_player.matched_pair_type


def active_in_stage2(group: Group):
    if group.round_number <= C.STAGE1_ROUNDS + 1:
        return True
    previous = group.in_round(group.round_number - 1)
    # A pair is active this round only if the previous round was itself active
    # AND chose to continue. Without the recursive check, an inactive round keeps
    # the model default stage2_should_continue=True, which would wrongly
    # re-activate the pair (and crash on the never-assigned treatment field).
    return active_in_stage2(previous) and previous.stage2_should_continue


def participant_part1_account(player: Player):
    return cu(player.participant.vars.get("part1_account", 0))


def set_participant_part1_account(player: Player, amount):
    player.participant.vars["part1_account"] = float(amount)


def participant_part2_account(player: Player):
    return cu(player.participant.vars.get("part2_account", 0))


def set_participant_part2_account(player: Player, amount):
    player.participant.vars["part2_account"] = float(amount)


def participant_total_account(player: Player):
    return participant_part1_account(player) + participant_part2_account(player)


def stage1_return_max(player_b: Player):
    return player_b.part1_realized_offer * C.MULTIPLIER


def stage2_return_max(player_b: Player):
    return player_b.received_amount


def responder_return(player: Player, offer):
    if int(float(offer)) == 0:
        return cu(0)
    return getattr(player, f"part1_return_{int(float(offer))}")


def responder_score(player: Player):
    """Mean fraction returned across the ten non-zero transfer cases."""
    rates = [
        float(getattr(player, f"part1_return_{offer}")) / (C.MULTIPLIER * offer)
        for offer in range(1, 11)
    ]
    return sum(rates) / len(rates)


def is_whole_points(value):
    """Participant action fields must contain whole point amounts."""
    return value is not None and float(value).is_integer()


def realize_part1_payoffs(subsession: Subsession):
    """Create the random match once, then use it in both Parts 1 and 2."""
    # Roles and pairs are assigned after all Part 1 strategies are submitted.
    # The same role/pair realizes Part 1 payoffs and then continues into Part 2.
    assign_stage2_matching_and_treatments(subsession)
    for group in subsession.get_groups():
        proposer = group.get_player_by_id(1)
        responder = group.get_player_by_id(2)
        offer = proposer.part1_proposer_offer
        returned = responder_return(responder, offer)
        received = offer * C.MULTIPLIER

        proposer.part1_payoff_role = "proposer"
        responder.part1_payoff_role = "responder"
        for player in [proposer, responder]:
            player.part1_realized_offer = offer
            player.part1_realized_return = returned
            player.transfer = offer
            player.intended_return = returned
            player.realized_return = returned

        proposer.round_payoff = C.ENDOWMENT - offer + returned
        responder.round_payoff = received - returned
        part1_payoff_scale = C.PART1_USD_PER_POINT / C.PART2_USD_PER_POINT
        proposer.payoff = proposer.round_payoff * part1_payoff_scale
        responder.payoff = responder.round_payoff * part1_payoff_scale
        set_participant_part1_account(proposer, proposer.round_payoff)
        set_participant_part1_account(responder, responder.round_payoff)

        for player in [proposer, responder]:
            player.participant.vars["part1_proposer_offer"] = float(player.part1_proposer_offer)
            player.participant.vars["part1_trustee_score"] = responder_score(player)
            player.participant.vars["part1_payoff_role"] = player.part1_payoff_role


def apply_stage2_cell(group, treatment, noise_treatment, pair_type):
    group.treatment = treatment
    group.noise_treatment = noise_treatment
    group.treatment_cell = f"{treatment}_{noise_treatment}"
    group.pair_type = pair_type
    for participant in group.get_players():
        participant.matched_pair_type = pair_type
        participant.participant.vars["pair_type"] = pair_type
        participant.participant.vars["treatment"] = treatment
        participant.participant.vars["noise_treatment"] = noise_treatment
        participant.participant.vars["treatment_cell"] = group.treatment_cell


def assign_stage2_matching_and_treatments(subsession: Subsession):
    """Randomize roles, partners, and Part 2 cells independently of Part 1 answers."""
    players = list(subsession.get_players())
    if len(players) % 2:
        raise RuntimeError("Part 2 requires an even number of participants.")

    # Roles and partners are assigned by unrestricted random draws. Part 1
    # choices are retained as analysis covariates but never enter this process.
    random.shuffle(players)
    role_size = len(players) // 2
    trusters = players[:role_size]
    trustees = players[role_size:]
    random.shuffle(trustees)

    for player in trusters:
        round1_player = player.in_round(1)
        truster_score = float(round1_player.part1_proposer_offer)
        trustee_score = responder_score(round1_player)
        player.stage2_role = "truster"
        player.behavior_type = "not_stratified"
        player.part1_truster_score = truster_score
        player.part1_trustee_score = trustee_score
        player.participant.vars.update(
            stage2_role="truster",
            behavior_type="not_stratified",
            part1_truster_score=truster_score,
            part1_trustee_score=trustee_score,
        )
    for player in trustees:
        round1_player = player.in_round(1)
        truster_score = float(round1_player.part1_proposer_offer)
        trustee_score = responder_score(round1_player)
        player.stage2_role = "trustee"
        player.behavior_type = "not_stratified"
        player.part1_truster_score = truster_score
        player.part1_trustee_score = trustee_score
        player.participant.vars.update(
            stage2_role="trustee",
            behavior_type="not_stratified",
            part1_truster_score=truster_score,
            part1_trustee_score=trustee_score,
        )

    matrix = [[truster, trustee] for truster, trustee in zip(trusters, trustees)]

    forced_treatment = subsession.session.config.get("forced_treatment")
    forced_noise = subsession.session.config.get("forced_noise")
    if forced_treatment and forced_noise:
        specs = [(forced_treatment, forced_noise, "random")] * len(matrix)
    else:
        cells = [
            (C.NO_REINVESTMENT, C.NO_NOISE),
            (C.NO_REINVESTMENT, C.NOISE),
            (C.REINVESTMENT, C.NO_NOISE),
            (C.REINVESTMENT, C.NOISE),
        ]
        if len(matrix) % len(cells):
            raise RuntimeError(
                "Equal Part 2 cell sizes require the number of pairs to be "
                "divisible by four."
            )
        pairs_per_cell = len(matrix) // len(cells)
        specs = [
            (treatment, noise_treatment, "random")
            for treatment, noise_treatment in cells
            for _ in range(pairs_per_cell)
        ]
        random.shuffle(specs)

    subsession.set_group_matrix(matrix)
    for group, (treatment, noise_treatment, pair_type) in zip(subsession.get_groups(), specs):
        truster = group.get_player_by_id(1)
        trustee = group.get_player_by_id(2)
        truster.role_label = "A"
        trustee.role_label = "B"
        truster.stage2_role = "truster"
        trustee.stage2_role = "trustee"
        apply_stage2_cell(group, treatment, noise_treatment, pair_type)

    if not (forced_treatment and forced_noise):
        realized_cells = sorted(group.treatment_cell for group in subsession.get_groups())
        expected_cells = sorted(
            f"{treatment}_{noise_treatment}"
            for treatment, noise_treatment, _ in specs
        )
        if realized_cells != expected_cells:
            raise RuntimeError("Part 2 treatment-cell balancing failed.")


def carry_part1_match_into_stage2(subsession: Subsession):
    """Copy the payoff-relevant Part 1 match unchanged into every Part 2 round."""
    # Round 2 was initially created before Part 1 choices were known, so copy
    # the final round-1 matrix again after the Part 1 matching has been made.
    subsession.group_like_round(1)
    for group in subsession.get_groups():
        source_group = group.in_round(1)
        group.treatment = source_group.treatment
        group.noise_treatment = source_group.noise_treatment
        group.treatment_cell = source_group.treatment_cell
        group.pair_type = source_group.pair_type
        group.stage2_should_continue = True
        for player in group.get_players():
            source_player = source_group.get_player_by_id(player.id_in_group)
            player.role_label = "A" if player.id_in_group == 1 else "B"
            player.stage2_role = source_player.stage2_role
            player.behavior_type = source_player.behavior_type
            player.part1_truster_score = source_player.field_maybe_none("part1_truster_score")
            player.part1_trustee_score = source_player.field_maybe_none("part1_trustee_score")
            player.matched_pair_type = source_player.matched_pair_type

def uses_account_in_part2(player: Player):
    return player.group.treatment == C.REINVESTMENT


def has_noise_in_part2(player: Player):
    return player.group.noise_treatment == C.NOISE


def in_stage2_instruction_cell(player: Player, treatment, noise_treatment, role_id):
    return (
        player.round_number == C.STAGE1_ROUNDS + 1
        and player.group.treatment == treatment
        and player.group.noise_treatment == noise_treatment
        and player.id_in_group == role_id
    )


def apply_stage2_noise(amount, noise_treatment):
    if noise_treatment != C.NOISE:
        return 1.0, amount
    factor = random.choices(C.NOISE_FACTORS, weights=C.NOISE_WEIGHTS, k=1)[0]
    return factor, amount * factor


def set_stage2_received_amount(group: Group):
    player_a = group.get_player_by_id(1)
    player_b = group.get_player_by_id(2)
    player_a.safe_account_start = participant_part2_account(player_a)
    player_b.safe_account_start = participant_part2_account(player_b)
    # Player 1 enters a single send amount; spend the current-period endowment
    # first, then draw any remainder from the accumulated account.
    player_a.transfer = min(player_a.amount_sent, C.ENDOWMENT)
    player_a.reinvestment = player_a.amount_sent - player_a.transfer
    player_a.total_exposure = player_a.transfer + player_a.reinvestment
    player_a.retained_amount = player_a.safe_account_start - player_a.reinvestment

    # Player 2 receives the full multiplied amount; the noise is applied later to
    # player 2's chosen return, so player 1 (not player 2) faces the ambiguity.
    received = player_a.total_exposure * C.MULTIPLIER
    player_a.received_amount = received
    player_b.received_amount = received


def set_stage2_payoffs(group: Group):
    player_a = group.get_player_by_id(1)
    player_b = group.get_player_by_id(2)

    # Noise is applied to the return player 2 chose. Player 1 receives the
    # adjusted amount and never observes player 2's intended return directly,
    # which is the attribution ambiguity the design studies.
    factor, realized = apply_stage2_noise(player_b.intended_return, group.noise_treatment)
    player_a.noise_factor = factor
    player_b.noise_factor = factor
    player_a.realized_return = realized
    player_b.realized_return = player_b.intended_return

    player_a.round_payoff = C.ENDOWMENT - player_a.transfer + realized
    player_b.round_payoff = player_b.received_amount - player_b.intended_return
    # oTree's participant payoff must change by exactly the same amount as the
    # accumulated Part 2 account. In reinvestment cells, points drawn from the
    # account are therefore deducted here as well as in the account update.
    player_a.payoff = player_a.round_payoff - player_a.reinvestment
    player_b.payoff = player_b.round_payoff

    set_participant_part2_account(
        player_a,
        player_a.safe_account_start - player_a.reinvestment + player_a.round_payoff,
    )
    set_participant_part2_account(
        player_b,
        player_b.safe_account_start + player_b.round_payoff,
    )

    round_in_stage2 = stage2_round_number(player_a)
    fixed_stage2_rounds = group.session.config.get("fixed_stage2_rounds")
    if fixed_stage2_rounds is not None:
        group.stage2_should_continue = round_in_stage2 < int(fixed_stage2_rounds)
    elif round_in_stage2 < C.STAGE2_MIN_ROUNDS:
        group.stage2_should_continue = True
    else:
        group.stage2_should_continue = random.random() >= C.STOPPING_PROBABILITY


class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        stopping_probability_percent = int(C.STOPPING_PROBABILITY * 100)
        show_up_fee = float(player.session.config.get("participation_fee", 5.00))
        return dict(
            stopping_probability_percent=stopping_probability_percent,
            continue_probability_percent=100 - stopping_probability_percent,
            part1_rate=f"${C.PART1_USD_PER_POINT:.2f}",
            part2_rate=f"${C.PART2_USD_PER_POINT:.2f}",
            show_up_fee=f"${show_up_fee:.2f}",
        )


class Part1Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Part1RulesIntro(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Part1Quiz(Page):
    form_model = "player"
    form_fields = [
        "part1_quiz_p1_multiplied",
        "part1_quiz_p1_payoff",
        "part1_quiz_p2_payoff",
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        errors = {}
        if values["part1_quiz_p1_multiplied"] != 12:
            errors["part1_quiz_p1_multiplied"] = "Not correct yet. Remember that Player 2 receives three times the amount Player 1 sends."
        if values["part1_quiz_p1_payoff"] != 11:
            errors["part1_quiz_p1_payoff"] = "Not correct yet. Player 1 earns the points kept plus the points returned."
        if values["part1_quiz_p2_payoff"] != 7:
            errors["part1_quiz_p2_payoff"] = "Not correct yet. Player 2 earns the points received minus the points returned."
        return errors


class Part1QuestionsIntro(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Part1ProposerDecision(Page):
    form_model = "player"
    form_fields = ["part1_proposer_offer"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            endowment=C.ENDOWMENT,
            multiplier=C.MULTIPLIER,
        )


class Part1ResponderStrategy(Page):
    form_model = "player"
    form_fields = [f"part1_return_{offer}" for offer in range(1, 11)]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            endowment=C.ENDOWMENT,
            multiplier=C.MULTIPLIER,
        )

    @staticmethod
    def error_message(player: Player, values):
        return {
            field: "Please enter a whole number of points."
            for field, value in values.items()
            if not is_whole_points(value)
        }


class Part1DecisionWait(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = realize_part1_payoffs

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Part1Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        proposer_earnings = C.ENDOWMENT - player.part1_realized_offer + player.part1_realized_return
        responder_earnings = player.part1_realized_offer * C.MULTIPLIER - player.part1_realized_return
        is_player_1 = player.part1_payoff_role == "proposer"
        return dict(
            payoff_role=player.part1_payoff_role,
            payoff_role_display="Player 1" if is_player_1 else "Player 2",
            partner_decision_label="Your partner returned" if is_player_1 else "Your partner sent",
            partner_decision=player.part1_realized_return if is_player_1 else player.part1_realized_offer,
            realized_offer=player.part1_realized_offer,
            received_amount=player.part1_realized_offer * C.MULTIPLIER,
            realized_return=player.part1_realized_return,
            part1_earnings=participant_part1_account(player),
            proposer_earnings=proposer_earnings,
            responder_earnings=responder_earnings,
        )


class Stage2SetupWait(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = carry_part1_match_into_stage2

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.STAGE1_ROUNDS + 1


class Part2RoleAssignment(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.STAGE1_ROUNDS + 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(role_number=player.id_in_group)


def stage2_instructions_vars(player: Player):
    stopping_probability = int(C.STOPPING_PROBABILITY * 100)
    return dict(
        treatment=player.group.treatment,
        noise_treatment=player.group.noise_treatment,
        treatment_cell=player.group.treatment_cell,
        is_reinvestment=uses_account_in_part2(player),
        has_noise=has_noise_in_part2(player),
        min_rounds=C.STAGE2_MIN_ROUNDS,
        stopping_probability=stopping_probability,
        continue_probability=100 - stopping_probability,
        role_number=player.id_in_group,
        part1_rate=f"${C.PART1_USD_PER_POINT:.2f}",
        part2_rate=f"${C.PART2_USD_PER_POINT:.2f}",
    )


class Stage2InstructionsNoReinvestmentNoNoiseP1(Page):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.NO_REINVESTMENT, C.NO_NOISE, 1)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2InstructionsNoReinvestmentNoNoiseP2(Page):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.NO_REINVESTMENT, C.NO_NOISE, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2InstructionsNoReinvestmentNoiseP1(Page):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.NO_REINVESTMENT, C.NOISE, 1)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2InstructionsNoReinvestmentNoiseP2(Page):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.NO_REINVESTMENT, C.NOISE, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2InstructionsReinvestmentNoNoiseP1(Page):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.REINVESTMENT, C.NO_NOISE, 1)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2InstructionsReinvestmentNoNoiseP2(Page):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.REINVESTMENT, C.NO_NOISE, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2InstructionsReinvestmentNoiseP1(Page):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.REINVESTMENT, C.NOISE, 1)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2InstructionsReinvestmentNoiseP2(Page):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.REINVESTMENT, C.NOISE, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2QuizP1(Page):
    form_model = "player"
    form_fields = [
        "part2_quiz_p1_account",
        "part2_quiz_p1_multiplier",
        "part2_quiz_p1_realized_return",
        "part2_quiz_p1_maxsend",
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.STAGE1_ROUNDS + 1 and is_player_a(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            is_reinvestment=uses_account_in_part2(player),
            has_noise=has_noise_in_part2(player),
        )

    @staticmethod
    def error_message(player: Player, values):
        errors = {}
        expected_account_answer = 1 if uses_account_in_part2(player) else 0
        if values["part2_quiz_p1_account"] != expected_account_answer:
            errors["part2_quiz_p1_account"] = "Please check the account rule for Part 2."
        if values["part2_quiz_p1_multiplier"] != 12:
            errors["part2_quiz_p1_multiplier"] = "Please check the multiplication rule."
        expected_return_answer = UNCERTAIN_RETURN_CODE if has_noise_in_part2(player) else RETURN_SIX_CODE
        if values["part2_quiz_p1_realized_return"] != expected_return_answer:
            errors["part2_quiz_p1_realized_return"] = "Please check the return rule for Part 2."
        expected_maxsend = (
            "endowment_plus_account" if uses_account_in_part2(player) else "endowment_only"
        )
        if values["part2_quiz_p1_maxsend"] != expected_maxsend:
            errors["part2_quiz_p1_maxsend"] = "Please check how much you can send in Part 2."
        return errors


class Stage2QuizP2(Page):
    form_model = "player"
    form_fields = [
        "part2_quiz_p2_account",
        "part2_quiz_p2_multiplier",
        "part2_quiz_p2_realized_return",
        "part2_quiz_p2_maxsend",
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.STAGE1_ROUNDS + 1 and is_player_b(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            is_reinvestment=uses_account_in_part2(player),
            has_noise=has_noise_in_part2(player),
        )

    @staticmethod
    def error_message(player: Player, values):
        errors = {}
        expected_account_answer = 1 if uses_account_in_part2(player) else 0
        if values["part2_quiz_p2_account"] != expected_account_answer:
            errors["part2_quiz_p2_account"] = "Please check the account rule for Part 2."
        if values["part2_quiz_p2_multiplier"] != 12:
            errors["part2_quiz_p2_multiplier"] = "Please check the multiplication rule."
        expected_return_answer = UNCERTAIN_RETURN_CODE if has_noise_in_part2(player) else RETURN_SIX_CODE
        if values["part2_quiz_p2_realized_return"] != expected_return_answer:
            errors["part2_quiz_p2_realized_return"] = "Please check the return rule for Part 2."
        expected_maxsend = (
            "endowment_plus_account" if uses_account_in_part2(player) else "endowment_only"
        )
        if values["part2_quiz_p2_maxsend"] != expected_maxsend:
            errors["part2_quiz_p2_maxsend"] = "Please check how much player 1 can send in Part 2."
        return errors


class Stage2StateWait(WaitPage):
    after_all_players_arrive = copy_stage2_state

    @staticmethod
    def is_displayed(player: Player):
        return (
            current_stage(player) == 2
            and player.round_number > C.STAGE1_ROUNDS + 1
            and active_in_stage2(player.group)
        )


class Stage2RoundIntro(Page):
    template_name = "trust_reinvestment/Stage2RoundIntro.html"

    @staticmethod
    def is_displayed(player: Player):
        return current_stage(player) == 2 and active_in_stage2(player.group)

    @staticmethod
    def vars_for_template(player: Player):
        round_number = stage2_round_number(player)
        return dict(
            stage2_round=round_number,
            is_first_stage2_round=round_number == 1,
        )


class Stage2Transfer(Page):
    form_model = "player"
    form_fields = ["amount_sent", "belief_partner_intended_return"]

    @staticmethod
    def is_displayed(player: Player):
        return current_stage(player) == 2 and active_in_stage2(player.group) and is_player_a(player)

    @staticmethod
    def vars_for_template(player: Player):
        safe_account = participant_part2_account(player)
        player.safe_account_start = safe_account
        max_send = C.ENDOWMENT + safe_account if uses_account_in_part2(player) else C.ENDOWMENT
        return dict(
            treatment=player.group.treatment,
            endowment=C.ENDOWMENT,
            safe_account=safe_account,
            max_send=max_send,
            is_reinvestment=uses_account_in_part2(player),
            has_noise=has_noise_in_part2(player),
            stage2_round=stage2_round_number(player),
        )

    @staticmethod
    def error_message(player: Player, values):
        safe_account = participant_part2_account(player)
        max_send = C.ENDOWMENT + safe_account if uses_account_in_part2(player) else C.ENDOWMENT
        amount_sent = values["amount_sent"]
        if not is_whole_points(amount_sent):
            return "Please enter a whole number of points to send."
        if amount_sent > max_send:
            return f"The amount you send cannot exceed {max_send} this round."
        max_possible_return = amount_sent * C.MULTIPLIER
        if values["belief_partner_intended_return"] > max_possible_return:
            return "Belief about player 2's return cannot exceed the maximum amount player 2 could return."


class Stage2TransferBelief(Page):
    form_model = "player"
    form_fields = ["belief_partner_transfer"]

    @staticmethod
    def is_displayed(player: Player):
        return current_stage(player) == 2 and active_in_stage2(player.group) and is_player_b(player)

    @staticmethod
    def vars_for_template(player: Player):
        player_a = player.group.get_player_by_id(1)
        max_send = (
            C.ENDOWMENT + participant_part2_account(player_a)
            if uses_account_in_part2(player)
            else C.ENDOWMENT
        )
        return dict(
            account=participant_part2_account(player),
            endowment=C.ENDOWMENT,
            max_send=max_send,
            is_reinvestment=uses_account_in_part2(player),
            stage2_round=stage2_round_number(player),
        )

    @staticmethod
    def error_message(player: Player, values):
        player_a = player.group.get_player_by_id(1)
        max_possible_transfer = (
            C.ENDOWMENT + participant_part2_account(player_a)
            if uses_account_in_part2(player)
            else C.ENDOWMENT
        )
        if values["belief_partner_transfer"] > max_possible_transfer:
            return "Belief about player 1's chosen amount cannot exceed the maximum amount player 1 could send."


class Stage2Return(Page):
    form_model = "player"
    form_fields = ["intended_return"]

    @staticmethod
    def is_displayed(player: Player):
        return current_stage(player) == 2 and active_in_stage2(player.group) and is_player_b(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            account=participant_part2_account(player),
            amount_sent=player.group.get_player_by_id(1).total_exposure,
            received_amount=player.received_amount,
            max_return=stage2_return_max(player),
            multiplier=C.MULTIPLIER,
            has_noise=has_noise_in_part2(player),
            stage2_round=stage2_round_number(player),
        )

    @staticmethod
    def error_message(player: Player, values):
        if not is_whole_points(values["intended_return"]):
            return "Please enter a whole number of points to return."
        if values["intended_return"] > stage2_return_max(player):
            return "Return cannot exceed the amount you received."


class WaitForStage2Transfer(WaitPage):
    after_all_players_arrive = set_stage2_received_amount

    @staticmethod
    def is_displayed(player: Player):
        return current_stage(player) == 2 and active_in_stage2(player.group)


class WaitForStage2Return(WaitPage):
    after_all_players_arrive = set_stage2_payoffs

    @staticmethod
    def is_displayed(player: Player):
        return current_stage(player) == 2 and active_in_stage2(player.group)

    @staticmethod
    def vars_for_template(player: Player):
        player_b = player.group.get_player_by_id(2)
        return dict(received_amount=player_b.received_amount)


class Stage2Results(Page):
    form_model = "player"
    form_fields = []

    @staticmethod
    def is_displayed(player: Player):
        return current_stage(player) == 2 and active_in_stage2(player.group)

    @staticmethod
    def get_form_fields(player: Player):
        # In the noise condition, Player 1 reports one concise post-result belief.
        if has_noise_in_part2(player) and is_player_a(player):
            return ["belief_partner_return_post"]
        return []

    @staticmethod
    def error_message(player: Player, values):
        if has_noise_in_part2(player) and is_player_a(player):
            player_b = player.group.get_player_by_id(2)
            max_possible_return = player_b.received_amount
            if values["belief_partner_return_post"] > max_possible_return:
                return (
                    "Your belief about player 2's return cannot exceed the "
                    "amount player 2 received this round."
                )

    @staticmethod
    def vars_for_template(player: Player):
        partner = player.get_others_in_group()[0]
        return dict(
            partner=partner,
            partner_transfer=player.group.get_player_by_id(1).total_exposure,
            view_as_p1=is_player_a(player),
            treatment=player.group.treatment,
            is_reinvestment=uses_account_in_part2(player),
            has_noise=has_noise_in_part2(player),
            received_amount=player.group.get_player_by_id(2).received_amount,
            realized_return=player.group.get_player_by_id(1).realized_return,
            should_continue=player.group.stage2_should_continue,
            pilot_forced_stop=bool(
                player.session.config.get("fixed_stage2_rounds")
                and not player.group.stage2_should_continue
            ),
            account_balance=participant_part2_account(player),
            stage2_round=stage2_round_number(player),
        )


class SurveyIntro(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(part2_account=participant_part2_account(player))


class Survey(Page):
    form_model = "player"
    form_fields = [
        "gender",
        "age",
        "risk_preference",
        "trust_most_people",
        "trust_willingness",
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


class FinalWait(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


class FinalResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        part1_account = participant_part1_account(player)
        part2_account = participant_part2_account(player)
        total_payoff = part1_account + part2_account
        part1_payment = float(part1_account) * C.PART1_USD_PER_POINT
        part2_payment = float(part2_account) * C.PART2_USD_PER_POINT
        decision_payment = part1_payment + part2_payment
        show_up_fee = float(player.session.config.get("participation_fee", 5.00))
        return dict(
            part1_account=part1_account,
            part2_account=part2_account,
            total_payoff=total_payoff,
            part1_rate=f"${C.PART1_USD_PER_POINT:.2f}",
            part2_rate=f"${C.PART2_USD_PER_POINT:.2f}",
            part1_payment_usd=f"${part1_payment:.2f}",
            part2_payment_usd=f"${part2_payment:.2f}",
            decision_payment_usd=f"${decision_payment:.2f}",
            show_up_fee_usd=f"${show_up_fee:.2f}",
            final_payment_usd=f"${decision_payment + show_up_fee:.2f}",
        )


page_sequence = [
    Introduction,
    Part1RulesIntro,
    Part1Instructions,
    Part1Quiz,
    Part1QuestionsIntro,
    Part1ProposerDecision,
    Part1ResponderStrategy,
    Part1DecisionWait,
    Part1Results,
    Stage2SetupWait,
    Part2RoleAssignment,
    Stage2InstructionsNoReinvestmentNoNoiseP1,
    Stage2InstructionsNoReinvestmentNoNoiseP2,
    Stage2InstructionsNoReinvestmentNoiseP1,
    Stage2InstructionsNoReinvestmentNoiseP2,
    Stage2InstructionsReinvestmentNoNoiseP1,
    Stage2InstructionsReinvestmentNoNoiseP2,
    Stage2InstructionsReinvestmentNoiseP1,
    Stage2InstructionsReinvestmentNoiseP2,
    Stage2QuizP1,
    Stage2QuizP2,
    Stage2StateWait,
    Stage2RoundIntro,
    Stage2Transfer,
    Stage2TransferBelief,
    WaitForStage2Transfer,
    Stage2Return,
    WaitForStage2Return,
    Stage2Results,
    SurveyIntro,
    Survey,
    FinalResults,
]
