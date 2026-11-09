# Implementation freeze — after qwen3:14b comparison run

Frozen at run 3 (`results/argverify_dev_run3_qwen14b`). Any further edits
to these files require a new run ID and re-evaluation.

| file | sha256 |
|---|---|
| src/tool_routing/argverify/methods.py | bd5c0cd26f8a007f8cb1b4f7aa0f6e7c702ab96e44d5fdfa8cb34bbeb18f9609 |
| src/tool_routing/argverify/policy.py | eca016b8e10b7424cfe5c4b68f3678e8fb1155c25bbec426719c3c8a814f9d9c |
| src/tool_routing/argverify/llm.py | cb66d9544031fc3edce36f7c14151561900011a1cafc2a47cf3bd73cb78694e9 |
| src/tool_routing/argverify/evidence.py | 9de24553f8e671c551027eb1fe4e3c3579cde32d7422b22d2f450225f68558c6 |

Frozen artifacts:
- `rule_baseline` (slot-level), `cross_argument_baseline`, `schema_baseline`
- `PROMPT` template (sha `68efada2872c58b9`, recorded in `run_config`)
- `next_action` findings→action policy
- AI run config: `qwen3:14b` via Ollama `/v1`, temperature 0,
  max_tokens 2048, timeout 300 s, retries 0
