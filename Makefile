.PHONY: reproduce-tables test

# Regenerate all derived paper artifacts from frozen traces into a scratch
# dir and diff against the on-disk/committed versions (no model calls, no
# writes under results/). See ARTIFACTS.md.
reproduce-tables:
	@bash scripts/reproduce_tables.sh

test:
	python -m pytest -q
