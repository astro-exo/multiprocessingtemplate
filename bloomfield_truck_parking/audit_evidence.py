"""Evidence grading and a distributional answer.

Two failures in the original work this corrects:

  1. Point estimates dressed as findings. The dominant input has no local
     evidence, so the honest output is a distribution and a required value,
     not a single DSCR.
  2. Precision unrelated to knowledge. Forty inputs were specified to the cent;
     elasticity analysis shows about six of them can change the conclusion.

Grades
  A  primary source - statute, published tariff, executed transaction
  B  published secondary source or market report
  C  engineering estimate derived from first principles, arithmetic checkable
  D  analogy or judgement - defensible but unverified
  F  no basis - invented for the model. Must be reduced to a range or removed.
"""
import random, statistics as st, io, contextlib, sys
sys.path.insert(0, ".")
with contextlib.redirect_stdout(io.StringIO()):
    import verify as V
    import framework as FW

# elasticity of DSCR, from audit_elasticity.py
INVENTORY = [
    # input,                       value,        grade, elasticity, basis
    ("Blended revenue $/stall/mo", "$309",        "F",  1.67,
     "NO Hartford comp exists for a secured 53ft stall. Inferred from a national $150-500 band."),
    ("Stabilized occupancy",       "88%",         "D",  1.67,
     "Own source says 70% is the typical stabilization target; 88% contradicts it."),
    ("Paved SF per stall",         "1,450",       "C", -1.59,
     "12ft x 75ft stall + half a 75ft back-in aisle. Arithmetic is checkable; the half-aisle allocation assumes every row is double-loaded."),
    ("Net yard efficiency",        "72%",         "D",  1.00,
     "No site plan behind it. Real figure depends on wetlands, setbacks and basin siting on a specific parcel."),
    ("Loan to cost",               "65%",         "B", -1.00,
     "Market standard for the asset class."),
    ("Monthly / transient mix",    "80 / 20",     "D", -0.87,
     "Judgement about an off-highway location. Untested."),
    ("Permanent loan rate",        "7.25%",       "B", -0.65,
     "2026 quotes start ~5.74%; niche collateral prices wider."),
    ("Transient rate & utilisation","$24 / 58%",  "D",  0.63,
     "Same evidence problem as the monthly rate, on a smaller share of revenue."),
    ("Gross site acres",           "10.0",        "C",  0.61,
     "A programme choice, not a measurement."),
    ("Land $/acre",                "$175,000",    "D", -0.38,
     "No usable comp found. The one Bloomfield sale located was improved property with a building."),
    ("Bloomfield mill rate",       "34.40",       "A", -0.31,
     "Adopted 2025 Grand List rate, Town of Bloomfield."),
    ("CT assessment ratio",        "70%",         "A", -0.31,
     "Connecticut statute."),
    ("Snow & ice $/paved acre",    "$8,200",      "F", -0.18,
     "Never sourced. Reasoned about, then asserted."),
    ("Assessor factor on improvements","45%",     "F", -0.17,
     "Invented. A CT assessor may use cost or income approach; 45% has no basis."),
    ("Insurance, R&M, utilities, reserves","various","D", "<0.16",
     "Plausible operating estimates. Individually immaterial."),
    ("Contingency, soft-cost loadings","12% / 5%","C", "<0.09",
     "Standard practice. Immaterial to the test."),
    ("Exit cap rate",              "7.75%",       "B",  0.00,
     "ZERO elasticity on DSCR. Also conceptually wrong: a per-stall retail operation is an operating business, not a leased asset."),
    ("Revenue & opex growth",      "3.0%",        "D",  0.00,
     "Zero elasticity on the year-one test. Decoration."),
    ("Construction cost behaviour splits","$0.31/$3.88/$5.26","F","<0.10",
     "The mobilisation/production/material split was invented line by line. Conclusion 'material is 56%' rests entirely on it."),
    ("Production learning exponent","0.070",      "F", "<0.05",
     "Invented. Presented as if calibrated."),
    ("Material volume tier table", "5 steps",     "F", "<0.05",
     "Invented. The source said only '5-15% for bulk orders' and '500+ tons prices better'."),
]

W = 108
print("=" * W)
print("EVIDENCE INVENTORY  -  graded, ranked by how much the answer depends on it")
print("=" * W)
print(f"{'input':<38}{'value':>16}{'grade':>7}{'|elast|':>9}   basis")
print("-" * W)
for name, val, grade, e, basis in INVENTORY:
    es = f"{abs(e):.2f}" if isinstance(e, float) else str(e)
    print(f"{name:<38}{val:>16}{grade:>7}{es:>9}")
    print(f"{'':<70}{basis[:70]}")
    if len(basis) > 70:
        print(f"{'':<70}{basis[70:140]}")

grades = {}
for _, _, g, _, _ in INVENTORY:
    grades[g] = grades.get(g, 0) + 1
print()
print("Grade distribution:", "  ".join(f"{g}:{n}" for g, n in sorted(grades.items())))
print()
print("The single highest-elasticity input in the model carries the lowest grade.")
print("That combination - maximum leverage, minimum evidence - is the whole finding.")

# ---------------------------------------------------------------- distribution
print()
print("=" * W)
print("DISTRIBUTIONAL ANSWER  -  Monte Carlo over the six identity parameters")
print("=" * W)
random.seed(7)
N_SIM = 200_000
D, LTC, K, RATE = 1.25, 0.65, 0.086738, 0.0725


def tri(lo, mode, hi):
    return random.triangular(lo, hi, mode)


def draw(acres=10.0):
    y = tri(0.62, 0.72, 0.80)              # net yard efficiency
    s = tri(1200, 1450, 1750)              # SF per stall
    N = acres * 43560 * y / s
    R = tri(190, 300, 470)                 # blended revenue $/stall/month
    c = tri(70, 88, 118) + 0.055 * R       # per-stall opex, incl. revenue-linked
    F = tri(180_000, 226_000, 310_000)     # fixed annual opex
    v = tri(8_500, 13_100, 18_500)         # variable capex per stall
    PHI = tri(3_600_000, 4_700_000, 6_200_000)   # fixed capex
    noi = N * (R - c) * 12 - F
    cost = N * v + PHI
    return noi / (LTC * K * cost), noi / cost, N


res = [draw() for _ in range(N_SIM)]
dscrs = sorted(r[0] for r in res)
yocs = sorted(r[1] for r in res)
p_dscr = sum(1 for d in dscrs if d >= D) / N_SIM
p_lev = sum(1 for y in yocs if y > RATE) / N_SIM


def pct(a, q):
    return a[int(q * (len(a) - 1))]


print(f"simulations: {N_SIM:,}   site fixed at 10 gross acres")
print()
print(f"{'':<22}{'P10':>10}{'P25':>10}{'median':>10}{'P75':>10}{'P90':>10}")
print("-" * W)
print(f"{'DSCR at 65% LTC':<22}{pct(dscrs,.10):>10.2f}{pct(dscrs,.25):>10.2f}"
      f"{pct(dscrs,.50):>10.2f}{pct(dscrs,.75):>10.2f}{pct(dscrs,.90):>10.2f}")
print(f"{'Yield on cost':<22}{pct(yocs,.10):>10.2%}{pct(yocs,.25):>10.2%}"
      f"{pct(yocs,.50):>10.2%}{pct(yocs,.75):>10.2%}{pct(yocs,.90):>10.2%}")
print()
print(f"P(DSCR >= 1.25x)          = {p_dscr:6.1%}")
print(f"P(positive leverage)      = {p_lev:6.1%}   (yield on cost above the {RATE:.2%} debt rate)")
print()
print("Even with priors deliberately widened to the edge of plausibility, a 10-acre")
print("programme clears the financing test in a minority of draws. The spread is driven")
print("almost entirely by the revenue prior - which is the input with no local evidence.")
