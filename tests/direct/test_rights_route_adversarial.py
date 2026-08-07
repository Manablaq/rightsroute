"""Adversarial Direct Mode coverage for RightsRoute v0.2.

This file intentionally does not modify the contract. It expands behavioral,
consensus, authorization, failure, terminal-state, and serialization coverage
against the already lint-green and Direct-Mode-green RightsRoute baseline.
"""

import hashlib
import json


CONTRACT_PATH = "contracts/rights_route.py"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
POLICY_URL = "https://example.org/licenses/rightsroute-adversarial.txt"

BASE_POLICY_TEXT = """RightsRoute Test Policy

Section 1. General Permission.
Internal and commercial use are permitted unless another section restricts
the requested operation.

Section 2. Attribution.
Public derivatives require attribution to the publisher.

Section 3. Redistribution.
Redistribution of the original asset is prohibited.

Section 4. Unspecified Uses.
Uses not addressed by this policy require separate clarification.
"""


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _deploy_and_register(
    direct_vm,
    direct_deploy,
    sender,
    *,
    policy_text: str = BASE_POLICY_TEXT,
    title: str = "RightsRoute Test Policy",
    policy_kind: str = "LICENSE",
):
    contract = direct_deploy(CONTRACT_PATH)
    direct_vm.sender = sender
    policy_id = contract.register_policy(
        title,
        POLICY_URL,
        _sha256_text(policy_text),
        policy_kind,
    )
    return contract, policy_id


def _request(
    contract,
    *,
    policy_id=1,
    client_reference="adversarial-order-001",
    operation="MODEL_TRAINING",
    commercial=True,
    redistributes_original=False,
    distributes_derivative=True,
    attribution_planned=True,
    intended_audience="PUBLIC",
):
    return contract.request_assessment(
        policy_id,
        client_reference,
        "DATASET",
        operation,
        commercial,
        redistributes_original,
        distributes_derivative,
        attribution_planned,
        intended_audience,
        ZERO_ADDRESS,
    )


def _mock_policy(direct_vm, policy_text: str = BASE_POLICY_TEXT):
    direct_vm.mock_web(
        r".*example\.org/licenses/rightsroute-adversarial\.txt",
        {"status": 200, "body": policy_text},
    )


def _llm_payload(
    *,
    decision,
    obligations=None,
    restrictions=None,
    evidence=None,
    summary="Evidence-grounded RightsRoute test result.",
):
    if obligations is None:
        obligations = []
    if restrictions is None:
        restrictions = []
    if evidence is None:
        evidence = [
            {
                "section": "Section 1",
                "excerpt": "Internal and commercial use are permitted.",
                "supports": "DECISION",
            }
        ]

    return {
        "decision": decision,
        "obligations": obligations,
        "restrictions": restrictions,
        "evidence": evidence,
        "summary": summary,
    }


def _mock_llm(direct_vm, payload):
    direct_vm.mock_llm(
        r".*RIGHTSROUTE_DECISION_V1.*",
        json.dumps(payload),
    )


def _resolve_with(
    direct_vm,
    contract,
    payload,
    *,
    policy_text: str = BASE_POLICY_TEXT,
    assessment_id=1,
):
    _mock_policy(direct_vm, policy_text)
    _mock_llm(direct_vm, payload)
    contract.resolve_assessment(assessment_id)


def _get_assessment(contract, assessment_id=1):
    return json.loads(contract.get_assessment(assessment_id))


def test_permitted_resolution_has_no_obligations_or_restrictions(
    direct_vm, direct_deploy, direct_alice
):
    contract, _ = _deploy_and_register(direct_vm, direct_deploy, direct_alice)
    _request(
        contract,
        operation="INTERNAL_USE",
        commercial=False,
        distributes_derivative=False,
        attribution_planned=False,
        intended_audience="PRIVATE",
    )

    _resolve_with(
        direct_vm,
        contract,
        _llm_payload(
            decision="PERMITTED",
            evidence=[
                {
                    "section": "Section 1",
                    "excerpt": "Internal and commercial use are permitted.",
                    "supports": "DECISION",
                }
            ],
            summary="Private internal use is permitted without a listed obligation.",
        ),
    )

    result = _get_assessment(contract)
    assert result["status"] == "RESOLVED"
    assert result["decision"] == "PERMITTED"
    assert result["obligations"] == []
    assert result["restrictions"] == []


def test_prohibited_resolution_records_blocking_restriction(
    direct_vm, direct_deploy, direct_alice
):
    contract, _ = _deploy_and_register(direct_vm, direct_deploy, direct_alice)
    _request(
        contract,
        operation="REDISTRIBUTE",
        redistributes_original=True,
        distributes_derivative=False,
    )

    _resolve_with(
        direct_vm,
        contract,
        _llm_payload(
            decision="PROHIBITED",
            restrictions=["REDISTRIBUTION_FORBIDDEN"],
            evidence=[
                {
                    "section": "Section 3",
                    "excerpt": "Redistribution of the original asset is prohibited.",
                    "supports": "RESTRICTION",
                }
            ],
            summary="The declared use redistributes the original asset and is prohibited.",
        ),
    )

    result = _get_assessment(contract)
    assert result["decision"] == "PROHIBITED"
    assert result["obligations"] == []
    assert result["restrictions"] == ["REDISTRIBUTION_FORBIDDEN"]


def test_undetermined_resolution_records_ambiguity_without_false_restriction(
    direct_vm, direct_deploy, direct_alice
):
    contract, _ = _deploy_and_register(direct_vm, direct_deploy, direct_alice)
    _request(contract, operation="SUBLICENSE")

    _resolve_with(
        direct_vm,
        contract,
        _llm_payload(
            decision="UNDETERMINED",
            evidence=[
                {
                    "section": "Section 4",
                    "excerpt": "Uses not addressed by this policy require separate clarification.",
                    "supports": "AMBIGUITY",
                }
            ],
            summary="The policy does not determine whether sublicensing is permitted.",
        ),
    )

    result = _get_assessment(contract)
    assert result["decision"] == "UNDETERMINED"
    assert result["restrictions"] == []
    assert result["summary"]


def test_malformed_llm_response_reverts_without_resolving(
    direct_vm, direct_deploy, direct_alice
):
    contract, _ = _deploy_and_register(direct_vm, direct_deploy, direct_alice)
    _request(contract)
    _mock_policy(direct_vm)
    direct_vm.mock_llm(
        r".*RIGHTSROUTE_DECISION_V1.*",
        json.dumps("not-a-json-object"),
    )

    with direct_vm.expect_revert("LLM response must be a JSON object"):
        contract.resolve_assessment(1)

    result = _get_assessment(contract)
    assert result["status"] == "REQUESTED"
    assert result["decision"] == ""


def test_unsupported_obligation_code_reverts_without_resolving(
    direct_vm, direct_deploy, direct_alice
):
    contract, _ = _deploy_and_register(direct_vm, direct_deploy, direct_alice)
    _request(contract)
    _mock_policy(direct_vm)
    _mock_llm(
        direct_vm,
        _llm_payload(
            decision="PERMITTED_WITH_OBLIGATIONS",
            obligations=["UNSUPPORTED_PAYMENT_REQUIRED"],
        ),
    )

    with direct_vm.expect_revert("unsupported code"):
        contract.resolve_assessment(1)

    assert _get_assessment(contract)["status"] == "REQUESTED"


def test_contradictory_permitted_result_reverts_without_resolving(
    direct_vm, direct_deploy, direct_alice
):
    contract, _ = _deploy_and_register(direct_vm, direct_deploy, direct_alice)
    _request(contract)
    _mock_policy(direct_vm)
    _mock_llm(
        direct_vm,
        _llm_payload(
            decision="PERMITTED",
            obligations=["ATTRIBUTION_REQUIRED"],
        ),
    )

    with direct_vm.expect_revert(
        "PERMITTED must not include obligations or restrictions"
    ):
        contract.resolve_assessment(1)

    assert _get_assessment(contract)["status"] == "REQUESTED"


def test_oversized_summary_reverts_without_resolving(
    direct_vm, direct_deploy, direct_alice
):
    contract, _ = _deploy_and_register(direct_vm, direct_deploy, direct_alice)
    _request(contract)
    _mock_policy(direct_vm)
    _mock_llm(
        direct_vm,
        _llm_payload(
            decision="PERMITTED",
            summary="x" * 1001,
        ),
    )

    with direct_vm.expect_revert("LLM summary is empty or too long"):
        contract.resolve_assessment(1)

    assert _get_assessment(contract)["status"] == "REQUESTED"


def test_oversized_policy_source_reverts_without_llm_or_state_change(
    direct_vm, direct_deploy, direct_alice
):
    oversized_policy = "x" * 65_537
    contract, _ = _deploy_and_register(
        direct_vm,
        direct_deploy,
        direct_alice,
        policy_text=oversized_policy,
    )
    _request(contract)
    _mock_policy(direct_vm, oversized_policy)

    with direct_vm.expect_revert("Policy source exceeds the V1 size limit"):
        contract.resolve_assessment(1)

    result = _get_assessment(contract)
    assert result["status"] == "REQUESTED"
    assert result["source_sha256"] == ""


def test_only_registrar_can_deactivate_policy(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract, policy_id = _deploy_and_register(
        direct_vm, direct_deploy, direct_alice
    )

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("Only the policy registrar can deactivate it"):
        contract.deactivate_policy(policy_id)

    assert json.loads(contract.get_policy(policy_id))["active"] is True


def test_inactive_policy_rejects_new_assessment(
    direct_vm, direct_deploy, direct_alice
):
    contract, policy_id = _deploy_and_register(
        direct_vm, direct_deploy, direct_alice
    )
    contract.deactivate_policy(policy_id)

    with direct_vm.expect_revert("Policy is inactive"):
        _request(contract, policy_id=policy_id)


def test_existing_request_remains_resolvable_after_policy_deactivation(
    direct_vm, direct_deploy, direct_alice
):
    contract, policy_id = _deploy_and_register(
        direct_vm, direct_deploy, direct_alice
    )
    _request(contract, policy_id=policy_id)
    contract.deactivate_policy(policy_id)

    _resolve_with(
        direct_vm,
        contract,
        _llm_payload(
            decision="PERMITTED_WITH_OBLIGATIONS",
            obligations=["ATTRIBUTION_REQUIRED"],
            evidence=[
                {
                    "section": "Section 2",
                    "excerpt": "Public derivatives require attribution to the publisher.",
                    "supports": "OBLIGATION",
                }
            ],
            summary="The pre-existing request remains evaluable and requires attribution.",
        ),
    )

    assert _get_assessment(contract)["decision"] == "PERMITTED_WITH_OBLIGATIONS"


def test_only_requester_can_cancel(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract, _ = _deploy_and_register(direct_vm, direct_deploy, direct_alice)
    _request(contract)

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("Only the requester can cancel"):
        contract.cancel_assessment(1)

    direct_vm.sender = direct_alice
    contract.cancel_assessment(1)
    assert _get_assessment(contract)["status"] == "CANCELLED"


def test_cancelled_assessment_cannot_be_resolved(
    direct_vm, direct_deploy, direct_alice
):
    contract, _ = _deploy_and_register(direct_vm, direct_deploy, direct_alice)
    _request(contract)
    contract.cancel_assessment(1)

    with direct_vm.expect_revert("Assessment is not resolvable"):
        contract.resolve_assessment(1)


def test_resolved_assessment_is_terminal(
    direct_vm, direct_deploy, direct_alice
):
    contract, _ = _deploy_and_register(direct_vm, direct_deploy, direct_alice)
    _request(contract)
    _resolve_with(
        direct_vm,
        contract,
        _llm_payload(
            decision="PERMITTED_WITH_OBLIGATIONS",
            obligations=["ATTRIBUTION_REQUIRED"],
        ),
    )

    with direct_vm.expect_revert("Only a requested assessment can be cancelled"):
        contract.cancel_assessment(1)

    with direct_vm.expect_revert("Assessment is not resolvable"):
        contract.resolve_assessment(1)


def test_same_client_reference_is_allowed_for_different_requesters(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    contract, _ = _deploy_and_register(direct_vm, direct_deploy, direct_alice)

    alice_id = _request(contract, client_reference="shared-reference")
    direct_vm.sender = direct_bob
    bob_id = _request(contract, client_reference="shared-reference")

    assert int(alice_id) == 1
    assert int(bob_id) == 2


def test_validator_accepts_different_explanation_with_same_critical_fields(
    direct_vm, direct_deploy, direct_alice
):
    contract, _ = _deploy_and_register(direct_vm, direct_deploy, direct_alice)
    _request(contract)

    _resolve_with(
        direct_vm,
        contract,
        _llm_payload(
            decision="PERMITTED_WITH_OBLIGATIONS",
            obligations=["ATTRIBUTION_REQUIRED"],
            evidence=[
                {
                    "section": "Section 2",
                    "excerpt": "Public derivatives require attribution to the publisher.",
                    "supports": "OBLIGATION",
                }
            ],
            summary="Leader explanation.",
        ),
    )

    direct_vm.clear_mocks()
    _mock_policy(direct_vm)
    _mock_llm(
        direct_vm,
        _llm_payload(
            decision="PERMITTED_WITH_OBLIGATIONS",
            obligations=["ATTRIBUTION_REQUIRED"],
            evidence=[
                {
                    "section": "Attribution clause",
                    "excerpt": "Public derivatives require attribution.",
                    "supports": "OBLIGATION",
                }
            ],
            summary="Validator uses different prose but reaches the same material result.",
        ),
    )

    assert direct_vm.run_validator() is True


def test_validator_rejects_different_obligations_with_same_decision(
    direct_vm, direct_deploy, direct_alice
):
    contract, _ = _deploy_and_register(direct_vm, direct_deploy, direct_alice)
    _request(contract)

    _resolve_with(
        direct_vm,
        contract,
        _llm_payload(
            decision="PERMITTED_WITH_OBLIGATIONS",
            obligations=["ATTRIBUTION_REQUIRED"],
        ),
    )

    direct_vm.clear_mocks()
    _mock_policy(direct_vm)
    _mock_llm(
        direct_vm,
        _llm_payload(
            decision="PERMITTED_WITH_OBLIGATIONS",
            obligations=["LICENSE_NOTICE_REQUIRED"],
            summary="Validator derives a materially different obligation.",
        ),
    )

    assert direct_vm.run_validator() is False


def test_pickling_enabled_for_full_resolution_flow(
    direct_vm, direct_deploy, direct_alice
):
    direct_vm.check_pickling = True

    contract, _ = _deploy_and_register(direct_vm, direct_deploy, direct_alice)
    _request(contract)
    _resolve_with(
        direct_vm,
        contract,
        _llm_payload(
            decision="PERMITTED_WITH_OBLIGATIONS",
            obligations=["ATTRIBUTION_REQUIRED"],
        ),
    )

    result = _get_assessment(contract)
    assert result["status"] == "RESOLVED"
    assert len(result["resolution_sha256"]) == 64
