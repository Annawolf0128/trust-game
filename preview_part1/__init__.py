from otree.api import *


doc = """Preview-only click-through for the one-shot Part 1 strategy method."""


class C(BaseConstants):
    NAME_IN_URL = "preview_part1"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    ENDOWMENT = cu(10)
    MULTIPLIER = 3
    STAGE1_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
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
        label="If Player 1 sends 4 points, how many points does Player 2 receive?",
        min=0,
        blank=True,
    )
    part1_quiz_p2_payoff = models.IntegerField(
        label="3. How many points does Player 2 earn?",
        min=0,
        blank=True,
    )
    part1_proposer_offer = models.CurrencyField(
        label="Suppose you are Player 1. How many points will you send?",
        choices=[[i, str(i)] for i in range(0, 11)],
        widget=widgets.RadioSelectHorizontal,
        blank=True,
    )
    part1_return_1 = models.CurrencyField(label="Return if Player 1 sends 1 point", choices=[[i, str(i)] for i in range(4)], widget=widgets.RadioSelectHorizontal, blank=True)
    part1_return_2 = models.CurrencyField(label="Return if Player 1 sends 2 points", choices=[[i, str(i)] for i in range(7)], widget=widgets.RadioSelectHorizontal, blank=True)
    part1_return_3 = models.CurrencyField(label="Return if Player 1 sends 3 points", choices=[[i, str(i)] for i in range(10)], widget=widgets.RadioSelectHorizontal, blank=True)
    part1_return_4 = models.CurrencyField(label="Return if Player 1 sends 4 points", choices=[[i, str(i)] for i in range(13)], widget=widgets.RadioSelectHorizontal, blank=True)
    part1_return_5 = models.CurrencyField(label="Return if Player 1 sends 5 points", choices=[[i, str(i)] for i in range(16)], widget=widgets.RadioSelectHorizontal, blank=True)
    part1_return_6 = models.CurrencyField(label="Return if Player 1 sends 6 points", choices=[[i, str(i)] for i in range(19)], widget=widgets.RadioSelectHorizontal, blank=True)
    part1_return_7 = models.CurrencyField(label="Return if Player 1 sends 7 points", choices=[[i, str(i)] for i in range(22)], widget=widgets.RadioSelectHorizontal, blank=True)
    part1_return_8 = models.CurrencyField(label="Return if Player 1 sends 8 points", choices=[[i, str(i)] for i in range(25)], widget=widgets.RadioSelectHorizontal, blank=True)
    part1_return_9 = models.CurrencyField(label="Return if Player 1 sends 9 points", choices=[[i, str(i)] for i in range(28)], widget=widgets.RadioSelectHorizontal, blank=True)
    part1_return_10 = models.CurrencyField(label="Return if Player 1 sends 10 points", choices=[[i, str(i)] for i in range(31)], widget=widgets.RadioSelectHorizontal, blank=True)


class Introduction(Page):
    template_name = "trust_reinvestment/Introduction.html"

    @staticmethod
    def vars_for_template(player: Player):
        show_up_fee = float(player.session.config.get("participation_fee", 10.00))
        return dict(
            show_name_form=False,
            part1_rate="¥0.10",
            part2_rate="¥0.10",
            show_up_fee=f"¥{show_up_fee:.2f}",
        )


class Part1Instructions(Page):
    template_name = "trust_reinvestment/Part1Instructions.html"


class Part1RulesIntro(Page):
    template_name = "trust_reinvestment/Part1RulesIntro.html"


class Part1Quiz(Page):
    template_name = "trust_reinvestment/Part1Quiz.html"
    form_model = "player"
    form_fields = [
        "part1_quiz_p1_multiplied",
        "part1_quiz_p1_payoff",
        "part1_quiz_p2_payoff",
    ]

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
    template_name = "trust_reinvestment/Part1QuestionsIntro.html"


class Part1ProposerDecision(Page):
    template_name = "trust_reinvestment/Part1ProposerDecision.html"
    form_model = "player"
    form_fields = ["part1_proposer_offer"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(endowment=C.ENDOWMENT, multiplier=C.MULTIPLIER)


class Part1ResponderStrategy(Page):
    template_name = "trust_reinvestment/Part1ResponderStrategy.html"
    form_model = "player"
    form_fields = [f"part1_return_{offer}" for offer in range(1, 11)]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(endowment=C.ENDOWMENT, multiplier=C.MULTIPLIER)


def show_result_for_role(player: Player, role: int):
    """Show both results in the standalone preview, one in a role TEST."""
    configured_role = player.session.config.get("preview_role")
    return configured_role is None or int(configured_role) == role


class Part1ResultsProposer(Page):
    template_name = "trust_reinvestment/Part1Results.html"

    @staticmethod
    def is_displayed(player: Player):
        return show_result_for_role(player, 1)

    @staticmethod
    def vars_for_template(player: Player):
        realized_offer = player.part1_proposer_offer
        if realized_offer is None:
            realized_offer = cu(4)
        # A fixed simulated partner response keeps the one-player TEST moving,
        # while never exceeding the amount that Player 2 received.
        realized_return = min(cu(5), realized_offer * C.MULTIPLIER)
        proposer_earnings = C.ENDOWMENT - realized_offer + realized_return
        responder_earnings = realized_offer * C.MULTIPLIER - realized_return
        player.participant.vars["part1_account"] = float(proposer_earnings)
        return dict(
            payoff_role="proposer",
            payoff_role_display="Player 1",
            partner_decision_label="Your partner returned",
            partner_decision=realized_return,
            realized_offer=realized_offer,
            received_amount=realized_offer * C.MULTIPLIER,
            realized_return=realized_return,
            part1_earnings=proposer_earnings,
            proposer_earnings=proposer_earnings,
            responder_earnings=responder_earnings,
        )


class Part1ResultsResponder(Page):
    template_name = "trust_reinvestment/Part1Results.html"

    @staticmethod
    def is_displayed(player: Player):
        return show_result_for_role(player, 2)

    @staticmethod
    def vars_for_template(player: Player):
        realized_offer = cu(4)
        realized_return = player.part1_return_4
        if realized_return is None:
            realized_return = cu(5)
        proposer_earnings = C.ENDOWMENT - realized_offer + realized_return
        responder_earnings = realized_offer * C.MULTIPLIER - realized_return
        player.participant.vars["part1_account"] = float(responder_earnings)
        return dict(
            payoff_role="responder",
            payoff_role_display="Player 2",
            partner_decision_label="Your partner sent",
            partner_decision=realized_offer,
            realized_offer=realized_offer,
            received_amount=realized_offer * C.MULTIPLIER,
            realized_return=realized_return,
            part1_earnings=responder_earnings,
            proposer_earnings=proposer_earnings,
            responder_earnings=responder_earnings,
        )


page_sequence = [
    Introduction,
    Part1RulesIntro,
    Part1Instructions,
    Part1Quiz,
    Part1QuestionsIntro,
    Part1ProposerDecision,
    Part1ResponderStrategy,
    Part1ResultsProposer,
    Part1ResultsResponder,
]
