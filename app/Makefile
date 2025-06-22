.PHONY: fmt
fmt:
    docker compose exec indexer poetry run black .
    docker compose exec indexer poetry run isort .
