from otree.api import Bot, Submission, cu
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
    Stage1TransferBelief,
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
    Stage2TransferBelief,
    Survey,
    participant_part2_account,
    uses_account_in_part2,
)


def ai_strategy_enabled(player):
    return player.session.config.get("ai_agent_strategy") == "trust_cycle"


def stage1_ai_transfer(player):
    # Start with a clearly trusting but not maximal transfer, then gently
    # increase. This creates positive relationship history before Stage 2.
    return min(8, 6 + player.round_number)


def stage1_ai_return(player):
    player_a = player.group.get_player_by_id(1)
    received = player_a.transfer * C.MULTIPLIER
    # Return roughly 60% of what B received, capped by the available amount.
    return min(received, cu(round(float(received) * 0.60)))


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
                transfer = stage1_ai_transfer(self.player) if use_ai else 5
                yield Stage1Transfer, dict(
                    transfer=transfer,
                    belief_partner_intended_return=round(transfer * C.MULTIPLIER * 0.6) if use_ai else 6,
                )
            else:
                yield Stage1TransferBelief, dict(
                    belief_partner_transfer=stage1_ai_transfer(self.player) if use_ai else 5
                )
                yield Stage1Return, dict(
                    intended_return=stage1_ai_return(self.player) if use_ai else 7
                )
            yield Stage1Results
            return

        if self.round_number == C.STAGE1_ROUNDS + 1:
            realized_return_answer = 2 if self.group.noise_treatment == C.NOISE else 4
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
                    signal_attribution=stage2_ai_attribution(self.player) if use_ai else 5,
                )
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
