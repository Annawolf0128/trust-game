from otree.api import *
import random


doc = """
Dynamic two-person allocation task with account rules and random stopping after
a minimum second-stage length.
"""


class C(BaseConstants):
    NAME_IN_URL = "two_person_allocation"
    PLAYERS_PER_GROUP = 2

    STAGE1_ROUNDS = 3
    STAGE2_MIN_ROUNDS = 5
    # Hard ceiling on Stage 2 length. With a 15% per-round stopping probability
    # after the minimum, a pair reaches round 24 with probability ~0.85**19 < 5%,
    # so this cap almost never binds and barely truncates the random-stopping
    # (geometric) distribution.
    STAGE2_MAX_ROUNDS = 24
    NUM_ROUNDS = STAGE1_ROUNDS + STAGE2_MAX_ROUNDS

    ENDOWMENT = cu(10)
    MULTIPLIER = 3
    STOPPING_PROBABILITY = 0.15

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

    NOISE_FACTORS = [0.5, 1.0, 1.5]
    NOISE_WEIGHTS = [0.1, 0.8, 0.1]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    treatment = models.StringField(choices=C.TREATMENT_CHOICES)
    noise_treatment = models.StringField(choices=C.NOISE_CHOICES, blank=True)
    treatment_cell = models.StringField(blank=True)
    relationship_quality = models.FloatField(initial=0)
    stage2_should_continue = models.BooleanField(initial=True)


# Quiz choice sets. Defined at module level (not as Player class attributes),
# because oTree forbids list/dict class attributes on a model class.
MAX_SEND_CHOICES = [
    ["endowment_only", "Only your current-period endowment"],
    ["endowment_plus_account", "Your current-period endowment plus your accumulated account"],
    ["triple", "Three times your current-period endowment"],
    ["unlimited", "Any amount, with no limit"],
]
MAX_SEND_CHOICES_P2 = [
    ["endowment_only", "Only player 1's current-period endowment"],
    ["endowment_plus_account", "Player 1's current-period endowment plus their accumulated account"],
    ["triple", "Three times player 1's current-period endowment"],
    ["unlimited", "Any amount, with no limit"],
]
MULTIPLIER_CHOICES = [[1, "1"], [4, "4"], [7, "7"], [12, "12"]]
REALIZED_RETURN_CHOICES = [[2, "2"], [4, "4"], [6, "6"], [12, "12"]]


class Player(BasePlayer):
    role_label = models.StringField()

    stage = models.IntegerField()
    stage2_round = models.IntegerField(blank=True)

    transfer = models.CurrencyField(label="Amount to send", min=0)
    amount_sent = models.CurrencyField(label="Amount to send", min=0, blank=True)
    intended_return = models.CurrencyField(label="Amount to return", min=0, blank=True)
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
    stage1_avg_transfer = models.FloatField(blank=True)
    stage1_avg_return_rate = models.FloatField(blank=True)
    stage1_pair_surplus = models.FloatField(blank=True)
    stage1_relationship_quality = models.FloatField(blank=True)

    belief_partner_intended_return = models.CurrencyField(
        label="How many points do you think player 2 will return to you this round?",
        min=0,
        blank=True,
    )
    belief_partner_transfer = models.CurrencyField(
        label="How many points do you think player 1 chose to send to you this round?",
        min=0,
        blank=True,
    )
    belief_partner_return_post = models.CurrencyField(
        label="Now that you have seen the amount that reached you, how many points do you think player 2 actually chose to return this round?",
        min=0,
        blank=True,
    )
    signal_attribution = models.IntegerField(
        label="To what extent did the amount that reached you reflect player 2's chosen return rather than the computer adjustment? (0 - entirely the computer adjustment, 10 - entirely player 2's choice)",
        choices=[[i, str(i)] for i in range(0, 11)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )

    gender = models.StringField(
        label="What is your gender?",
        choices=[
            ["female", "Female"],
            ["male", "Male"],
            ["other", "Other"],
            ["prefer_not", "Prefer not to say"],
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    age = models.IntegerField(
        label="What is your age?",
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
        label="In general, how willing are you to trust other people? (1 - Not at all willing, 7 - Completely willing)",
        choices=[[i, str(i)] for i in range(1, 8)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    part1_quiz_p1_multiplied = models.IntegerField(
        label="If you send 4 points in Part 1, how many points does player 2 receive?",
        min=0,
        blank=True,
    )
    part1_quiz_p1_payoff = models.IntegerField(
        label="If you send 4 points and player 2 returns 5 points, how many points do you earn in that round?",
        min=0,
        blank=True,
    )
    part1_quiz_p2_received = models.IntegerField(
        label="If player 1 sends 4 points to you in Part 1, how many points do you receive?",
        min=0,
        blank=True,
    )
    part1_quiz_p2_payoff = models.IntegerField(
        label="If player 1 sends 4 points to you and you return 5 points, how many points do you earn in that round?",
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
        label="How many points reach you?",
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
        label="How many points reach player 1?",
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


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        subsession.group_randomly(fixed_id_in_group=True)
        for player in subsession.get_players():
            player.participant.vars["part1_account"] = 0
            player.participant.vars["part2_account"] = 0
    else:
        subsession.group_like_round(1)
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
    group.relationship_quality = previous.relationship_quality
    group.stage2_should_continue = previous.stage2_should_continue


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
    player_a = player_b.group.get_player_by_id(1)
    return player_a.transfer * C.MULTIPLIER


def stage2_return_max(player_b: Player):
    return player_b.received_amount


def set_stage1_payoffs(group: Group):
    player_a = group.get_player_by_id(1)
    player_b = group.get_player_by_id(2)
    sent_multiplied = player_a.transfer * C.MULTIPLIER
    player_a.realized_return = player_b.intended_return
    player_b.realized_return = player_b.intended_return

    player_a.round_payoff = C.ENDOWMENT - player_a.transfer + player_b.intended_return
    player_b.round_payoff = sent_multiplied - player_b.intended_return
    player_a.payoff = player_a.round_payoff
    player_b.payoff = player_b.round_payoff

    set_participant_part1_account(
        player_a,
        participant_part1_account(player_a) + player_a.round_payoff,
    )
    set_participant_part1_account(
        player_b,
        participant_part1_account(player_b) + player_b.round_payoff,
    )


def summarize_stage1(group: Group):
    rounds = [group.in_round(round_number) for round_number in range(1, C.STAGE1_ROUNDS + 1)]
    transfers = [float(round_group.get_player_by_id(1).transfer) for round_group in rounds]
    return_rates = []
    surplus = []
    for round_group in rounds:
        player_a = round_group.get_player_by_id(1)
        player_b = round_group.get_player_by_id(2)
        exposure = float(player_a.transfer * C.MULTIPLIER)
        rate = float(player_b.intended_return) / exposure if exposure else 0
        return_rates.append(rate)
        surplus.append(float(player_a.round_payoff + player_b.round_payoff))

    avg_transfer = sum(transfers) / len(transfers)
    avg_return_rate = sum(return_rates) / len(return_rates)
    avg_surplus = sum(surplus) / len(surplus)

    transfer_component = avg_transfer / float(C.ENDOWMENT)
    quality = 0.5 * transfer_component + 0.5 * avg_return_rate
    return avg_transfer, avg_return_rate, avg_surplus, quality


def apply_stage2_cell(group, treatment, noise_treatment, avg_transfer, avg_return_rate, avg_surplus, quality):
    group.treatment = treatment
    group.noise_treatment = noise_treatment
    group.treatment_cell = f"{treatment}_{noise_treatment}"
    group.relationship_quality = quality
    for participant in group.get_players():
        participant.stage1_avg_transfer = avg_transfer
        participant.stage1_avg_return_rate = avg_return_rate
        participant.stage1_pair_surplus = avg_surplus
        participant.stage1_relationship_quality = quality
        participant.participant.vars["stage1_relationship_quality"] = quality
        participant.participant.vars["treatment"] = group.treatment
        participant.participant.vars["noise_treatment"] = group.noise_treatment
        participant.participant.vars["treatment_cell"] = group.treatment_cell


def assign_stage2_treatments(subsession: Subsession):
    groups = subsession.get_groups()
    summaries = []
    for group in groups:
        avg_transfer, avg_return_rate, avg_surplus, quality = summarize_stage1(group)
        summaries.append((group, avg_transfer, avg_return_rate, avg_surplus, quality))

    # Review/testing override: pin every pair to a single 2x2 cell so the cell's
    # Part 2 instructions, quiz, and flow can be inspected in isolation. Set
    # `forced_treatment` and `forced_noise` in the session config to use this.
    forced_treatment = subsession.session.config.get("forced_treatment")
    forced_noise = subsession.session.config.get("forced_noise")
    if forced_treatment and forced_noise:
        for group, avg_transfer, avg_return_rate, avg_surplus, quality in summaries:
            apply_stage2_cell(
                group, forced_treatment, forced_noise,
                avg_transfer, avg_return_rate, avg_surplus, quality,
            )
        return

    # Stratified, balanced assignment across the four 2x2 cells. Rank the pairs
    # by Stage 1 relationship quality, then walk the sorted list in consecutive
    # blocks of four; within each block assign the four cells one-to-one in a
    # random order. Each cell therefore receives one pair from each quality band,
    # so Stage 1 history is balanced across cells (e.g. 12 pairs -> 3 per cell,
    # one from the low/mid/high third of the quality distribution). The official
    # session is fixed at 12 pairs so the pair count is a multiple of four.
    summaries.sort(key=lambda item: item[4])
    cells = [
        (C.NO_REINVESTMENT, C.NO_NOISE),
        (C.NO_REINVESTMENT, C.NOISE),
        (C.REINVESTMENT, C.NO_NOISE),
        (C.REINVESTMENT, C.NOISE),
    ]
    n_cells = len(cells)
    for block_start in range(0, len(summaries), n_cells):
        block = summaries[block_start:block_start + n_cells]
        cell_order = list(cells)
        random.shuffle(cell_order)
        for (treatment, noise_treatment), (
            group,
            avg_transfer,
            avg_return_rate,
            avg_surplus,
            quality,
        ) in zip(cell_order, block):
            apply_stage2_cell(
                group, treatment, noise_treatment,
                avg_transfer, avg_return_rate, avg_surplus, quality,
            )


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
    player_a.payoff = player_a.round_payoff
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
    if round_in_stage2 < C.STAGE2_MIN_ROUNDS:
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
        return dict(
            stopping_probability_percent=stopping_probability_percent,
            continue_probability_percent=100 - stopping_probability_percent,
            payment_rate="$0.10",
        )


class RoleAssignment(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(role_number=player.id_in_group)


class Part1InstructionsP1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and is_player_a(player)


class Part1InstructionsP2(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and is_player_b(player)


class Part1QuizP1(Page):
    form_model = "player"
    form_fields = ["part1_quiz_p1_multiplied", "part1_quiz_p1_payoff"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and is_player_a(player)

    @staticmethod
    def error_message(player: Player, values):
        errors = {}
        if values["part1_quiz_p1_multiplied"] != 12:
            errors["part1_quiz_p1_multiplied"] = "Please check the multiplication rule."
        if values["part1_quiz_p1_payoff"] != 11:
            errors["part1_quiz_p1_payoff"] = "Please check how your payoff is calculated."
        return errors


class Part1QuizP2(Page):
    form_model = "player"
    form_fields = ["part1_quiz_p2_received", "part1_quiz_p2_payoff"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and is_player_b(player)

    @staticmethod
    def error_message(player: Player, values):
        errors = {}
        if values["part1_quiz_p2_received"] != 12:
            errors["part1_quiz_p2_received"] = "Please check the multiplication rule."
        if values["part1_quiz_p2_payoff"] != 7:
            errors["part1_quiz_p2_payoff"] = "Please check how your payoff is calculated."
        return errors


class Stage1Transfer(Page):
    form_model = "player"
    form_fields = ["transfer", "belief_partner_intended_return"]

    @staticmethod
    def is_displayed(player: Player):
        return current_stage(player) == 1 and is_player_a(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            account=participant_part1_account(player),
            endowment=C.ENDOWMENT,
            multiplier=C.MULTIPLIER,
            stage1_round=player.round_number,
            stage1_rounds=C.STAGE1_ROUNDS,
        )

    @staticmethod
    def error_message(player: Player, values):
        if values["transfer"] > C.ENDOWMENT:
            return "Transfer cannot exceed your current-period endowment."
        max_possible_return = values["transfer"] * C.MULTIPLIER
        if values["belief_partner_intended_return"] > max_possible_return:
            return (
                "Your belief about the return cannot exceed the multiplied "
                "amount player 2 would receive."
            )


class Stage1TransferBelief(Page):
    form_model = "player"
    form_fields = ["belief_partner_transfer"]

    @staticmethod
    def is_displayed(player: Player):
        return current_stage(player) == 1 and is_player_b(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            account=participant_part1_account(player),
            endowment=C.ENDOWMENT,
            multiplier=C.MULTIPLIER,
            stage1_round=player.round_number,
            stage1_rounds=C.STAGE1_ROUNDS,
        )

    @staticmethod
    def error_message(player: Player, values):
        if values["belief_partner_transfer"] > C.ENDOWMENT:
            return (
                "Your belief about the amount sent cannot exceed player 1's "
                "current-period endowment."
            )


class Stage1Return(Page):
    form_model = "player"
    form_fields = ["intended_return"]

    @staticmethod
    def is_displayed(player: Player):
        return current_stage(player) == 1 and is_player_b(player)

    @staticmethod
    def vars_for_template(player: Player):
        player_a = player.group.get_player_by_id(1)
        return dict(
            account=participant_part1_account(player),
            transfer=player_a.transfer,
            multiplied_amount=stage1_return_max(player),
            max_return=stage1_return_max(player),
            multiplier=C.MULTIPLIER,
            stage1_round=player.round_number,
            stage1_rounds=C.STAGE1_ROUNDS,
        )

    @staticmethod
    def error_message(player: Player, values):
        if values["intended_return"] > stage1_return_max(player):
            return "Return cannot exceed the multiplied amount you received."


class WaitForStage1Transfer(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return current_stage(player) == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            stage1_round=player.round_number,
            stage1_rounds=C.STAGE1_ROUNDS,
        )


class WaitForStage1Return(WaitPage):
    after_all_players_arrive = set_stage1_payoffs

    @staticmethod
    def is_displayed(player: Player):
        return current_stage(player) == 1


class Stage1Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return current_stage(player) == 1

    @staticmethod
    def vars_for_template(player: Player):
        partner = player.get_others_in_group()[0]
        return dict(
            partner=partner,
            view_as_p1=is_player_a(player),
            account_balance=participant_part1_account(player),
        )


class Stage2SetupWait(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = assign_stage2_treatments

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.STAGE1_ROUNDS + 1


def stage2_instructions_vars(player: Player):
    stopping_probability = int(C.STOPPING_PROBABILITY * 100)
    return dict(
        treatment=player.group.treatment,
        noise_treatment=player.group.noise_treatment,
        treatment_cell=player.group.treatment_cell,
        relationship_quality=player.group.relationship_quality,
        is_reinvestment=uses_account_in_part2(player),
        has_noise=has_noise_in_part2(player),
        min_rounds=C.STAGE2_MIN_ROUNDS,
        stopping_probability=stopping_probability,
        continue_probability=100 - stopping_probability,
    )


class Stage2InstructionsNoReinvestmentNoNoiseP1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.NO_REINVESTMENT, C.NO_NOISE, 1)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2InstructionsNoReinvestmentNoNoiseP2(Page):
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.NO_REINVESTMENT, C.NO_NOISE, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2InstructionsNoReinvestmentNoiseP1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.NO_REINVESTMENT, C.NOISE, 1)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2InstructionsNoReinvestmentNoiseP2(Page):
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.NO_REINVESTMENT, C.NOISE, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2InstructionsReinvestmentNoNoiseP1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.REINVESTMENT, C.NO_NOISE, 1)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2InstructionsReinvestmentNoNoiseP2(Page):
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.REINVESTMENT, C.NO_NOISE, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2InstructionsReinvestmentNoiseP1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return in_stage2_instruction_cell(player, C.REINVESTMENT, C.NOISE, 1)

    @staticmethod
    def vars_for_template(player: Player):
        return stage2_instructions_vars(player)


class Stage2InstructionsReinvestmentNoiseP2(Page):
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
        expected_return_answer = 2 if has_noise_in_part2(player) else 4
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
        expected_return_answer = 2 if has_noise_in_part2(player) else 4
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
            received_amount=player.received_amount,
            max_return=stage2_return_max(player),
            multiplier=C.MULTIPLIER,
            has_noise=has_noise_in_part2(player),
            stage2_round=stage2_round_number(player),
        )

    @staticmethod
    def error_message(player: Player, values):
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
    form_fields = ["signal_attribution"]

    @staticmethod
    def is_displayed(player: Player):
        return current_stage(player) == 2 and active_in_stage2(player.group)

    @staticmethod
    def get_form_fields(player: Player):
        # Only player 1 faces the ambiguity, so only player 1 reports attribution.
        if has_noise_in_part2(player) and is_player_a(player):
            return ["belief_partner_return_post", "signal_attribution"]
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
            view_as_p1=is_player_a(player),
            treatment=player.group.treatment,
            has_noise=has_noise_in_part2(player),
            received_amount=player.group.get_player_by_id(2).received_amount,
            realized_return=player.group.get_player_by_id(1).realized_return,
            should_continue=player.group.stage2_should_continue,
            account_balance=participant_part2_account(player),
        )


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
        return dict(
            part1_account=participant_part1_account(player),
            part2_account=participant_part2_account(player),
            total_payoff=participant_total_account(player),
        )


page_sequence = [
    Introduction,
    RoleAssignment,
    Part1InstructionsP1,
    Part1InstructionsP2,
    Part1QuizP1,
    Part1QuizP2,
    Stage1Transfer,
    Stage1TransferBelief,
    WaitForStage1Transfer,
    Stage1Return,
    WaitForStage1Return,
    Stage1Results,
    Stage2SetupWait,
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
    Stage2Transfer,
    Stage2TransferBelief,
    WaitForStage2Transfer,
    Stage2Return,
    WaitForStage2Return,
    Stage2Results,
    Survey,
    FinalWait,
    FinalResults,
]
