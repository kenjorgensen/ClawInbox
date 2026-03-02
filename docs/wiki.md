# ClawInbox Wiki

Complete reference for all MCP tools and CLI commands.

---

## Table of Contents

- [MCP Tools](#mcp-tools)
  - [list_mailboxes](#list_mailboxes)
  - [sync_mailbox](#sync_mailbox)
  - [search_messages](#search_messages)
  - [search_messages_exact](#search_messages_exact)
  - [search_messages_by_label](#search_messages_by_label)
  - [search_messages_hybrid](#search_messages_hybrid)
  - [create_label](#create_label)
  - [list_labels](#list_labels)
  - [apply_label](#apply_label)
  - [remove_label](#remove_label)
  - [create_rule](#create_rule)
  - [list_rules](#list_rules)
  - [apply_rules_to_message](#apply_rules_to_message)
  - [purge_messages](#purge_messages)
  - [sync_status](#sync_status)
  - [set_sync_enabled](#set_sync_enabled)
  - [job_status](#job_status)
- [CLI Commands](#cli-commands)
  - [email-mcp-cli register](#email-mcp-cli-register)
  - [email-mcp-cli register-account](#email-mcp-cli-register-account)
  - [email-mcp-cli list](#email-mcp-cli-list)
  - [email-mcp-cli init](#email-mcp-cli-init)
  - [email-mcp-cli list-mailboxes](#email-mcp-cli-list-mailboxes)
  - [email-mcp-cli sync](#email-mcp-cli-sync)
  - [email-mcp-cli status](#email-mcp-cli-status)
  - [email-mcp-cli search](#email-mcp-cli-search)
  - [email-mcp-cli search-exact](#email-mcp-cli-search-exact)
  - [email-mcp-cli search-by-label](#email-mcp-cli-search-by-label)
  - [email-mcp-cli search-hybrid](#email-mcp-cli-search-hybrid)
  - [email-mcp-cli label-create](#email-mcp-cli-label-create)
  - [email-mcp-cli label-list](#email-mcp-cli-label-list)
  - [email-mcp-cli label-apply](#email-mcp-cli-label-apply)
  - [email-mcp-cli label-remove](#email-mcp-cli-label-remove)
  - [email-mcp-cli rules-create](#email-mcp-cli-rules-create)
  - [email-mcp-cli rules-list](#email-mcp-cli-rules-list)
  - [email-mcp-cli rules-apply](#email-mcp-cli-rules-apply)
  - [email-mcp-cli purge](#email-mcp-cli-purge)
  - [email-mcp-cli set-sync-enabled](#email-mcp-cli-set-sync-enabled)
  - [email-mcp-cli job-status](#email-mcp-cli-job-status)

---

## MCP Tools

MCP tools are exposed over the Model Context Protocol (stdio or HTTP) and can be called by any MCP-compatible client.

---

### list_mailboxes

Lists all mailboxes (folders) available on the configured IMAP account.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `account_name` | `string \| null` | No | `null` | Name of the account to list mailboxes for. If omitted, lists all registered accounts. |

**Returns**

`object` — Structured response with mailboxes per account.

```json
{
  "status": "ok",
  "accounts": [
    { "account": "primary", "mailboxes": ["INBOX", "Sent"] }
  ]
}
```

**Example**

```python
list_mailboxes()
# => {"status":"ok","accounts":[...]}

list_mailboxes(account_name="primary")
# => {"status":"ok","account":"primary","mailboxes":[...]}
```

---

### sync_mailbox

Fetches new messages from the given IMAP mailbox, stores them locally, and updates the sync state. Supports date-range filtering. When `account_name` is omitted, syncs across all registered accounts.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `mailbox` | `string` | **Yes** | — | Mailbox name to sync (e.g. `"INBOX"`). |
| `account_name` | `string \| null` | No | `null` | Name of the account to sync. If omitted, syncs all accounts. |
| `since_date` | `string \| null` | No | `null` | Fetch messages on or after this date in `DD-Mon-YYYY` format (e.g. `"01-Jan-2024"`). When set, UID-based incremental sync is bypassed to allow full backfill. |
| `before_date` | `string \| null` | No | `null` | Fetch messages before this date in `DD-Mon-YYYY` format (e.g. `"31-Dec-2024"`). Requires `since_date` to be set for most IMAP servers. |

**Returns**

`object` — Structured response with job ids and account count.

```json
{"status":"ok","account":"primary","mailbox":"INBOX","job_id":123}
```

or for a multi-account sync:

```json
{"status":"ok","mailbox":"INBOX","accounts":3,"job_ids":[1,2,3]}
```

**Example**

```python
sync_mailbox("INBOX")
# => {"status":"ok","mailbox":"INBOX","accounts":3,"job_ids":[...]}

sync_mailbox("INBOX", account_name="primary", since_date="01-Jan-2024", before_date="31-Jan-2024")
# => {"status":"ok","mailbox":"INBOX","accounts":3,"job_ids":[...]}
```

---

### search_messages

Performs a full-text search (FTS) across locally stored message subjects, senders, and body text.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | `string` | **Yes** | — | The search query string. |
| `limit` | `integer` | No | `20` | Maximum number of results to return. |
| `account_name` | `string \| null` | No | `null` | Restrict search to a specific account. If omitted, searches all accounts. |

**Returns**

`list[dict]` — A list of message objects. Each object contains:

| Field | Type | Description |
|---|---|---|
| `account` | `string` | Account name the message belongs to. |
| `id` | `integer` | Internal message ID. |
| `subject` | `string \| null` | Message subject. |
| `from` | `string \| null` | Sender address. |
| `to` | `string \| null` | Recipient address(es). |
| `date` | `string \| null` | Message date string. |

```json
[
  {
    "account": "primary",
    "id": 42,
    "subject": "Meeting tomorrow",
    "from": "alice@example.com",
    "to": "bob@example.com",
    "date": "Mon, 15 Jan 2024 10:00:00 +0000"
  }
]
```

**Example**

```python
search_messages("invoice")
# => [{"account": "primary", "id": 7, "subject": "Invoice #1234", ...}]

search_messages("project update", limit=5, account_name="work")
# => [{"account": "work", "id": 22, "subject": "Project update Q1", ...}]
```

---

### search_messages_exact

Searches for messages with an exact sender address match.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `from_addr` | `string` | **Yes** | — | Exact sender email address to match. |
| `account_name` | `string \| null` | No | `null` | Restrict search to a specific account. If omitted, searches all accounts. |

**Returns**

`list[dict]` — Same message object format as [`search_messages`](#search_messages).

```json
[
  {
    "account": "primary",
    "id": 15,
    "subject": "Hello",
    "from": "alice@example.com",
    "to": "me@example.com",
    "date": "Tue, 16 Jan 2024 09:30:00 +0000"
  }
]
```

**Example**

```python
search_messages_exact("newsletter@company.com")
# => [{"account": "primary", "id": 3, "subject": "Weekly Digest", ...}]

search_messages_exact("alice@example.com", account_name="personal")
# => [{"account": "personal", "id": 8, "subject": "Lunch plans", ...}]
```

---

### search_messages_by_label

Retrieves all messages that have a given label applied.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `label` | `string` | **Yes** | — | Label name to filter by. |
| `account_name` | `string \| null` | No | `null` | Restrict to a specific account. If omitted, searches all accounts. |

**Returns**

`list[dict]` — Same message object format as [`search_messages`](#search_messages).

```json
[
  {
    "account": "primary",
    "id": 5,
    "subject": "Q4 Report",
    "from": "boss@example.com",
    "to": "me@example.com",
    "date": "Wed, 17 Jan 2024 14:00:00 +0000"
  }
]
```

**Example**

```python
search_messages_by_label("important")
# => [{"account": "primary", "id": 5, "subject": "Q4 Report", ...}]

search_messages_by_label("newsletter", account_name="personal")
# => [{"account": "personal", "id": 9, "subject": "Weekly Digest", ...}]
```

---

### search_messages_hybrid

Performs a hybrid search combining full-text search (FTS) and vector (semantic) similarity search. Falls back to FTS-only if vector search is not enabled.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | `string` | **Yes** | — | The search query string. |
| `limit` | `integer` | No | `20` | Maximum number of results to return. |
| `vector_limit` | `integer` | No | `10` | Number of vector nearest-neighbor candidates to retrieve before re-ranking. |
| `account_name` | `string \| null` | No | `null` | Restrict search to a specific account. If omitted, searches all accounts. |

**Returns**

`list[dict]` — Same message object format as [`search_messages`](#search_messages), ranked by a combined FTS and vector similarity score.

```json
[
  {
    "account": "primary",
    "id": 33,
    "subject": "Budget proposal",
    "from": "finance@example.com",
    "to": "me@example.com",
    "date": "Thu, 18 Jan 2024 11:00:00 +0000"
  }
]
```

**Example**

```python
search_messages_hybrid("quarterly financial results")
# => [{"account": "primary", "id": 33, "subject": "Budget proposal", ...}]

search_messages_hybrid("travel itinerary", limit=5, vector_limit=20, account_name="work")
# => [{"account": "work", "id": 44, "subject": "Trip to NYC", ...}]
```

> **Note:** Vector search requires the optional `[vector]` extra (`pip install -e .[vector]`) and `EMAIL_MCP_VECTOR_ENABLED=true`.

---

### create_label

Creates a new label in the local database for one or all accounts. If the label already exists for an account, it is skipped.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `name` | `string` | **Yes** | — | Label name to create. |
| `account_name` | `string \| null` | No | `null` | Create the label for this account only. If omitted, creates the label for all accounts. |

**Returns**

`string` — A confirmation message.

- Single account: `"Created label <name>"` or `"Label already exists: <name>"`
- All accounts: `"Created label <name> for <N> accounts"`

```json
"Created label important"
```

**Example**

```python
create_label("important")
# => "Created label important for 2 accounts"

create_label("newsletters", account_name="personal")
# => "Created label newsletters"
```

---

### list_labels

Lists all labels defined in the local database.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `account_name` | `string \| null` | No | `null` | List labels for this account only. If omitted, lists labels for all accounts prefixed with `"<account>:"`. |

**Returns**

`list[string]` — A list of label name strings.

- Single account: `["important", "newsletters"]`
- All accounts: `["primary:important", "work:newsletters"]`

```json
["important", "newsletters"]
```

**Example**

```python
list_labels()
# => ["primary:important", "work:newsletters"]

list_labels(account_name="primary")
# => ["important"]
```

---

### apply_label

Applies a label to a message. Creates the label if it does not already exist for the account.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `message_id` | `integer` | **Yes** | — | Internal ID of the message (from search results). |
| `label_name` | `string` | **Yes** | — | Name of the label to apply. |
| `account_name` | `string \| null` | No | `null` | Account context for resolving the label. If omitted, uses the account of the message. |

**Returns**

`string` — A confirmation or status message.

- Success: `"Applied label <label_name> to message <message_id>"`
- Already applied: `"Label already applied: <label_name>"`
- Message not found: `"Message not found: <message_id>"`

```json
"Applied label important to message 42"
```

**Example**

```python
apply_label(42, "important")
# => "Applied label important to message 42"

apply_label(42, "important")
# => "Label already applied: important"
```

---

### remove_label

Removes a label from a message.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `message_id` | `integer` | **Yes** | — | Internal ID of the message. |
| `label_name` | `string` | **Yes** | — | Name of the label to remove. |
| `account_name` | `string \| null` | No | `null` | Account context for resolving the label. If omitted, uses the account of the message. |

**Returns**

`string` — A confirmation or status message.

- Success: `"Removed label <label_name> from message <message_id>"`
- Label not applied: `"Label not applied: <label_name>"`
- Label not found: `"Label not found: <label_name>"`
- Message not found: `"Message not found: <message_id>"`

```json
"Removed label important from message 42"
```

**Example**

```python
remove_label(42, "important")
# => "Removed label important from message 42"
```

---

### create_rule

Creates an auto-labeling rule. Rules are applied to messages based on field pattern matching.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `name` | `string` | **Yes** | — | Unique name for the rule. |
| `field` | `string` | **Yes** | — | Message field to match against. Supported values: `"from"`, `"subject"`, `"to"`, `"text"`. |
| `pattern` | `string` | **Yes** | — | Regular expression pattern to match against the field value. |
| `label` | `string` | **Yes** | — | Label to apply when the pattern matches. |
| `enabled` | `boolean` | No | `true` | Whether the rule is active. |
| `account_name` | `string \| null` | No | `null` | Create the rule for this account. If omitted, creates for all accounts. |

**Returns**

`string` — A confirmation message.

- Single account: `"Created rule <name>"`
- All accounts: `"Created rule <name> for <N> accounts"`

```json
"Created rule mark-newsletters"
```

**Example**

```python
create_rule(
    name="mark-newsletters",
    field="from",
    pattern="newsletter@.*\\.com",
    label="newsletters"
)
# => "Created rule mark-newsletters for 2 accounts"

create_rule(
    name="flag-invoices",
    field="subject",
    pattern="(?i)invoice",
    label="invoices",
    account_name="work"
)
# => "Created rule flag-invoices"
```

---

### list_rules

Lists all rules defined in the local database.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `account_name` | `string \| null` | No | `null` | List rules for this account only. If omitted, lists rules for all accounts prefixed with `"<account>:"`. |

**Returns**

`list[string]` — A list of rule name strings.

- Single account: `["mark-newsletters", "flag-invoices"]`
- All accounts: `["primary:mark-newsletters", "work:flag-invoices"]`

```json
["mark-newsletters", "flag-invoices"]
```

**Example**

```python
list_rules()
# => ["primary:mark-newsletters", "work:flag-invoices"]

list_rules(account_name="work")
# => ["flag-invoices"]
```

---

### apply_rules_to_message

Evaluates all rules for the message's account against the message content and returns the list of matching labels. Does not persist labels; use `apply_label` to persist.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `message_id` | `integer` | **Yes** | — | Internal ID of the message. |
| `account_name` | `string \| null` | No | `null` | Account context for loading rules. If omitted, uses the account of the message. |

**Returns**

`list[string]` — A list of label names that matched. Returns an empty list if no rules matched or the message was not found.

```json
["newsletters", "promotions"]
```

**Example**

```python
apply_rules_to_message(42)
# => ["newsletters"]

apply_rules_to_message(99)
# => []  (no matching rules or message not found)
```

---

### purge_messages

Deletes messages from the local database and removes their stored `.eml` files. Optionally filter by account, label, and/or age. Also removes corresponding vector embeddings if vector storage is enabled.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `account_name` | `string \| null` | No | `null` | Delete messages only for this account. If omitted, deletes across all accounts. |
| `label` | `string \| null` | No | `null` | Delete only messages that have this label applied. |
| `older_than_days` | `integer \| null` | No | `null` | Delete only messages created more than this many days ago. |

**Returns**

`string` — A confirmation message with the number of deleted messages.

```json
"Deleted 17 messages."
```

**Example**

```python
purge_messages(older_than_days=90)
# => "Deleted 17 messages."

purge_messages(label="newsletters", account_name="primary")
# => "Deleted 5 messages."

purge_messages()
# => "Deleted 1024 messages."
```

---

### sync_status

Returns sync state and message counts for one or all accounts.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `account_name` | `string \| null` | No | `null` | Return status for this account only. If omitted, returns a list of statuses for all accounts. |

**Returns**

When `account_name` is provided, returns a single `dict`:

| Field | Type | Description |
|---|---|---|
| `account` | `string` | Account name. |
| `emails` | `integer` | Total messages stored locally. |
| `sync_enabled` | `boolean` | Whether sync is enabled for this account. |
| `last_pull_at` | `string \| null` | ISO-8601 timestamp of the last sync attempt. |
| `last_pull_count` | `integer \| null` | Number of messages fetched in the last sync. |
| `last_pull_status` | `string \| null` | Status string from the last sync (e.g. `"ok"`). |

When `account_name` is omitted, returns a `list[dict]` with one entry per account.

```json
{
  "account": "primary",
  "emails": 1240,
  "sync_enabled": true,
  "last_pull_at": "2024-01-18T12:00:00",
  "last_pull_count": 15,
  "last_pull_status": "ok"
}
```

**Example**

```python
sync_status(account_name="primary")
# => {"account": "primary", "emails": 1240, "sync_enabled": True, ...}

sync_status()
# => [{"account": "primary", ...}, {"account": "work", ...}]
```

---

### set_sync_enabled

Enables or disables automatic sync for one or all accounts.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `enabled` | `boolean` | **Yes** | — | `true` to enable sync, `false` to disable. |
| `account_name` | `string \| null` | No | `null` | Apply to this account only. If omitted, applies to all accounts. |

**Returns**

`string` — A confirmation message.

- Single account: `"Sync enabled set to <enabled> for <account_name>"`
- All accounts: `"Sync enabled set to <enabled> for <N> accounts"`

```json
"Sync enabled set to False for primary"
```

**Example**

```python
set_sync_enabled(False, account_name="primary")
# => "Sync enabled set to False for primary"

set_sync_enabled(True)
# => "Sync enabled set to True for 2 accounts"
```

---

### job_status

Returns the status and metadata of a background sync job.

**Parameters**

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `job_id` | `integer` | **Yes** | — | The job ID returned by `sync_mailbox` or the CLI `sync` command. |

**Returns**

`dict` with the following fields:

| Field | Type | Description |
|---|---|---|
| `job_id` | `integer` | The job ID. |
| `name` | `string` | Job name (e.g. `"sync_mailbox"`). |
| `status` | `string` | One of `"pending"`, `"done"`, `"failed"`, or `"not_found"`. |
| `account_name` | `string \| null` | Account the job ran for. |
| `started_at` | `string \| null` | ISO-8601 start timestamp. |
| `finished_at` | `string \| null` | ISO-8601 finish timestamp. |
| `message` | `string \| null` | Additional status message or error detail. |

If the job is not found, returns `{"status": "not_found", "job_id": <id>}`.

```json
{
  "job_id": 7,
  "name": "sync_mailbox",
  "status": "done",
  "account_name": "primary",
  "started_at": "2024-01-18T12:00:00",
  "finished_at": "2024-01-18T12:00:05",
  "message": "count=15"
}
```

**Example**

```python
job_status(7)
# => {"job_id": 7, "name": "sync_mailbox", "status": "done", ...}

job_status(999)
# => {"status": "not_found", "job_id": 999}
```

---

## CLI Commands

All commands are available under the `email-mcp-cli` entry point. Run `email-mcp-cli --help` for a summary. Results can be formatted as JSON with `--json` or as newline-delimited JSON with `--ndjson`.

---

### email-mcp-cli register

Registers all accounts defined in the `EMAIL_MCP_ACCOUNTS_JSON` environment variable into the local account registry.

**Usage**

```sh
email-mcp-cli register
```

**Options**

_None beyond the global `--json` / `--ndjson` flags._

**Output**

```json
{"count": 2, "message": "Registered 2 accounts."}
```

**Example**

```sh
export EMAIL_MCP_ACCOUNTS_JSON='[{"name":"primary","host":"imap.gmail.com","user":"me@gmail.com","credential_env":"EMAIL_MCP_CRED_PRIMARY"}]'
email-mcp-cli register
# {"count": 1, "message": "Registered 1 accounts."}
```

---

### email-mcp-cli register-account

Registers a single account by providing its details directly on the command line. The credential is stored in the OS keyring.

**Usage**

```sh
email-mcp-cli register-account --name <name> --host <host> --user <user> --credential <password>
```

**Options**

| Option | Type | Required | Description |
|---|---|---|---|
| `--name` | string | **Yes** | Account name. |
| `--host` | string | **Yes** | IMAP host (e.g. `imap.gmail.com`). |
| `--user` | string | **Yes** | IMAP username / email. |
| `--credential` | string | **Yes** | App password or IMAP password (stored in OS keyring). |

**Output**

```json
{"name": "primary", "message": "Registered account primary."}
```

**Example**

```sh
email-mcp-cli register-account --name primary --host imap.gmail.com --user me@gmail.com --credential myapppassword
# {"name": "primary", "message": "Registered account primary."}
```

---

### email-mcp-cli list

Lists all accounts in the registry, including their IMAP host, user, and whether a stored credential is available.

**Usage**

```sh
email-mcp-cli list
```

**Output**

```json
[
  {
    "name": "primary",
    "host": "imap.gmail.com",
    "user": "me@gmail.com",
    "has_credential": true
  }
]
```

**Example**

```sh
email-mcp-cli list
```

---

### email-mcp-cli init

Initializes the local SQLite database. Safe to run multiple times; skips initialization if the database already exists.

**Usage**

```sh
email-mcp-cli init
```

**Output**

```json
{"message": "Database initialized."}
```

or, if already initialized:

```json
{"message": "Database already initialized."}
```

**Example**

```sh
email-mcp-cli init
```

---

### email-mcp-cli list-mailboxes

Lists all mailboxes (IMAP folders) for the specified account by connecting to the IMAP server.

**Usage**

```sh
email-mcp-cli list-mailboxes [--account <name>]
```

**Options**

| Option | Type | Required | Description |
|---|---|---|---|
| `--account` | string | No | Account name to use. Falls back to default account settings. |

**Output**

```json
["INBOX", "Sent", "Drafts", "Trash"]
```

**Example**

```sh
email-mcp-cli list-mailboxes --account primary
# ["INBOX", "Sent", "[Gmail]/All Mail"]
```

---

### email-mcp-cli sync

Syncs a mailbox for one or all accounts. Returns the job ID(s) for the sync operation.

**Usage**

```sh
email-mcp-cli sync [MAILBOX] [--account <name>] [--since-date <date>] [--before-date <date>]
```

**Options**

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `MAILBOX` | string | No | `INBOX` | Mailbox to sync. |
| `--account` | string | No | `null` | Sync this account only. If omitted, syncs all accounts. |
| `--since-date` | string | No | `null` | Fetch messages on or after this date (`DD-Mon-YYYY`). |
| `--before-date` | string | No | `null` | Fetch messages before this date (`DD-Mon-YYYY`). |

**Output**

Single account:

```json
{"mailbox": "INBOX", "account": "primary", "job_id": 7}
```

All accounts:

```json
{"mailbox": "INBOX", "accounts": 2, "job_ids": [7, 8]}
```

**Example**

```sh
email-mcp-cli sync INBOX --account primary
# {"mailbox": "INBOX", "account": "primary", "job_id": 7}

email-mcp-cli sync INBOX --since-date 01-Jan-2024
# {"mailbox": "INBOX", "accounts": 2, "job_ids": [7, 8]}
```

---

### email-mcp-cli status

Displays the sync status and message counts for one or all accounts.

**Usage**

```sh
email-mcp-cli status [--account <name>]
```

**Options**

| Option | Type | Required | Description |
|---|---|---|---|
| `--account` | string | No | Account name. If omitted, shows all accounts. |

**Output**

Single account:

```json
{
  "account": "primary",
  "emails": 1240,
  "sync_enabled": true,
  "last_pull_at": "2024-01-18T12:00:00",
  "last_pull_count": 15,
  "last_pull_status": "ok"
}
```

**Example**

```sh
email-mcp-cli status --account primary
```

---

### email-mcp-cli search

Performs a full-text search against locally stored messages.

**Usage**

```sh
email-mcp-cli search <query> [--limit <n>] [--account <name>]
```

**Options**

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | **Yes** | — | Search query. |
| `--limit` | integer | No | `20` | Maximum number of results. |
| `--account` | string | No | `null` | Restrict to this account. |

**Output**

```json
[
  {
    "account": "primary",
    "id": 42,
    "subject": "Invoice #1234",
    "from": "billing@example.com",
    "to": "me@example.com",
    "date": "Mon, 15 Jan 2024 10:00:00 +0000"
  }
]
```

**Example**

```sh
email-mcp-cli search "invoice" --limit 5
```

---

### email-mcp-cli search-exact

Searches for messages from an exact sender address.

**Usage**

```sh
email-mcp-cli search-exact <from_addr> [--account <name>]
```

**Options**

| Option | Type | Required | Description |
|---|---|---|---|
| `from_addr` | string | **Yes** | Exact sender email address. |
| `--account` | string | No | Restrict to this account. |

**Output**

Same format as [`email-mcp-cli search`](#email-mcp-cli-search).

**Example**

```sh
email-mcp-cli search-exact "newsletter@company.com"
```

---

### email-mcp-cli search-by-label

Lists all messages with a given label applied.

**Usage**

```sh
email-mcp-cli search-by-label <label> [--account <name>]
```

**Options**

| Option | Type | Required | Description |
|---|---|---|---|
| `label` | string | **Yes** | Label name. |
| `--account` | string | No | Restrict to this account. |

**Output**

Same format as [`email-mcp-cli search`](#email-mcp-cli-search).

**Example**

```sh
email-mcp-cli search-by-label "newsletters"
```

---

### email-mcp-cli search-hybrid

Performs a hybrid FTS + vector semantic search.

**Usage**

```sh
email-mcp-cli search-hybrid <query> [--limit <n>] [--vector-limit <n>] [--account <name>]
```

**Options**

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | **Yes** | — | Search query. |
| `--limit` | integer | No | `20` | Maximum results. |
| `--vector-limit` | integer | No | `10` | Vector nearest-neighbor candidates. |
| `--account` | string | No | `null` | Restrict to this account. |

**Output**

Same format as [`email-mcp-cli search`](#email-mcp-cli-search).

**Example**

```sh
email-mcp-cli search-hybrid "quarterly financial results" --limit 10
```

---

### email-mcp-cli label-create

Creates a label in the local database.

**Usage**

```sh
email-mcp-cli label-create <name> [--account <name>]
```

**Options**

| Option | Type | Required | Description |
|---|---|---|---|
| `name` | string | **Yes** | Label name to create. |
| `--account` | string | No | Limit to this account. |

**Output**

```json
{"message": "Created label newsletters"}
```

**Example**

```sh
email-mcp-cli label-create "newsletters"
# {"message": "Created label newsletters for 2 accounts"}
```

---

### email-mcp-cli label-list

Lists all labels in the local database.

**Usage**

```sh
email-mcp-cli label-list [--account <name>]
```

**Options**

| Option | Type | Required | Description |
|---|---|---|---|
| `--account` | string | No | List labels for this account only. |

**Output**

```json
["primary:important", "primary:newsletters"]
```

**Example**

```sh
email-mcp-cli label-list --account primary
# ["important", "newsletters"]
```

---

### email-mcp-cli label-apply

Applies a label to a message.

**Usage**

```sh
email-mcp-cli label-apply <message_id> <label_name> [--account <name>]
```

**Options**

| Option | Type | Required | Description |
|---|---|---|---|
| `message_id` | integer | **Yes** | Internal message ID. |
| `label_name` | string | **Yes** | Label to apply. |
| `--account` | string | No | Account context. |

**Output**

```json
{"message": "Applied label important to message 42"}
```

**Example**

```sh
email-mcp-cli label-apply 42 "important"
```

---

### email-mcp-cli label-remove

Removes a label from a message.

**Usage**

```sh
email-mcp-cli label-remove <message_id> <label_name> [--account <name>]
```

**Options**

| Option | Type | Required | Description |
|---|---|---|---|
| `message_id` | integer | **Yes** | Internal message ID. |
| `label_name` | string | **Yes** | Label to remove. |
| `--account` | string | No | Account context. |

**Output**

```json
{"message": "Removed label important from message 42"}
```

**Example**

```sh
email-mcp-cli label-remove 42 "important"
```

---

### email-mcp-cli rules-create

Creates an auto-labeling rule.

**Usage**

```sh
email-mcp-cli rules-create <name> <field> <pattern> <label> [--enabled <bool>] [--account <name>]
```

**Options**

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `name` | string | **Yes** | — | Rule name. |
| `field` | string | **Yes** | — | Field to match: `from`, `subject`, `to`, or `text`. |
| `pattern` | string | **Yes** | — | Regex pattern. |
| `label` | string | **Yes** | — | Label to apply on match. |
| `--enabled` | boolean | No | `true` | Whether the rule is active. |
| `--account` | string | No | `null` | Limit to this account. |

**Output**

```json
{"message": "Created rule mark-newsletters"}
```

**Example**

```sh
email-mcp-cli rules-create mark-newsletters from "newsletter@.*" newsletters
# {"message": "Created rule mark-newsletters for 2 accounts"}
```

---

### email-mcp-cli rules-list

Lists all rules in the local database.

**Usage**

```sh
email-mcp-cli rules-list [--account <name>]
```

**Options**

| Option | Type | Required | Description |
|---|---|---|---|
| `--account` | string | No | List rules for this account only. |

**Output**

```json
["primary:mark-newsletters", "work:flag-invoices"]
```

**Example**

```sh
email-mcp-cli rules-list --account primary
# ["mark-newsletters"]
```

---

### email-mcp-cli rules-apply

Evaluates all rules against a message and returns the matching label names.

**Usage**

```sh
email-mcp-cli rules-apply <message_id> [--account <name>]
```

**Options**

| Option | Type | Required | Description |
|---|---|---|---|
| `message_id` | integer | **Yes** | Internal message ID. |
| `--account` | string | No | Account context. |

**Output**

```json
["newsletters"]
```

**Example**

```sh
email-mcp-cli rules-apply 42
# ["newsletters"]
```

---

### email-mcp-cli purge

Deletes messages from the local database and disk. Optionally filter by account, label, and/or age.

**Usage**

```sh
email-mcp-cli purge [--account <name>] [--label <label>] [--older-than-days <n>]
```

**Options**

| Option | Type | Required | Description |
|---|---|---|---|
| `--account` | string | No | Delete messages for this account only. |
| `--label` | string | No | Delete only messages with this label. |
| `--older-than-days` | integer | No | Delete only messages older than this many days. |

**Output**

```json
{"message": "Deleted 17 messages."}
```

**Example**

```sh
email-mcp-cli purge --older-than-days 90
# {"message": "Deleted 17 messages."}

email-mcp-cli purge --label newsletters --account primary
# {"message": "Deleted 5 messages."}
```

---

### email-mcp-cli set-sync-enabled

Enables or disables sync for one or all accounts.

**Usage**

```sh
email-mcp-cli set-sync-enabled <enabled> [--account <name>]
```

**Options**

| Option | Type | Required | Description |
|---|---|---|---|
| `enabled` | boolean | **Yes** | `true` or `false`. |
| `--account` | string | No | Apply to this account only. |

**Output**

```json
{"message": "Sync enabled set to False for primary"}
```

**Example**

```sh
email-mcp-cli set-sync-enabled false --account primary
# {"message": "Sync enabled set to False for primary"}

email-mcp-cli set-sync-enabled true
# {"message": "Sync enabled set to True for 2 accounts"}
```

---

### email-mcp-cli job-status

Shows the status of a background sync job.

**Usage**

```sh
email-mcp-cli job-status <job_id>
```

**Options**

| Option | Type | Required | Description |
|---|---|---|---|
| `job_id` | integer | **Yes** | Job ID returned by `sync`. |

**Output**

```json
{
  "job_id": 7,
  "name": "sync_mailbox",
  "status": "done",
  "account_name": "primary",
  "started_at": "2024-01-18T12:00:00",
  "finished_at": "2024-01-18T12:00:05",
  "message": "count=15"
}
```

**Example**

```sh
email-mcp-cli job-status 7
```



