"""Hosted GenLayer Studionet proof: deploy, review, and read from public chain."""
import json
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus


def _confirmed_write(call, label):
    receipt = call.transact(
        consensus_max_rotations=4,
        wait_transaction_status=TransactionStatus.FINALIZED,
        wait_interval=10000,
        wait_retries=55,
    )
    print(f"{label}_RECEIPT={json.dumps(receipt, default=str)}", flush=True)
    assert tx_execution_succeeded(receipt), f"{label} failed: {receipt}"
    print(f"{label}_TX={receipt.get('hash', '')}", flush=True)
    return receipt


def test_clausemirror_real_studionet_lifecycle(default_account):
    contract = get_contract_factory("ClauseMirror").deploy(
        account=default_account,
        consensus_max_rotations=4,
    )
    address = str(contract.address)
    assert address.startswith("0x") and len(address) == 42
    print(f"CLAUSEMIRROR_DEPLOYED_ADDRESS={address}", flush=True)
    print(f"CLAUSEMIRROR_EXPLORER=https://explorer-studio.genlayer.com/address/{address}", flush=True)

    _confirmed_write(
        contract.submit(args=[
            "en", "tr",
            "The buyer may cancel this order within fourteen calendar days of receipt.",
            "Alici bu siparisi teslimattan itibaren yedi takvim gunu icinde iptal edebilir.",
        ]),
        "CLAUSEMIRROR_SUBMIT",
    )
    assert int(contract.total_cases().call()) == 1
    before = json.loads(contract.get_case(args=[1]).call())
    assert before["verdict"] == "PENDING"

    _confirmed_write(contract.review(args=[1]), "CLAUSEMIRROR_REVIEW")
    after = json.loads(contract.get_case(args=[1]).call())
    assert after["verdict"] in {"SAME", "DIFFERENT", "UNCLEAR"}
    assert after["source_clause"] == before["source_clause"]
    assert after["target_clause"] == before["target_clause"]
    print(f"CLAUSEMIRROR_FINAL_VERDICT={after['verdict']}", flush=True)
