"""Official GenLayer SDK Direct Mode checks (same runner/API as live Studionet)."""
import json
import pytest


def _mock(vm, verdict):
    vm.clear_mocks()
    vm.mock_llm(r"(?s).*Compare the meanings of these user-supplied clauses.*",
                json.dumps({"verdict": verdict}))


def _create(contract):
    contract.submit(
        "public-case-001", "en", "tr",
        "The customer can cancel the order within fourteen calendar days.",
        "Musteri siparisi yedi takvim gunu icinde iptal edebilir."
    )


def test_submit_and_public_receipt(direct_deploy):
    c = direct_deploy("contracts/ClauseMirror.py")
    _create(c)
    data = json.loads(c.get_case("public-case-001"))
    assert data["verdict"] == "PENDING"
    assert data["source_language"] == "en"
    assert data["target_language"] == "tr"


def test_ai_review_validator_agreement_and_disagreement(direct_vm, direct_deploy):
    c = direct_deploy("contracts/ClauseMirror.py")
    _create(c)
    _mock(direct_vm, "DIFFERENT")
    c.review("public-case-001")
    assert json.loads(c.get_case("public-case-001"))["verdict"] == "DIFFERENT"
    assert direct_vm.run_validator() is True
    _mock(direct_vm, "SAME")
    assert direct_vm.run_validator() is False


def test_owner_and_replay_are_blocked(direct_vm, direct_deploy, direct_bob):
    c = direct_deploy("contracts/ClauseMirror.py")
    _create(c)
    owner = direct_vm.sender
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("Only submitter can review"):
        c.review("public-case-001")
    direct_vm.sender = owner
    _mock(direct_vm, "DIFFERENT")
    c.review("public-case-001")
    with direct_vm.expect_revert("Already reviewed"):
        c.review("public-case-001")
    with direct_vm.expect_revert("Case already exists"):
        _create(c)


def test_reject_invalid_languages_and_controls(direct_vm, direct_deploy):
    c = direct_deploy("contracts/ClauseMirror.py")
    with direct_vm.expect_revert("Invalid language pair"):
        c.submit("case-1", "en", "EN", "The deadline is fourteen days.", "The deadline is seven days.")
    with direct_vm.expect_revert("Disallowed control characters"):
        c.submit("case-2", "en", "tr", "The deadline is fourteen days.\u202e", "The deadline is seven days.")
    with direct_vm.expect_revert("Case not found"):
        c.get_case("missing")
