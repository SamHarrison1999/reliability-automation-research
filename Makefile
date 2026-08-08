.PHONY: bootstrap verify

verify:
	@bash scripts/verify-repository.sh

bootstrap:
	@bash scripts/bootstrap.sh
