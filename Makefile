.PHONY: bootstrap verify quality quality-python cloc

verify:
	@bash scripts/verify-repository.sh

bootstrap:
	@bash scripts/bootstrap.sh

quality:
	@bash scripts/run-quality-checks.sh --strict-infrastructure

quality-python:
	@bash scripts/run-quality-checks.sh --python-only

cloc:
	@bash scripts/run-cloc.sh
