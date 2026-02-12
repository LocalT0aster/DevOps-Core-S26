# LAB03 - Continuous Integration (Python)

## 1. Overview

**Testing framework used:** `pytest`

**Why this choice:**

- concise assertions and clear failure output
- fixtures simplify Flask test-client setup
- `monkeypatch` enables controlled error-path testing

**What is covered by tests:**

- endpoint tests for `GET /` and `GET /health` (success + error behavior)
- JSON schema/type assertions
- helper/unit tests for runtime/platform/request metadata
- entrypoint behavior test for `main.run()` argument wiring

**Current CI trigger configuration:**

- workflow file: `.github/workflows/app_python.yml`
- trigger: `push` with path filters for `app_python/**` and workflow file changes

**Versioning strategy (SemVer/CalVer):**

- `TODO`: not documented/implemented yet for Docker image tagging in CI

## 2. Workflow Evidence

Provide links/terminal output for:

- Tests passing locally (terminal output below)
- Successful workflow run link (GitHub Actions): `TODO`
- Docker image on Docker Hub (link): `TODO`
- Status badge in `app_python/README.md`:
  - <https://github.com/LocalT0aster/DevOps-Core-S25/actions/workflows/python-ci.yml>

```text
$ poetry run pytest --cov=src --cov-report=term-missing
========================= test session starts =========================
platform linux -- Python 3.14.2, pytest-9.0.2, pluggy-1.6.0
rootdir: /home/t0ast/Repos/DevOps-Core-S26/app_python
configfile: pyproject.toml
plugins: anyio-4.12.1, mock-3.15.1, cov-7.0.0
collected 10 items

tests/test_endpoints.py .....                                   [ 50%]
tests/test_unit_helpers.py .....                                [100%]

=========================== tests coverage ============================
___________ coverage: platform linux, python 3.14.2-final-0 ___________

Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/flask_instance.py       7      0   100%
src/main.py                10      0   100%
src/router.py              60      0   100%
-----------------------------------------------------
TOTAL                      77      0   100%
========================= 10 passed in 0.06s ==========================
```

Coverage note:

- The output above was captured before excluding launcher-only code.
- `src/main.py` line 27 (`if __name__ == "__main__":`) is now marked with `# pragma: no cover`.

## 3. Best Practices Implemented

- **Practice 1: Path-based trigger filtering**: avoids running Python CI when unrelated folders change.
- **Practice 2: Lint + test stages in CI**: catches style and functional issues early.
- **Practice 3: Coverage reporting in CI command**: makes test quality visible, not just pass/fail.
- **Caching**: `actions/setup-python` Poetry cache enabled with lockfile-based invalidation.
- **Snyk**: `TODO` (not integrated/documented yet).

## 4. Key Decisions

- **Versioning Strategy:** `TODO` (SemVer or CalVer not yet implemented for Docker tags).
- **Docker Tags:** `TODO` (version tags + `latest` not yet shown).
- **Workflow Triggers:** path-filtered `push` trigger to reduce unnecessary runs in a monorepo.
- **Test Coverage:** endpoint and helper logic are covered; launcher-only code is excluded with pragma.

## 5. Challenges (Optional)

- Moving from endpoint-only tests to helper-level unit tests increased meaningful coverage.
- Local and CI environments may have different tool availability; Poetry-based commands are used for reproducibility.
