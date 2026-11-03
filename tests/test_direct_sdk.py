"""Official genlayer-test direct-mode checks, executed in CI.

Unlike tests/test_contract.py these fixtures use the real GenLayer direct-mode
runtime, so deployment, storage and ABI handling are exercised in-process.
This is NOT a Studio multi-validator network test.
"""
import json

SOURCE = "The customer may cancel within 14 calendar days and receive a full refund."
TARGET = "Müşteri 7 takvim günü içinde iptal ederek tam ücret iadesi alabilir."


def test_native_creation_persistence_and_access_control(direct_vm, direct_deploy, direct_bob):
    direct_vm.check_pickling = True
    contract = direct_deploy("contracts/ClauseMirror.py")
    cid = contract.submit_pair("en", "tr", SOURCE, TARGET, "Public fictional example")
    assert cid == 1
    record = json.loads(contract.get_case(cid))
    assert record["status"] == "PENDING"
    assert record["target_clause"] == TARGET
    assert contract.get_total_cases() == 1
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("Only author may request review"):
        contract.review(cid)


def test_native_review_and_validator_agreement(direct_vm, direct_deploy):
    direct_vm.check_pickling = True
    direct_vm.mock_llm(r".*", json.dumps(json.dumps({
        "verdict": "MATERIAL_DIFFERENCE",
        "note": "Cancellation deadline differs (14 days versus 7 days).",
    })))
    contract = direct_deploy("contracts/ClauseMirror.py")
    cid = contract.submit_pair("en", "tr", SOURCE, TARGET, "Public fictional example")
    assert contract.review(cid) == "MATERIAL_DIFFERENCE"
    record = json.loads(contract.get_case(cid))
    assert record["status"] == "REVIEWED"
    assert record["note_verified"] is False
    assert direct_vm.run_validator() is True
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r".*", json.dumps(json.dumps({
        "verdict": "EQUIVALENT",
        "note": "This validator disagrees with the proposed verdict.",
    })))
    assert direct_vm.run_validator() is False
