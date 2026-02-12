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

- workflow files:
  - `.github/workflows/python-ci.yml` (lint + tests + coverage reports)
  - `.github/workflows/python-snyk.yml` (security scan)
  - `.github/workflows/python-docker.yml` (container publish)
- triggers:
  - CI/Snyk: `push` + `pull_request` with path filters
  - Docker publish:
    - branch pushes to `lab*` publish `1.<lab-number>.<short-sha>`
    - merged PRs to `master` publish `1.<lab-number>` + `latest`

**Versioning strategy (SemVer/CalVer):**

- SemVer-style lab release tags: `1.<lab-number>` + `latest`
- lab number is extracted from merged branch name (example: `lab03` -> `1.3`)

## 2. Workflow Evidence

Provide links/terminal output for:

- Tests passing locally (terminal output below)
- Successful workflow run link (GitHub Actions): `TODO`
- Docker image on Docker Hub (link): `TODO`
- Status badge in `app_python/README.md`:
  - <https://github.com/LocalT0aster/DevOps-Core-S25/actions/workflows/python-ci.yml>

```log
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

- `src/main.py` launcher-only branch is excluded with `# pragma: no cover`.

## 3. Best Practices Implemented

- **Practice 1: Path-based trigger filtering**: avoids running Python CI when unrelated folders change.
- **Practice 2: Lint + test stages in CI**: catches style and functional issues early.
- **Practice 3: Coverage reporting in CI command**: makes test quality visible, not just pass/fail.
- **Practice 4: Pipeline separation by concern**: test, security, and deploy concerns run independently for clearer failure diagnosis.
- **Practice 5: Reusable setup action**: shared Python/Poetry setup is centralized in `.github/actions/python-setup/action.yml` to avoid duplication.
- **Caching**: `actions/cache` stores `~/.cache/pypoetry` and `app_python/.venv` using a `poetry.lock`-based key.
- **Snyk**: integrated via `snyk/actions/setup` + `snyk test --severity-threshold=high`.
- **Snyk token handling**: workflow skips Snyk step if `SNYK_TOKEN` secret is missing.

## 4. Key Decisions

- **Versioning Strategy:** SemVer-style `1.<lab-number>` because releases happen once per lab and are easy to map back to coursework milestones.
- **Docker Tags:** branch builds publish `1.<lab-number>.<short-sha>`; merged lab releases publish `1.<lab-number>` and `latest`.
- **Workflow Triggers:** path-filtered pushes/PRs for CI and Snyk, with container publishing gated on merged PRs to `master`.
- **Test Coverage:** endpoint and helper logic are covered; launcher-only code is excluded with pragma.
- **Snyk policy:** CI fails only for vulnerabilities at `high` severity or above.

## 5. Challenges (Optional)

- Moving from endpoint-only tests to helper-level unit tests increased meaningful coverage.
- Local and CI environments may have different tool availability; Poetry-based commands are used for reproducibility.
