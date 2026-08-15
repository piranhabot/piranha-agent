"""Regression tests for csv_data_summarizer and postgres.

Before this fix, both returned canned markdown templates with bracketed
placeholders ("[count]", "[data]") regardless of input - csv_data_summarizer
never opened the file it was given, and postgres never executed the query
its own docstring/security-check implied it would run.
"""

import csv
import os
import tempfile

import pytest
from piranha_agent.official_claude_skills import (
    _validate_readonly_sql,
    csv_data_summarizer,
    postgres,
)
from piranha_agent.skill import agent_permissions

_TEST_POSTGRES_DSN = os.environ.get(
    "PIRANHA_TEST_POSTGRES_DSN", "postgresql://localhost/piranha_test"
)


def _postgres_reachable() -> bool:
    try:
        import psycopg

        with psycopg.connect(_TEST_POSTGRES_DSN, connect_timeout=2):
            return True
    except Exception:
        return False


@pytest.fixture
def csv_path():
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "age", "score"])
        writer.writerow(["alice", "30", "95.5"])
        writer.writerow(["bob", "", "88.0"])
        writer.writerow(["carol", "25", "91.0"])
    yield path
    os.unlink(path)


@pytest.fixture(autouse=True)
def _permissions():
    token = agent_permissions.set(["file_read", "network_read"])
    yield
    agent_permissions.reset(token)


class TestCsvDataSummarizer:
    def test_requires_file_read_permission(self, csv_path):
        token = agent_permissions.set([])
        try:
            with pytest.raises(PermissionError):
                csv_data_summarizer(csv_path)
        finally:
            agent_permissions.reset(token)

    def test_computes_real_row_and_column_counts(self, csv_path):
        result = csv_data_summarizer(csv_path)
        assert "Rows: 3" in result
        assert "Columns: 3" in result
        assert "[count]" not in result

    def test_detects_real_missing_values(self, csv_path):
        result = csv_data_summarizer(csv_path)
        assert "Missing Values: 1" in result
        assert "Missing values found in: age" in result

    def test_computes_real_numeric_stats(self, csv_path):
        result = csv_data_summarizer(csv_path)
        assert "25.00" in result  # min age
        assert "30.00" in result  # max age
        assert "27.50" in result  # mean age

    def test_missing_file_gives_clear_error(self):
        result = csv_data_summarizer("/tmp/definitely_does_not_exist_piranha.csv")
        assert "❌" in result
        assert "not found" in result.lower()


class TestPostgresValidation:
    def test_rejects_non_select(self):
        assert _validate_readonly_sql("DELETE FROM users") is not None

    def test_rejects_multi_statement(self):
        assert _validate_readonly_sql("SELECT 1; DROP TABLE users;--") is not None

    def test_rejects_forbidden_keyword_anywhere(self):
        assert _validate_readonly_sql("SELECT * FROM (DROP TABLE x) y") is not None

    def test_accepts_plain_select(self):
        assert _validate_readonly_sql("SELECT * FROM users") is None

    def test_missing_dsn_gives_clear_error(self, monkeypatch):
        monkeypatch.delenv("PIRANHA_POSTGRES_DSN", raising=False)
        result = postgres("SELECT 1")
        assert "❌" in result
        assert "PIRANHA_POSTGRES_DSN" in result


@pytest.mark.skipif(not _postgres_reachable(), reason="no local Postgres reachable")
class TestPostgresLive:
    def test_real_query_returns_real_data(self, monkeypatch):
        monkeypatch.setenv("PIRANHA_POSTGRES_DSN", _TEST_POSTGRES_DSN)
        result = postgres("SELECT 1 AS one, 2 AS two")
        assert "| one | two |" in result
        assert "| 1 | 2 |" in result
        assert "Rows returned: 1" in result

    def test_write_disguised_as_select_is_blocked_by_readonly_transaction(self, monkeypatch):
        monkeypatch.setenv("PIRANHA_POSTGRES_DSN", _TEST_POSTGRES_DSN)
        import psycopg

        with psycopg.connect(_TEST_POSTGRES_DSN, autocommit=True) as conn:
            conn.execute("CREATE SEQUENCE IF NOT EXISTS piranha_test_readonly_seq")
        try:
            result = postgres("SELECT setval('piranha_test_readonly_seq', 5)")
            assert "❌" in result
            assert "read-only" in result.lower()
        finally:
            with psycopg.connect(_TEST_POSTGRES_DSN, autocommit=True) as conn:
                conn.execute("DROP SEQUENCE IF EXISTS piranha_test_readonly_seq")

    def test_limit_is_enforced(self, monkeypatch):
        monkeypatch.setenv("PIRANHA_POSTGRES_DSN", _TEST_POSTGRES_DSN)
        result = postgres("SELECT generate_series(1, 10) AS n", limit=3)
        assert "Rows returned: 3" in result
