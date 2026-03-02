# Rollout Procedure

## Branching
1. Use `main` as the stable branch.
1. Create a short-lived feature branch per iteration: `iter-1`, `iter-2`, `iter-3`.
1. Merge via PR (even if local) to keep history clean.

## Environment
1. Create a virtual environment at `.venv` before installing dependencies.
1. Install dependencies only inside the venv.

## Commits
1. Prefer small, reviewable commits (1-3 logical changes each).
1. Use conventional-ish messages:
   - `feat:` new behavior
   - `fix:` bug fix
   - `chore:` tooling/docs/cleanup
1. Tie commits to the iteration step when possible (include step number in body).
1. Commit at each stable point (buildable + tests passing for the iteration scope).

## Testing
1. Run unit tests for the changed area before merge.
1. Run a minimal end-to-end smoke test per iteration:
   - Iter 1: IMAP sync + normalization + DB write
   - Iter 2: FTS search + vector search + hybrid query
   - Iter 3: Auth modes + multi-account + retention
1. If tests are missing, add a TODO and create an issue.
1. Include property-based tests for critical parsing/normalization code.

## Safety Check (PII)
1. Before every commit, run a quick scan for secrets and personal data (email addresses, tokens, passwords).
1. Verify `.eml` files, local caches, and credentials are excluded via `.gitignore`.
1. If any sensitive data is found, remove it from history before proceeding.

## Proactive Security
1. Use a local `.env` and never commit secrets or tokens.
1. Store any sample data in `data/` or `cache/` which are ignored.
1. Run a secrets scan before each release (e.g., `git ls-files | rg -n \"(password|token|secret|api[_-]?key)\"`).
1. If sensitive data is discovered, rotate credentials and scrub git history before continuing.
1. Enable the local pre-commit hook in `.git/hooks/pre-commit` to block obvious secrets.

## Release Tags
1. Tag after each iteration merge:
   - `v0.1-iter1`
   - `v0.2-iter2`
   - `v0.3-iter3`

## Documentation
1. Update `docs/project-state.md` each iteration.
1. Update README with new tools/config changes.
1. Update `docs/engineering-guide.md` when process or project guidance changes.
