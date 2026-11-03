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



def test_native_revision_chain_immutability_and_owner_permission(direct_vm, direct_deploy, direct_bob):
    direct_vm.mock_llm(r".*", json.dumps(json.dumps({
        "verdict": "MATERIAL_DIFFERENCE",
        "note": "The cancellation deadline differs.",
    })))
    contract = direct_deploy("contracts/ClauseMirror.py")
    original_id = contract.submit_pair("en", "tr", SOURCE, TARGET, "Public fictional example")
    assert contract.review(original_id) == "MATERIAL_DIFFERENCE"
    before = contract.get_case(original_id)
    corrected = "Müşteri 14 takvim günü içinde iptal ederek tam ücret iadesi alabilir."

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("Only author may revise"):
        contract.revise_target(original_id, corrected)
    assert contract.get_total_cases() == 1

    direct_vm.sender = contract.get_author(original_id)
    new_id = contract.revise_target(original_id, corrected)
    assert new_id == 2
    assert contract.get_case(original_id) == before
    new_case = json.loads(contract.get_case(new_id))
    assert new_case["parent_id"] == original_id
    assert new_case["target_clause"] == corrected
    assert new_case["status"] == "PENDING"
    with direct_vm.expect_revert("Review parent before revision"):
        contract.revise_target(new_id, TARGET)


def test_native_rejects_format_controls_and_same_language(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/ClauseMirror.py")
    with direct_vm.expect_revert("Source and target languages must differ"):
        contract.submit_pair("en", "EN", SOURCE, TARGET, "")
    with direct_vm.expect_revert("Source clause contains unsafe Unicode/control characters"):
        contract.submit_pair("en", "tr", SOURCE + "\u202e", TARGET, "")
    assert contract.get_total_cases() == 0