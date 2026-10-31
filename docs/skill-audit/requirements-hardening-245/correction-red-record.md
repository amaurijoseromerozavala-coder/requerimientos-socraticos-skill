RED reproducido antes de la corrección, confirmado por audit/requirements-hardening-245/independent-review.json y correction-red-tests.log:

- RLIMIT_AS hard=128 MiB, workload lógico, headroom visible=2048 MiB: versión previa devolvía READY_FOR_LIVE_ADMISSION y selected_profile_mib=512 aunque rol solver requería448 MiB.
- Baseline CLI=100 MiB y caller role de32 MiB: versión previa devolvía READY con perfil512.
- evaluate no aceptaba workload/caller_scope/baseline_bytes (TypeError); por tanto no podía expresar admisión por rol ni distinguir API externa.
- `python -B scripts/activation_preflight.py --memory-budget-mib 0` y `--memory-budget-mib 520`: exit1, stdout vacío, traceback por stderr.

La salida independiente con los valores originales está registrada en `audit/requirements-hardening-245/independent-review.json`; reproducciones CLI del checkout previo están en `correction-red.log` y `correction-red-tests.log`.
