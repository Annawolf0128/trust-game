from otree.api import *
from types import SimpleNamespace


doc = """
Preview-only app for Part 1. It lets you click straight through every Part 1
page a participant sees -- the overall introduction, role assignment, the Part 1
rules for both roles, both comprehension quizzes, the send/return decision
screens, and the round-results page for both roles -- without being matched with
a partner or waiting. It reuses the real templates from trust_reinvestment, so
what you see here is exactly what participants see. Decision and results screens
are filled with placeholder numbers (player 1 sends 4, player 2 returns 5).
"""


class C(BaseConstants):
    NAME_IN_URL = "preview_part1"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # Mirrors trust_reinvestment so the shared templates render the same numbers.
    ENDOWMENT = cu(10)
    MULTIPLIER = 3
    STAGE1_ROUNDS = 3

    # Placeholder scenario shown on the decision/results screens.
    DEMO_TRANSFER = cu(4)
    DEMO_RETURN = cu(5)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Quiz fields, identical to trust_reinvestment so the quiz checks match.
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

    # Decision fields, so the send/return templates render their form widgets.
    transfer = models.CurrencyField(label="Amount to send", min=0, blank=True)
    intended_return = models.CurrencyField(label="Amount to return", min=0, blank=True)

    # Used only to feed the results template.
    realized_return = models.CurrencyField(initial=0)
    round_payoff = models.CurrencyField(initial=0)


# Placeholder payoffs for the demo scenario (send 4, multiplied to 12, return 5).
_P1_PAYOFF = C.ENDOWMENT - C.DEMO_TRANSFER + C.DEMO_RETURN          # 10 - 4 + 5 = 11
_P2_PAYOFF = C.DEMO_TRANSFER * C.MULTIPLIER - C.DEMO_RETURN          # 12 - 5 = 7
_MULTIPLIED = C.DEMO_TRANSFER * C.MULTIPLIER                         # 12


class Introduction(Page):
    template_name = "trust_reinvestment/Introduction.html"

    @staticmethod
    def vars_for_template(player: Player):
        return dict(payment_rate="$0.10")


class RoleAssignment(Page):
    template_name = "trust_reinvestment/RoleAssignment.html"

    @staticmethod
    def vars_for_template(player: Player):
        return dict(role_number=1)


class Part1InstructionsP1(Page):
    template_name = "trust_reinvestment/Part1InstructionsP1.html"


class Part1InstructionsP2(Page):
    template_name = "trust_reinvestment/Part1InstructionsP2.html"


class Part1QuizP1(Page):
    template_name = "trust_reinvestment/Part1QuizP1.html"
    form_model = "player"
    form_fields = ["part1_quiz_p1_multiplied", "part1_quiz_p1_payoff"]

    @staticmethod
    def error_message(player: Player, values):
        errors = {}
        if values["part1_quiz_p1_multiplied"] != 12:
            errors["part1_quiz_p1_multiplied"] = "Please check the multiplication rule."
        if values["part1_quiz_p1_payoff"] != 11:
            errors["part1_quiz_p1_payoff"] = "Please check how your payoff is calculated."
        return errors


class Part1QuizP2(Page):
    template_name = "trust_reinvestment/Part1QuizP2.html"
    form_model = "player"
    form_fields = ["part1_quiz_p2_received", "part1_quiz_p2_payoff"]

    @staticmethod
    def error_message(player: Player, values):
        errors = {}
        if values["part1_quiz_p2_received"] != 12:
            errors["part1_quiz_p2_received"] = "Please check the multiplication rule."
        if values["part1_quiz_p2_payoff"] != 7:
            errors["part1_quiz_p2_payoff"] = "Please check how your payoff is calculated."
        return errors


class Stage1Transfer(Page):
    template_name = "trust_reinvestment/Stage1Transfer.html"
    form_model = "player"
    form_fields = ["transfer"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            endowment=C.ENDOWMENT,
            multiplier=C.MULTIPLIER,
            stage1_round=1,
            stage1_rounds=C.STAGE1_ROUNDS,
        )

    @staticmethod
    def error_message(player: Player, values):
        if values["transfer"] > C.ENDOWMENT:
            return "Transfer cannot exceed your current-period endowment."


class Stage1Return(Page):
    template_name = "trust_reinvestment/Stage1Return.html"
    form_model = "player"
    form_fields = ["intended_return"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            transfer=C.DEMO_TRANSFER,
            multiplied_amount=_MULTIPLIED,
            max_return=_MULTIPLIED,
            multiplier=C.MULTIPLIER,
            stage1_round=1,
            stage1_rounds=C.STAGE1_ROUNDS,
        )

    @staticmethod
    def error_message(player: Player, values):
        if values["intended_return"] > _MULTIPLIED:
            return "Return cannot exceed the multiplied amount you received."


class Stage1ResultsP1(Page):
    template_name = "trust_reinvestment/Stage1Results.html"

    @staticmethod
    def vars_for_template(player: Player):
        # Mutate the single preview player so the template's player.* fields render.
        player.transfer = C.DEMO_TRANSFER
        player.realized_return = C.DEMO_RETURN
        player.round_payoff = _P1_PAYOFF
        partner = SimpleNamespace(round_payoff=_P2_PAYOFF, transfer=C.DEMO_TRANSFER)
        return dict(
            view_as_p1=True,
            partner=partner,
            account_balance=_P1_PAYOFF,
        )


class Stage1ResultsP2(Page):
    template_name = "trust_reinvestment/Stage1Results.html"

    @staticmethod
    def vars_for_template(player: Player):
        player.intended_return = C.DEMO_RETURN
        player.round_payoff = _P2_PAYOFF
        partner = SimpleNamespace(round_payoff=_P1_PAYOFF, transfer=C.DEMO_TRANSFER)
        return dict(
            view_as_p1=False,
            partner=partner,
            account_balance=_P2_PAYOFF,
        )


page_sequence = [
    Introduction,
    RoleAssignment,
    Part1InstructionsP1,
    Part1InstructionsP2,
    Part1QuizP1,
    Part1QuizP2,
    Stage1Transfer,
    Stage1Return,
    Stage1ResultsP1,
    Stage1ResultsP2,
]
