"""Official GenLayer Direct Mode checks (real SDK, simulated I/O).

This exercises GenLayer SDK storage, ABI, leader/validator logic, and pickling.
It does NOT deploy to GenVM or provide actual multi-validator finality.
"""
import json

SOURCE = "The customer may cancel within 14 calendar days and receive a full refund."
TARGET = "Müşteri 7 takvim günü içinde iptal ederek tam ücret iadesi alabilir."


def _sdk_json_mock(verdict: str, note: str) -> str:
    """Bridge genlayer-test 0.30rc2 auto-parsing and SDK 0.3 JSON decoding.

    The Direct Mode WASI mock unconditionally json.loads() any valid JSON
    response string; the SDK's response_format="json" decoder independently
    requires JSON *text* and parses it itself. Double-encoding only the test
    fixture prevents the Direct Mode shim from prematurely passing a dict.
    The actual contract and production response handling are unchanged.
    """
    payload = {"verdict": verdict, "note": note}
    return json.dumps(json.dumps(payload, ensure_ascii=False), ensure_ascii=False)


def _setup_llm(direct_vm, verdict="MATERIAL_DIFFERENCE",
               note="Cancellation deadline differs (14 days versus 7 days)."):
    direct_vm.mock_llm(r".*", _sdk_json_mock(verdict, note))


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
    direct_vm.strict_mocks = True
    _setup_llm(direct_vm)
    contract = direct_deploy("contracts/ClauseMirror.py")
    cid = contract.submit_pair("en", "tr", SOURCE, TARGET, "Public fictional example")
    assert contract.review(cid) == "MATERIAL_DIFFERENCE"
    record = json.loads(contract.get_case(cid))
    assert record["status"] == "REVIEWED"
    assert record["verdict"] == "MATERIAL_DIFFERENCE"
    assert record["note_verified"] is False
    assert direct_vm.run_validator() is True


def test_native_validator_rejects_independent_disagreement(direct_vm, direct_deploy):
    direct_vm.check_pickling = True
    _setup_llm(direct_vm)
    contract = direct_deploy("contracts/ClauseMirror.py")
    cid = contract.submit_pair("en", "tr", SOURCE, TARGET, "")
    contract.review(cid)
    direct_vm.clear_mocks()
    _setup_llm(direct_vm, "EQUIVALENT", "No material differences detected.")
    # Direct Mode captures the validator callback; this is only an isolated
    # negative vote test, not an actual transaction rollback/finality test.
    assert direct_vm.run_validator() is False


def test_native_validator_rejects_invalid_model_decision(direct_vm, direct_deploy):
    direct_vm.check_pickling = True
    _setup_llm(direct_vm)
    contract = direct_deploy("contracts/ClauseMirror.py")
    cid = contract.submit_pair("en", "tr", SOURCE, TARGET, "")
    contract.review(cid)
    direct_vm.clear_mocks()
    _setup_llm(direct_vm, "APPROVED", "Unrecognized verdict.")
    assert direct_vm.run_validator() is False
