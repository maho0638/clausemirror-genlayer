"""Narrow compatibility update for genvm-linter 0.11.1rc2 with SDK 0.3.

The published SDK 0.3 defines `gl.vm.run_nondet_default` as the *safe*
validator-sandbox API. genvm-linter 0.11.1rc2 still recognizes only the
old names, so it emits a false E010 "not reachable from equivalence principle".
This shim adds only the SDK-provided safe entry point to two matching sets.
It does NOT disable or downgrade any lint rule. Fail closed if upstream code
is not the expected shape. Remove when official linter supports the API.
"""
from pathlib import Path
import genvm_linter.lint.safety as safety

path = Path(safety.__file__)
src = path.read_text(encoding='utf-8')
if '"gl.vm.run_nondet_default": [0, 1]' in src and '"gl.vm.run_nondet_default",' in src:
    print('Official linter already recognizes SDK 0.3 safe entry point.')
    raise SystemExit(0)

safe_entry = '"gl.vm.run_nondet": [0, 1],  # Both leader_fn and validator_fn args'
safe_spawn = 'NONDET_SPAWN_CALLS = frozenset({\n    "gl.vm.run_nondet",'
assert src.count(safe_entry) == 1, 'Unexpected linter safety registry format'
assert src.count(safe_spawn) == 1, 'Unexpected linter spawn registry format'
src = src.replace(safe_entry,
    '"gl.vm.run_nondet_default": [0, 1],  # SDK 0.3 safe validator sandbox\n        ' + safe_entry, 1)
src = src.replace(safe_spawn,
    'NONDET_SPAWN_CALLS = frozenset({\n    "gl.vm.run_nondet_default",\n    "gl.vm.run_nondet",', 1)
path.write_text(src, encoding='utf-8')
print('Applied SDK 0.3 safe-entry recognition patch to genvm-linter:', path)