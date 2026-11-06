"""Every case fails its check as shipped, and passes once the fix in solutions/ is applied. A fix
stays small: a weakness closes in a few lines, it does not need the file rewritten."""

import importlib
from pathlib import Path

import pytest

from trust.__main__ import CASES
from trust.checks import CHECKS


@pytest.mark.parametrize("number", list(CASES))
def test_case_is_broken_as_shipped(number):
    case = importlib.import_module(f"cases.{CASES[number][0]}")

    results = CHECKS[number](case)

    assert not all(ok for _, ok in results), results


@pytest.mark.parametrize("number", list(CASES))
def test_case_passes_with_a_real_fix(number):
    fixed = importlib.import_module(f"tests.solutions.{CASES[number][0]}")

    failed = [label for label, ok in CHECKS[number](fixed) if not ok]

    assert failed == []


@pytest.mark.parametrize("number", list(CASES))
def test_a_fix_changes_only_a_few_lines(number):
    name = CASES[number][0]
    shipped = Path(f"cases/{name}.py").read_text().splitlines()
    fixed = Path(f"tests/solutions/{name}.py").read_text().splitlines()

    changed = len(set(fixed) - set(shipped)) + len(set(shipped) - set(fixed))

    assert 0 < changed <= 30
