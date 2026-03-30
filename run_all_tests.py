import json
import pathlib
import sys

import numpy as np
import torch
import torch.nn.functional as F
from torch.autograd import Variable
import unittest

ROOT = pathlib.Path(__file__).parent


def load_notebook_code(path: pathlib.Path, ns: dict) -> None:
    nb = json.loads(path.read_text(encoding="utf-8"))
    for cell in nb["cells"]:
        if cell.get("cell_type") != "code":
            continue
        src = "".join(cell.get("source", []))
        if not src.strip() or src.strip().startswith("%run"):
            continue
        exec(compile(src, str(path), "exec"), ns)


ns = {"np": np, "numpy": np, "torch": torch, "F": F, "Variable": Variable, "unittest": unittest}
load_notebook_code(ROOT / "homework_modules.ipynb", ns)

for name, obj in ns.items():
    if name.startswith("__"):
        continue
    setattr(sys.modules[__name__], name, obj)

# Load test class from notebook (cell 2, index 2)
test_nb = json.loads((ROOT / "homework_test_modules.ipynb").read_text(encoding="utf-8"))
test_src = ""
for cell in test_nb["cells"]:
    if cell.get("cell_type") != "code":
        continue
    src = "".join(cell.get("source", []))
    if src.strip().startswith("class TestLayers"):
        test_src = src
        break

if not test_src:
    raise RuntimeError("TestLayers not found")

if "suite = unittest.TestLoader()" in test_src:
    test_src = test_src.split("suite = unittest.TestLoader()")[0].rstrip()

exec(compile(test_src, "homework_test_modules.ipynb", "exec"), ns)

suite = unittest.TestLoader().loadTestsFromTestCase(ns["TestLayers"])
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
