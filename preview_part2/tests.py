from otree.api import Bot, Submission
from . import (
    NoReinvestmentNoNoiseP1,
    NoReinvestmentNoNoiseP2,
    NoReinvestmentNoNoiseTransfer,
    NoReinvestmentNoNoiseReturn,
    NoReinvestmentNoNoiseResultsP1,
    NoReinvestmentNoNoiseResultsP2,
    NoReinvestmentNoiseP1,
    NoReinvestmentNoiseP2,
    NoReinvestmentNoiseTransfer,
    NoReinvestmentNoiseReturn,
    NoReinvestmentNoiseResultsP1,
    NoReinvestmentNoiseResultsP2,
    ReinvestmentNoNoiseP1,
    ReinvestmentNoNoiseP2,
    ReinvestmentNoNoiseTransfer,
    ReinvestmentNoNoiseReturn,
    ReinvestmentNoNoiseResultsP1,
    ReinvestmentNoNoiseResultsP2,
    ReinvestmentNoiseP1,
    ReinvestmentNoiseP2,
    ReinvestmentNoiseTransfer,
    ReinvestmentNoiseReturn,
    ReinvestmentNoiseResultsP1,
    ReinvestmentNoiseResultsP2,
    Survey,
)


# Each cell maps to its six page classes, in display order.
CELLS = {
    ("no_reinvestment", "no_noise"): (
        NoReinvestmentNoNoiseP1,
        NoReinvestmentNoNoiseP2,
        NoReinvestmentNoNoiseTransfer,
        NoReinvestmentNoNoiseReturn,
        NoReinvestmentNoNoiseResultsP1,
        NoReinvestmentNoNoiseResultsP2,
    ),
    ("no_reinvestment", "noise"): (
        NoReinvestmentNoiseP1,
        NoReinvestmentNoiseP2,
        NoReinvestmentNoiseTransfer,
        NoReinvestmentNoiseReturn,
        NoReinvestmentNoiseResultsP1,
        NoReinvestmentNoiseResultsP2,
    ),
    ("reinvestment", "no_noise"): (
        ReinvestmentNoNoiseP1,
        ReinvestmentNoNoiseP2,
        ReinvestmentNoNoiseTransfer,
        ReinvestmentNoNoiseReturn,
        ReinvestmentNoNoiseResultsP1,
        ReinvestmentNoNoiseResultsP2,
    ),
    ("reinvestment", "noise"): (
        ReinvestmentNoiseP1,
        ReinvestmentNoiseP2,
        ReinvestmentNoiseTransfer,
        ReinvestmentNoiseReturn,
        ReinvestmentNoiseResultsP1,
        ReinvestmentNoiseResultsP2,
    ),
}


class PlayerBot(Bot):
    def play_round(self):
        cfg = self.session.config
        want_treatment = cfg.get("preview_treatment")
        want_noise = cfg.get("preview_noise")

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
            p1, p2, transfer, ret, results_p1, results_p2 = CELLS[(treatment, noise)]
            is_reinvestment = treatment == "reinvestment"
            has_noise = noise == "noise"

            yield p1
            yield p2

            transfer_data = dict(transfer=4, belief_partner_intended_return=6)
            if is_reinvestment:
                transfer_data["reinvestment"] = 2
            yield Submission(transfer, transfer_data, check_html=False)

            yield Submission(
                ret,
                dict(intended_return=5, belief_partner_transfer=4),
                check_html=False,
            )

            # Only player 1 reports signal attribution, and only under noise.
            p1_results_data = dict(signal_attribution=5) if has_noise else dict()
            yield Submission(results_p1, p1_results_data, check_html=False)
            yield Submission(results_p2, dict(), check_html=False)

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
