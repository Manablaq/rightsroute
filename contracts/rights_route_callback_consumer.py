# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

"""
Minimal finalized-callback consumer for RightsRoute.

The contract accepts callbacks only from one immutable RightsRoute contract.
An exact duplicate callback is idempotent. A conflicting callback for an
already-recorded assessment is rejected.
"""

from dataclasses import dataclass
import json

from genlayer import *


ZERO_ADDRESS = Address("0x0000000000000000000000000000000000000000")

VALID_DECISIONS = (
    "PERMITTED",
    "PERMITTED_WITH_OBLIGATIONS",
    "PROHIBITED",
    "UNDETERMINED",
)

MAX_CLIENT_REFERENCE_CHARS = 128
MAX_ARRAY_JSON_CHARS = 4_096


def _fail(message: str) -> None:
    raise gl.vm.UserError(message)


def _canonical_json(value) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _is_lower_hex_sha256(value: str) -> bool:
    return (
        len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _validate_string_array_json(raw: str, field_name: str) -> None:
    if len(raw) > MAX_ARRAY_JSON_CHARS:
        _fail(f"{field_name} is too large")

    try:
        parsed = json.loads(raw)
    except Exception:
        _fail(f"{field_name} must be valid JSON")

    if not isinstance(parsed, list):
        _fail(f"{field_name} must be a JSON array")

    seen: list[str] = []
    for item in parsed:
        if not isinstance(item, str) or item == "":
            _fail(f"{field_name} must contain non-empty strings")
        if item in seen:
            _fail(f"{field_name} must not contain duplicates")
        seen.append(item)

    if _canonical_json(parsed) != raw:
        _fail(f"{field_name} must use canonical JSON")


@allow_storage
@dataclass
class ResolutionReceipt:
    assessment_id: u256
    client_reference: str
    decision: str
    obligations_json: str
    restrictions_json: str
    resolution_sha256: str
    origin_address: Address
    received_at: str


class RightsRouteCallbackConsumer(gl.Contract):
    rights_route_address: Address
    receipts: TreeMap[u256, ResolutionReceipt]
    receipt_count: u256

    def __init__(self, rights_route_address: str):
        try:
            normalized_rights_route_address = Address(rights_route_address)
        except Exception:
            _fail("Invalid RightsRoute address")

        if normalized_rights_route_address == ZERO_ADDRESS:
            _fail("RightsRoute address cannot be zero")

        self.rights_route_address = normalized_rights_route_address
        self.receipt_count = u256(0)

    def _require_receipt(self, assessment_id: u256) -> None:
        if assessment_id not in self.receipts:
            _fail("Unknown callback receipt")

    def _matches_existing(
        self,
        existing: ResolutionReceipt,
        assessment_id: u256,
        client_reference: str,
        decision: str,
        obligations_json: str,
        restrictions_json: str,
        resolution_sha256: str,
        origin_address: Address,
    ) -> bool:
        return (
            existing.assessment_id == assessment_id
            and existing.client_reference == client_reference
            and existing.decision == decision
            and existing.obligations_json == obligations_json
            and existing.restrictions_json == restrictions_json
            and existing.resolution_sha256 == resolution_sha256
            and existing.origin_address == origin_address
        )

    @gl.public.write
    def on_rights_resolution(
        self,
        assessment_id: u256,
        client_reference: str,
        decision: str,
        obligations_json: str,
        restrictions_json: str,
        resolution_sha256: str,
    ) -> None:
        if gl.message.sender_address != self.rights_route_address:
            _fail("Only the configured RightsRoute contract may call this method")

        if assessment_id == u256(0):
            _fail("Assessment ID must be positive")

        if client_reference == "" or len(client_reference) > MAX_CLIENT_REFERENCE_CHARS:
            _fail("Invalid client reference")

        if decision not in VALID_DECISIONS:
            _fail("Unsupported decision")

        _validate_string_array_json(obligations_json, "obligations_json")
        _validate_string_array_json(restrictions_json, "restrictions_json")

        if not _is_lower_hex_sha256(resolution_sha256):
            _fail("Invalid resolution SHA-256")

        origin_address = gl.message.origin_address

        if assessment_id in self.receipts:
            existing = self.receipts[assessment_id]
            if not self._matches_existing(
                existing,
                assessment_id,
                client_reference,
                decision,
                obligations_json,
                restrictions_json,
                resolution_sha256,
                origin_address,
            ):
                _fail("Conflicting duplicate callback")
            return

        self.receipts[assessment_id] = ResolutionReceipt(
            assessment_id=assessment_id,
            client_reference=client_reference,
            decision=decision,
            obligations_json=obligations_json,
            restrictions_json=restrictions_json,
            resolution_sha256=resolution_sha256,
            origin_address=origin_address,
            received_at=gl.message_raw["datetime"],
        )
        self.receipt_count = self.receipt_count + u256(1)

    @gl.public.view
    def has_receipt(self, assessment_id: u256) -> bool:
        return assessment_id in self.receipts

    @gl.public.view
    def get_config(self) -> str:
        return _canonical_json(
            {
                "receipt_count": int(self.receipt_count),
                "rights_route_address": self.rights_route_address.as_hex,
            }
        )

    @gl.public.view
    def get_receipt(self, assessment_id: u256) -> str:
        self._require_receipt(assessment_id)
        receipt = self.receipts[assessment_id]

        return _canonical_json(
            {
                "assessment_id": int(receipt.assessment_id),
                "client_reference": receipt.client_reference,
                "decision": receipt.decision,
                "obligations": json.loads(receipt.obligations_json),
                "origin_address": receipt.origin_address.as_hex,
                "received_at": receipt.received_at,
                "resolution_sha256": receipt.resolution_sha256,
                "restrictions": json.loads(receipt.restrictions_json),
            }
        )
