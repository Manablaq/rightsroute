import json


CONTRACT_PATH = "contracts/rights_route_callback_consumer.py"
RESOLUTION_HASH = "a" * 64


def _address_hex(address) -> str:
    if isinstance(address, (bytes, bytearray)):
        return "0x" + bytes(address).hex()

    if hasattr(address, "as_hex"):
        return address.as_hex

    return str(address)


def _deploy_consumer(direct_deploy, rights_route):
    return direct_deploy(CONTRACT_PATH, _address_hex(rights_route))


def _deliver(
    consumer,
    *,
    assessment_id=1,
    client_reference="studio-callback-001",
    decision="PERMITTED_WITH_OBLIGATIONS",
    obligations_json='["ATTRIBUTION_REQUIRED"]',
    restrictions_json="[]",
    resolution_sha256=RESOLUTION_HASH,
):
    consumer.on_rights_resolution(
        assessment_id,
        client_reference,
        decision,
        obligations_json,
        restrictions_json,
        resolution_sha256,
    )


def test_constructor_rejects_zero_rights_route(
    direct_vm,
    direct_deploy,
):
    zero_address = "0x0000000000000000000000000000000000000000"

    with direct_vm.expect_revert("RightsRoute address cannot be zero"):
        direct_deploy(CONTRACT_PATH, zero_address)


def test_only_configured_rights_route_can_deliver(
    direct_vm,
    direct_deploy,
    direct_alice,
):
    consumer = _deploy_consumer(direct_deploy, direct_alice)

    with direct_vm.expect_revert(
        "Only the configured RightsRoute contract may call this method"
    ):
        _deliver(consumer)

    assert json.loads(consumer.get_config())["receipt_count"] == 0
    assert consumer.has_receipt(1) is False


def test_authorized_callback_is_stored(
    direct_vm,
    direct_deploy,
    direct_alice,
):
    consumer = _deploy_consumer(direct_deploy, direct_alice)

    with direct_vm.prank(direct_alice):
        _deliver(consumer)

    receipt = json.loads(consumer.get_receipt(1))
    config = json.loads(consumer.get_config())

    assert config["receipt_count"] == 1
    assert (
        config["rights_route_address"].lower()
        == _address_hex(direct_alice).lower()
    )
    assert receipt["assessment_id"] == 1
    assert receipt["client_reference"] == "studio-callback-001"
    assert receipt["decision"] == "PERMITTED_WITH_OBLIGATIONS"
    assert receipt["obligations"] == ["ATTRIBUTION_REQUIRED"]
    assert receipt["restrictions"] == []
    assert receipt["resolution_sha256"] == RESOLUTION_HASH
    assert receipt["received_at"]
    assert consumer.has_receipt(1) is True


def test_exact_duplicate_callback_is_idempotent(
    direct_vm,
    direct_deploy,
    direct_alice,
):
    consumer = _deploy_consumer(direct_deploy, direct_alice)

    with direct_vm.prank(direct_alice):
        _deliver(consumer)
        first_receipt = consumer.get_receipt(1)
        _deliver(consumer)

    assert consumer.get_receipt(1) == first_receipt
    assert json.loads(consumer.get_config())["receipt_count"] == 1


def test_conflicting_duplicate_callback_reverts_without_state_change(
    direct_vm,
    direct_deploy,
    direct_alice,
):
    consumer = _deploy_consumer(direct_deploy, direct_alice)

    with direct_vm.prank(direct_alice):
        _deliver(consumer)
        first_receipt = consumer.get_receipt(1)

        with direct_vm.expect_revert("Conflicting duplicate callback"):
            _deliver(
                consumer,
                decision="PROHIBITED",
                obligations_json="[]",
                restrictions_json='["REDISTRIBUTION_PROHIBITED"]',
                resolution_sha256="b" * 64,
            )

    assert consumer.get_receipt(1) == first_receipt
    assert json.loads(consumer.get_config())["receipt_count"] == 1


def test_rejects_noncanonical_array_json(
    direct_vm,
    direct_deploy,
    direct_alice,
):
    consumer = _deploy_consumer(direct_deploy, direct_alice)

    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert(
            "obligations_json must use canonical JSON"
        ):
            _deliver(
                consumer,
                obligations_json='["ATTRIBUTION_REQUIRED", "NOTICE_REQUIRED"]',
            )

    assert consumer.has_receipt(1) is False


def test_rejects_invalid_decision_and_hash(
    direct_vm,
    direct_deploy,
    direct_alice,
):
    consumer = _deploy_consumer(direct_deploy, direct_alice)

    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("Unsupported decision"):
            _deliver(consumer, decision="MAYBE")

        with direct_vm.expect_revert("Invalid resolution SHA-256"):
            _deliver(consumer, resolution_sha256="ABC")

    assert json.loads(consumer.get_config())["receipt_count"] == 0


def test_pickling_enabled_for_callback_receipt(
    direct_vm,
    direct_deploy,
    direct_alice,
):
    direct_vm.check_pickling = True
    consumer = _deploy_consumer(direct_deploy, direct_alice)

    with direct_vm.prank(direct_alice):
        _deliver(consumer)

    receipt = json.loads(consumer.get_receipt(1))
    assert receipt["decision"] == "PERMITTED_WITH_OBLIGATIONS"
    assert json.loads(consumer.get_config())["receipt_count"] == 1
