# Consentimiento RDD del cambio de retención

Alcance: documentos del supervisor QA local y comprobaciones documentales. Sin implementación, CI ni ensayos físicos. Revisión de cambios respecto a los candidatos previos; protocolo sin cambios.

## core

sha256:bc55626f42805c8f9cb97349463956daa12526758816cd775f7b2c9ad26fe3f6 — 6 archivos, 102 líneas, riesgo medium.

```json
{
  "schema": "gentle-ai.review-integration.consent/v3",
  "contract": "gentle-ai.review-integration/v2",
  "operation": "review.start",
  "action": "consent_required",
  "agent": "codex",
  "blocking": true,
  "target_identity": "sha256:bc55626f42805c8f9cb97349463956daa12526758816cd775f7b2c9ad26fe3f6",
  "projection": "workspace",
  "risk_level": "medium",
  "changed_files": 6,
  "changed_lines": 102,
  "headline": "Gentle AI can review this change before you call it done.",
  "reason": "Review can help detect regressions in these changes.",
  "value": "Reviewing takes a little longer and makes the result safer.",
  "risk_evidence": [
    "this change is not purely passive documentation, so it gets one consolidated review.",
    "a configuration change in docs/requirements/qa-supervisor/closure-proposal.json"
  ],
  "choices": [
    {
      "answer": "granted",
      "label": "Review this change",
      "effect": "Reviews only this change; later medium- or high-risk changes ask again, and delivery needs separate approval.",
      "invocation": "gentle-ai review start --contract gentle-ai.review-integration/v2 --cwd /workspace/replica-gentle-ai --target sha256:bc55626f42805c8f9cb97349463956daa12526758816cd775f7b2c9ad26fe3f6 --target-evidence v1:base-workspace-overlay:workspace:8b05a201b816ef7e5f90151fd209b4a4ba554019:857f21f03303ba98e02ed8497ed6006ad8a03bb3:sha256:62dba2c5165567a93d134342d86a9a4460798d770eb44ee6937a10642cdeb175 --projection workspace --agent codex --lineage review-615572b011759538 --base-ref 8b05a201b816ef7e5f90151fd209b4a4ba554019 --workspace-overlay --untracked-scope=select --expected-untracked-inventory=sha256:d46edaf41aa3f47bba21a06ad726bc31218dda1911f6e355d651432bf7f45200 --intended-untracked=docs/requirements/qa-supervisor/PRD.md --intended-untracked=docs/requirements/qa-supervisor/closure-proposal.json --intended-untracked=docs/requirements/qa-supervisor/fsm-propuesta.json --intended-untracked=docs/requirements/qa-supervisor/prd-draft.json --intended-untracked=docs/requirements/qa-supervisor/propuesta-cierre.md --intended-untracked=docs/requirements/qa-supervisor/recovery-contract.json --intended-untracked=docs/requirements/qa-supervisor/retention-change.json --intended-untracked=docs/requirements/qa-supervisor/tabla-decision.json --lenses review-resilience,review-reliability --lenses-reason 'Documentary follow-up: manual raw QA output retention32MiB and three advisories. Other partitions separate; no implementation approval.' --consent granted"
    },
    {
      "answer": "declined",
      "label": "Skip this time",
      "effect": "Skips only this change; no review record is created, and future reviews stay enabled.",
      "invocation": "gentle-ai review start --contract gentle-ai.review-integration/v2 --cwd /workspace/replica-gentle-ai --target sha256:bc55626f42805c8f9cb97349463956daa12526758816cd775f7b2c9ad26fe3f6 --target-evidence v1:base-workspace-overlay:workspace:8b05a201b816ef7e5f90151fd209b4a4ba554019:857f21f03303ba98e02ed8497ed6006ad8a03bb3:sha256:62dba2c5165567a93d134342d86a9a4460798d770eb44ee6937a10642cdeb175 --projection workspace --agent codex --lineage review-615572b011759538 --base-ref 8b05a201b816ef7e5f90151fd209b4a4ba554019 --workspace-overlay --untracked-scope=select --expected-untracked-inventory=sha256:d46edaf41aa3f47bba21a06ad726bc31218dda1911f6e355d651432bf7f45200 --intended-untracked=docs/requirements/qa-supervisor/PRD.md --intended-untracked=docs/requirements/qa-supervisor/closure-proposal.json --intended-untracked=docs/requirements/qa-supervisor/fsm-propuesta.json --intended-untracked=docs/requirements/qa-supervisor/prd-draft.json --intended-untracked=docs/requirements/qa-supervisor/propuesta-cierre.md --intended-untracked=docs/requirements/qa-supervisor/recovery-contract.json --intended-untracked=docs/requirements/qa-supervisor/retention-change.json --intended-untracked=docs/requirements/qa-supervisor/tabla-decision.json --lenses review-resilience,review-reliability --lenses-reason 'Documentary follow-up: manual raw QA output retention32MiB and three advisories. Other partitions separate; no implementation approval.' --consent declined"
    }
  ],
  "off_path": {
    "note": "To turn reviews off for good, run 'gentle-ai review mode disable'.",
    "command": "gentle-ai review mode disable"
  }
}
```

## interview

sha256:253ee548817ed343bb1b152d174e2c3967ce88fce3d8142be990aeefc0ac00fd — 2 archivos, 13 líneas, riesgo medium.

```json
{
  "schema": "gentle-ai.review-integration.consent/v3",
  "contract": "gentle-ai.review-integration/v2",
  "operation": "review.start",
  "action": "consent_required",
  "agent": "codex",
  "blocking": true,
  "target_identity": "sha256:253ee548817ed343bb1b152d174e2c3967ce88fce3d8142be990aeefc0ac00fd",
  "projection": "workspace",
  "risk_level": "medium",
  "changed_files": 2,
  "changed_lines": 13,
  "headline": "Gentle AI can review this change before you call it done.",
  "reason": "Review can help detect regressions in these changes.",
  "value": "Reviewing takes a little longer and makes the result safer.",
  "risk_evidence": [
    "this change is not purely passive documentation, so it gets one consolidated review.",
    "a configuration change in docs/requirements/qa-supervisor/interview.json"
  ],
  "choices": [
    {
      "answer": "granted",
      "label": "Review this change",
      "effect": "Reviews only this change; later medium- or high-risk changes ask again, and delivery needs separate approval.",
      "invocation": "gentle-ai review start --contract gentle-ai.review-integration/v2 --cwd /workspace/replica-gentle-ai --target sha256:253ee548817ed343bb1b152d174e2c3967ce88fce3d8142be990aeefc0ac00fd --target-evidence v1:base-workspace-overlay:workspace:f3e1cb4b709326cbf4e2a697bd4af26d68ca3f84:eafb7412dc4b5433b3db7533fcd63cc723554151:sha256:f774b832df5c11133f5213231c95b943ea10826d8b38d61ef73cee4c62baa80c --projection workspace --agent codex --lineage review-55dd99a391c31587 --base-ref f3e1cb4b709326cbf4e2a697bd4af26d68ca3f84 --workspace-overlay --untracked-scope=select --expected-untracked-inventory=sha256:d46edaf41aa3f47bba21a06ad726bc31218dda1911f6e355d651432bf7f45200 --intended-untracked=docs/requirements/qa-supervisor/design-proposals.json --intended-untracked=docs/requirements/qa-supervisor/human-question.json --intended-untracked=docs/requirements/qa-supervisor/interview.json --intended-untracked=docs/requirements/qa-supervisor/receipts/A-HUMAN-SUP-001.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-001.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-002.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-003.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-004.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-005.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-006.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-007.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-008.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-HUMAN-SUP-001.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-001.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-002.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-003.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-004.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-005.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-006.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-007.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-008.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/RETENTION-OPTIONS.txt --intended-untracked=docs/requirements/qa-supervisor/registro-skill-asistente.md --lenses review-resilience,review-reliability --lenses-reason 'Documentary follow-up: manual raw QA output retention32MiB and three advisories. Other partitions separate; no implementation approval.' --consent granted"
    },
    {
      "answer": "declined",
      "label": "Skip this time",
      "effect": "Skips only this change; no review record is created, and future reviews stay enabled.",
      "invocation": "gentle-ai review start --contract gentle-ai.review-integration/v2 --cwd /workspace/replica-gentle-ai --target sha256:253ee548817ed343bb1b152d174e2c3967ce88fce3d8142be990aeefc0ac00fd --target-evidence v1:base-workspace-overlay:workspace:f3e1cb4b709326cbf4e2a697bd4af26d68ca3f84:eafb7412dc4b5433b3db7533fcd63cc723554151:sha256:f774b832df5c11133f5213231c95b943ea10826d8b38d61ef73cee4c62baa80c --projection workspace --agent codex --lineage review-55dd99a391c31587 --base-ref f3e1cb4b709326cbf4e2a697bd4af26d68ca3f84 --workspace-overlay --untracked-scope=select --expected-untracked-inventory=sha256:d46edaf41aa3f47bba21a06ad726bc31218dda1911f6e355d651432bf7f45200 --intended-untracked=docs/requirements/qa-supervisor/design-proposals.json --intended-untracked=docs/requirements/qa-supervisor/human-question.json --intended-untracked=docs/requirements/qa-supervisor/interview.json --intended-untracked=docs/requirements/qa-supervisor/receipts/A-HUMAN-SUP-001.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-001.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-002.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-003.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-004.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-005.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-006.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-007.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/A-SUP-008.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-HUMAN-SUP-001.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-001.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-002.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-003.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-004.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-005.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-006.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-007.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/Q-SUP-008.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/RETENTION-OPTIONS.txt --intended-untracked=docs/requirements/qa-supervisor/registro-skill-asistente.md --lenses review-resilience,review-reliability --lenses-reason 'Documentary follow-up: manual raw QA output retention32MiB and three advisories. Other partitions separate; no implementation approval.' --consent declined"
    }
  ],
  "off_path": {
    "note": "To turn reviews off for good, run 'gentle-ai review mode disable'.",
    "command": "gentle-ai review mode disable"
  }
}
```

## evidence

sha256:dcdc8ae7f0da32cf4d52ba441df3869f95448c58b275e65d917260b32a8a4fbf — 4 archivos, 146 líneas, riesgo medium.

```json
{
  "schema": "gentle-ai.review-integration.consent/v3",
  "contract": "gentle-ai.review-integration/v2",
  "operation": "review.start",
  "action": "consent_required",
  "agent": "codex",
  "blocking": true,
  "target_identity": "sha256:dcdc8ae7f0da32cf4d52ba441df3869f95448c58b275e65d917260b32a8a4fbf",
  "projection": "workspace",
  "risk_level": "medium",
  "changed_files": 4,
  "changed_lines": 146,
  "headline": "Gentle AI can review this change before you call it done.",
  "reason": "Review can help detect regressions in these changes.",
  "value": "Reviewing takes a little longer and makes the result safer.",
  "risk_evidence": [
    "this change is not purely passive documentation, so it gets one consolidated review.",
    "a configuration change in docs/requirements/qa-supervisor/verification/canonical-model-results.json"
  ],
  "choices": [
    {
      "answer": "granted",
      "label": "Review this change",
      "effect": "Reviews only this change; later medium- or high-risk changes ask again, and delivery needs separate approval.",
      "invocation": "gentle-ai review start --contract gentle-ai.review-integration/v2 --cwd /workspace/replica-gentle-ai --target sha256:dcdc8ae7f0da32cf4d52ba441df3869f95448c58b275e65d917260b32a8a4fbf --target-evidence v1:base-workspace-overlay:workspace:4377fa1087d8d758f215a3454447ce434cb1d0a3:967e110109efee286d41ec5dd1bb5a9f11ff5102:sha256:bfec3ae9ec16237a0f4e59e88f1827b8ab4febb6a799dbcb99b5d64588881b7f --projection workspace --agent codex --lineage review-2383ffa61c4de09b --base-ref 4377fa1087d8d758f215a3454447ce434cb1d0a3 --workspace-overlay --untracked-scope=select --expected-untracked-inventory=sha256:d46edaf41aa3f47bba21a06ad726bc31218dda1911f6e355d651432bf7f45200 --intended-untracked=docs/requirements/qa-supervisor/activation-preflight.json --intended-untracked=docs/requirements/qa-supervisor/receipts/context7-result.json --intended-untracked=docs/requirements/qa-supervisor/receipts/python-resource.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/python-subprocess.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/research-discovery.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/web-result.json --intended-untracked=docs/requirements/qa-supervisor/research.json --intended-untracked=docs/requirements/qa-supervisor/verificacion-borrador.json --intended-untracked=docs/requirements/qa-supervisor/verification/RESULTADO.md --intended-untracked=docs/requirements/qa-supervisor/verification/activation-resumed.json --intended-untracked=docs/requirements/qa-supervisor/verification/activation.json --intended-untracked=docs/requirements/qa-supervisor/verification/canonical-independent.md --intended-untracked=docs/requirements/qa-supervisor/verification/canonical-model-results.json --intended-untracked=docs/requirements/qa-supervisor/verification/canonical-validation.json --intended-untracked=docs/requirements/qa-supervisor/verification/check-canonical-model.py --intended-untracked=docs/requirements/qa-supervisor/verification/check-document-model.py --intended-untracked=docs/requirements/qa-supervisor/verification/check-output-contract.py --intended-untracked=docs/requirements/qa-supervisor/verification/closure-independent.md --intended-untracked=docs/requirements/qa-supervisor/verification/green.json --intended-untracked=docs/requirements/qa-supervisor/verification/independent.md --intended-untracked=docs/requirements/qa-supervisor/verification/interview-validation.json --intended-untracked=docs/requirements/qa-supervisor/verification/model-results.json --intended-untracked=docs/requirements/qa-supervisor/verification/output-contract-results.json --intended-untracked=docs/requirements/qa-supervisor/verification/output-contract-run.log --intended-untracked=docs/requirements/qa-supervisor/verification/red.json --lenses review-resilience,review-reliability --lenses-reason 'Documentary follow-up: manual raw QA output retention32MiB and three advisories. Other partitions separate; no implementation approval.' --consent granted"
    },
    {
      "answer": "declined",
      "label": "Skip this time",
      "effect": "Skips only this change; no review record is created, and future reviews stay enabled.",
      "invocation": "gentle-ai review start --contract gentle-ai.review-integration/v2 --cwd /workspace/replica-gentle-ai --target sha256:dcdc8ae7f0da32cf4d52ba441df3869f95448c58b275e65d917260b32a8a4fbf --target-evidence v1:base-workspace-overlay:workspace:4377fa1087d8d758f215a3454447ce434cb1d0a3:967e110109efee286d41ec5dd1bb5a9f11ff5102:sha256:bfec3ae9ec16237a0f4e59e88f1827b8ab4febb6a799dbcb99b5d64588881b7f --projection workspace --agent codex --lineage review-2383ffa61c4de09b --base-ref 4377fa1087d8d758f215a3454447ce434cb1d0a3 --workspace-overlay --untracked-scope=select --expected-untracked-inventory=sha256:d46edaf41aa3f47bba21a06ad726bc31218dda1911f6e355d651432bf7f45200 --intended-untracked=docs/requirements/qa-supervisor/activation-preflight.json --intended-untracked=docs/requirements/qa-supervisor/receipts/context7-result.json --intended-untracked=docs/requirements/qa-supervisor/receipts/python-resource.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/python-subprocess.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/research-discovery.txt --intended-untracked=docs/requirements/qa-supervisor/receipts/web-result.json --intended-untracked=docs/requirements/qa-supervisor/research.json --intended-untracked=docs/requirements/qa-supervisor/verificacion-borrador.json --intended-untracked=docs/requirements/qa-supervisor/verification/RESULTADO.md --intended-untracked=docs/requirements/qa-supervisor/verification/activation-resumed.json --intended-untracked=docs/requirements/qa-supervisor/verification/activation.json --intended-untracked=docs/requirements/qa-supervisor/verification/canonical-independent.md --intended-untracked=docs/requirements/qa-supervisor/verification/canonical-model-results.json --intended-untracked=docs/requirements/qa-supervisor/verification/canonical-validation.json --intended-untracked=docs/requirements/qa-supervisor/verification/check-canonical-model.py --intended-untracked=docs/requirements/qa-supervisor/verification/check-document-model.py --intended-untracked=docs/requirements/qa-supervisor/verification/check-output-contract.py --intended-untracked=docs/requirements/qa-supervisor/verification/closure-independent.md --intended-untracked=docs/requirements/qa-supervisor/verification/green.json --intended-untracked=docs/requirements/qa-supervisor/verification/independent.md --intended-untracked=docs/requirements/qa-supervisor/verification/interview-validation.json --intended-untracked=docs/requirements/qa-supervisor/verification/model-results.json --intended-untracked=docs/requirements/qa-supervisor/verification/output-contract-results.json --intended-untracked=docs/requirements/qa-supervisor/verification/output-contract-run.log --intended-untracked=docs/requirements/qa-supervisor/verification/red.json --lenses review-resilience,review-reliability --lenses-reason 'Documentary follow-up: manual raw QA output retention32MiB and three advisories. Other partitions separate; no implementation approval.' --consent declined"
    }
  ],
  "off_path": {
    "note": "To turn reviews off for good, run 'gentle-ai review mode disable'.",
    "command": "gentle-ai review mode disable"
  }
}
```

## canonical

sha256:fff814fc0c47bb600d329ee7653510a28b41fcf806f1fffae8d9cb53e3e7ed1c — 1 archivos, 2 líneas, riesgo medium.

```json
{
  "schema": "gentle-ai.review-integration.consent/v3",
  "contract": "gentle-ai.review-integration/v2",
  "operation": "review.start",
  "action": "consent_required",
  "agent": "codex",
  "blocking": true,
  "target_identity": "sha256:fff814fc0c47bb600d329ee7653510a28b41fcf806f1fffae8d9cb53e3e7ed1c",
  "projection": "workspace",
  "risk_level": "medium",
  "changed_files": 1,
  "changed_lines": 2,
  "headline": "Gentle AI can review this change before you call it done.",
  "reason": "Review can help detect regressions in these changes.",
  "value": "Reviewing takes a little longer and makes the result safer.",
  "risk_evidence": [
    "this change is not purely passive documentation, so it gets one consolidated review.",
    "a configuration change in docs/requirements/qa-supervisor/prd.json"
  ],
  "choices": [
    {
      "answer": "granted",
      "label": "Review this change",
      "effect": "Reviews only this change; later medium- or high-risk changes ask again, and delivery needs separate approval.",
      "invocation": "gentle-ai review start --contract gentle-ai.review-integration/v2 --cwd /workspace/replica-gentle-ai --target sha256:fff814fc0c47bb600d329ee7653510a28b41fcf806f1fffae8d9cb53e3e7ed1c --target-evidence v1:base-workspace-overlay:workspace:6bce9e84046fd49bf5200bec9fcb697bb99f930f:00de2774d90901b880920b2b92849c03df4598f9:sha256:0320457a93238ccdb19282280251a90864e6637f35435a808dd1803085c063f4 --projection workspace --agent codex --lineage review-b0c6940b9bfa0dc6 --base-ref 6bce9e84046fd49bf5200bec9fcb697bb99f930f --workspace-overlay --untracked-scope=select --expected-untracked-inventory=sha256:d46edaf41aa3f47bba21a06ad726bc31218dda1911f6e355d651432bf7f45200 --intended-untracked=docs/requirements/qa-supervisor/prd.json --lenses review-resilience,review-reliability --lenses-reason 'Documentary follow-up: manual raw QA output retention32MiB and three advisories. Other partitions separate; no implementation approval.' --consent granted"
    },
    {
      "answer": "declined",
      "label": "Skip this time",
      "effect": "Skips only this change; no review record is created, and future reviews stay enabled.",
      "invocation": "gentle-ai review start --contract gentle-ai.review-integration/v2 --cwd /workspace/replica-gentle-ai --target sha256:fff814fc0c47bb600d329ee7653510a28b41fcf806f1fffae8d9cb53e3e7ed1c --target-evidence v1:base-workspace-overlay:workspace:6bce9e84046fd49bf5200bec9fcb697bb99f930f:00de2774d90901b880920b2b92849c03df4598f9:sha256:0320457a93238ccdb19282280251a90864e6637f35435a808dd1803085c063f4 --projection workspace --agent codex --lineage review-b0c6940b9bfa0dc6 --base-ref 6bce9e84046fd49bf5200bec9fcb697bb99f930f --workspace-overlay --untracked-scope=select --expected-untracked-inventory=sha256:d46edaf41aa3f47bba21a06ad726bc31218dda1911f6e355d651432bf7f45200 --intended-untracked=docs/requirements/qa-supervisor/prd.json --lenses review-resilience,review-reliability --lenses-reason 'Documentary follow-up: manual raw QA output retention32MiB and three advisories. Other partitions separate; no implementation approval.' --consent declined"
    }
  ],
  "off_path": {
    "note": "To turn reviews off for good, run 'gentle-ai review mode disable'.",
    "command": "gentle-ai review mode disable"
  }
}
```
