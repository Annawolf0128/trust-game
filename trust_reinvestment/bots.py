from otree.api import Bot, Submission
from . import (
    active_in_stage2,
    C,
    FinalResults,
    Introduction,
    Part1InstructionsP1,
    Part1InstructionsP2,
    Part1QuizP1,
    Part1QuizP2,
    RoleAssignment,
    Stage1Results,
    Stage1Return,
    Stage1Transfer,
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
    Stage2Results,
    Stage2Return,
    Stage2Transfer,
    Survey,
)


def stage2_instruction_page(player):
    pages = {
        (C.NO_REINVESTMENT, C.NO_NOISE, 1): Stage2InstructionsNoReinvestmentNoNoiseP1,
        (C.NO_REINVESTMENT, C.NO_NOISE, 2): Stage2InstructionsNoReinvestmentNoNoiseP2,
        (C.NO_REINVESTMENT, C.NOISE, 1): Stage2InstructionsNoReinvestmentNoiseP1,
        (C.NO_REINVESTMENT, C.NOISE, 2): Stage2InstructionsNoReinvestmentNoiseP2,
        (C.REINVESTMENT, C.NO_NOISE, 1): Stage2InstructionsReinvestmentNoNoiseP1,
        (C.REINVESTMENT, C.NO_NOISE, 2): Stage2InstructionsReinvestmentNoNoiseP2,
        (C.REINVESTMENT, C.NOISE, 1): Stage2InstructionsReinvestmentNoiseP1,
        (C.REINVESTMENT, C.NOISE, 2): Stage2InstructionsReinvestmentNoiseP2,
    }
    return pages[(player.group.treatment, player.group.noise_treatment, player.id_in_group)]


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            yield Introduction
            yield RoleAssignment
            if self.player.id_in_group == 1:
                yield Part1InstructionsP1
                yield Part1QuizP1, dict(
                    part1_quiz_p1_multiplied=12,
                    part1_quiz_p1_payoff=11,
                )
            else:
                yield Part1InstructionsP2
                yield Part1QuizP2, dict(
                    part1_quiz_p2_received=12,
                    part1_quiz_p2_payoff=7,
                )

        if self.round_number <= C.STAGE1_ROUNDS:
            if self.player.id_in_group == 1:
                yield Stage1Transfer, dict(transfer=5)
            else:
                yield Stage1Return, dict(intended_return=7)
            yield Stage1Results
            return

        if self.round_number == C.STAGE1_ROUNDS + 1:
            realized_return_answer = 2 if self.group.noise_treatment == C.NOISE else 4
            if self.player.id_in_group == 1:
                yield stage2_instruction_page(self.player)
                yield Stage2QuizP1, dict(
                    part2_quiz_p1_account=1 if self.group.treatment == C.REINVESTMENT else 0,
                    part2_quiz_p1_realized_return=realized_return_answer,
                )
            else:
                yield stage2_instruction_page(self.player)
                yield Stage2QuizP2, dict(
                    part2_quiz_p2_account=1 if self.group.treatment == C.REINVESTMENT else 0,
                    part2_quiz_p2_realized_return=realized_return_answer,
                )

        pair_active = active_in_stage2(self.group)
        if pair_active:
            if self.player.id_in_group == 1:
                form = dict(transfer=4)
                if self.group.treatment == C.REINVESTMENT:
                    form["reinvestment"] = 0
                form["belief_partner_intended_return"] = 6
                yield Stage2Transfer, form
            else:
                yield Stage2Return, dict(
                    intended_return=6,
                    belief_partner_transfer=4,
                )
            if self.group.noise_treatment == C.NOISE and self.player.id_in_group == 1:
                yield Stage2Results, dict(signal_attribution=5)
            else:
                yield Stage2Results

        if self.round_number == C.NUM_ROUNDS:
            survey_form = dict(
                gender="male",
                age=25,
                risk_preference=5,
                trust_most_people=6,
                trust_willingness=5,
            )
            yield Survey, survey_form
            yield Submission(FinalResults, check_html=False)
