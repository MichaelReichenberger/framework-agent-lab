# Week 2 verified coding-agent lab

This lab replaces Week 1's controller with a live local Ollama model,
LangGraph tool routing, and an explicit verification decision. You use
four supplied scoped tools and implement response validation, model invocation,
graph construction, and verification.

Start with [HANDOUT.md](HANDOUT.md). Begin the lab by setting up Python 3.12,
installing the dependencies from `requirements-lock.txt`, downloading
`qwen3:8b`, and running `checks/probe_model.py`.
The model uses native calls, with reasoning disabled and bounded context,
generation, and timeouts. A scripted or manual repair does not complete the lab.

- `starter/agent.py`: supplied tools, model factory, CLI, and completed graph/verification.
- `checks/probe_model.py`: local native-tool preflight before granting file tools.
- `checks/smoke.py`: read-only graph/state diagnostic.
- `checks/workflow.py`: harmless temporary-fixture write/test/verification checks.
- `target-service/`: model-repaired service, nine original acceptance tests, and student regression.
- `task.txt`: the repair task, configurable through `--task`.
- `questionnaire.md`: answered questionnaire; personal name and video remain to be added.
- `requirements.txt` / `requirements-lock.txt`: pinned framework dependencies.

Keep the agent outside the service. Independently author a regression before
running the live repair, then show ten passing tests and an empty protected-file
diff. Submit source, questionnaire, and one four-minute explanation video.

## Implementation and reproducible commands

The four TODOs in `starter/agent.py` are implemented. The graph runs
`START -> model -> tools -> model` for native tool calls, then routes the final
response through `verify -> END`. The verifier accepts only linked tool
observations, invalidates test success after a successful pricing edit or a
later unsuccessful test, and requires nonempty final text without tool calls.
JSON-looking model text remains text; malformed native calls raise `ValueError`.
The supplied tools, model factory, public interface, CLI, and 32-step limit are
unchanged. The agent never writes the independent student test.

For WSL2 with Docker Desktop, use the project configuration described in
[WSL.md](WSL.md). Run these commands in the Ubuntu WSL terminal:

```bash
cd path/to/repo/framework-agent-lab/framework-agent-lab
bash scripts/wsl.sh up -d --build
bash scripts/wsl.sh exec lab python -m pip check
bash scripts/wsl.sh exec lab ollama list
bash scripts/wsl.sh exec lab python checks/probe_model.py --model qwen3:8b
bash scripts/wsl.sh exec lab python checks/smoke.py --agent starter/agent.py --root target-service
bash scripts/wsl.sh exec lab python checks/workflow.py --agent starter/agent.py
bash scripts/wsl.sh exec lab python -m unittest discover -s checks -p test_verification.py -v
bash scripts/wsl.sh exec lab python starter/agent.py --root target-service --model qwen3:8b --task "$(cat task.txt)"
```

Review the pricing diff before entering exactly `yes` at the test prompt.
After the agent finishes, independently run:

```bash
cd target-service
git status --short
git diff -- orders/pricing.py
git diff --exit-code -- orders/validation.py orders/service.py orders/storage.py tests/test_acceptance.py docs
cd ..
bash scripts/wsl.sh exec -w /workspace/target-service lab python -m unittest discover -s tests -v
```

The first run on 14 October used native Windows Python 3.12.14 and Windows
Ollama. The WSL configuration now runs Python 3.12 and Ollama together in one
Linux container on Docker Desktop's WSL2 backend with the NVIDIA GPU. It uses
the container's `/opt/venv`, not the Windows `.venv`. Existing model files are
imported once from a read-only mount into a private Linux model volume using
the ignored local `.env.wsl`; see WSL.md for a machine without that cache.
The agent still connects only to its unchanged
local endpoint, `http://127.0.0.1:11434`, inside the Linux container.

## WSL setup status (20 October 2026)

The Linux image built with Python 3.12.15 and the unchanged dependency lock;
`pip check` passed during the build. The initial startup exposed an Ollama
metadata-migration error on the read-only model mount. The configuration now
imports the required qwen3:8b blobs into a private Linux model volume, where
Ollama can also migrate its metadata. Direct inference from the Windows weight
mount timed out in the first preflight; the repeated preflight with the native
Linux cache passed (`LIVE PROBE PASSED`). The final image is pinned to Ollama
0.35.1, matching the installed Windows version, and uses Python 3.12.15 with
qwen3:8b at the required 16,384-token context. Its preflight also passed.
Ubuntu commands subsequently timed out and Docker returned HTTP 500. After
personal approval on 20 October, the old global WSL settings were backed up,
the limits changed to 8 GB RAM/4 GB swap, and WSL/Docker restarted. Ubuntu now
reports 7.8 GiB RAM and 4.0 GiB swap; Docker 28.0.4 and Compose 2.34.0 respond
through Ubuntu's WSL integration. Both graph diagnostics, eleven verification
tests, and ten independent service tests passed under Linux. The fresh baseline
also demonstrates the expected five original failures, failing student test,
and both tool denials without modifying pricing. After pinning Ollama 0.35.1,
both graph diagnostics, eleven verification tests, the ten tests of the repaired
service, and the qwen3:8b preflight passed again in that final image.
The earlier Ollama 0.40.6 qwen3 attempts made partial, incorrect changes and were
stopped; the allowed alternative qwen2.5:7b passed preflight but returned an empty
final response after reading, correctly producing INCOMPLETE. None of these
fresh WSL repair attempts is claimed as verified. A complete new model-selected
repair with the pinned 0.35.1 image has not yet been performed; no repair agent
is currently running.
The original successful service is preserved; the fresh demonstration lives
outside it under `.wsl-runs/2026-10-19/service`. The failed qwen3 source is
preserved under `.wsl-runs/2026-10-20-qwen3-incomplete-service`.

## Earlier Windows results (14 October 2026)

- Dependency installation from the unchanged lock file and `pip check`: passed.
- Service baseline commit: `f0beede`; nine original tests, five failures and four passes.
- Independent regression: `99.995` EUR rounds to `100.00` before shipping;
  expected subtotal/total `100.00` and shipping `0.00`. The original implementation
  fails, returning subtotal `99.995`, shipping `5`, and total `105.00`.
- Traversal read and ambiguous `Decimal` replacement: both denied with `ERROR`;
  pricing's SHA-256 was unchanged before/after those requests.
- `checks/smoke.py`: passed; read-only work correctly finishes incomplete.
- `checks/workflow.py`: passed, including denied approval, failed tests, stale
  success after an edit, premature completion, and bounded termination.
- Eleven additional verification/response boundary tests: passed.
- `qwen3:8b` preflight: `LIVE PROBE PASSED`, with a native `get_lab_status`
  request, its linked observation, and a final response; no files changed.
- Live `qwen3:8b` run: read business rules, acceptance tests, and pricing in that
  order, then selected `edit_pricing` and received `Updated orders/pricing.py once`.
  After the human approved the fixed test command in chat, `yes` was forwarded
  to the waiting prompt. The native `run_tests` observation returned
  `exit_code=0` and ten passing tests; the final response passed `verify`.
  The CLI reported `VERIFIED` and exited with code 0, with no later edit.
- The reviewed repair rounds each line and the discount amount with HALF_UP,
  computes shipping from discounted goods, and adds undiscounted shipping.
  The independent service test run also passed all ten tests. The protected-file
  diff is empty; service status contains only `orders/pricing.py` and the new
  `tests/test_student.py`.
- The personal explanation video and partner review remain to be performed.

The source ZIP excludes virtual environments, models, Git metadata, and caches.
The baseline commit and `git diff` commands refer to this local checkout; the
ZIP itself contains the repaired source. The questionnaire is supplied separately.

Do not weaken acceptance tests: doing so would allow the customer's incorrect
totals to pass without fixing the business rules. Passing finite tests does not
prove correctness for every monetary input, Decimal context, or hostile model
output, and the supplied tool checks do not constitute an OS sandbox.
