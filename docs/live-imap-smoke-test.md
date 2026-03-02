# Live IMAP Smoke Test

## Preconditions
1. Two accounts registered in the registry (keyring credentials stored).
1. IMAP connectivity verified for both accounts.

## Steps
1. Run `sync_mailbox("INBOX", account_name="primary", since_date="01-Jan-2024")`.
1. Verify `sync_status("primary")` shows `last_pull_status=ok` and non-zero count.
1. Run `sync_mailbox("INBOX", account_name="secondary", since_date="01-Jan-2024")`.
1. Verify `sync_status("secondary")` shows `last_pull_status=ok` and non-zero count.
1. Run `search_messages("invoice")` with no `account_name` and verify mixed-account results include `account`.

## Expected Result
All steps complete without errors and status fields update as expected.
