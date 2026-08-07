# RightsRoute documentation

RightsRoute is a contract package, not a complete end-user product. It contains two reusable GenLayer Intelligent Contracts, their Direct Mode tests, one public immutable-policy fixture, and evidence for the finalized Hosted Studio workflow.

## Reading order

1. [API reference](API_REFERENCE.md) for public methods and result records.
2. [Architecture specification](RIGHTSROUTE_SPECIFICATION.md) for the consensus and callback model.
3. [Security and limits](SECURITY_AND_LIMITS.md) before integrating any policy workflow.
4. [Integration guide](INTEGRATION_GUIDE.md) for user- and application-facing transaction handling.
5. [Hosted Studio validation](RIGHTSROUTE_STUDIO_VALIDATION.md) for exact finalized evidence.
6. [Verification status](RIGHTSROUTE_STATUS.md) for local coverage and known limits.
7. [Submission correction](SUBMISSION_CORRECTION.md) for the contract-only repository-scope correction.

## Package layout

```text
contracts/
  rights_route.py                    Primary compatibility primitive
  rights_route_callback_consumer.py  Restricted finalized-callback receiver
fixtures/policies/                   Public, hash-pinned sample policy
tests/direct/                        Targeted Direct Mode suite
docs/                                API, architecture, security, integration, evidence
```

No frontend, wallet integration, application workflows, unrelated contracts, consumer-market logic, or application deployment code is included in this submission package.
