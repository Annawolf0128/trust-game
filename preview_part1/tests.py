from otree.api import Bot, Submission, SubmissionMustFail
from . import (
    Introduction,
    Part1RulesIntro,
    Part1Instructions,
    Part1Quiz,
    Part1QuestionsIntro,
    Part1ProposerDecision,
    Part1ResponderStrategy,
    Part1ResultsProposer,
    Part1ResultsResponder,
)


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction
        yield Part1RulesIntro
        yield Part1Instructions
        # Verify that the understanding test is a hard gate. One incorrect
        # payoff answer must keep the participant on this page.
        yield SubmissionMustFail(
            Part1Quiz,
            dict(
                part1_quiz_p1_multiplied=12,
                part1_quiz_p1_payoff=10,
                part1_quiz_p2_payoff=7,
            ),
            check_html=False,
            error_fields=["part1_quiz_p1_payoff"],
        )
        yield Submission(
            Part1Quiz,
            dict(
                part1_quiz_p1_multiplied=12,
                part1_quiz_p1_payoff=11,
                part1_quiz_p2_payoff=7,
            ),
            check_html=False,
        )
        yield Part1QuestionsIntro
        yield Submission(
            Part1ProposerDecision,
            dict(part1_proposer_offer=4),
            check_html=False,
        )
        yield Submission(
            Part1ResponderStrategy,
            dict(
                part1_return_1=1,
                part1_return_2=2,
                part1_return_3=3,
                part1_return_4=5,
                part1_return_5=6,
                part1_return_6=7,
                part1_return_7=8,
                part1_return_8=9,
                part1_return_9=10,
                part1_return_10=11,
            ),
            check_html=False,
        )
        configured_role = self.session.config.get("preview_role")
        if configured_role in (None, 1, "1"):
            yield Part1ResultsProposer
        if configured_role in (None, 2, "2"):
            yield Part1ResultsResponder
