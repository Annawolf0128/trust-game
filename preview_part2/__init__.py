from otree.api import *
from types import SimpleNamespace


doc = """
Preview-only app for Part 2. Each session previews a single 2x2 cell (set via
the session config's `preview_treatment` and `preview_noise`). For that cell it
walks both roles through the instruction page, the send screen, the return
screen, and the round-results page (both roles), then the final survey -- with
no Part 1 and no partner. It reuses the real templates from trust_reinvestment,
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
    STAGE2_MIN_ROUNDS = 5
    STOPPING_PROBABILITY = 0.15

    NO_REINVESTMENT = "no_reinvestment"
    REINVESTMENT = "reinvestment"

    # Placeholder scenario shown on the decision/results screens.
    SAFE_ACCOUNT = cu(8)
    DEMO_TRANSFER = cu(4)
    DEMO_REINVEST = cu(2)
    DEMO_RETURN = cu(5)
    NOISE_FACTOR = 1.5


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

    # Decision fields, identical to trust_reinvestment so the send/return
    # screens render their form widgets and the results screen has data.
    transfer = models.CurrencyField(label="Amount to send", min=0, blank=True)
    reinvestment = models.CurrencyField(
        label="Amount from Part 2 accumulated account to use this round",
        min=0,
        blank=True,
    )
    intended_return = models.CurrencyField(label="Amount to return", min=0, blank=True)
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
    signal_attribution = models.IntegerField(
        label="To what extent did the amount that reached you reflect player 2's chosen return rather than the computer adjustment? (0 - entirely the computer adjustment, 10 - entirely player 2's choice)",
        choices=[[i, str(i)] for i in range(0, 11)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    received_amount = models.CurrencyField(initial=0)
    noise_factor = models.FloatField(blank=True)
    round_payoff = models.CurrencyField(initial=0)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _instruction_vars(player: Player):
    stopping_probability = int(C.STOPPING_PROBABILITY * 100)
    return dict(
        min_rounds=C.STAGE2_MIN_ROUNDS,
        stopping_probability=stopping_probability,
        continue_probability=100 - stopping_probability,
    )


def _treatment(is_reinvestment):
    return C.REINVESTMENT if is_reinvestment else C.NO_REINVESTMENT


def _in_cell(player: Player, is_reinvestment, has_noise):
    """Show this page only if it belongs to the cell set in the session config.

    If the config does not pin a cell, show every cell in sequence.
    """
    cfg = player.session.config
    want_treatment = cfg.get("preview_treatment")
    want_noise = cfg.get("preview_noise")
    if not want_treatment or not want_noise:
        return True
    noise_str = "noise" if has_noise else "no_noise"
    return want_treatment == _treatment(is_reinvestment) and want_noise == noise_str


def _cell_numbers(is_reinvestment, has_noise):
    reinvest = C.DEMO_REINVEST if is_reinvestment else cu(0)
    exposure = C.DEMO_TRANSFER + reinvest
    # Player 2 always receives the full multiplied amount; the noise applies to
    # the return on its way back to player 1.
    received = exposure * C.MULTIPLIER
    factor = C.NOISE_FACTOR if has_noise else 1.0
    realized_return = C.DEMO_RETURN * factor
    p1_payoff = C.ENDOWMENT - C.DEMO_TRANSFER + realized_return
    p2_payoff = received - C.DEMO_RETURN
    return dict(
        reinvest=reinvest,
        received=received,
        factor=factor,
        realized_return=realized_return,
        p1_payoff=p1_payoff,
        p2_payoff=p2_payoff,
        p1_account=C.SAFE_ACCOUNT - reinvest + p1_payoff,
        p2_account=C.SAFE_ACCOUNT + p2_payoff,
    )


def _transfer_fields(is_reinvestment):
    if is_reinvestment:
        return ["reinvestment", "transfer", "belief_partner_intended_return"]
    return ["transfer", "belief_partner_intended_return"]


def _transfer_vars(is_reinvestment, has_noise):
    return dict(
        treatment=_treatment(is_reinvestment),
        endowment=C.ENDOWMENT,
        safe_account=C.SAFE_ACCOUNT,
        is_reinvestment=is_reinvestment,
        has_noise=has_noise,
        stage2_round=1,
    )


def _return_vars(is_reinvestment, has_noise):
    n = _cell_numbers(is_reinvestment, has_noise)
    return dict(
        received_amount=n["received"],
        max_return=n["received"],
        multiplier=C.MULTIPLIER,
        has_noise=has_noise,
        stage2_round=1,
    )


def _results_p1_vars(player, is_reinvestment, has_noise):
    n = _cell_numbers(is_reinvestment, has_noise)
    player.transfer = C.DEMO_TRANSFER
    player.reinvestment = n["reinvest"]
    player.noise_factor = n["factor"]
    player.round_payoff = n["p1_payoff"]
    partner = SimpleNamespace(intended_return=C.DEMO_RETURN)
    return dict(
        view_as_p1=True,
        treatment=_treatment(is_reinvestment),
        has_noise=has_noise,
        received_amount=n["received"],
        realized_return=n["realized_return"],
        should_continue=True,
        partner=partner,
        account_balance=n["p1_account"],
    )


def _results_p2_vars(player, is_reinvestment, has_noise):
    n = _cell_numbers(is_reinvestment, has_noise)
    player.received_amount = n["received"]
    player.intended_return = C.DEMO_RETURN
    player.round_payoff = n["p2_payoff"]
    return dict(
        view_as_p1=False,
        treatment=_treatment(is_reinvestment),
        has_noise=has_noise,
        received_amount=n["received"],
        should_continue=True,
        account_balance=n["p2_account"],
    )


def _results_fields(has_noise):
    return ["signal_attribution"] if has_noise else []


# ---------------------------------------------------------------------------
# Base page classes (shared template wiring)
# ---------------------------------------------------------------------------


class _Instruction(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return _instruction_vars(player)


class _Transfer(Page):
    template_name = "trust_reinvestment/Stage2Transfer.html"
    form_model = "player"


class _Return(Page):
    template_name = "trust_reinvestment/Stage2Return.html"
    form_model = "player"
    form_fields = ["intended_return", "belief_partner_transfer"]


class _Results(Page):
    template_name = "trust_reinvestment/Stage2Results.html"
    form_model = "player"


# ---------------------------------------------------------------------------
# Cell 1: no reinvestment, no noise
# ---------------------------------------------------------------------------


class NoReinvestmentNoNoiseP1(_Instruction):
    template_name = "trust_reinvestment/Stage2InstructionsNoReinvestmentNoNoiseP1.html"

    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, False)


class NoReinvestmentNoNoiseP2(_Instruction):
    template_name = "trust_reinvestment/Stage2InstructionsNoReinvestmentNoNoiseP2.html"

    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, False)


class NoReinvestmentNoNoiseTransfer(_Transfer):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, False)

    @staticmethod
    def get_form_fields(player: Player):
        return _transfer_fields(False)

    @staticmethod
    def vars_for_template(player: Player):
        return _transfer_vars(False, False)


class NoReinvestmentNoNoiseReturn(_Return):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, False)

    @staticmethod
    def vars_for_template(player: Player):
        return _return_vars(False, False)


class NoReinvestmentNoNoiseResultsP1(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, False)

    @staticmethod
    def get_form_fields(player: Player):
        return _results_fields(False)

    @staticmethod
    def vars_for_template(player: Player):
        return _results_p1_vars(player, False, False)


class NoReinvestmentNoNoiseResultsP2(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, False)

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
    template_name = "trust_reinvestment/Stage2InstructionsNoReinvestmentNoiseP1.html"

    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, True)


class NoReinvestmentNoiseP2(_Instruction):
    template_name = "trust_reinvestment/Stage2InstructionsNoReinvestmentNoiseP2.html"

    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, True)


class NoReinvestmentNoiseTransfer(_Transfer):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, True)

    @staticmethod
    def get_form_fields(player: Player):
        return _transfer_fields(False)

    @staticmethod
    def vars_for_template(player: Player):
        return _transfer_vars(False, True)


class NoReinvestmentNoiseReturn(_Return):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, True)

    @staticmethod
    def vars_for_template(player: Player):
        return _return_vars(False, True)


class NoReinvestmentNoiseResultsP1(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, True)

    @staticmethod
    def get_form_fields(player: Player):
        return _results_fields(True)

    @staticmethod
    def vars_for_template(player: Player):
        return _results_p1_vars(player, False, True)


class NoReinvestmentNoiseResultsP2(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, False, True)

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
    template_name = "trust_reinvestment/Stage2InstructionsReinvestmentNoNoiseP1.html"

    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, False)


class ReinvestmentNoNoiseP2(_Instruction):
    template_name = "trust_reinvestment/Stage2InstructionsReinvestmentNoNoiseP2.html"

    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, False)


class ReinvestmentNoNoiseTransfer(_Transfer):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, False)

    @staticmethod
    def get_form_fields(player: Player):
        return _transfer_fields(True)

    @staticmethod
    def vars_for_template(player: Player):
        return _transfer_vars(True, False)


class ReinvestmentNoNoiseReturn(_Return):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, False)

    @staticmethod
    def vars_for_template(player: Player):
        return _return_vars(True, False)


class ReinvestmentNoNoiseResultsP1(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, False)

    @staticmethod
    def get_form_fields(player: Player):
        return _results_fields(False)

    @staticmethod
    def vars_for_template(player: Player):
        return _results_p1_vars(player, True, False)


class ReinvestmentNoNoiseResultsP2(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, False)

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
    template_name = "trust_reinvestment/Stage2InstructionsReinvestmentNoiseP1.html"

    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, True)


class ReinvestmentNoiseP2(_Instruction):
    template_name = "trust_reinvestment/Stage2InstructionsReinvestmentNoiseP2.html"

    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, True)


class ReinvestmentNoiseTransfer(_Transfer):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, True)

    @staticmethod
    def get_form_fields(player: Player):
        return _transfer_fields(True)

    @staticmethod
    def vars_for_template(player: Player):
        return _transfer_vars(True, True)


class ReinvestmentNoiseReturn(_Return):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, True)

    @staticmethod
    def vars_for_template(player: Player):
        return _return_vars(True, True)


class ReinvestmentNoiseResultsP1(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, True)

    @staticmethod
    def get_form_fields(player: Player):
        return _results_fields(True)

    @staticmethod
    def vars_for_template(player: Player):
        return _results_p1_vars(player, True, True)


class ReinvestmentNoiseResultsP2(_Results):
    @staticmethod
    def is_displayed(player: Player):
        return _in_cell(player, True, True)

    @staticmethod
    def get_form_fields(player: Player):
        return []

    @staticmethod
    def vars_for_template(player: Player):
        return _results_p2_vars(player, True, True)


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


page_sequence = [
    # Cell 1: no reinvestment, no noise
    NoReinvestmentNoNoiseP1,
    NoReinvestmentNoNoiseP2,
    NoReinvestmentNoNoiseTransfer,
    NoReinvestmentNoNoiseReturn,
    NoReinvestmentNoNoiseResultsP1,
    NoReinvestmentNoNoiseResultsP2,
    # Cell 2: no reinvestment, noise
    NoReinvestmentNoiseP1,
    NoReinvestmentNoiseP2,
    NoReinvestmentNoiseTransfer,
    NoReinvestmentNoiseReturn,
    NoReinvestmentNoiseResultsP1,
    NoReinvestmentNoiseResultsP2,
    # Cell 3: reinvestment, no noise
    ReinvestmentNoNoiseP1,
    ReinvestmentNoNoiseP2,
    ReinvestmentNoNoiseTransfer,
    ReinvestmentNoNoiseReturn,
    ReinvestmentNoNoiseResultsP1,
    ReinvestmentNoNoiseResultsP2,
    # Cell 4: reinvestment, noise
    ReinvestmentNoiseP1,
    ReinvestmentNoiseP2,
    ReinvestmentNoiseTransfer,
    ReinvestmentNoiseReturn,
    ReinvestmentNoiseResultsP1,
    ReinvestmentNoiseResultsP2,
    # Final survey
    Survey,
]
