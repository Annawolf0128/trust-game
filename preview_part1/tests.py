from otree.api import Bot, Submission
from . import (
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
)


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction
        yield RoleAssignment
        yield Part1InstructionsP1
        yield Part1InstructionsP2
        yield Submission(
            Part1QuizP1,
            dict(part1_quiz_p1_multiplied=12, part1_quiz_p1_payoff=11),
            check_html=False,
        )
        yield Submission(
            Part1QuizP2,
            dict(part1_quiz_p2_received=12, part1_quiz_p2_payoff=7),
            check_html=False,
        )
        yield Submission(Stage1Transfer, dict(transfer=4), check_html=False)
        yield Submission(Stage1Return, dict(intended_return=5), check_html=False)
        yield Stage1ResultsP1
        yield Stage1ResultsP2
