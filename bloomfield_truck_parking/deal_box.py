"""What combination of land price, rate and density actually clears a 1.25x DSCR?
Re-uses the verify.py engine, sweeping the levers that matter."""
import copy, math
import verify as V

BASE = copy.deepcopy(V.S["S2"])   # value-engineered greenfield is the most plausible new-build


def dscr(over):
    p = copy.deepcopy(BASE)
    p.update(over)
    o = V.run(p)
    return o


print("=" * 100)
print("DEAL BOX  |  DSCR at 65% LTC for the value-engineered scenario")
print("=" * 100)
rates = [300, 325, 350, 375, 400, 425, 450, 475]
lands = [0, 40000, 80000, 120000, 160000, 200000]
print(f"{'rate $/mo':>10} |" + "".join(f"{('$%dk/ac' % (l/1000)):>12}" for l in lands))
print("-" * 100)
for rt in rates:
    row = f"{rt:>10} |"
    for l in lands:
        o = dscr(dict(rate_month=rt, rate_night=round(rt / 13.0), land_ac=l))
        row += f"{o['dscr65']:>11.2f}x"
    print(row)

print()
print("=" * 100)
print("DENSITY EFFECT  |  all-in cost per stall and DSCR, holding rate at $350/mo, land at $120k/acre")
print("=" * 100)
print(f"{'SF/stall':>10}{'yield %':>10}{'stalls':>9}{'cost/stall':>13}{'NOI/stall':>12}{'cost:NOI':>10}{'DSCR':>9}{'YoC':>9}")
for sfs, yp in [(1650, 0.66), (1450, 0.72), (1300, 0.76), (1150, 0.80)]:
    o = dscr(dict(sf_stall=sfs, yield_pct=yp, rate_month=350, rate_night=27, land_ac=120000))
    print(f"{sfs:>10}{yp:>10.0%}{o['stalls']:>9,}{o['cps_t']:>13,.0f}{o['noi_stall']:>12,.0f}"
          f"{o['cps_t']/o['noi_stall']:>9.1f}x{o['dscr65']:>9.2f}x{o['yoc']:>9.2%}")

print()
print("=" * 100)
print("SITE SCALE  |  fixed costs spread, rate $350/mo, land $120k/acre")
print("=" * 100)
print(f"{'acres':>10}{'stalls':>9}{'fixed/stall':>14}{'var/stall':>12}{'all-in/stall':>14}{'DSCR':>9}{'YoC':>9}")
for ac in [4, 6, 8, 10, 14, 20, 30]:
    o = dscr(dict(acres=ac, rate_month=350, rate_night=27, land_ac=120000))
    print(f"{ac:>10}{o['stalls']:>9,}{o['cps_f']:>14,.0f}{o['cps_v']:>12,.0f}"
          f"{o['cps_t']:>14,.0f}{o['dscr65']:>9.2f}x{o['yoc']:>9.2%}")

print()
print("=" * 100)
print("THE VIABLE CASE  |  every lever pulled at once")
print("=" * 100)
viable = dict(acres=14, land_ac=95000, sf_stall=1300, yield_pct=0.76,
              rate_month=395, rate_night=32, occ_month=0.92, occ_night=0.65,
              mix_month=0.85, anc=0.05, monitor=60000, tv_impr=0.35)
o = dscr(viable)
for k, lbl, f in [("stalls","Stalls","{:,.0f}"), ("density","Stalls per gross acre","{:,.1f}"),
                  ("total","Total project cost","${:,.0f}"),
                  ("cps_f","Fixed cost per stall","${:,.0f}"),
                  ("cps_v","Variable cost per stall","${:,.0f}"),
                  ("cps_t","All-in cost per stall","${:,.0f}"),
                  ("rev_stall","Blended revenue/stall/mo","${:,.0f}"),
                  ("opex_stall","Opex/stall/mo","${:,.0f}"),
                  ("egi","EGI","${:,.0f}"), ("opex","Opex","${:,.0f}"),
                  ("opex_ratio","Opex ratio","{:.1%}"),
                  ("noi","NOI","${:,.0f}"), ("noi_stall","NOI per stall","${:,.0f}"),
                  ("yoc","Yield on cost","{:.2%}"),
                  ("dscr65","DSCR at 65% LTC","{:.2f}x"),
                  ("dy","Debt yield","{:.1%}"),
                  ("val","Value at exit cap","${:,.0f}"),
                  ("profit","Development profit","${:,.0f}"),
                  ("max_land","Max supportable land $/ac","${:,.0f}")]:
    print(f"{lbl:<34}{f.format(o[k]):>18}")
print(f"{'Cost per stall : NOI per stall':<34}{o['cps_t']/o['noi_stall']:>17.1f}x")

print()
print("=" * 100)
print("COST : NOI RATIO REQUIRED  |  at 65% LTC and an 8.67% constant, 1.25x DSCR needs a 7.05% yield on cost")
print("   -> all-in cost per stall must be no more than ~14.2x NOI per stall")
print("=" * 100)
for name in ["S1", "S2", "S3"]:
    o = V.R[name]
    print(f"{name}: cost/stall ${o['cps_t']:>8,.0f}   NOI/stall ${o['noi_stall']:>6,.0f}"
          f"   ratio {o['cps_t']/o['noi_stall']:>5.1f}x   (needs <= 14.2x)")

print()
print("=" * 100)
print("BRACKETING THE VIABLE CASE  |  same 14-acre high-density program, three rate/basis assumptions")
print("=" * 100)
cases = {
 "Conservative  14ac @ $150k/ac, 1,450 SF/stall, $340/mo, 88% occ":
   dict(acres=14, land_ac=150000, sf_stall=1450, yield_pct=0.72, rate_month=340,
        rate_night=27, occ_month=0.88, occ_night=0.58),
 "Moderate      14ac @ $120k/ac, 1,300 SF/stall, $365/mo, 90% occ":
   dict(acres=14, land_ac=120000, sf_stall=1300, yield_pct=0.74, rate_month=365,
        rate_night=29, occ_month=0.90, occ_night=0.62, mix_month=0.85),
 "Aggressive    14ac @ $95k/ac,  1,300 SF/stall, $395/mo, 92% occ":
   dict(acres=14, land_ac=95000, sf_stall=1300, yield_pct=0.76, rate_month=395,
        rate_night=32, occ_month=0.92, occ_night=0.65, mix_month=0.85, anc=0.05,
        monitor=60000, tv_impr=0.35),
}
print(f"{'':<62}{'stalls':>8}{'$/stall':>10}{'NOI':>12}{'YoC':>8}{'DSCR':>8}{'cost:NOI':>10}")
for lbl, ov in cases.items():
    o = dscr(ov)
    print(f"{lbl:<62}{o['stalls']:>8,}{o['cps_t']:>10,.0f}{o['noi']:>12,.0f}"
          f"{o['yoc']:>8.2%}{o['dscr65']:>7.2f}x{o['cps_t']/o['noi_stall']:>9.1f}x")
