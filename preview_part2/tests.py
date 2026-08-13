from otree.api import Bot, Submission, SubmissionMustFail
from . import (
    Part2Transition,
    Part2QuizP1,
    Part2QuizP2,
    Part2RoundIntro,
    FinalResults,
    NoReinvestmentNoNoiseP1,
    NoReinvestmentNoNoiseTransfer,
    NoReinvestmentNoNoiseBelief,
    NoReinvestmentNoNoiseReturn,
    NoReinvestmentNoNoiseResultsP1,
    NoReinvestmentNoNoiseResultsP2,
    NoReinvestmentNoiseP1,
    NoReinvestmentNoiseTransfer,
    NoReinvestmentNoiseBelief,
    NoReinvestmentNoiseReturn,
    NoReinvestmentNoiseResultsP1,
    NoReinvestmentNoiseResultsP2,
    ReinvestmentNoNoiseP1,
    ReinvestmentNoNoiseTransfer,
    ReinvestmentNoNoiseBelief,
    ReinvestmentNoNoiseReturn,
    ReinvestmentNoNoiseResultsP1,
    ReinvestmentNoNoiseResultsP2,
    ReinvestmentNoiseP1,
    ReinvestmentNoiseTransfer,
    ReinvestmentNoiseBelief,
    ReinvestmentNoiseReturn,
    ReinvestmentNoiseResultsP1,
    ReinvestmentNoiseResultsP2,
    SurveyIntro,
    Survey,
)


# Each cell maps to its page classes, in display order.
CELLS = {
    ("no_reinvestment", "no_noise"): (
        NoReinvestmentNoNoiseP1,
        NoReinvestmentNoNoiseTransfer,
        NoReinvestmentNoNoiseBelief,
        NoReinvestmentNoNoiseReturn,
        NoReinvestmentNoNoiseResultsP1,
        NoReinvestmentNoNoiseResultsP2,
    ),
    ("no_reinvestment", "noise"): (
        NoReinvestmentNoiseP1,
        NoReinvestmentNoiseTransfer,
        NoReinvestmentNoiseBelief,
        NoReinvestmentNoiseReturn,
        NoReinvestmentNoiseResultsP1,
        NoReinvestmentNoiseResultsP2,
    ),
    ("reinvestment", "no_noise"): (
        ReinvestmentNoNoiseP1,
        ReinvestmentNoNoiseTransfer,
        ReinvestmentNoNoiseBelief,
        ReinvestmentNoNoiseReturn,
        ReinvestmentNoNoiseResultsP1,
        ReinvestmentNoNoiseResultsP2,
    ),
    ("reinvestment", "noise"): (
        ReinvestmentNoiseP1,
        ReinvestmentNoiseTransfer,
        ReinvestmentNoiseBelief,
        ReinvestmentNoiseReturn,
        ReinvestmentNoiseResultsP1,
        ReinvestmentNoiseResultsP2,
    ),
}


class PlayerBot(Bot):
    def play_round(self):
        cfg = self.session.config
        if cfg.get("preview_survey_only"):
            yield SurveyIntro
            yield Submission(
                Survey,
                dict(
                    gender="male",
                    age=25,
                    risk_preference=5,
                    trust_most_people=6,
                    trust_willingness=5,
                ),
                check_html=False,
            )
            return
        want_treatment = cfg.get("preview_treatment")
        want_noise = cfg.get("preview_noise")

        yield Part2Transition

        if want_treatment and want_noise:
            cells = [(want_treatment, want_noise)]
        else:
            # No cell pinned: walk every cell in sequence.
            cells = [
                ("no_reinvestment", "no_noise"),
                ("no_reinvestment", "noise"),
                ("reinvestment", "no_noise"),
                ("reinvestment", "noise"),
            ]

        for treatment, noise in cells:
            instructions, transfer, belief, ret, results_p1, results_p2 = CELLS[
                (treatment, noise)
            ]
            is_reinvestment = treatment == "reinvestment"
            has_noise = noise == "noise"
            preview_role = cfg.get("preview_role")

            if not cfg.get("preview_skip_instructions"):
                yield instructions

            if want_treatment and want_noise and not cfg.get("preview_skip_instructions"):
                account_answer = 1 if is_reinvestment else 0
                realized_return_answer = -1 if has_noise else 6
                maxsend_answer = "endowment_plus_account" if is_reinvestment else "endowment_only"
                if preview_role in (None, 1):
                    yield SubmissionMustFail(
                        Part2QuizP1,
                        dict(
                            part2_quiz_p1_account=account_answer,
                            part2_quiz_p1_multiplier=4,
                            part2_quiz_p1_realized_return=realized_return_answer,
                            part2_quiz_p1_maxsend=maxsend_answer,
                        ),
                        check_html=False,
                        error_fields=["part2_quiz_p1_multiplier"],
                    )
                    yield Submission(
                        Part2QuizP1,
                        dict(
                            part2_quiz_p1_account=account_answer,
                            part2_quiz_p1_multiplier=12,
                            part2_quiz_p1_realized_return=realized_return_answer,
                            part2_quiz_p1_maxsend=maxsend_answer,
                        ),
                        check_html=False,
                    )
                if preview_role in (None, 2):
                    yield SubmissionMustFail(
                        Part2QuizP2,
                        dict(
                            part2_quiz_p2_account=account_answer,
                            part2_quiz_p2_multiplier=4,
                            part2_quiz_p2_realized_return=realized_return_answer,
                            part2_quiz_p2_maxsend=maxsend_answer,
                        ),
                        check_html=False,
                        error_fields=["part2_quiz_p2_multiplier"],
                    )
                    yield Submission(
                        Part2QuizP2,
                        dict(
                            part2_quiz_p2_account=account_answer,
                            part2_quiz_p2_multiplier=12,
                            part2_quiz_p2_realized_return=realized_return_answer,
                            part2_quiz_p2_maxsend=maxsend_answer,
                        ),
                        check_html=False,
                    )

            yield Part2RoundIntro

            if preview_role is None:
                yield Submission(
                    transfer,
                    dict(amount_sent=4, belief_partner_intended_return=6),
                    check_html=False,
                )
                yield Submission(
                    belief,
                    dict(belief_partner_transfer=4),
                    check_html=False,
                )
                yield Submission(
                    ret,
                    dict(intended_return=5),
                    check_html=False,
                )
                p1_results_data = dict(belief_partner_return_post=3) if has_noise else dict()
                yield Submission(results_p1, p1_results_data, check_html=False)
                yield Submission(results_p2, dict(), check_html=False)

            elif preview_role == 1:
                transfer_data = dict(amount_sent=4, belief_partner_intended_return=6)
                yield Submission(transfer, transfer_data, check_html=False)

                # Player 2's return is simulated in the fast Player 1 path.
                p1_results_data = dict(belief_partner_return_post=3) if has_noise else dict()
                yield Submission(results_p1, p1_results_data, check_html=False)

            elif preview_role == 2:
                # Player 1's 4-point send is simulated in the fast Player 2 path.
                yield Submission(
                    belief,
                    dict(belief_partner_transfer=4),
                    check_html=False,
                )
                yield Submission(
                    ret,
                    dict(intended_return=5),
                    check_html=False,
                )
                yield Submission(results_p2, dict(), check_html=False)

        yield SurveyIntro
        yield Submission(
            Survey,
            dict(
                gender="male",
                age=25,
                risk_preference=5,
                trust_most_people=6,
                trust_willingness=5,
            ),
            check_html=False,
        )
        yield Submission(FinalResults, check_html=False)
