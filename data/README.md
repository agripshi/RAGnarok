# Local-folder demo — mapped to the "Documents - Engineering Albania" Teams channel

This folder lets RAGnarok demo answering questions "from a Teams channel" **without** any
Microsoft Graph / SharePoint integration (which is not implemented — see
`docs/TEAMS_CHANNEL_DOCUMENT_ACCESS_VERIFICATION.md`).

Instead of reading the channel's SharePoint document library over Graph, the AI backend
ingests the local files in `data/hr-docs/` and **tags** each chunk with the real channel's
identifiers, so the rest of the system behaves exactly as if the documents came from the
channel.

## Mapped channel

| Field | Value |
|-------|-------|
| Channel name | `Documents - Engineering Albania` |
| Team / group ID | `1531e68a-4716-43aa-bc3b-41b11451cbbb` |
| Channel ID | `19:11b56c75623d48ac828e2797373cacae@thread.tacv2` |
| Tenant ID | `f2d7d6c5-1bee-41ff-9e79-b372a5cce71d` |

These IDs are configured as defaults in `apps/api/app/core/config.py`
(`team_id` / `hr_private_channel_id`) and `apps/ai/app/core/config.py`
(`default_team_id` / `default_channel_id`), and in the matching `.env.example` files.
Ingestion tags (`team_id`, `channel_id`) must equal the retrieval scope, otherwise queries
return `NOT_FOUND`.

## How it works

1. On AI backend startup (`apps/ai/app/main.py` lifespan), documents in `hr-docs/` are
   auto-ingested with `default_team_id` / `default_channel_id`.
2. Each `*.md` / `*.pdf` / `*.docx` / `*.txt` file may have a sidecar
   `<filename>.metadata.json` providing `office`, `language`, `modified_at`, and
   `source_url`.
3. The `source_url` in the sidecars is set to the **real channel deep link**, so the
   "Open source" link on each answer's source card opens the actual Teams channel.

## Files in `hr-docs/`

| Document | Language | Office |
|----------|----------|--------|
| `engineering-albania-leave-policy.md` | English | albania |
| `engineering-albania-working-hours.md` | English | albania |
| `politika-burimeve-njerezore-shqiperi.md` | Albanian (sq) | albania |

> Note: only files inside `hr-docs/` are ingested. This `README.md` lives one level up in
> `data/` on purpose, so it is **not** indexed.

## Re-ingesting

Auto-ingest runs on AI backend startup. To trigger manually:

```bash
curl -X POST http://localhost:8001/ai/ingest/sync \
  -H "Authorization: Bearer dev-internal-token" \
  -H "Content-Type: application/json" \
  -d '{"source_mode":"local","team_id":"1531e68a-4716-43aa-bc3b-41b11451cbbb","channel_id":"19:11b56c75623d48ac828e2797373cacae@thread.tacv2","force_reindex":true}'
```

Or, as an admin user, via the backend API: `POST /api/admin/ingest/sync`.
