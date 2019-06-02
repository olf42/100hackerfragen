.DEFAULT_GOAL := help

BFF=build/fragenfragen

.PHONY: help
help:   ## Show this help information
    @grep -E '^[\.a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build-fragenfragen
build-fragenfragen: ## Build the fragenfragen docker image
	mkdir -p $(BFF)
	cp -r 100hackerfragen $(BFF)
	cp deploy/fragenfragen/* $(BFF)
	cp -r requirements_fragenfragen.txt $(BFF)
	cd $(BFF); docker build -t "olf42:100hackerfragen_fragenfragen" .
