from otree.api import *
from types import SimpleNamespace


doc = """
Preview-only app for Part 2. Each session previews a single 2x2 cell (set via
the session config's internal condition flags). For that cell it shows the
shared animated instructions, the send screen, the return screen, and the
round-results page (both roles), then the final-survey transition and survey --
with no Part 1 and no partner. It reuses the real templates from trust_reinvestment,
so what you see is exactly what participants see. Decision/results screens use
placeholder numbers (player 1 sends 4 from the endowment, plus 2 from the
account when reinvestment is available; player 2 returns 5). If no cell is set
in the config, every cell is shown in sequence.
"""


class C(BaseConstants):
    NAME_IN_URL = "preview_part2"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # Mirrors trust_reinvestment so the shared templates render the same numbers.
    ENDOWMENT = cu(10)
    MULTIPLIER = 3
    STAGE2_MIN_ROUNDS = 4

    NO_REINVESTMENT = "no_reinvestment"
    REINVESTMENT = "reinvestment"

    # Placeholder scenario shown on the decision/results screens.
    # Part 2 starts with an empty accumulated account, just as in the official app.
    SAFE_ACCOUNT = cu(0)
    DEMO_TRANSFER = cu(4)
    DEMO_REINVEST = cu(0)
    DEMO_RETURN = cu(5)
    NOISE_FACTOR = 2


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Survey fields, kept identical to trust_reinvestment so Survey.html renders.
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

    # Decision fields, identical to trust_reinvestment so the send/return
    # screens render their form widgets and the results screen has data.
    transfer = models.CurrencyField(label="Amount to send", min=0, blank=True)
    amount_sent = models.CurrencyField(label="Whole number of points to send", min=0, blank=True)
    reinvestment = models.CurrencyField(
        label="Amount from Part 2 accumulated account to use this round",
        min=0,
        blank=True,
    )
    intended_return = models.CurrencyField(label="Whole number of points to return", min=0, blank=True)
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
    part2_quiz_p1_account = models.IntegerField(
        label="In your Part 2 rules, can you use points from your accumulated account in the current round?",
        choices=[[1, "Yes"], [0, "No"]],
        widget=widgets.RadioSelect,
        blank=True,
    )
    part2_quiz_p1_multiplier = models.IntegerField(
        label="If you send 4 points to Player 2, how many points does Player 2 receive?",
        choices=[[2, "2"], [4, "4"], [8, "8"], [12, "12"]],
        widget=widgets.RadioSelect,
        blank=True,
    )
    part2_quiz_p1_realized_return = models.IntegerField(
        label="Which amount or amounts can reach you?",
        choices=[[0, "0 points"], [6, "6 points"], [12, "12 points"], [-1, "0, 6, or 12 points"]],
        widget=widgets.RadioSelect,
        blank=True,
    )
    part2_quiz_p1_maxsend = models.StringField(
        label="What is the most you can send to Player 2 in a round?",
        choices=[
            ["endowment_only", "Only your current-period endowment"],
            ["endowment_plus_account", "Your current-period endowment plus your accumulated account"],
            ["multiple", "Three times your current-period endowment"],
            ["unlimited", "Any amount, with no limit"],
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    part2_quiz_p2_account = models.IntegerField(
        label="In your Part 2 rules, can the points sent to you include points from Player 1's accumulated account?",
        choices=[[1, "Yes"], [0, "No"]],
        widget=widgets.RadioSelect,
        blank=True,
    )
    part2_quiz_p2_multiplier = models.IntegerField(
        label="If Player 1 sends 4 points to you, how many points do you receive?",
        choices=[[2, "2"], [4, "4"], [8, "8"], [12, "12"]],
        widget=widgets.RadioSelect,
        blank=True,
    )
    part2_quiz_p2_realized_return = models.IntegerField(
        label="Which amount or amounts can reach Player 1?",
        choices=[[0, "0 points"], [6, "6 points"], [12, "12 points"], [-1, "0, 6, or 12 points"]],
        widget=widgets.RadioSelect,
        blank=True,
    )
    part2_quiz_p2_maxsend = models.StringField(
        label="What is the most Player 1 can send to you in a round?",
        choices=[
            ["endowment_only", "Only Player 1's current-period endowment"],
            ["endowment_plus_account", "Player 1's current-period endowment plus their accumulated account"],
            ["multiple", "Three times Player 1's current-period endowment"],
            ["unlimited", "Any amount, with no limit"],
        ],
        widget=widgets.RadioSelect,
        blank=True,
    )
    received_amount = models.CurrencyField(initial=0)
    noise_factor = models.FloatField(blank=True)
    round_payoff = models.CurrencyField(initial=0)


def _preview_has_noise(player: Player):
    return player.session.config.get("preview_noise", "no_noise") == "noise"


def part2_quiz_p1_realized_return_label(player: Player):
    if _preview_has_noise(player):
        return "Which amount or amounts can reach you after the computer adjustment?"
    return "How many points reach you?"


def part2_quiz_p2_realized_return_label(player: Player):
    if _preview_has_noise(player):
        return "Which amount or amounts can reach Player 1 after the computer adjustment?"
    return "How many points reach Player 1?"


def part2_quiz_p1_realized_return_choices(player: Player):
    return [[0, "0 points"], [6, "6 points"], [12, "12 points"], [-1, "0, 6, or 12 points"]]


def part2_quiz_p2_realized_return_choices(player: Player):
    return part2_quiz_p1_realized_return_choices(player)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _instruction_vars(player: Player):
    treatment = player.session.config.get("preview_treatment", C.NO_REINVESTMENT)
    noise_treatment = player.session.config.get("preview_noise", "no_noise")
    return dict(
        min_rounds=C.STAGE2_MIN_ROUNDS,
        treatment=treatment,
        noise_treatment=noise_treatment,
        treatment_cell=f"{treatment}_{noise_treatment}",
        is_reinvestment=treatment == C.REINVESTMENT,
        has_noise=noise_treatment == "noise",
        role_number=int(player.session.config.get("preview_role", 1)),
        part1_rate="¥0.10",
        part2_rate="¥0.10",
    )


def _treatment(is_reinvestment):
    return C.REINVESTMENT if is_reinvestment else C.NO_REINVESTMENT


def _in_cell(player: Player, is_reinvestment, has_noise):
    """Show this page only if it belongs to the cell set in the session config.

    If the config does not pin a cell, show every cell in sequence.
    """
    cfg = player.session.config
    if cfg.get("preview_survey_only"):
        return False
    want_treatment = cfg.get("preview_treatment")
    want_noise = cfg.get("preview_noise")
    if not want_treatment or not want_noise:
        return True
    noise_str = "noise" if has_noise else "no_noise"
    return want_treatment == _treatment(is_reinvestment) and want_noise == noise_str


def _show_instructions(player: Player):
    return not player.session.config.get("preview_skip_instructions", False)


def _show_role(player: Player, role):
    """Pin fast tests to one role; legacy previews still show both roles."""
    configured_role = player.session.config.get("preview_role")
    return configured_role is None or int(configured_role) == role


def _cell_numbers(is_reinvestment, has_noise, total_sent=None, intended_return=None):
    if total_sent is None:
        total_sent = C.DEMO_TRANSFER + (C.DEMO_REINVEST if is_reinvestment else cu(0))
    total_sent = cu(total_sent)
    transfer = min(total_sent, C.ENDOWMENT)
    reinvest = total_sent - transfer if is_reinvestment else cu(0)
    exposure = transfer + reinvest
    # Player 2 always receives the full multiplied amount; the noise applies to
    # the return on its way back to player 1.
    received = exposure * C.MULTIPLIER
    factor = C.NOISE_FACTOR if has_noise else 1.0
    chosen_return = min(cu(intended_return if intended_return is not None else C.DEMO_RETURN), received)
    realized_return = chosen_return * factor
    p1_payoff = C.ENDOWMENT - transfer + realized_return
    p2_payoff = received - chosen_return
    return dict(
        transfer=transfer,
        reinvest=reinvest,
        total_sent=exposure,
        received=received,
        factor=factor,
        intended_return=chosen_return,
        realized_return=realized_return,
        p1_payoff=p1_payoff,
        p2_payoff=p2_payoff,
        p1_account=C.SAFE_ACCOUNT - reinvest + p1_payoff,
        p2_account=C.SAFE_ACCOUNT + p2_payoff,
    )


def _transfer_fields(is_reinvestment):
    return ["amount_sent", "belief_partner_intended_return"]


def _transfer_vars(is_reinvestment, has_noise):
    max_send = C.ENDOWMENT + C.SAFE_ACCOUNT if is_reinvestment else C.ENDOWMENT
    return dict(
        treatment=_treatment(is_reinvestment),
        endowment=C.ENDOWMENT,
        safe_account=C.SAFE_ACCOUNT,
        max_send=max_send,
        is_reinvestment=is_reinvestment,
        has_noise=has_noise,
        stage2_round=1,
    )


def _belief_vars(is_reinvestment, has_noise):
    max_send = C.ENDOWMENT + C.SAFE_ACCOUNT if is_reinvestment else C.ENDOWMENT
    return dict(
        account=C.SAFE_ACCOUNT,
        endowment=C.ENDOWMENT,
        max_send=max_send,
        is_reinvestment=is_reinvestment,
        stage2_round=1,
    )


def _return_vars(is_reinvestment, has_noise):
    n = _cell_numbers(is_reinvestment, has_noise)
    return dict(
        account=C.SAFE_ACCOUNT,
        amount_sent=n["total_sent"],
        received_amount=n["received"],
        max_return=n["received"],
        multiplier=C.MULTIPLIER,
        has_noise=has_noise,
        stage2_round=1,
    )


def _results_p1_vars(player, is_reinvestment, has_noise):
    chosen_send = player.amount_sent if player.amount_sent is not None else None
    n = _cell_numbers(is_reinvestment, has_noise, total_sent=chosen_send)
    player.transfer = n["transfer"]
    player.reinvestment = n["reinvest"]
    player.noise_factor = n["factor"]
    player.round_payoff = n["p1_payoff"]
    player.participant.vars["part2_account"] = float(n["p1_account"])
    partner = SimpleNamespace(intended_return=n["intended_return"])
    return dict(
        view_as_p1=True,
        treatment=_treatment(is_reinvestment),
        is_reinvestment=is_reinvestment,
        has_noise=has_noise,
        received_amount=n["received"],
        realized_return=n["realized_return"],
        should_continue=not bool(player.session.config.get("fast_role_test")),
        pilot_forced_stop=False,
        partner=partner,
        account_balance=n["p1_account"],
        stage2_round=1,
    )


def _results_p2_vars(player, is_reinvestment, has_noise):
    chosen_return = player.intended_return if player.intended_return is not None else None
    n = _cell_numbers(
        is_reinvestment,
        has_noise,
        total_sent=C.DEMO_TRANSFER,
        intended_return=chosen_return,
    )
    player.received_amount = n["received"]
    player.intended_return = n["intended_return"]
    player.round_payoff = n["p2_payoff"]
    player.participant.vars["part2_account"] = float(n["p2_account"])
    return dict(
        view_as_p1=False,
        treatment=_treatment(is_reinvestment),
        is_reinvestment=is_reinvestment,
        has_noise=has_noise,
        received_amount=n["received"],
        should_continue=not bool(player.session.config.get("fast_role_test")),
        pilot_forced_stop=False,
        partner_transfer=n["total_sent"],
        account_balance=n["p2_account"],
        stage2_round=1,
    )


def _results_fields(has_noise, is_p1=False):
    if has_noise and is_p1:
        return ["belief_partner_return_post"]
    return []


# ---------------------------------------------------------------------------
# Base page classes (shared template wiring)
# ---------------------------------------------------------------------------


class Part2Transition(Page):
    template_name = "trust_reinvestment/Part2RoleAssignment.html"

    @staticmethod
    def is_displayed(player: Player):
        return not player.session.config.get("preview_survey_only", False)


class _Instruction(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return _instruction_vars(player)


def _quiz_is_displayed(player: Player, role: int):
    return (
        not player.session.config.get("preview_survey_only", False)
        and not player.session.config.get("preview_skip_instructions", False)
        and _show_role(player, role)
    )


def _quiz_error_message(player: Player, values, role: int):
    cfg = player.session.config
    is_reinvestment = cfg.get("preview_treatment", C.NO_REINVESTMENT) == C.REINVESTMENT
    has_noise = cfg.get("preview_noise", "no_noise") == "noise"
    prefix = f"part2_quiz_p{role}_"
    errors = {}
    if values[prefix + "account"] != (1 if is_reinvestment else 0):
        errors[prefix + "account"] = "Please check the accumulated-account rule."
    if values[prefix + "multiplier"] != 12:
        errors[prefix + "multiplier"] = "Please check the multiplication rule."
    if values[prefix + "realized_return"] != (-1 if has_noise else 6):
        errors[prefix + "realized_return"] = "Please check the return rule."
    expected_maxsend = "endowment_plus_account" if is_reinvestment else "endowment_only"
    if values[prefix + "maxsend"] != expected_maxsend:
        errors[prefix + "maxsend"] = "Please check the sending limit."
    return errors


class Part2QuizP1(Page):
    template_name = "trust_reinvestment/Stage2QuizP1.html"
    form_model = "player"
    form_fields = [
        "part2_quiz_p1_account",
        "part2_quiz_p1_multiplier",
        "part2_quiz_p1_realized_return",
        "part2_quiz_p1_maxsend",
    ]

    @staticmethod
    def is_displayed(player: Player):
        return _quiz_is_displayed(player, 1)

    @staticmethod
    def vars_for_template(player: Player):
        return _instruction_vars(player)

    @staticmethod
    def error_message(player: Player, values):
        return _quiz_error_message(player, values, 1)


class Part2QuizP2(Page):
    template_name = "trust_reinvestment/Stage2QuizP2.html"
    form_model = "player"
    form_fields = [
        "part2_quiz_p2_account",
        "part2_quiz_p2_multiplier",
        "part2_quiz_p2_realized_return",
        "part2_quiz_p2_maxsend",
    ]

    @staticmethod
    def is_displayed(player: Player):
        return _quiz_is_displayed(player, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return _instruction_vars(player)

    @staticmethod
    def error_message(player: Player, values):
        return _quiz_error_message(player, values, 2)


class Part2RoundIntro(Page):
    template_name = "trust_reinvestment/Stage2RoundIntro.html"

    @staticmethod
    def is_displayed(player: Player):
        return not player.session.config.get("preview_survey_only")

    @staticmethod
    def vars_for_template(player: Player):
        return dict(stage2_round=1, is_first_stage2_round=True)


class _Transfer(Page):
    template_name = "trust_reinvestment/Stage2Transfer.html"
    form_model = "player"


class _TransferBelief(Page):
    template_name = "trust_reinvestment/Stage2TransferBelief.html"
    form_model = "player"
    form_fields = ["belief_partner_transfer"]


class _Return(Page):
    template_name = "trust_reinvestment/Stage2Return.html"
    form_model = "player"
    form_fields = ["intended_return"]


class _Results(Page):
    template_name = "trust_reinvestment/Stage2Results.html"
    form_model = "player"


# ---------------------------------------------------------------------------
# Cell 1: no reinvestment, no noise
# ---------------------------------------------------------------------------


class NoReinvestmentNoNoiseP1(_Instruction):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"

    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, False) and _show_instructions(player)


class NoReinvestmentNoNoiseP2(_Instruction):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"

    @staticmethod
    def is_displayed(player: Player):
        return False


class NoReinvestmentNoNoiseTransfer(_Transfer):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, False) and _show_role(player, 1)

    @staticmethod
    def get_form_fields(player: Player):
        return _transfer_fields(False)

    @staticmethod
    def vars_for_template(player: Player):
        return _transfer_vars(False, False)


class NoReinvestmentNoNoiseBelief(_TransferBelief):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, False) and _show_role(player, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return _belief_vars(False, False)


class NoReinvestmentNoNoiseReturn(_Return):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, False) and _show_role(player, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return _return_vars(False, False)


class NoReinvestmentNoNoiseResultsP1(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, False) and _show_role(player, 1)

    @staticmethod
    def get_form_fields(player: Player):
        return _results_fields(False, is_p1=True)

    @staticmethod
    def vars_for_template(player: Player):
        return _results_p1_vars(player, False, False)


class NoReinvestmentNoNoiseResultsP2(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, False) and _show_role(player, 2)

    @staticmethod
    def get_form_fields(player: Player):
        return _results_fields(False)

    @staticmethod
    def vars_for_template(player: Player):
        return _results_p2_vars(player, False, False)


# ---------------------------------------------------------------------------
# Cell 2: no reinvestment, noise
# ---------------------------------------------------------------------------


class NoReinvestmentNoiseP1(_Instruction):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"

    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, True) and _show_instructions(player)


class NoReinvestmentNoiseP2(_Instruction):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"

    @staticmethod
    def is_displayed(player: Player):
        return False


class NoReinvestmentNoiseTransfer(_Transfer):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, True) and _show_role(player, 1)

    @staticmethod
    def get_form_fields(player: Player):
        return _transfer_fields(False)

    @staticmethod
    def vars_for_template(player: Player):
        return _transfer_vars(False, True)


class NoReinvestmentNoiseBelief(_TransferBelief):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, True) and _show_role(player, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return _belief_vars(False, True)


class NoReinvestmentNoiseReturn(_Return):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, True) and _show_role(player, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return _return_vars(False, True)


class NoReinvestmentNoiseResultsP1(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, True) and _show_role(player, 1)

    @staticmethod
    def get_form_fields(player: Player):
        return _results_fields(True, is_p1=True)

    @staticmethod
    def vars_for_template(player: Player):
        return _results_p1_vars(player, False, True)


class NoReinvestmentNoiseResultsP2(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, True) and _show_role(player, 2)

    @staticmethod
    def get_form_fields(player: Player):
        return []

    @staticmethod
    def vars_for_template(player: Player):
        return _results_p2_vars(player, False, True)


# ---------------------------------------------------------------------------
# Cell 3: reinvestment, no noise
# ---------------------------------------------------------------------------


class ReinvestmentNoNoiseP1(_Instruction):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"

    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, False) and _show_instructions(player)


class ReinvestmentNoNoiseP2(_Instruction):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"

    @staticmethod
    def is_displayed(player: Player):
        return False


class ReinvestmentNoNoiseTransfer(_Transfer):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, False) and _show_role(player, 1)

    @staticmethod
    def get_form_fields(player: Player):
        return _transfer_fields(True)

    @staticmethod
    def vars_for_template(player: Player):
        return _transfer_vars(True, False)


class ReinvestmentNoNoiseBelief(_TransferBelief):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, False) and _show_role(player, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return _belief_vars(True, False)


class ReinvestmentNoNoiseReturn(_Return):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, False) and _show_role(player, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return _return_vars(True, False)


class ReinvestmentNoNoiseResultsP1(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, False) and _show_role(player, 1)

    @staticmethod
    def get_form_fields(player: Player):
        return _results_fields(False, is_p1=True)

    @staticmethod
    def vars_for_template(player: Player):
        return _results_p1_vars(player, True, False)


class ReinvestmentNoNoiseResultsP2(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, False) and _show_role(player, 2)

    @staticmethod
    def get_form_fields(player: Player):
        return _results_fields(False)

    @staticmethod
    def vars_for_template(player: Player):
        return _results_p2_vars(player, True, False)


# ---------------------------------------------------------------------------
# Cell 4: reinvestment, noise
# ---------------------------------------------------------------------------


class ReinvestmentNoiseP1(_Instruction):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"

    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, True) and _show_instructions(player)


class ReinvestmentNoiseP2(_Instruction):
    template_name = "trust_reinvestment/Stage2InstructionsAnimated.html"

    @staticmethod
    def is_displayed(player: Player):
        return False


class ReinvestmentNoiseTransfer(_Transfer):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, True) and _show_role(player, 1)

    @staticmethod
    def get_form_fields(player: Player):
        return _transfer_fields(True)

    @staticmethod
    def vars_for_template(player: Player):
        return _transfer_vars(True, True)


class ReinvestmentNoiseBelief(_TransferBelief):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, True) and _show_role(player, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return _belief_vars(True, True)


class ReinvestmentNoiseReturn(_Return):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, True) and _show_role(player, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return _return_vars(True, True)


class ReinvestmentNoiseResultsP1(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, True) and _show_role(player, 1)

    @staticmethod
    def get_form_fields(player: Player):
        return _results_fields(True, is_p1=True)

    @staticmethod
    def vars_for_template(player: Player):
        return _results_p1_vars(player, True, True)


class ReinvestmentNoiseResultsP2(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, True) and _show_role(player, 2)

    @staticmethod
    def get_form_fields(player: Player):
        return []

    @staticmethod
    def vars_for_template(player: Player):
        return _results_p2_vars(player, True, True)


class SurveyIntro(Page):
    template_name = "trust_reinvestment/SurveyIntro.html"

    @staticmethod
    def vars_for_template(player: Player):
        return dict(part2_account=cu(player.participant.vars.get("part2_account", 0)))


class Survey(Page):
    template_name = "trust_reinvestment/Survey.html"
    form_model = "player"
    form_fields = [
        "gender",
        "age",
        "risk_preference",
        "trust_most_people",
        "trust_willingness",
    ]


class FinalResults(Page):
    template_name = "trust_reinvestment/FinalResults.html"

    @staticmethod
    def vars_for_template(player: Player):
        part1_account = cu(player.participant.vars.get("part1_account", 0))
        part2_account = cu(player.participant.vars.get("part2_account", 0))
        part1_payment = float(part1_account) * 0.10
        part2_payment = float(part2_account) * 0.10
        decision_payment = part1_payment + part2_payment
        show_up_fee = float(player.session.config.get("participation_fee", 10.00))
        return dict(
            part1_account=part1_account,
            part2_account=part2_account,
            total_payoff=part1_account + part2_account,
            part1_payment_usd=f"¥{part1_payment:.2f}",
            part2_payment_usd=f"¥{part2_payment:.2f}",
            decision_payment_usd=f"¥{decision_payment:.2f}",
            show_up_fee_usd=f"¥{show_up_fee:.2f}",
            final_payment_usd=f"¥{decision_payment + show_up_fee:.2f}",
        )


page_sequence = [
    Part2Transition,
    # Exactly one of these instruction pages is shown in a pinned TEST.
    NoReinvestmentNoNoiseP1,
    NoReinvestmentNoNoiseP2,
    NoReinvestmentNoiseP1,
    NoReinvestmentNoiseP2,
    ReinvestmentNoNoiseP1,
    ReinvestmentNoNoiseP2,
    ReinvestmentNoiseP1,
    ReinvestmentNoiseP2,
    Part2QuizP1,
    Part2QuizP2,
    Part2RoundIntro,
    # Cell 1: no reinvestment, no noise
    NoReinvestmentNoNoiseTransfer,
    NoReinvestmentNoNoiseBelief,
    NoReinvestmentNoNoiseReturn,
    NoReinvestmentNoNoiseResultsP1,
    NoReinvestmentNoNoiseResultsP2,
    # Cell 2: no reinvestment, noise
    NoReinvestmentNoiseTransfer,
    NoReinvestmentNoiseBelief,
    NoReinvestmentNoiseReturn,
    NoReinvestmentNoiseResultsP1,
    NoReinvestmentNoiseResultsP2,
    # Cell 3: reinvestment, no noise
    ReinvestmentNoNoiseTransfer,
    ReinvestmentNoNoiseBelief,
    ReinvestmentNoNoiseReturn,
    ReinvestmentNoNoiseResultsP1,
    ReinvestmentNoNoiseResultsP2,
    # Cell 4: reinvestment, noise
    ReinvestmentNoiseTransfer,
    ReinvestmentNoiseBelief,
    ReinvestmentNoiseReturn,
    ReinvestmentNoiseResultsP1,
    ReinvestmentNoiseResultsP2,
    # Final survey
    SurveyIntro,
    Survey,
    FinalResults,
]
