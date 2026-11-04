"""Real GenLayer Direct SDK tests; no public chain transactions."""
import json
import pytest

SOURCE = "The customer may cancel within fourteen calendar days."
TARGET = "Musteri yedi takvim gunu icinde iptal edebilir."


def mock_verdict(vm, verdict):
    # GenLayer direct mock returns JSON-encoded SDK response text.
    vm.mock_llm(r".*", json.dumps(json.dumps({"verdict": verdict})))


def test_real_direct_deployment_storage_and_authorization(direct_vm, direct_deploy, direct_bob):
    direct_vm.check_pickling = True
    c = direct_deploy("contracts/ClauseMirror.py")
    cid = c.submit("en", "tr", SOURCE, TARGET)
    assert cid == 1
    assert c.total_cases() == 1
    assert json.loads(c.get_case(cid))["verdict"] == "PENDING"
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("Only author can review"):
        c.review(cid)


def test_real_direct_validator_matches_and_rejects_disagreement(direct_vm, direct_deploy):
    direct_vm.check_pickling = True
    mock_verdict(direct_vm, "DIFFERENT")
    c = direct_deploy("contracts/ClauseMirror.py")
    cid = c.submit("en", "tr", SOURCE, TARGET)
    assert c.review(cid) == "DIFFERENT"
    assert json.loads(c.get_case(cid))["verdict"] == "DIFFERENT"
    assert direct_vm.run_validator() is True
    direct_vm.clear_mocks()
    mock_verdict(direct_vm, "SAME")
    assert direct_vm.run_validator() is False
    with direct_vm.expect_revert("Already reviewed"):
        c.review(cid)


def test_direct_input_validation_and_bounds(direct_vm, direct_deploy):
    c = direct_deploy("contracts/ClauseMirror.py")
    with direct_vm.expect_revert("Languages must differ"):
        c.submit("en", "EN", SOURCE, TARGET)
    with direct_vm.expect_revert("Invalid text length"):
        c.submit("en", "tr", "x", TARGET)
    with direct_vm.expect_revert("Invalid control character"):
        c.submit("en", "tr", SOURCE + "\u202e", TARGET)
    with direct_vm.expect_revert("Language must contain letters only"):
        c.submit("en-us", "tr", SOURCE, TARGET)
    assert c.total_cases() == 0
