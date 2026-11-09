# MND development milestone freeze

Frozen 2026-02-13, git HEAD `9ce515d` (dirty tree noted). Any change to
method, policy, fixture, or runner requires a new run ID and separate
reporting — this run's artifacts are immutable.

## Frozen inputs/outputs (sha256)

- `src/tool_routing/argverify/disclosure.py` — `3009615105e92d4878cd45c3c14c1333475fbdd48c12a69a9387f4bf52e0cf17` (unchanged since prior freeze)
- `src/tool_routing/argverify/min_disclosure.py` — `33adb8e79ae65b0a51debde4476908de541a9015d54980d263ef878265e71337`
- `scripts/run_disclosure_mnd.py` — `1668fe0e05e510382a55fc9e027ecbedf70761cdc067b6a8d161757ddec7a6e1`
- `scripts/build_disclosure_mnd_v1.py` — `0d8e8c13b251b185834d5f62232e0ec1435d10a2be1806a89b6acb16b37d2554`
- `src/tool_routing/argverify/fixtures/disclosure_cases_mnd_v1.json` — `1c5f5fd189411b22c3cfa2f3e36f16d0af805c12e4be22f7bae7b3fec90ef892`
- `docs/security_min_disclosure_spec.md` — `97c4433034a3f1ec0f81b15546072908b2c512d46b93b7b81475eb9ef7d75d2b`
- `docs/security_mnd_dev_report.md` — `d35e781bb6805fb237dc5e8e6739c746837ffd0c6e3825d14309101ef354dc3d`
- `results/disclosure_mnd_dev/results.json` — `5b43a8d8b8b49efacfdd64eabee9171e529b6c4baa6c2e0f89d07771062e49f5`
- `results/disclosure_mnd_dev/MANIFEST.txt` — `f9059d3ef3e9295a7cdbb71ada454dedd9c062305206bd9f0afbfd924b276817`
- `tests/test_min_disclosure.py` — `963e966a829711c06f9bf22ddbc0199f28329f7a3fd8dcaba95da9ce7c8cf688`

## Policy/fixture versions

- `mnd-pol-1.0` (dev draft, `security_min_disclosure_spec.md`)
- Fixture `mnd-v1`: 4 development cases, disclosed expected behavior.
- Frozen policy `disc-pol-1.0` / `rec-pol-1.0` untouched.

## Post-freeze additions (disclosed)

- `ref_optimistic` baseline (same records/checks; unknown acceptance is
  assumed, never clarified) — added after this freeze to make the
  comparison substitution-vs-substitution, not substitution-vs-none.
  It runs under a new run ID (`disclosure_mnd_dev2`) with a new
  manifest; hashes there record the post-freeze code.
