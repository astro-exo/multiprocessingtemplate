"""The demand-side sanity check the original analysis never ran.

Every version of this work modelled the SUPPLY side - what it costs to build a
stall - and then asserted an occupancy. Nothing ever asked whether enough trucks
exist within a catchment of Bloomfield to fill the recommended programme.

That omission matters because the recommendation was 'buy more scale', and scale
is exactly what a demand constraint would forbid.
"""
CT_TOTAL = 1238        # CTDOT statewide truck parking study
CT_PUBLIC_NOW = 420    # public service plazas and rest areas
CT_PUBLIC_2030 = 600   # after the $31M CTDOT expansion programme
CT_PRIVATE = CT_TOTAL - CT_PUBLIC_NOW
DEMAND_GROWTH_2040 = 0.18

W = 84
print("=" * W)
print("DEMAND-SIDE SANITY CHECK  -  never run in the original analysis")
print("=" * W)
print(f"Connecticut statewide truck parking spaces        {CT_TOTAL:>8,}")
print(f"  of which public (plazas, rest areas)            {CT_PUBLIC_NOW:>8,}")
print(f"  implied private / other                         {CT_PRIVATE:>8,}")
print(f"Projected demand growth to 2040                   {DEMAND_GROWTH_2040:>8.0%}")
print()
print(f"{'programme':<34}{'stalls':>8}{'% of CT total':>15}{'% of CT private':>17}")
print("-" * W)
for lab, n in [("S2 as modelled", 216),
               ("N* - the financing threshold", 339),
               ("14 acres (original recommendation)", 303),
               ("18 acres (50% probability point)", 390),
               ("20 acres", 433),
               ("30 acres", 649)]:
    print(f"{lab:<34}{n:>8,}{n/CT_TOTAL:>15.1%}{n/CT_PRIVATE:>17.1%}")

print()
print("=" * W)
print("WHAT THIS MEANS")
print("=" * W)
n_star = 339
print(f"- The financing threshold of {n_star} stalls is {n_star/CT_TOTAL:.0%} of every truck parking")
print(f"  space in Connecticut, and {n_star/CT_PRIVATE:.0%} of the private supply.")
print(f"- The 50%-probability programme ({390} stalls) is {390/CT_PRIVATE:.0%} of private supply.")
print("- No single facility plausibly holds that share of a statewide market unless")
print("  Bloomfield sits on a demand concentration that was never demonstrated.")
print()
print("- The model holds stabilized occupancy CONSTANT at 88% while stall count triples.")
print("  That is the flaw. Occupancy is an OUTPUT of demand versus supply, not an input")
print("  independent of programme size. Every 'scale fixes it' conclusion in this work")
print("  rests on that independence, and it is almost certainly false.")
print()
print("- Direction of the error: scale raises stall count faster than it raises")
print("  capturable demand, so true occupancy FALLS as the programme grows. The")
print("  recommendation to buy site size is therefore biased optimistic by an")
print("  unquantified amount.")

# how sensitive is the conclusion to occupancy falling with size?
print()
print("=" * W)
print("IF OCCUPANCY DECAYS WITH PROGRAMME SIZE  -  illustrative only, not calibrated")
print("=" * W)
import sys, io, contextlib
sys.path.insert(0, ".")
with contextlib.redirect_stdout(io.StringIO()):
    import verify as V
    import framework as FW
z = FW.reduce_scenario("S2")
D, LTC, K = 1.25, 0.65, z["k"]


def dscr_at(N, occ_factor):
    R = z["R"] * occ_factor
    c = z["c"] - 0.0546 * z["R"] + 0.0546 * R
    return (N * (R - c) * 12 - z["F"]) / (LTC * K * (N * z["v"] + z["PHI"]))


print(f"{'acres':>7}{'stalls':>8}{'occ flat':>11}{'occ -10%/doubling':>21}{'occ -20%/doubling':>21}")
print("-" * W)
import math
for ac in [10, 14, 18, 20, 25, 30, 40]:
    N = ac * 43560 * 0.72 / 1450
    doublings = math.log2(N / 216)
    print(f"{ac:>7}{N:>8.0f}{dscr_at(N,1.0):>11.2f}"
          f"{dscr_at(N,0.90**doublings):>21.2f}{dscr_at(N,0.80**doublings):>21.2f}")
print()
print("A 10%-per-doubling occupancy decay pushes the 1.25x crossing well past 30 acres.")
print("A 20% decay removes the crossing entirely - scale stops being a solution at all.")
print("These decay rates are ILLUSTRATIVE. The point is that the sign of the scale")
print("conclusion depends on a demand elasticity nobody has measured.")
