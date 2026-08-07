# RightsRoute verification status

## Verified package scope

This repository is a standalone Intelligent Contract package. It contains only RightsRoute, its restricted callback consumer, a public fixture, Direct Mode tests, documentation, and verification tooling. It contains no frontend, wallet integration, consumer-market flow, unrelated application contract, or application deployment script.

## Local validation

The targeted Direct Mode suite previously recorded 34 passing tests across:

- all four decision outcomes;
- registered source hash matching and mismatch rollback;
- malformed, unsupported, and contradictory model output;
- policy lifecycle and requester authorization;
- terminal assessment states and client-reference idempotency;
- validator acceptance of matching consensus-critical fields and rejection of divergent fields;
- callback sender authorization, canonical callback input validation, idempotent duplicates, and conflicting duplicate rejection.

Run the current package tests with the pinned dependencies:

```bash
pytest tests/direct/test_rights_route.py \
       tests/direct/test_rights_route_adversarial.py \
       tests/direct/test_rights_route_callback_consumer.py -v
```

Run structural verification without network access:

```bash
python3 scripts/verify_package.py
```

## Hosted Studio validation

The evidence record documents finalized Hosted Studio deployment of both contracts, registration of a commit-pinned public fixture, finalized assessment resolution, terminal-state rollback, and a finalized cross-contract callback receipt. It is available in [Hosted Studio validation](RIGHTSROUTE_STUDIO_VALIDATION.md).

The documented public fixture URL, SHA-256, contract addresses, deployment transactions, and resolution transactions are preserved as historical evidence.

## Boundary of the evidence

The recorded evidence is for **GenLayer Hosted Studio**. It does not make a Bradbury deployment or Bradbury-finality claim. The automatic callback child transaction hash and its validator metadata were not exposed in the captured Studio interface; the finalized parent-to-consumer state correspondence is documented, but that separate child-transaction metadata remains unavailable.

## Production-readiness requirements for integrators

An integrating application must independently handle access control, policy publication, source availability, user disclosure, transaction-state polling, finality monitoring, and human/legal review. See [Integration guide](INTEGRATION_GUIDE.md) and [Security and limits](SECURITY_AND_LIMITS.md).
