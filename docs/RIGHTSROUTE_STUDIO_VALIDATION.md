# RightsRoute Hosted Studio Validation

## Environment

- Validation date: 2026-08-01
- Environment: GenLayer Hosted Studio
- Studio execution mode: Normal (Full Consensus)
- RightsRoute address: `0xe8026345019DBCDece926F3C7cDE2E4d693e865c`
- Callback consumer address: `0xd00A72C43412F8693692A26c8213daE459652f7C`

## Deployment

Deployment transaction:

`0x3a254e1e53dd1aabdf8a2270f8d63abacbea81d7d685a0773a73b440eeee6d4b`

Result:

- Status: `FINALIZED`
- Execution result: `SUCCESS`
- Five validators agreed on deployment.

## Callback consumer deployment

Consumer address:

`0xd00A72C43412F8693692A26c8213daE459652f7C`

Deployment transaction:

`0xa15362fc96554ea5601633fe3a99833401408abd6373d9693959422bd69a6290`

Constructor configuration:

`0xe8026345019DBCDece926F3C7cDE2E4d693e865c`

Result:

- Status: `FINALIZED`
- Execution result: `SUCCESS`
- Five validators agreed.
- Finalized `get_config` returned a receipt count of `0` and the expected
  immutable RightsRoute address.
- Finalized `has_receipt(2)` returned `false` before the callback assessment.

## Immutable policy fixture

Policy ID: `1`

Fixture commit:

`3db67a297b8df3017365c0f6b9603075290066c5`

Fixture URI:

`https://raw.githubusercontent.com/Manablaq/rightsroute/3db67a297b8df3017365c0f6b9603075290066c5/fixtures/policies/dataset_policy_v1.txt`

Expected and fetched SHA-256:

`18f003993472c55475710908ba1921d3aa5f561c175e9f59ecc59d8bada53551`

Exact fixture size:

`580` bytes

The finalized policy record stored the expected URI, SHA-256, kind, registrar,
and active state.

## Assessment request

Assessment ID: `1`

Client reference:

`studio-conditional-001`

Declared use:

- Asset kind: `DATASET`
- Operation: `MODEL_TRAINING`
- Commercial: `true`
- Redistributes original: `false`
- Distributes derivative: `true`
- Attribution planned: `false`
- Intended audience: `PUBLIC`
- Callback: zero address

Use-profile SHA-256:

`541101824cd92e575f260e19c617feb5522fdf014403ba0fe8bfb17bf134ec29`

The finalized pre-resolution state was `REQUESTED`, with no decision,
obligations, restrictions, evidence, source hash, or resolution hash.

## Successful resolution

Transaction:

`0x399bea7f97c58c280b7496e954822570449fe8bb5a10e1c540185336dc773803`

Result:

- Status: `FINALIZED`
- Execution result: `SUCCESS`
- Decision: `PERMITTED_WITH_OBLIGATIONS`
- Obligations: `["ATTRIBUTION_REQUIRED"]`
- Restrictions: `[]`

Consensus observations:

- Three validators agreed.
- One validator disagreed.
- One validator execution was cancelled after quorum.
- The supplied Studio record does not expose the disagreeing validator's
  alternative result, so its reason is unresolved.

Stored source SHA-256:

`18f003993472c55475710908ba1921d3aa5f561c175e9f59ecc59d8bada53551`

Stored resolution SHA-256:

`88c6a6a20820de516ba23bbab9d1e9bbb13f0da890327947ac5a5681ffecd0ee`

The finalized state was `RESOLVED` and contained a non-empty summary,
three policy evidence excerpts, the expected obligation, and no restriction.

## Terminal-state enforcement

Duplicate resolution transaction:

`0x4e1ad7fbad470f504972b7415ad122fcc8b7fbb44d026999a73b5330d1a530c8`

Second duplicate resolution transaction:

`0x1c8946367f872c05c1f79bb529923d77126a1b1fd29635cf5fe28301a89b8f38`

Both transactions:

- reached `FINALIZED`;
- had execution result `ERROR`;
- were rejected with `[rollback] Assessment is not resolvable`;
- had unanimous validator agreement on the rollback.

This verifies that a resolved assessment is terminal and duplicate resolution
attempts cannot modify its state.

## Finalized callback validation

Assessment ID: `2`

Client reference:

`studio-callback-002`

Callback address:

`0xd00A72C43412F8693692A26c8213daE459652f7C`

The request used the same declared use profile as assessment `1`. Its finalized
pre-resolution state was `REQUESTED`, and the stored callback address matched
the deployed consumer.

Resolution transaction:

`0x7cc41c979b3702cea17fe7bfef8430470bf2085e455a06144303aa94e5832e31`

Result:

- Status: `FINALIZED`
- Execution result: `SUCCESS`
- Decision: `PERMITTED_WITH_OBLIGATIONS`
- Obligations: `["ATTRIBUTION_REQUIRED"]`
- Restrictions: `[]`
- Three validators agreed.
- One validator disagreed.
- One validator execution was cancelled after quorum.

Stored source SHA-256:

`18f003993472c55475710908ba1921d3aa5f561c175e9f59ecc59d8bada53551`

Stored resolution SHA-256:

`e1aa03447b22101b3f6e3156f92c1458efb89484fdf4084633d96b9bc0522b15`

The RightsRoute assessment resolved at:

`2026-08-01T01:38:34.345128Z`

Finalized consumer reads after resolution returned:

- `receipt_count`: `1`
- `has_receipt(2)`: `true`
- Assessment ID: `2`
- Client reference: `studio-callback-002`
- Decision: `PERMITTED_WITH_OBLIGATIONS`
- Obligations: `["ATTRIBUTION_REQUIRED"]`
- Restrictions: `[]`
- Resolution SHA-256:
  `e1aa03447b22101b3f6e3156f92c1458efb89484fdf4084633d96b9bc0522b15`
- Received at: `2026-08-01T01:39:21.081643Z`
- Observed stored origin address:
  `0xe8026345019DBCDece926F3C7cDE2E4d693e865c`

The consumer receipt hash exactly matched the finalized RightsRoute assessment
hash. The consumer permits this write method only when the immediate sender is
its configured RightsRoute contract, establishing that the authorized
finalized callback path persisted the receipt.

The stored `origin_address` is recorded as an observed runtime value only. In
this Hosted Studio execution it was the RightsRoute contract address; it is not
documented here as the original external requester.

Hosted Studio displayed only the consumer deployment in the consumer
transaction list. It did not expose the automatically triggered callback
transaction hash, validator set, or trigger metadata in the available panel.

## Remaining validation boundary

This hosted-Studio run verifies:

- deployment under full consensus;
- finalized reads and writes;
- immutable public evidence fetching;
- exact source-byte hashing;
- live LLM evaluation;
- validator equivalence voting;
- finalized result persistence;
- terminal-state rollback;
- deployment of a restricted callback consumer;
- nonzero callback configuration;
- finalized callback delivery;
- cross-contract receipt persistence;
- exact parent-to-consumer resolution-hash correspondence.

The callback child transaction hash and its validator metadata were not exposed
by the available Hosted Studio transaction panel. That metadata remains
unresolved, while the finalized cross-contract state transition is verified.
