"""Dependency-free safety helpers (easy to unit-test offline)."""
from __future__ import annotations

import ast
import math
import operator
from pathlib import Path

_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod, ast.Pow: operator.pow}
_UNARY = {ast.USub: operator.neg, ast.UAdd: operator.pos}
_FUNCS = {"sqrt": math.sqrt, "log": math.log, "log10": math.log10, "exp": math.exp,
          "sin": math.sin, "cos": math.cos, "tan": math.tan, "abs": abs, "round": round,
          "floor": math.floor, "ceil": math.ceil, "min": min, "max": max}
_CONSTS = {"pi": math.pi, "e": math.e}


def safe_eval(expression: str) -> float:
    """Evaluate a math expression via the AST. No eval(), no attribute access, no imports."""

    def ev(n: ast.AST):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _BIN:
            left, right = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Pow) and abs(right) > 1000:
                raise ValueError("exponent too large")
            return _BIN[type(n.op)](left, right)
        if isinstance(n, ast.UnaryOp) and type(n.op) in _UNARY:
            return _UNARY[type(n.op)](ev(n.operand))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _FUNCS and not n.keywords:
            return _FUNCS[n.func.id](*[ev(a) for a in n.args])
        if isinstance(n, ast.Name) and n.id in _CONSTS:
            return _CONSTS[n.id]
        raise ValueError(f"unsupported element: {type(n).__name__}")

    return ev(ast.parse(expression.strip(), mode="eval").body)


def resolve_in_workspace(workspace: Path, user_path: str) -> Path:
    """Resolve user_path inside workspace; refuse anything that escapes it (../, absolute paths)."""
    root = workspace.resolve()
    target = (root / user_path).resolve()
    if not target.is_relative_to(root):
        raise PermissionError("Access outside the workspace folder is not allowed.")
    return target
