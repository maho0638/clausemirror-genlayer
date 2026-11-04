"""Opt-in REAL GenLayer Studio localnet integration gate.

WARNING: This file DEPLOYS a contract and WRITES transactions if executed.
It is deliberately excluded from all automatic CI jobs and skips unless
CLAUSEMIRROR_ENABLE_STUDIO_TESTS=1. Use only on an isolated, disposable
LOCAL GenLayer Studio after explicit user approval. Never run on a public
testnet or a wallet with meaningful funds.
"""
import json
import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("CLAUSEMIRROR_ENABLE_STUDIO_TESTS") != "1",
    reason="No authorization to deploy/run Studio transactions.",
)

@pytest.fixture(autouse=True)
def _fix_studio_localnet_evm_gas_estimate(monkeypatch):
    """CI-only workaround for Studio v0.121.25's hardcoded 500k gas estimate.

    The RPC eth_estimateGas method always returns 0x7a120; 5m was also
    insufficient for addTransaction. 20m is below the 30m local block limit.
    This never patches the contract or SDK on public networks.
    """
    from genlayer_py.contracts import actions

    original = actions._prepare_transaction

    def prepare(*args, **kwargs):
        client = kwargs.get("self") or args[0]
        assert client.chain.id == 61127, "Studio gas override is forbidden off disposable localnet"
        tx = original(*args, **kwargs)
        given = int(tx["gas"], 16) if isinstance(tx["gas"], str) else int(tx["gas"])
        tx["gas"] = hex(max(given, 20_000_000))
        print(f"CI localnet EVM gas estimate adjusted: {given} -> {int(tx['gas'], 16)}")
        return tx

    monkeypatch.setattr(actions, "_prepare_transaction", prepare)


SOURCE = "The customer may cancel within 14 calendar days and receive a full refund."
TARGET = "Müşteri 7 takvim günü içinde iptal ederek tam ücret iadesi alabilir."


def _mock_context(verdict, note):
    from gltest import get_validator_factory

    response = {"verdict": verdict, "note": note}
    mocked = {
        "nondet_exec_prompt": {
            "independent multilingual clause-comparison reviewer": json.dumps(response),
        }
    }
    validators = get_validator_factory().batch_create_mock_validators(
        count=5, mock_llm_response=mocked
    )
    return {"validators": [validator.to_dict() for validator in validators]}


def _fresh_case(context):
    from gltest import get_contract_factory
    from gltest.assertions import tx_execution_succeeded

    contract = get_contract_factory("ClauseMirror").deploy(
        args=[], transaction_context=context, consensus_max_rotations=3, wait_retries=120
    )
    tx = contract.submit_pair(
        args=["en", "tr", SOURCE, TARGET, "Fictional public clause"]
    ).transact(transaction_context=context)
    assert tx_execution_succeeded(tx), f"submit_pair did not execute: {tx}"
    assert contract.get_total_cases(args=[]).call() == 1
    return contract


def test_studio_five_mock_validators_confirm_receipt():
    """Requires real Studio, full validator mode and localnet; not leader-only."""
    from gltest.assertions import tx_execution_succeeded

    context = _mock_context(
        "MATERIAL_DIFFERENCE", "Cancellation deadline differs (14 versus 7 days)."
    )
    contract = _fresh_case(context)
    tx = contract.review(args=[1]).transact(
        transaction_context=context, consensus_max_rotations=3
    )
    assert tx_execution_succeeded(tx), f"Consensus did not accept review: {tx}"

    receipt = json.loads(contract.get_case(args=[1]).call())
    assert receipt["verdict"] == "MATERIAL_DIFFERENCE"
    assert receipt["status"] == "REVIEWED"
    assert receipt["note_verified"] is False

    corrected = "Müşteri 14 takvim günü içinde iptal ederek tam ücret iadesi alabilir."
    tx2 = contract.revise_target(args=[1, corrected]).transact(transaction_context=context)
    assert tx_execution_succeeded(tx2)
    child = json.loads(contract.get_case(args=[2]).call())
    assert child["parent_id"] == 1 and child["status"] == "PENDING"
    assert json.loads(contract.get_case(args=[1]).call()) == receipt


def test_studio_invalid_model_decision_does_not_commit_receipt():
    """Verify rejection and unchanged PENDING state under real Studio processing."""
    from gltest.assertions import tx_execution_failed

    context = _mock_context("APPROVED", "This verdict is not in the allowed enum.")
    contract = _fresh_case(context)
    rejected = contract.review(args=[1]).transact(
        transaction_context=context, consensus_max_rotations=1
    )
    assert tx_execution_failed(rejected), f"Unexpectedly accepted invalid verdict: {rejected}"
    record = json.loads(contract.get_case(args=[1]).call())
    assert record["status"] == "PENDING"
    assert record["verdict"] == ""
