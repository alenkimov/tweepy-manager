@echo off
poetry install
poetry run alembic upgrade head
pause
