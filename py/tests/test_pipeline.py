"""Test harness — exercises the verification pipeline directly (no MCP).

Run with: eval $(opam env); .venv/bin/python -m pytest py/tests/ -v
"""

import ast
import os
import sys
import textwrap
from pathlib import Path

# Make oracle/ importable directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from oracle.contract_linter import ContractLinter, AssertInfo
from oracle.python_to_imp import python_to_imp
from oracle.mcp_server import (
    _generate_coq, _classify_assert, _expand_params,
    _verify_function,
)
from oracle.reporting import GoalStatus, ProofLevel


BUILD_DIR = Path(__file__).resolve().parent.parent.parent / "_build" / "default" / "coq"


def run_verification(source: str, func_name: str) -> GoalStatus | None:
    tree = ast.parse(source)
    func_node = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == func_name
    )
    params = [arg.arg for arg in func_node.args.args]
    expanded, _, _, _, _ = _expand_params(tree, params, func_node)
    linter_pre = ContractLinter(expanded, "precondition")
    linter_post = ContractLinter(expanded, "postcondition")
    lint_results = []
    for stmt in ast.walk(func_node):
        if isinstance(stmt, ast.Assert):
            cls = _classify_assert(func_node, stmt)
            linter = linter_pre if cls == "precondition" else linter_post
            lr = linter.lint_expression(stmt.test)
            lint_results.append(AssertInfo(
                node=stmt, lineno=stmt.lineno, col_offset=stmt.col_offset,
                classification=cls, lint_result=lr,
            ))
    os.environ.setdefault("REFACTORING_ROBOTS_ROOT", str(BUILD_DIR.parent.parent))
    return _verify_function(source, func_name, None)


EXAMPLES = [
    ("add", "def add(a,b):\n assert True\n result = a+b\n assert result == a+b\n return result"),
    ("max_of_two", "def max_of_two(a,b):\n assert a>=0; assert b>=0\n if a>=b: result=a\n else: result=b\n assert result>=a; assert result>=b\n return result"),
    ("clamp", "def clamp(val,lo,hi):\n assert lo<=hi\n if val<lo: result=lo\n elif val>hi: result=hi\n else: result=val\n assert lo<=result<=hi\n return result"),
    ("sum_to", "def sum_to(n):\n assert n>=0\n acc=0; i=0\n while i<n:\n  assert acc==i*(i+1)//2; assert i<=n\n  i=i+1; acc=acc+i\n assert acc==n*(n+1)//2; assert i==n\n return acc"),
    ("count_to", "def count_to(n):\n assert n>=0\n i=0\n for _ in range(n): i=i+1\n assert i==n\n return i"),
    ("fill_list", "def fill_list(n):\n assert n>=0\n xs=[]; i=0\n while i<n:\n  assert len(xs)==i; assert i<=n\n  xs.append(i); i=i+1\n result=len(xs)\n assert result==n\n return result"),
    ("count_append", "def count_append(x):\n assert x>0\n items=[]; items.append(x)\n result=len(items)\n assert result==1\n return result"),
]


@pytest.mark.parametrize("name,source", EXAMPLES)
def test_verification_passes(name, source):
    goal = run_verification(source, name)
    assert goal is not None, f"None return for {name}"
    assert goal.is_proved(), f"Not proved ({goal.level}): {goal.error_detail[:200]}"
    assert goal.level == ProofLevel.LEVEL1_LTAC


def test_linter_precondition_scoping():
    linter = ContractLinter(params=["a","b"], context="precondition")
    expr = ast.parse("a>=0 and b>=0", mode="eval").body
    result = linter.lint_expression(expr)
    assert result.is_valid
    assert "s " not in result.coq_translation


def test_linter_postcondition_scoping():
    linter = ContractLinter(params=["a","b"], context="postcondition")
    expr = ast.parse("result>=a and result>=b", mode="eval").body
    result = linter.lint_expression(expr)
    assert result.is_valid
    assert 's "result"' in result.coq_translation


def test_linter_len_invariant():
    linter = ContractLinter(params=["n"], context="invariant")
    expr = ast.parse("len(xs)==i", mode="eval").body
    result = linter.lint_expression(expr)
    assert result.is_valid
    assert "xs._len" in result.coq_translation


def test_linter_produces_smt():
    linter = ContractLinter(params=["a","b"], context="postcondition")
    expr = ast.parse("result>=a and result>=b", mode="eval").body
    result = linter.lint_expression(expr)
    assert result.is_valid
    assert result.smt_translation
    assert "s " not in result.smt_translation


def test_ir_roundtrip():
    from oracle.contract_ir import Var, BinOp, Logical, IntLit
    ir = Logical("and", [
        BinOp("=", Var("acc"), BinOp("/", BinOp("*", Var("i"), BinOp("+", Var("i"), IntLit(1))), IntLit(2))),
        BinOp("<=", Var("i"), Var("n")),
    ])
    assert ir.to_coq(scoped=True)
    smt = ir.to_smt()
    assert "and" in smt and "div" in smt and "<=" in smt


def test_smt_vcg_sum_to():
    from oracle.contract_ir import Var, BinOp, Logical, IntLit
    from oracle.mcp_server import _try_smt_vcg_ir
    inv = Logical("and", [
        BinOp("=", Var("acc"), BinOp("/", BinOp("*", Var("i"), BinOp("+", Var("i"), IntLit(1))), IntLit(2))),
        BinOp("<=", Var("i"), Var("n")),
    ])
    post = Logical("and", [
        BinOp("=", Var("acc"), BinOp("/", BinOp("*", Var("n"), BinOp("+", Var("n"), IntLit(1))), IntLit(2))),
        BinOp("=", Var("i"), Var("n")),
    ])
    assert _try_smt_vcg_ir(inv.operands, "Z.leb (i + 1) n = false", post.operands, "result = acc")


def test_smt_vcg_fill_list():
    from oracle.contract_ir import Var, BinOp, Logical, IntLit
    from oracle.mcp_server import _try_smt_vcg_ir
    inv = Logical("and", [
        BinOp("=", Var("xs__len"), Var("i")),
        BinOp("<=", Var("i"), Var("n")),
    ])
    post = BinOp("=", Var("result"), Var("n"))
    assert _try_smt_vcg_ir(inv.operands, "Z.leb (i + 1) n = false", [post], "result = xs__len")
