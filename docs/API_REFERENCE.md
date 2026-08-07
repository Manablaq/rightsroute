# API reference

## `RightsRoute`

### `register_policy`

```python
register_policy(title, policy_uri, expected_sha256, policy_kind) -> u256
```

Registers one policy record and returns its sequential `policy_id`.

| Input | Requirements |
| --- | --- |
| `title` | Non-empty; 160 characters or fewer. |
| `policy_uri` | Public HTTPS URL; 512 characters or fewer. |
| `expected_sha256` | Exactly 64 lowercase hexadecimal characters, calculated over the raw policy response bytes. |
| `policy_kind` | One of `LICENSE`, `TERMS_OF_USE`, `DATA_POLICY`, `MODEL_POLICY`, `API_POLICY`, or `CONTENT_POLICY`. |

The caller becomes the policy registrar. A registered policy begins in the `ACTIVE` state.

### `deactivate_policy`

```python
deactivate_policy(policy_id) -> None
```

Only the original registrar may deactivate an active policy. Deactivation prevents new assessment requests; it does not rewrite existing policy or assessment records.

### `request_assessment`

```python
request_assessment(
    policy_id,
    client_reference,
    asset_kind,
    operation,
    commercial,
    redistributes_original,
    distributes_derivative,
    attribution_planned,
    intended_audience,
    callback_address,
) -> u256
```

Creates an assessment in `REQUESTED` state and returns its sequential `assessment_id`. The pair `(requester, client_reference)` is unique.

`asset_kind` is one of `SOFTWARE`, `DATASET`, `AI_MODEL`, `DIGITAL_CONTENT`, or `API_OR_SERVICE`.

`operation` is one of `INTERNAL_USE`, `COMMERCIAL_USE`, `COPY`, `MODIFY`, `REDISTRIBUTE`, `CREATE_DERIVATIVE`, `MODEL_TRAINING`, `FINE_TUNING`, `EMBEDDING_OR_INDEXING`, `HOST_AS_SERVICE`, `GENERATE_OUTPUTS`, or `SUBLICENSE`.

`intended_audience` is one of `PRIVATE`, `ORGANIZATION`, `CUSTOMERS`, or `PUBLIC`. `callback_address` must parse as a GenLayer address; use the zero address when no callback is required.

### `cancel_assessment`

```python
cancel_assessment(assessment_id) -> None
```

Only the requester may cancel an assessment, and only while its status is `REQUESTED`. `CANCELLED` and `RESOLVED` are terminal states.

### `resolve_assessment`

```python
resolve_assessment(assessment_id) -> None
```

Public write method. Anyone can request resolution of a `REQUESTED` assessment. The leader and validators independently fetch the policy URL and require the fetched SHA-256 to equal the registered value before the model evaluation can produce an accepted result.

The accepted result has one decision: `PERMITTED`, `PERMITTED_WITH_OBLIGATIONS`, `PROHIBITED`, or `UNDETERMINED`.

Obligation codes and restriction codes are allow-listed in the source. The contract rejects malformed, unsupported, duplicated, or contradictory model output. An optional callback is queued only after result storage and only with `on="finalized"`.

### View methods

| Method | Returns |
| --- | --- |
| `get_policy(policy_id)` | Canonical JSON policy record, including registrar, URI, expected hash, kind, active state, and registration time. |
| `get_assessment(assessment_id)` | Canonical JSON assessment, including declared-use profile, status, decision, codes, evidence, source hash, and resolution hash. |
| `get_counts()` | Canonical JSON counts for policies and assessments. |

## `RightsRouteCallbackConsumer`

Constructor:

```python
RightsRouteCallbackConsumer(rights_route_address)
```

The constructor requires a nonzero RightsRoute address. It is immutable after deployment.

| Method | Access | Behaviour |
| --- | --- | --- |
| `on_rights_resolution(...)` | Write | Accepts a callback only when `gl.message.sender_address` is the configured RightsRoute address. Exact duplicates are idempotent; conflicting duplicates revert. |
| `has_receipt(assessment_id)` | View | Returns whether a receipt exists. |
| `get_config()` | View | Returns the configured RightsRoute address and receipt count as canonical JSON. |
| `get_receipt(assessment_id)` | View | Returns the canonical receipt or fails for an unknown ID. |

The consumer is an example of a safe downstream receiver. It does not itself establish the original user identity or policy validity.
