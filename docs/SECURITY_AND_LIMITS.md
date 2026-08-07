# Security and limits

## What RightsRoute establishes

For an accepted resolution, RightsRoute establishes that the contract fetched public policy bytes whose SHA-256 matched the value registered for that policy and produced a bounded, consensus-mediated compatibility output for the declared use profile.

It does not establish ownership, authorship, policy authority, policy validity, legal enforceability, jurisdictional applicability, fair use, consent, requester identity, or the truthfulness of the declared use.

## Trust boundaries

| Boundary | Checked by the contract | Not guaranteed by the contract |
| --- | --- | --- |
| Policy URL | HTTPS prefix, bounded URI length, fetched byte size, UTF-8 decoding, and expected SHA-256 match | Publisher identity, permanent availability, TLS endpoint governance, or legal status |
| Registered hash | Raw byte equality at resolution | That the registrar selected the right document or that the document is legally binding |
| Declared use | Fixed vocabulary and deterministic use-profile hash | That the requester’s description is complete or true |
| Model output | Strict JSON shape, bounded sizes, fixed codes, and decision consistency | A universally correct legal interpretation |
| Callback | Configured sender check, canonical arrays, idempotence, and finalization scheduling | Cross-application authorization or business policy outside the receiving contract |

## Evidence safety

Policy text is untrusted evidence. The prompt labels it as such and instructs the model not to follow commands embedded in it. This is a mitigation, not proof that the text is harmless or authoritative.

Use stable, public, non-personal policy sources. Prefer an immutable URL such as a commit-pinned raw file. Preserve the exact bytes, hash, contract address, and finalized transaction hash in the integrating system’s own audit record.

## Public-call and storage model

Any account may register a policy and resolve a requested assessment. Only a policy’s registrar can deactivate it, and only the assessment requester can cancel it. The contract is an open primitive; applications requiring allow-lists, payment, roles, multi-party approval, or private records must implement those controls separately.

The contract holds no funds and performs no token transfers. It must not be represented as escrow, settlement, payment authorization, or legal adjudication.

## Finality and operations

Treat a write as pending until the network marks it final. A wallet broadcast or an accepted consensus status alone is not finality. Handle web-fetch failures, source-hash mismatches, validator disagreement, and network timeouts as non-success outcomes; retain the transaction hash and present the actual network state to users.

Do not use RightsRoute as the sole basis for high-stakes legal, employment, financial, medical, insurance, or safety decisions.
