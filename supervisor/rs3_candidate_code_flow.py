"""Bind synthetic coordinate use to a recomputed candidate challenge.

Inputs are caller proposals. This module does not authenticate the presenter,
enforce expiry against a trusted clock, issue receipts, or grant authority.
"""

from pathlib import Path

from supervisor.rs3_coordinate_ledger import CoordinateLedger, LedgerBlocked
from supervisor.rs3_printed_code_challenge import (
    ChallengeBlocked, build_candidate_challenge)
from supervisor.rs3_printed_code_verifier import (
    CodeVerifierBlocked, PrintedCodeVerifier)


class CandidateFlowBlocked(RuntimeError):
    pass


class CandidateCodeFlow:
    def __init__(self, root):
        self.root = Path(root).absolute()

    def _candidate(self, presentation, selected_option_id, metadata):
        try:
            candidate = build_candidate_challenge(
                presentation, selected_option_id, **metadata)
            snapshot = CoordinateLedger(self.root).snapshot()
        except (ChallengeBlocked, LedgerBlocked) as error:
            raise CandidateFlowBlocked('CANDIDATE_UNAVAILABLE') from error
        if (candidate['card_id'] != snapshot['card_id']
                or candidate['coordinate'] not in snapshot['coordinates']):
            raise CandidateFlowBlocked('CARD_OR_COORDINATE_MISMATCH')
        return candidate

    def reserve(self, presentation, selected_option_id, **metadata):
        """Reserve the digest derived from the complete candidate proposal."""
        candidate = self._candidate(presentation, selected_option_id, metadata)
        try:
            PrintedCodeVerifier(self.root).require_ready(
                candidate['card_id'], candidate['coordinate'])
            CoordinateLedger(self.root).reserve(
                candidate['coordinate'], candidate['challenge_sha256'])
        except (CodeVerifierBlocked, LedgerBlocked) as error:
            raise CandidateFlowBlocked('RESERVATION_UNCONFIRMED') from error
        return {'state': 'PENDING', 'challenge': candidate,
                'authority_verification': 'NOT_ESTABLISHED',
                'execution_authorized': False}

    def check_and_spend(self, presentation, selected_option_id, code, **metadata):
        """Match only a previously reserved exact candidate, then burn it."""
        candidate = self._candidate(presentation, selected_option_id, metadata)
        try:
            return PrintedCodeVerifier(self.root).check_and_spend(
                candidate['coordinate'], candidate['challenge_sha256'], code)
        except CodeVerifierBlocked as error:
            raise CandidateFlowBlocked('CHECK_OR_SPEND_UNCONFIRMED') from error
