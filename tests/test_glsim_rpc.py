"""Docker-free GenLayer RPC smoke tests against the official GLSim.

Important: GLSim runs Python, not GenVM WASM. `sim_call` is a simulated
transaction and does not establish independent, real validator consensus.
All interactions happen entirely in this temporary in-process simulator.
"""
import json
from pathlib import Path

import pytest

SOURCE = "The customer may cancel within 14 calendar days and receive a full refund."
TARGET = "Müşteri 7 takvim günü içinde iptal ederek tam ücret iadesi alabilir."
CORRECTED = "Müşteri 14 takvim günü içinde iptal ederek tam ücret iadesi alabilir."
CONTRACT_PATH = str(Path(__file__).resolve().parents[1] / "contracts" / "ClauseMirror.py")
ALICE = "0x" + "11" * 20
BOB = "0x" + "22" * 20


@pytest.fixture
def simulator():
    from glsim.server import create_app
    from starlette.testclient import TestClient

    app = create_app(num_validators=3, max_rotations=2, llm_provider=None, use_browser=False)
    with TestClient(app) as client:
        yield client, app.state.engine


def rpc(client, method, params=None):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        payload["params"] = params
    response = client.post("/api", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "error" not in data, f"{method} unexpectedly failed: {data}"
    assert "result" in data, f"{method} returned no result: {data}"
    return data["result"]


def deploy(client):
    data = rpc(client, "sim_deploy", {"code_path": CONTRACT_PATH, "args": [], "sender": ALICE})
    assert data["tx_hash"]
    return data["contract_address"]


def call(client, contract_address, method, args=None, sender=ALICE):
    return rpc(client, "sim_call", {
        "to": contract_address, "method": method, "args": args or [], "sender": sender,
    })


def read(client, contract_address, method, args=None):
    return rpc(client, "sim_read", {
        "to": contract_address, "method": method, "args": args or [],
    })["result"]


def test_simulated_rpc_persistence_and_receipts(simulator):
    client, _engine = simulator
    addr = deploy(client)
    assert read(client, addr, "get_total_cases") == 0
    tx = call(client, addr, "submit_pair", ["en", "tr", SOURCE, TARGET, "Public demo"])
    assert tx["result"] == 1
    receipt = rpc(client, "sim_getTransactionReceipt", {"transaction_hash": tx["tx_hash"]})
    assert receipt["status"] == "0x1"
    assert read(client, addr, "get_total_cases") == 1
    record = json.loads(read(client, addr, "get_case", [1]))
    assert record["target_clause"] == TARGET
    assert record["status"] == "PENDING"
    assert record["note_verified"] is False


def test_simulated_rpc_review_revision_and_unauthorized_revert(simulator):
    client, engine = simulator
    addr = deploy(client)
    original = call(client, addr, "submit_pair", ["en", "tr", SOURCE, TARGET, ""])["result"]
    # genlayer-test's Direct Mode mock pre-parses JSON. Double-encoding
    # supplies JSON TEXT to the actual SDK response_format='json' decoder.
    assessment = {"verdict": "MATERIAL_DIFFERENCE", "note": "14 vs 7 day cancellation."}
    engine.vm.mock_llm(r".*", json.dumps(json.dumps(assessment)))
    review = call(client, addr, "review", [original])
    assert review["result"] == "MATERIAL_DIFFERENCE"
    snapshot = read(client, addr, "get_case", [original])
    assert json.loads(snapshot)["status"] == "REVIEWED"

    # A failed simulated write must be recorded as failed and leave state intact.
    payload = {"to": addr, "method": "revise_target", "args": [original, CORRECTED], "sender": BOB}
    response = client.post("/api", json={"jsonrpc": "2.0", "id": 5, "method": "sim_call", "params": payload}).json()
    assert "error" in response
    assert read(client, addr, "get_total_cases") == 1
    assert read(client, addr, "get_case", [original]) == snapshot

    child = call(client, addr, "revise_target", [original, CORRECTED])["result"]
    assert child == original + 1
    assert read(client, addr, "get_case", [original]) == snapshot
    child_record = json.loads(read(client, addr, "get_case", [child]))
    assert child_record["parent_id"] == original
    assert child_record["target_clause"] == CORRECTED
    assert child_record["status"] == "PENDING"
