from otree.api import Bot, Submission, cu
from . import (
    active_in_stage2,
    C,
    FinalResults,
    Introduction,
    Part1Instructions,
    Part1QuestionsIntro,
    Part1RulesIntro,
    Part1ProposerDecision,
    Part1Quiz,
    Part1ResponderStrategy,
    Part1Results,
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
    Stage2RoundIntro,
    Stage2Results,
    Stage2Return,
    Stage2Transfer,
    Stage2TransferBelief,
    SurveyIntro,
    Survey,
    participant_part2_account,
    uses_account_in_part2,
)


def ai_strategy_enabled(player):
    return player.session.config.get("ai_agent_strategy") == "trust_cycle"


def part1_bot_offer(player):
    return (player.id_in_subsession - 1) % 11


def part1_bot_returns(player):
    # Alternate relatively low and high reciprocity schedules so automated
    # sessions exercise a broad range of Part 1 pre-treatment responses.
    fraction = 0.2 if player.id_in_subsession % 2 else 0.5
    return {
        f"part1_return_{offer}": round(C.MULTIPLIER * offer * fraction)
        for offer in range(1, 11)
    }


def stage2_ai_amount_sent(player):
    safe_account = participant_part2_account(player)
    max_send = C.ENDOWMENT + safe_account if uses_account_in_part2(player) else C.ENDOWMENT
    stage2_round = player.round_number - C.STAGE1_ROUNDS
    if stage2_round == 1:
        desired = 8 if uses_account_in_part2(player) else 7
    else:
        previous = player.in_round(player.round_number - 1)
        previous_sent = float(previous.amount_sent or 0)
        previous_realized = float(previous.realized_return or 0)
        # If A got back at least as much as was risked, raise trust. If not,
        # reduce exposure but avoid collapsing to zero after one noisy signal.
        if previous_realized >= previous_sent:
            desired = previous_sent + 2
        elif previous_realized >= 0.6 * previous_sent:
            desired = previous_sent
        else:
            desired = max(3, previous_sent - 2)
        if uses_account_in_part2(player) and float(safe_account) > 15:
            desired += min(4, float(safe_account) * 0.20)
    return cu(min(float(max_send), round(desired)))


def stage2_ai_return(player):
    received = player.received_amount
    # Strong reciprocity: returning half of the received amount keeps B ahead
    # while usually letting A recover the amount risked, sustaining the cycle.
    return min(received, cu(round(float(received) * 0.50)))


def stage2_ai_attribution(player):
    if player.round_number <= C.STAGE1_ROUNDS + 1:
        return 5
    previous = player.in_round(player.round_number - 1)
    if float(previous.realized_return or 0) < float(previous.amount_sent or 0):
        return 4 if player.group.noise_treatment == C.NOISE else 7
    return 7


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
        use_ai = ai_strategy_enabled(self.player)
        if self.round_number == 1:
            yield Introduction, dict(student_name=f"bot-{self.player.id_in_group}")
            yield Part1RulesIntro
            yield Part1Instructions
            yield Part1Quiz, dict(
                part1_quiz_p1_multiplied=12,
                part1_quiz_p1_payoff=11,
                part1_quiz_p2_payoff=7,
            )
            yield Part1QuestionsIntro
            yield Part1ProposerDecision, dict(
                part1_proposer_offer=part1_bot_offer(self.player),
            )
            yield Part1ResponderStrategy, part1_bot_returns(self.player)
            yield Part1Results
            return

        if self.round_number == C.STAGE1_ROUNDS + 1:
            yield Part2RoleAssignment
            realized_return_answer = -1 if self.group.noise_treatment == C.NOISE else 6
            account_answer = 1 if self.group.treatment == C.REINVESTMENT else 0
            maxsend_answer = (
                "endowment_plus_account"
                if self.group.treatment == C.REINVESTMENT
                else "endowment_only"
            )
            if self.player.id_in_group == 1:
                yield stage2_instruction_page(self.player)
                yield Stage2QuizP1, dict(
                    part2_quiz_p1_account=account_answer,
                    part2_quiz_p1_multiplier=12,
                    part2_quiz_p1_realized_return=realized_return_answer,
                    part2_quiz_p1_maxsend=maxsend_answer,
                )
            else:
                yield stage2_instruction_page(self.player)
                yield Stage2QuizP2, dict(
                    part2_quiz_p2_account=account_answer,
                    part2_quiz_p2_multiplier=12,
                    part2_quiz_p2_realized_return=realized_return_answer,
                    part2_quiz_p2_maxsend=maxsend_answer,
                )

        pair_active = active_in_stage2(self.group)
        if pair_active:
            yield Stage2RoundIntro
            if self.player.id_in_group == 1:
                amount_sent = stage2_ai_amount_sent(self.player) if use_ai else 4
                yield Stage2Transfer, dict(
                    amount_sent=amount_sent,
                    belief_partner_intended_return=round(float(amount_sent) * C.MULTIPLIER * 0.5),
                )
            else:
                expected_transfer = (
                    stage2_ai_amount_sent(self.player.group.get_player_by_id(1))
                    if use_ai else 4
                )
                yield Stage2TransferBelief, dict(belief_partner_transfer=expected_transfer)
                yield Stage2Return, dict(
                    intended_return=stage2_ai_return(self.player) if use_ai else 6
                )
            if self.group.noise_treatment == C.NOISE and self.player.id_in_group == 1:
                player_b = self.group.get_player_by_id(2)
                yield Stage2Results, dict(
                    belief_partner_return_post=round(min(float(self.player.realized_return), float(player_b.received_amount))),
                )
            else:
                yield Stage2Results

        if self.round_number == C.NUM_ROUNDS:
            yield SurveyIntro
            survey_form = dict(
                gender="male",
                age=25,
                risk_preference=5,
                trust_most_people=6,
                trust_willingness=5,
                self_trustworthy=5,
            )
            if self.player.id_in_group == 1:
                survey_form["partner_trustworthy"] = 4
            else:
                survey_form["partner_trusting"] = 4
            yield Survey, survey_form
            yield Submission(FinalResults, check_html=False)
