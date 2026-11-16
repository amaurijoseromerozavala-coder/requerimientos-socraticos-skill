"""Documentary oracle for the ratified Windows-account D05 profile."""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
DECISION = ROOT / "docs/design/rs3/authority-boundary-decision.json"
DEPLOYMENT = ROOT / "skills/requerimientos-socraticos/assets/rs3-authority-deployment.json"
PORTABILITY = ROOT / "docs/design/rs3/authority-portability-contract.json"
ADR = ROOT / "docs/design/rs3/ADR-005-windows-sid-guardian.md"
REFERENCE = ROOT / "skills/requerimientos-socraticos/references/authority-deployment.md"
TARGET = "WINDOWS_SPLIT_SID_AGENT_WSL_GUARDIAN_WINDOWS"


def require_blocked(profile):
    assert profile["status"] == "TARGET_UNVERIFIED"
    assert profile["execution_authorized"] is False
    assert profile["required_distinct_windows_sids"] is True
    assert profile["same_windows_sid_wsl_uids_sufficient"] is False
    needed = {"AGENT_STANDARD_WINDOWS_ACCOUNT", "GUARDIAN_DISTINCT_WINDOWS_SID",
              "GUARDIAN_PRIVATE_STORE_ACL", "AGENT_CANNOT_READ_CODES_OR_SIGNING_KEY",
              "TRUSTED_GUARDIAN_UI_SESSION", "EXACT_DECISION_SIGNED_RECEIPT",
              "ONE_TIME_PRINTED_CODE", "AGENT_CANNOT_EXECUTE_PROTECTED_OPERATION",
              "REVOCATION_AND_RECOVERY", "TARGET_NEGATIVE_TESTS"}
    assert needed <= set(profile["required_evidence"])


class WindowsSidAuthorityContract(unittest.TestCase):
    def test_selected_profile_keeps_authority_blocked(self):
        decision = json.loads(DECISION.read_text())
        deployment = json.loads(DEPLOYMENT.read_text())
        portability = json.loads(PORTABILITY.read_text())
        self.assertEqual(decision["choice"], TARGET)
        self.assertEqual(deployment["selected_target"], TARGET)
        require_blocked(deployment["profiles"][TARGET])
        self.assertEqual(decision["real_authority_gate"], "SECURITY_BOUNDARY_UNMET")
        self.assertFalse(deployment["execution_authorized"])
        self.assertFalse(portability["execution_authorized"])
        self.assertEqual(portability["profiles"][TARGET]["decision_status"],
                         "RATIFIED_DESIGN_TARGET_UNVERIFIED")

    def test_historical_wsl_profile_does_not_claim_security_boundary(self):
        deployment = json.loads(DEPLOYMENT.read_text())
        old = deployment["profiles"]["POSIX_SPLIT_UID_LINUX_WSL"]
        self.assertFalse(old["execution_authorized"])
        self.assertEqual(old["same_windows_sid_boundary"], "NOT_ESTABLISHED")
        for unsafe in ({"status": "READY"}, {"execution_authorized": True},
                       {"required_distinct_windows_sids": False},
                       {"same_windows_sid_wsl_uids_sufficient": True}):
            altered = dict(deployment["profiles"][TARGET], **unsafe)
            with self.assertRaises(AssertionError):
                require_blocked(altered)

    def test_adr_and_skill_preserve_decision_and_human_channel(self):
        adr = " ".join(ADR.read_text().split())
        reference = REFERENCE.read_text()
        for phrase in ("cuentas Windows distintas", "códigos impresos",
                       "respuesta personalizada", "recibo firmado",
                       "NOT_ESTABLISHED"):
            self.assertIn(phrase, adr)
        self.assertIn("WINDOWS_SPLIT_SID_AGENT_WSL_GUARDIAN_WINDOWS", reference)
        self.assertIn("mismo usuario Windows", reference)


if __name__ == "__main__":
    unittest.main()
