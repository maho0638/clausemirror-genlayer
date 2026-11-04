"""Offline contract tests with a mocked GenLayer host; NOT real chain consensus."""
import importlib.util
import json
import sys
import types
from pathlib import Path
import pytest


class UserError(Exception):
    pass


class Return:
    def __init__(self, calldata):
        self.calldata = calldata


class TreeMap(dict):
    def __class_getitem__(cls, args):
        return cls


def setup_contract():
    gl = types.ModuleType("genlayer")
    gl.contract = types.SimpleNamespace(Contract=type("Contract", (), {}))
    gl.storage = types.SimpleNamespace(TreeMap=TreeMap, inmem_allocate=lambda cls: cls())
    gl.public = types.SimpleNamespace(write=lambda fn: fn, view=lambda fn: fn)
    gl.message = types.SimpleNamespace(sender_address="alice")
    gl.vm = types.SimpleNamespace(Result=object, Return=Return, UserError=UserError)
    gl.nondet = types.SimpleNamespace(exec_prompt=lambda p, response_format: {"verdict": "DIFFERENT"})

    def consensus(produce, verify):
        value = produce()
        if not verify(Return(value)):
            raise UserError("Validator disagreed")
        return value

    gl.vm.run_nondet_default = consensus
    types_module = types.ModuleType("genlayer.types")
    types_module.Address, types_module.u32 = str, int
    previous = (sys.modules.get("genlayer"), sys.modules.get("genlayer.types"))
    sys.modules["genlayer"], sys.modules["genlayer.types"] = gl, types_module
    path = Path(__file__).resolve().parents[1] / "contracts" / "ClauseMirror.py"
    spec = importlib.util.spec_from_file_location("clause_mirror_contract", path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    finally:
        for name, old in zip(("genlayer", "genlayer.types"), previous):
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old
    return module, gl


def test_review_and_no_replay():
    m, gl = setup_contract()
    c = m.ClauseMirror()
    i = c.submit("en", "tr", "The notice is due in 14 days", "Bildirim 7 gunde yapilmalidir")
    assert i == 1 and c.total_cases() == 1
    assert c.review(i) == "DIFFERENT"
    assert json.loads(c.get_case(i))["verdict"] == "DIFFERENT"
    with pytest.raises(UserError):
        c.review(i)


def test_reject_invalid_and_unauthorized():
    m, gl = setup_contract()
    c = m.ClauseMirror()
    with pytest.raises(UserError):
        c.submit("en", "en", "The period is 14 days", "The period is 7 days")
    with pytest.raises(UserError):
        c.submit("en", "tr", "X", "The period is 7 days")
    i = c.submit("en", "tr", "The period is 14 days", "The period is 7 days")
    gl.message.sender_address = "mallory"
    with pytest.raises(UserError):
        c.review(i)
    assert json.loads(c.get_case(i))["verdict"] == "PENDING"


def test_invalid_ai_and_validator_disagreement_leave_case_pending():
    m, gl = setup_contract()
    c = m.ClauseMirror()
    i = c.submit("en", "tr", "The period is 14 days", "The period is 7 days")
    gl.nondet.exec_prompt = lambda p, response_format: {"verdict": "APPROVED"}
    with pytest.raises(UserError):
        c.review(i)
    votes = iter([{"verdict": "SAME"}, {"verdict": "DIFFERENT"}])
    gl.nondet.exec_prompt = lambda p, response_format: next(votes)
    with pytest.raises(UserError):
        c.review(i)
    assert json.loads(c.get_case(i))["verdict"] == "PENDING"
