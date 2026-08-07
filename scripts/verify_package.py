#!/usr/bin/env python3
"""Offline structure and source-integrity checks for the RightsRoute package."""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = (
    "contracts/rights_route.py",
    "contracts/rights_route_callback_consumer.py",
    "fixtures/policies/dataset_policy_v1.txt",
    "docs/README.md",
    "docs/API_REFERENCE.md",
    "docs/RIGHTSROUTE_SPECIFICATION.md",
    "docs/RIGHTSROUTE_STUDIO_VALIDATION.md",
    "docs/RIGHTSROUTE_STATUS.md",
    "docs/SECURITY_AND_LIMITS.md",
    "docs/INTEGRATION_GUIDE.md",
    "docs/SUBMISSION_CORRECTION.md",
)

FORBIDDEN_TOP_LEVEL = (
    "app",
    "assets",
    "components",
    "config",
    "deploy",
    "frontend",
    "lib",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
    "node_modules",
    "package-lock.json",
    "package.json",
    "pages",
    "pnpm-lock.yaml",
    "postcss.config.js",
    "public",
    "src",
    "tailwind.config.js",
    "tailwind.config.ts",
    "tsconfig.json",
    "vercel.json",
    "yarn.lock",
)
FORBIDDEN_TEXT = (
    "football prediction",
    "football betting",
    "bet creation",
    "leaderboard",
    "next.js football",
    "wallet betting",
)
IGNORED_SCAN_PARTS = (
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".venv312",
    "__pycache__",
    "artifacts",
    "node_modules",
)
FIXTURE_SHA256 = "18f003993472c55475710908ba1921d3aa5f561c175e9f59ecc59d8bada53551"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


for relative_path in REQUIRED:
    if not (ROOT / relative_path).is_file():
        fail(f"missing required package file: {relative_path}")

for relative_path in FORBIDDEN_TOP_LEVEL:
    if (ROOT / relative_path).exists():
        fail(f"unrelated application artifact is present: {relative_path}")

for path in ROOT.rglob("*"):
    relative_parts = path.relative_to(ROOT).parts
    if path.is_dir() or any(part in IGNORED_SCAN_PARTS or part.startswith(".venv") for part in relative_parts):
        continue
    if path.relative_to(ROOT).as_posix() == "scripts/verify_package.py":
        continue
    if path.suffix.lower() not in {".md", ".py", ".txt", ".yaml", ".yml", ".toml", ".gitignore"}:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    for forbidden in FORBIDDEN_TEXT:
        if forbidden in text:
            fail(f"application-era wording found in {path.relative_to(ROOT)}: {forbidden}")

fixture = ROOT / "fixtures/policies/dataset_policy_v1.txt"
if hashlib.sha256(fixture.read_bytes()).hexdigest() != FIXTURE_SHA256:
    fail("immutable public fixture SHA-256 does not match documented value")

source = (ROOT / "contracts/rights_route.py").read_text(encoding="utf-8")
for required_symbol in (
    "gl.nondet.web.get",
    "gl.nondet.exec_prompt",
    "gl.vm.run_nondet_unsafe",
    "RightsRouteConsumer",
    "on=\"finalized\"",
):
    if required_symbol not in source:
        fail(f"RightsRoute source missing required design element: {required_symbol}")

print("RightsRoute standalone contract-package checks passed.")
