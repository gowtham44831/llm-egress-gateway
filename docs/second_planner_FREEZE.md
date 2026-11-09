# second-planner freeze — PREPARED, NOT RUN (real planner)

Written BEFORE any evaluation run, per
`docs/second_planner_protocol.md` § "Mandatory dry run". The runner
re-hashes `docs/second_planner_protocol.md` at startup and refuses to
run if it differs from the hash below.

## Protocol

- `2aa6ea846710e3f56db079477ed5fd2878c150dab0c59e08794df8f019d3a7a7`  docs/second_planner_protocol.md (with Amendment 1, 2026-11-08 — before any model output; prior pin `8a469dff…`)

## New runner code (second-planner harness)

- `f23260c1a880ad47f9ddf8be354a7ba4e4f4c81a1532cc7bdd0325ee1f8839b8`  scripts/run_second_planner.py
- `dc8bf6e12b0268932308bc900cd471be87272153d33fcbfacf23a3111200a5c5`  src/tool_routing/argverify/planner_client.py (planner-client-1.1; prior pin `80ea5cb0…`)
- `9c9a04134a5a288dc9933683a585471a1d3521808ce88ee388021166c7f36c3c`  scripts/verify_second_planner_dryrun.py

## Frozen inputs reused unchanged (hashes match their original freezes)

- `3fb88c61caee7840c1dc2db1253f0e479778993e1113f3b0d5834bd6dfc87e22`  src/tool_routing/argverify/fixtures/planner_pilot_cases_v2.json
- `b9fe54a006643a979007f2060ebfa3e703492809852e1c5a4af85b47e40a967b`  src/tool_routing/argverify/fixtures/multistep_cases_v2.json
- `435e932b59fda0de6a2c2a1b6dd960a2eb01bfb11756d644e6d0acc67df6e48e`  src/tool_routing/argverify/planner_adapter.py
- `3bb0b741145f9b7178fde738baf5273e3c33765783de36b4957c81a05a7ac6e7`  src/tool_routing/argverify/block_feedback.py
- `f3dd7f8a6e203e3dd0d10919ff394dbaba462f392d6cbfcd03856b9fc9d1e27a`  src/tool_routing/argverify/url_fetch_gateway.py
- `3c3c75114e810298f0e6334f6265074e2f6b60e277dc8ae778874dfd3c8162f4`  scripts/run_url_eval_v2.py
- `e88fad0d8df55b707878e3b0c23636069da4fe351987e4703d952990e6347f47`  scripts/run_planner_pilot_v1.py
- `66acb1423eef8e8583e36887c9698f9959ffe95747058e5752f93d020299cb75`  scripts/run_planner_pilot_v2.py
- `75361cd56b0835ba6fdb8272f8e813db97517af10fcb849159e3d8d5aa62db92`  scripts/run_eval_v4.py
- `088fa6b13079a0d99de713928bf57e01eab51b9a689de6da141b9e9f448b6de5`  scripts/run_multistep_pilot.py

Notes:

- The frozen runner scripts above are NOT modified; the new runner
  imports their templates/parsers/arms so their FREEZE entries remain
  the proof of what ran.
- `results/` traces are read-only inputs (mock source +
  decision reference); the runner writes only under
  `runs/second_planner/`.
- A real planner run records model id + full digest or provider
  version string at call time; nothing real has been run yet.
- Amendment 1 (2026-11-08): two failed `api:openai:gpt-6.1-sol`
  attempts preserved read-only under `runs/second_planner_failed/`
  (HTTP 429 quota; HTTP 400 `max_tokens` unsupported) — no model
  output in either. planner-client-1.1 deviations are in the
  protocol's Amendment 1 table.
