"""No-SDK AST guardrails for GenVM v0.3's safety-sensitive API names.

These are static guards, not GenVM integration tests. The official linter and
Studio are required separately.
"""
import ast
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / 'contracts' / 'ClauseMirror.py'
TREE = ast.parse(FILE.read_text(encoding='utf-8'))


def _qualified_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f'{_qualified_name(node.value)}.{node.attr}'
    return ''


def test_contract_never_calls_unsafe_nondet_sdk03():
    invoked = [_qualified_name(n.func) for n in ast.walk(TREE) if isinstance(n, ast.Call)]
    assert 'gl.vm.run_nondet' not in invoked, 'SDK 0.3 run_nondet is UNSAFE'
    assert 'gl.vm.run_nondet_default' in invoked, 'safe validator sandbox is mandatory'


def test_contract_pins_validated_runner_and_sdk03_public_api():
    text = FILE.read_text(encoding='utf-8')
    assert text.startswith('# { "Depends": "py-genlayer:babwp9t37jw9g4j2bccgn14g6x7x9s1f7dsmh7emvz735pz4zxa0" }')
    assert 'class ClauseMirror(gl.contract.Contract):' in text
    assert '@gl.public.write' in text
    assert '@gl.public.view' in text


def test_llm_structured_json_and_validator_return_existence():
    called = [_qualified_name(n.func) for n in ast.walk(TREE) if isinstance(n, ast.Call)]
    assert 'gl.nondet.exec_prompt' in called
    assert 'isinstance' in called
    assert 'gl.vm.Return' in FILE.read_text(encoding='utf-8')