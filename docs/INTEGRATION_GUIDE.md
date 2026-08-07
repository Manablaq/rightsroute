# Integration guide

## Application workflow

1. Publish or select a public UTF-8 policy source and calculate the SHA-256 over its exact raw bytes.
2. Call `register_policy` with the URL, hash, title, and policy kind.
3. Present the full declared-use profile to the user before they sign `request_assessment`.
4. Track the returned transaction hash through network consensus and finality; do not require a page refresh to reflect state changes.
5. Read `get_assessment` after the result becomes available. Display the raw decision, obligations, restrictions, source hash, and resolution hash.
6. If a downstream workflow needs an on-chain notification, deploy a receiver with the RightsRoute address fixed in its constructor and use that receiver as `callback_address`.

## Client behavior

Use a transparent transaction state model:

```text
awaiting signature → submitted → consensus in progress → accepted or failed → finalized
```

Persist each transaction hash immediately after submission. Poll the network or contract reads automatically, retain the form data during processing, and refresh application state once the chain result becomes readable. Never describe an assessment as legally approved, enforceable, or final until its write transaction is finalized.

## Safe policy registration

- Fetch the source yourself before signing and calculate the expected SHA-256 from the exact bytes.
- Use a URL that does not require login, cookies, a browser challenge, or client-specific rendering.
- Prefer a content-addressed location or a raw GitHub URL pinned to a commit SHA.
- Do not register private documents, secrets, personal information, or URLs you do not intend validators to fetch.

## Interpreting results

`PERMITTED` and `PERMITTED_WITH_OBLIGATIONS` are textual compatibility outcomes under the supplied profile; they are not legal clearance. `PROHIBITED` indicates a listed restriction in the policy text for the declared profile. `UNDETERMINED` must be shown as unresolved and routed to human review or a revised evidence/profile flow.

For auditable operations, record the policy ID, assessment ID, transaction hash, registered expected hash, returned source hash, use-profile hash, resolution hash, and finality state.
