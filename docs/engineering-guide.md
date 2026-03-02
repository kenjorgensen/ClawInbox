# Engineering Guide

## General Process
1. Define scope and milestones in a plan document.
1. Work in small, reviewable iterations with clear deliverables.
1. Use a virtual environment (`.venv`) for dependency isolation.
1. Add tests alongside features and run them before every commit.
1. Track security hygiene: ignore sensitive artifacts, scan for sensitive data, and rotate credentials if leaked.
1. Tag releases at stable iteration checkpoints.

## Project-Specific Notes
1. IMAP sync depends on environment variables for credentials; do not store sensitive data in code.
1. Multi-account behavior: leaving `account_name` empty performs operations across all accounts where it makes sense.
1. Sync supports date filtering via IMAP `SINCE` and optional `BEFORE` in `DD-Mon-YYYY` format.
1. Vector search is optional and requires the `vector` extra dependencies.
1. Use the maintenance tool to purge stored messages and reduce local data footprint.
