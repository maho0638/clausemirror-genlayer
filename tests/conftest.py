"""Minimal deterministic GenLayer stub for local control-flow tests ONLY.

This is not an official SDK or validator simulation. Integration gates remain open.
"""
import importlib.util
import sys
import types
from pathlib import Path

import pytest


class FakeTreeMap(dict):
    def __class_getitem__(cls, params):
        return cls


class ConsensusRejected(Exception):
    pass


@pytest.fixture()
def env(monkeypatch):
    responses = []
    fake = types.ModuleType("genlayer")
    fake.__all__ = ["gl", "TreeMap", "Address", "u32"]
    vm = types.SimpleNamespace()
    vm.UserError = type("UserError", (Exception,), {})

    class Return:
        def __init__(self, calldata):
            self.calldata = calldata

    vm.Return = Return
    vm.Result = Return

    def run_nondet_safe(producer, validator):
        proposed = producer()
        if not validator(Return(proposed)):
            raise ConsensusRejected("Two independent scripted outputs disagree")
        return proposed

    vm.run_nondet_default = run_nondet_safe

    def unsafe_nondet(*args, **kwargs):
        raise AssertionError("Unsafe run_nondet must never be used")
    vm.run_nondet = unsafe_nondet

    def exec_prompt(prompt, *, response_format=None):
        assert response_format == "json", "GenLayer structured output must be explicitly requested"
        seen.append(prompt)
        if not responses:
            raise RuntimeError("No queued synthetic AI response")
        return responses.pop(0)

    seen = []
    runtime = types.SimpleNamespace(
        contract=types.SimpleNamespace(Contract=object),
        storage=types.SimpleNamespace(TreeMap=FakeTreeMap, inmem_allocate=lambda t, *args, **kwargs: t(*args, **kwargs)),
        public=types.SimpleNamespace(write=lambda fn: fn, view=lambda fn: fn),
        message=types.SimpleNamespace(sender_address="0xALICE"),
        nondet=types.SimpleNamespace(exec_prompt=exec_prompt),
        vm=vm,
    )
    fake.contract = runtime.contract
    fake.storage = runtime.storage
    fake.public = runtime.public
    fake.message = runtime.message
    fake.nondet = runtime.nondet
    fake.vm = runtime.vm
    types_module = types.ModuleType("genlayer.types")
    types_module.Address = str
    types_module.u32 = int
    monkeypatch.setitem(sys.modules, "genlayer.types", types_module)
    monkeypatch.setitem(sys.modules, "genlayer", fake)
    location = Path(__file__).resolve().parents[1] / "contracts" / "ClauseMirror.py"
    spec = importlib.util.spec_from_file_location("clausemirror_test_contract", location)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return types.SimpleNamespace(
        module=module, contract=module.ClauseMirror(), user_error=vm.UserError,
        rejected=ConsensusRejected, responses=responses, seen=seen, gl=fake,
    )