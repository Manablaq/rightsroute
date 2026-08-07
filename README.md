# RightsRoute

[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e.svg)](LICENSE)
[![GenLayer Studio](https://img.shields.io/badge/GenLayer-Hosted%20Studio-6d5dfc.svg)](https://explorer-studio.genlayer.com/address/0xe8026345019DBCDece926F3C7cDE2E4d693e865c)

**A reusable GenLayer Intelligent Contract primitive for consensus-backed compatibility checks between a declared machine use and a public, hash-pinned policy document.**

RightsRoute registers a public HTTPS policy document with a pre-committed SHA-256 hash, stores a structured use profile, and reaches a bounded decision through GenLayer consensus. It can optionally notify a separate contract only after finalization.

## Repository status

This repository is intentionally scoped for an **Intelligent Contracts** submission. It contains contract source, a restricted callback example, Direct Mode tests, a public hash-pinned fixture, Hosted Studio validation evidence, and contract documentation only.

It does not include the previous user-facing product application, consumer wallet flow, ranking UI, frontend routes, browser app shell, or hosted-app deployment package. Those product artifacts are outside the scope of this contract repository.

## Scope

RightsRoute answers one narrow question: whether a declared use is compatible with the text of the registered policy, and which allow-listed obligations or restrictions the policy states.

It is useful as a primitive for dataset registries, model marketplaces, software/package registries, creator platforms, API access systems, and agent workflows. It is not a legal opinion, policy-enforcement service, ownership registry, identity system, or proof that a policy is authentic or enforceable.

## Contracts

| Contract | Purpose | Hosted Studio reference |
| --- | --- | --- |
| `RightsRoute` | Hash-pinned policy registration, assessment requests, consensus resolution, and optional finalization callback. | [`0xe802…865c`](https://explorer-studio.genlayer.com/address/0xe8026345019DBCDece926F3C7cDE2E4d693e865c) |
| `RightsRouteCallbackConsumer` | Example restricted receiver for finalized RightsRoute callbacks, with idempotent receipt handling. | [`0xd00A…2f7C`](https://explorer-studio.genlayer.com/address/0xd00A72C43412F8693692A26c8213daE459652f7C) |

## Design properties

- Public evidence must be HTTPS, UTF-8, at most 65,536 bytes, and match the SHA-256 registered before resolution.
- Validators independently fetch and evaluate the policy text.
- The validator compares source SHA-256, decision, obligation codes, and restriction codes—the consensus-critical fields.
- Every decision and code is restricted to a fixed vocabulary; malformed or contradictory output is rejected.
- State changes occur only after the nondeterministic consensus call returns.
- An optional callback is emitted with `on="finalized"`; the included consumer accepts messages from only one configured RightsRoute contract.

## Documentation

| Document | Contents |
| --- | --- |
| [Documentation index](docs/README.md) | Reading order and package map. |
| [API reference](docs/API_REFERENCE.md) | Complete public methods, inputs, outputs, and state transitions. |
| [Architecture](docs/RIGHTSROUTE_SPECIFICATION.md) | Consensus design, storage, callback, and bounded decision model. |
| [Security and limits](docs/SECURITY_AND_LIMITS.md) | Trust boundaries and safe-use requirements. |
| [Integration guide](docs/INTEGRATION_GUIDE.md) | Application workflow, transaction handling, and evidence preparation. |
| [Studio evidence](docs/RIGHTSROUTE_STUDIO_VALIDATION.md) | Finalized Hosted Studio deployment, resolution, and callback evidence. |
| [Verification status](docs/RIGHTSROUTE_STATUS.md) | Local test coverage and exact validation boundary. |
| [Submission correction](docs/SUBMISSION_CORRECTION.md) | How the repository addresses the prior scope rejection. |

## Validation

Run the targeted Direct Mode suite after installing the pinned dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/direct/test_rights_route.py \
       tests/direct/test_rights_route_adversarial.py \
       tests/direct/test_rights_route_callback_consumer.py -v
```

Run the offline package checks without a network or wallet:

```bash
python3 scripts/verify_package.py
```

## Evidence and limits

The repository records finalized Hosted Studio evidence for deployment, hash-pinned source resolution, terminal-state protection, and an authorized callback receipt. It does not claim Bradbury deployment or finality. See [Hosted Studio evidence](docs/RIGHTSROUTE_STUDIO_VALIDATION.md) for the precise verified facts and unresolved boundary.

## License

MIT. See [LICENSE](LICENSE).
