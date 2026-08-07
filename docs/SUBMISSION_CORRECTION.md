# RightsRoute submission correction

This document records the repository-scope correction for the RightsRoute Intelligent Contract submission.

## Correction summary

RightsRoute is now packaged as a standalone GenLayer Intelligent Contract repository. The repository contains only:

- `contracts/rights_route.py`
- `contracts/rights_route_callback_consumer.py`
- Direct Mode tests for the primary contract and callback consumer
- a hash-pinned public policy fixture
- contract documentation
- Hosted Studio validation evidence
- offline package-verification tooling

The repository no longer presents itself as an end-user product. It does not contain a frontend application, product routes, hosted-app package, consumer UI shell, or unrelated application workflows.

## Contract boundary

RightsRoute evaluates a declared software, dataset, model, content, or API use against immutable public policy text. The contract:

1. registers a public HTTPS policy URL and expected SHA-256;
2. records a structured declared-use profile;
3. fetches the public policy source during GenLayer consensus;
4. rejects the resolution if the fetched bytes do not match the registered hash;
5. restricts decisions and codes to fixed vocabularies;
6. stores obligations, restrictions, evidence excerpts, source hashes, and resolution hashes; and
7. optionally emits a finalized callback to a restricted receiver contract.

## What was not changed

The correction is a repository-scope and documentation correction. It does not invent a new product claim or broaden the contract’s authority. RightsRoute remains a bounded compatibility primitive, not a legal-opinion engine, ownership registry, identity system, or enforcement service.

## Verification files

Reviewers can inspect:

- [API reference](API_REFERENCE.md)
- [Architecture specification](RIGHTSROUTE_SPECIFICATION.md)
- [Security and limits](SECURITY_AND_LIMITS.md)
- [Hosted Studio validation](RIGHTSROUTE_STUDIO_VALIDATION.md)
- [Verification status](RIGHTSROUTE_STATUS.md)

The offline guard `scripts/verify_package.py` fails if common frontend/product artifacts are reintroduced at the repository root.
