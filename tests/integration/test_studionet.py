"""Hosted Studionet proof for the supported legacy GenLayer contract runner."""
import json
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded


def write(call, tag):
    tx = call.transact(consensus_max_rotations=4, wait_interval=10000, wait_retries=50)
    assert tx_execution_succeeded(tx), f"{tag} failed; tx={tx.get('hash', '')}"
    print(f"{tag}_TX={tx.get('hash', '')}", flush=True)


def test_public_studionet_contract(default_account):
    c = get_contract_factory("ClauseMirror").deploy(
        account=default_account, consensus_max_rotations=4)
    address = str(c.address)
    assert address.startswith("0x") and len(address) == 42
    print(f"CLAUSEMIRROR_CONTRACT_ADDRESS={address}", flush=True)
    print(f"CLAUSEMIRROR_EXPLORER=https://explorer-studio.genlayer.com/address/{address}", flush=True)

    write(c.submit(args=[
        "public-legal-test-001", "en", "tr",
        "The buyer can cancel this purchase within fourteen calendar days of delivery.",
        "Alici teslimattan itibaren yedi takvim gunu icinde bu siparisi iptal edebilir."
    ]), "CLAUSEMIRROR_SUBMIT")
    assert json.loads(c.get_case(args=["public-legal-test-001"]).call())["verdict"] == "PENDING"

    write(c.review(args=["public-legal-test-001"]), "CLAUSEMIRROR_REVIEW")
    result = json.loads(c.get_case(args=["public-legal-test-001"]).call())
    assert result["verdict"] in ("SAME", "DIFFERENT", "UNCLEAR")
    print(f"CLAUSEMIRROR_FINAL_VERDICT={result['verdict']}", flush=True)
