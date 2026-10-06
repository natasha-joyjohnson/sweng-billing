"""Run your subsystem inside VoltaNet, on your team's use case.

    python run.py                                  runs my_subsystem.py
    python run.py my_subsystem_with_modules.py     runs that copy instead

Python 3.8 or later, nothing to install. The other three subsystems are
played by standins.py. What comes back is printed; nothing is marked here.
"""
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "modules"))

import importlib                                 # noqa: E402

import standins                                  # noqa: E402
from scenarios import SCENARIOS                  # noqa: E402

# Which version of your subsystem to run: my_subsystem.py unless you name another file.
VERSION = sys.argv[1] if len(sys.argv) > 1 else "my_subsystem.py"

TEAM = "S3"


def show(value):
    text = repr(value)
    return text if len(text) <= 300 else text[:297] + "..."


LEGEND = """
VoltaNet · team S3 · your use case, run step by step
=========================================================
How to read what follows:
  Each block is one row of the published resolution of your use case: the
  table you walked on Monday 28 September. The row says who calls whom;
  here, it calls a method of YOUR my_subsystem.py.

  came back: ...          what that method of my_subsystem.py answered
  NOT WRITTEN YET: ...    that method still has its «raise» line (step 1 fixes it)
  S3 -> Sx: ...           a call your subsystem really made to another subsystem
                          (the other subsystems are played by us, in standins.py)
  [ ] / [x]               a call the resolution says this row needs;
                          [x] once your code makes it (step 4)
"""


HINTS = [
    ("takes no arguments",
     "one of your modules' classes has no __init__, and your subsystem's __init__ gives it\n"
     "   something (usually the coordinator, given others). Add the __init__ in that module's file."),
    ("No module named",
     "a file in modules/ is missing, or its name differs from the one after «from»."),
    ("cannot import name",
     "the class name after «import» differs from the class name inside that module's file."),
    ("SyntaxError",
     "a file has a typing mistake at the line shown. If it is a module you just saved, copy\n"
     "   its <name>_stub.py back over it, and the subsystem runs as before."),
]


def load():
    """Import the version named on the command line and create the subsystem.
    If either breaks, say where and what usually causes it, and stop."""
    name = os.path.basename(VERSION)
    name = name[:-3] if name.endswith(".py") else name
    try:
        module = importlib.import_module(name)
        return getattr(module, "S3Subsystem")(standins.Others(TEAM))
    except Exception:                            # noqa: BLE001
        text = traceback.format_exc().strip()
        print(f"\nIT BROKE while creating your subsystem from {VERSION}, before any row ran:")
        print("   " + text.replace("\n", "\n   "))
        for clue, hint in HINTS:
            if clue in text:
                print("\n   Usually: " + hint)
        if name != "my_subsystem":
            print("\n   python run.py (without a file name) still runs your untouched my_subsystem.py.")
        return None


def main():
    print(LEGEND)
    print(f"Running: {VERSION}")
    me = load()
    if me is None:
        return
    steps = SCENARIOS[TEAM](me)
    reached = expected = 0
    for title, call, expect, _ in steps:
        if call is None:
            print("\n" + title + "\n" + "=" * len(title))
            continue
        print("\n" + title)
        before = len(standins.CALLS)
        try:
            answer = call()
            print("   came back:", show(answer))
        except NotImplementedError as exc:
            print("   NOT WRITTEN YET:", exc)
            print("   -> step 1: make it return a plausible fixed answer (a stub).")
        except Exception:                        # noqa: BLE001
            print("   IT BROKE:")
            print("   " + traceback.format_exc().strip().replace("\n", "\n   "))
        made = standins.CALLS[before:]
        for frm, to, what, ans in made:
            print(f"   {frm} -> {to}: {what}  ->  {show(ans)}")
        for to, method, label in expect:
            expected += 1
            done = any(f == TEAM and t == to and w.startswith(method + "(") for f, t, w, _ in made)
            reached += done
            print(f"   [{'x' if done else ' '}] {label}")
    print(f"\nCalls across the edge that the resolution expects: {reached} of {expected} made.")
    print("(After step 1 this is still 0: your methods answer, but call nobody. "
          f"After step 4 it should be {expected} of {expected}.)")


if __name__ == "__main__":
    main()
