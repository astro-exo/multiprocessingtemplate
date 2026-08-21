"""Which inputs actually move the answer?

Computes the normalised elasticity of DSCR to every input in the model:
  e = (dDSCR/DSCR) / (dX/X)   evaluated by central difference at +/-5%.

An input with |e| < 0.1 cannot change the conclusion no matter how wrong it is.
An input with |e| > 1.0 is where all the diligence budget should go.
"""
import copy, io, contextlib, sys
sys.path.insert(0, ".")
with contextlib.redirect_stdout(io.StringIO()):
    import verify as V

BASE = copy.deepcopy(V.S["S2"])


def dscr(over=None):
    p = copy.deepcopy(BASE)
    if over:
        p.update(over)
    return V.run(p)["dscr65"]


BASE_DSCR = dscr()

# every scalar input that could plausibly be argued about
INPUTS = [k for k, v in BASE.items()
          if isinstance(v, (int, float)) and k not in ("p_amort",)]

rows = []
for k in INPUTS:
    x = BASE[k]
    if x == 0:
        rows.append((k, x, None, "zero-valued - elasticity undefined"))
        continue
    hi = dscr({k: x * 1.05})
    lo = dscr({k: x * 0.95})
    e = ((hi - lo) / BASE_DSCR) / 0.10
    rows.append((k, x, e, ""))

rows.sort(key=lambda r: -abs(r[2]) if r[2] is not None else 0)

print("=" * 88)
print(f"DSCR ELASTICITY  |  base DSCR = {BASE_DSCR:.3f}x   (scenario S2)")
print("=" * 88)
print(f"{'input':<26}{'value':>14}{'elasticity':>13}   interpretation")
print("-" * 88)
for k, x, e, note in rows:
    if e is None:
        print(f"{k:<26}{x:>14,.4g}{'n/a':>13}   {note}")
        continue
    if abs(e) >= 1.0:
        tag = "DOMINANT"
    elif abs(e) >= 0.4:
        tag = "material"
    elif abs(e) >= 0.1:
        tag = "minor"
    else:
        tag = "immaterial - cannot change the conclusion"
    print(f"{k:<26}{x:>14,.4g}{e:>13.3f}   {tag}")

print()
print("=" * 88)
print("HOW WRONG WOULD ONE INPUT HAVE TO BE, ALONE, TO REACH 1.25x?")
print("=" * 88)
target = 1.25
print(f"{'input':<26}{'base':>14}{'needed':>16}{'change':>12}")
print("-" * 88)
for k, x, e, note in rows[:14]:
    if e is None or x == 0 or abs(e) < 0.05:
        continue
    lo, hi = 1e-9, 1.0
    # search a multiplier in [0.02, 50] that hits the target, if one exists
    found = None
    a, b = 0.02, 50.0
    fa = dscr({k: x * a}) - target
    fb = dscr({k: x * b}) - target
    if fa * fb <= 0:
        for _ in range(80):
            m = (a + b) / 2
            fm = dscr({k: x * m}) - target
            if fa * fm <= 0:
                b, fb = m, fm
            else:
                a, fa = m, fm
        found = (a + b) / 2
    if found and 0.02 < found < 50:
        print(f"{k:<26}{x:>14,.4g}{x*found:>16,.4g}{found-1:>+11.0%}")
    else:
        print(f"{k:<26}{x:>14,.4g}{'unreachable':>16}{'—':>12}")
