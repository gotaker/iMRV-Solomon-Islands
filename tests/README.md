# v16 Test Harness

Single pytest harness, 5 layers, 50 tests. See the design spec at
[docs/superpowers/specs/2026-04-24-v16-test-harness-design.md](../docs/superpowers/specs/2026-04-24-v16-test-harness-design.md)
for architecture and intent.

## Quickstart

1. Working bench at `$BENCH_DIR` (default `../frappe-bench`) with both apps installed.
2. A `.sql.gz` in `.Sample DB/` or `$SAMPLE_DB_URL` set.
3. `pip install pytest pytest-timeout playwright axe-selenium-python requests httpx`
4. `playwright install chromium`
5. `./tests/run.sh`

## Flags

| Invocation | Behavior |
|---|---|
| `./tests/run.sh` | All layers, ~2–3 min |
| `./tests/run.sh --layer data` | Only Layer 1 |
| `./tests/run.sh --layer integration` | Only Layer 2 |
| `./tests/run.sh --layer ui` | Only Layer 3 |
| `./tests/run.sh --layer regression` | Only Layer 4 |
| `./tests/run.sh --layer security` | Only Layer 5 |
| `./tests/run.sh --fast` | Layers 1+2+5 (skip UI), ~45s |
| `./tests/run.sh --update-golden` | Regenerate Layer 4 snapshots |

## Env vars

| Var | Default | Purpose |
|---|---|---|
| `TEST_SITE` | `test_mrv.localhost` | Target bench site |
| `TEST_PORT` | `8001` | `bench serve` port (decoupled from dev `8000`) |
| `BENCH_DIR` | `../frappe-bench` | Bench root |
| `SAMPLE_DB_URL` | — | Fallback dump URL |
| `TESTS_UPDATE_GOLDEN` | `0` | Regenerate Layer 4 |
| `TESTS_SKIP_UI` | `0` | Skip Playwright |
| `TEST_SERVER_TIMEOUT` | `60` | `bench serve` ready-timeout (seconds) |

## Common failures

- **`bench migrate` fails during session setup** — That *is* the v16 gate firing.
  Fix the migration, don't work around the harness.
- **Port 8001 in use** — another bench serve running. `lsof -i :8001` to find it,
  or set `TEST_PORT=8002`.
- **`.Sample DB/` missing** — dumps are gitignored. Drop a current dump there or
  set `$SAMPLE_DB_URL` to a GitHub release asset.
- **Playwright chromium not found** — `playwright install chromium`.
- **axe-core scan returns zero results** — the CDN injection failed; check
  network or vendor `axe.min.js` to `tests/ui/vendor/` and update `_axe.py`.
