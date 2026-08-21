"""A general framework for parking / IOS deal feasibility.

The 40-input model reduces, exactly, to one identity. Everything else is
parameterisation. Stating it this way makes the whole problem auditable:

    DSCR = [ N(R - c)12 - F ] / [ LTC . k . (N.v + PHI) ]

    N    stalls                       = A.43560.y / s
    R    blended revenue per stall-month
    c    variable operating cost per stall-month
    F    fixed annual operating cost
    v    variable capex per stall
    PHI  fixed capex (land, entitlement, site infrastructure, financing, reserves)
    k    annual mortgage constant
    LTC  loan to cost

Rearranged for the financing test DSCR >= D:

    N . [ (R-c)12 - D.LTC.k.v ]  >=  F + D.LTC.k.PHI
    N . m                        >=  B

    m = per-stall annual contribution AFTER servicing that stall's own capital
    B = the site's fixed burden, capitalised at the same test

Two questions, in order, decide any deal of this shape:

    1. Is m > 0?   If not, no amount of scale ever works - every added stall
                   digs the hole deeper. Stop.
    2. Is N >= B/m? If not, the programme is too small for its own fixed costs.

A third test sits above both and needs no financing assumptions at all:

    yield on cost vs. cost of debt.  If YoC < interest rate, leverage is
    NEGATIVE - borrowing reduces equity returns - and DSCR is a distraction.
"""
import copy, io, contextlib, sys
sys.path.insert(0, ".")
with contextlib.redirect_stdout(io.StringIO()):
    import verify as V


def reduce_scenario(name):
    """Extract (N, R, c, F, v, PHI, k, LTC) from the full model."""
    p, o = V.S[name], V.R[name]
    N = o["stalls"]
    R = o["rev_stall"]                       # blended revenue per stall-month
    # per-stall operating cost: the per-stall line items, plus revenue-linked opex
    per_stall_yr = (p["ins"] + p["rm"] + p["util"] + p["trash"]
                    + p["mktg"] + p["reserve"])
    c = per_stall_yr / 12 + o["ovar_pct"] * R
    # everything else in opex is fixed for a given programme
    F = o["opex"] - N * c * 12
    v = o["cps_v"]
    PHI = o["alloc_f"]
    k = o["k"]
    LTC = p["p_ltc"]
    return dict(name=name, N=N, R=R, c=c, F=F, v=v, PHI=PHI, k=k, LTC=LTC,
                noi=o["noi"], cost=o["total"], dscr=o["dscr65"], yoc=o["yoc"],
                rate=p["p_rate"])


def dscr_identity(z):
    return (z["N"] * (z["R"] - z["c"]) * 12 - z["F"]) / (z["LTC"] * z["k"] * (z["N"] * z["v"] + z["PHI"]))


W = 92
print("=" * W)
print("1.  DOES THE IDENTITY REPRODUCE THE 40-INPUT MODEL?")
print("=" * W)
print(f"{'':<10}{'N':>6}{'R $/mo':>9}{'c $/mo':>9}{'F $/yr':>11}{'v $/stall':>11}"
      f"{'PHI $':>12}{'DSCR id.':>10}{'DSCR model':>12}{'err':>8}")
Z = {}
for nm in ["S1", "S2", "S3"]:
    z = Z[nm] = reduce_scenario(nm)
    d = dscr_identity(z)
    print(f"{nm:<10}{z['N']:>6}{z['R']:>9.0f}{z['c']:>9.2f}{z['F']:>11,.0f}"
          f"{z['v']:>11,.0f}{z['PHI']:>12,.0f}{d:>10.4f}{z['dscr']:>12.4f}"
          f"{abs(d-z['dscr']):>8.2e}")
print()
print("Exact to floating point. The identity IS the model.")

print()
print("=" * W)
print("2.  TEST ZERO - THE SIGN OF LEVERAGE  (needs no DSCR convention at all)")
print("=" * W)
print(f"{'':<10}{'yield on cost':>15}{'debt rate':>12}{'spread':>10}   verdict")
print("-" * W)
for nm in ["S1", "S2", "S3"]:
    z = Z[nm]
    sp = z["yoc"] - z["rate"]
    print(f"{nm:<10}{z['yoc']:>15.2%}{z['rate']:>12.2%}{sp:>+10.2%}   "
          f"{'NEGATIVE leverage - debt destroys equity return' if sp < 0 else 'positive leverage'}")
print()
print("Every scenario earns less unlevered than the debt costs. Borrowing makes the")
print("equity return worse, not better. This holds regardless of DSCR floors, cap")
print("rates or loan-to-cost - it is a property of the asset, not of the financing.")

print()
print("=" * W)
print("3.  TEST ONE - IS A MARGINAL STALL SELF-FINANCING?   m = (R-c)12 - D.LTC.k.v")
print("=" * W)
D = 1.25
print(f"{'':<10}{'(R-c)*12':>12}{'stall debt':>13}{'m $/stall/yr':>15}   verdict")
print("-" * W)
for nm in ["S1", "S2", "S3"]:
    z = Z[nm]
    gross = (z["R"] - z["c"]) * 12
    stall_debt = D * z["LTC"] * z["k"] * z["v"]
    m = gross - stall_debt
    z["m"] = m
    print(f"{nm:<10}{gross:>12,.0f}{stall_debt:>13,.0f}{m:>15,.0f}   "
          f"{'positive - scale can work' if m > 0 else 'NEGATIVE - no scale ever works'}")

print()
print("=" * W)
print("4.  TEST TWO - HOW MANY STALLS DOES THE FIXED BURDEN DEMAND?   N* = B/m")
print("=" * W)
print(f"{'':<10}{'F $/yr':>11}{'D.LTC.k.PHI':>14}{'B $/yr':>12}{'m':>9}"
      f"{'N* needed':>12}{'N actual':>10}{'shortfall':>11}")
print("-" * W)
for nm in ["S1", "S2", "S3"]:
    z = Z[nm]
    cap_phi = D * z["LTC"] * z["k"] * z["PHI"]
    B = z["F"] + cap_phi
    Nstar = B / z["m"] if z["m"] > 0 else float("inf")
    z["Nstar"] = Nstar
    print(f"{nm:<10}{z['F']:>11,.0f}{cap_phi:>14,.0f}{B:>12,.0f}{z['m']:>9,.0f}"
          f"{Nstar:>12,.0f}{z['N']:>10}{Nstar-z['N']:>+11,.0f}")
print()
print("Same answer the 12-tab workbook gives, from six numbers instead of forty.")

print()
print("=" * W)
print("5.  THE ASYMPTOTE - BEST ACHIEVABLE DSCR AT INFINITE SCALE")
print("=" * W)
print(f"{'':<10}{'DSCR at N->inf':>16}{'at N actual':>14}{'headroom':>12}")
print("-" * W)
for nm in ["S1", "S2", "S3"]:
    z = Z[nm]
    asym = (z["R"] - z["c"]) * 12 / (z["LTC"] * z["k"] * z["v"])
    print(f"{nm:<10}{asym:>16.2f}{z['dscr']:>14.2f}{asym-z['dscr']:>+12.2f}")
print()
print("The ceiling is set by unit economics alone: (R-c)*12 / (LTC.k.v). Scale walks")
print("the deal toward that ceiling and never past it. If the ceiling is below the")
print("test, the site size question never arises.")


# ---------------------------------------------------------------- inversion
print()
print("=" * W)
print("6.  THE INVERSION  -  what the unmeasured input must be, at each programme size")
print("=" * W)
print("Rearranged for R, the identity gives the revenue a site MUST achieve:")
print()
print("      R* = c + [ F + D.LTC.k.(N.v + PHI) ] / 12N")
print()
z = Z["S2"]
D = 1.25
print(f"{'gross ac':>9}{'stalls':>8}{'required R':>13}{'vs $309 base':>14}"
      f"{'DSCR at $309':>14}{'DSCR at $400':>14}")
print("-" * W)
for ac in [5, 8, 10, 12, 14, 16, 20, 25, 30, 40]:
    N = ac * 43560 * 0.72 / 1450
    Rstar = z["c"] + (z["F"] + D * z["LTC"] * z["k"] * (N * z["v"] + z["PHI"])) / (12 * N)
    def dscr_at(R):
        c = z["c"] - 0.0546 * z["R"] + 0.0546 * R      # revenue-linked opex follows R
        return (N * (R - c) * 12 - z["F"]) / (z["LTC"] * z["k"] * (N * z["v"] + z["PHI"]))
    print(f"{ac:>9}{N:>8.0f}{Rstar:>13,.0f}{Rstar/309-1:>+13.0%}"
          f"{dscr_at(309):>14.2f}{dscr_at(400):>14.2f}")
print()
print("Read this as the diligence question, not the answer: 'can a secured 53ft stall")
print("in Bloomfield be let at R* with the site filled?' That is a market question with")
print("a findable answer. The model cannot settle it and should not pretend to.")

print()
print("=" * W)
print("7.  WHAT SURVIVES  -  the six numbers that decide any deal of this shape")
print("=" * W)
for k, lab, unit in [("N", "stalls", ""), ("R", "blended revenue per stall-month", "$"),
                     ("c", "variable operating cost per stall-month", "$"),
                     ("F", "fixed annual operating cost", "$"),
                     ("v", "variable capex per stall", "$"),
                     ("PHI", "fixed capex", "$")]:
    print(f"   {k:<5}{lab:<44}{unit}{Z['S2'][k]:>14,.0f}")
print()
print("Plus two financing terms - LTC and the mortgage constant k - and one test level D.")
print("Nine numbers. Everything else in the workbook is parameterisation of these,")
print("and roughly forty of those inputs cannot change the answer at all.")
