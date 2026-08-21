"""Independent pure-Python replication of the workbook math.
Used to cross-check the XLSX and to source the numbers quoted in the write-up."""
import math

S = {}
common = dict(sf_stall=1450, close_pct=0.022, credit=0.020, growth=0.030,
              mill=34.40, assess=0.70, tv_land=1.00, tv_impr=0.45,
              mgmt_pct=0.040, cm=0.030, test=0.009, brisk=0.011,
              c_ltc=0.60, c_rate=0.0825, c_orig=0.010, p_ltc=0.65, p_ltv=0.65,
              p_rate=0.0725, p_amort=25, p_dscr=1.25, lu_months=6)

S["S1"] = dict(common, name="Greenfield, full-depth asphalt, staffed",
    acres=10.0, yield_pct=0.72, land_ac=175000,
    mix_month=0.80, rate_month=340, occ_month=0.90, rate_night=26, occ_night=0.62,
    anc=0.050, ins=230, staff=165000, monitor=42000, snow_ac=8800, rm=210, util=165,
    trash=95, proc=0.020, mktg=75, prof=22000, reserve=165,
    bond=0.010, cont=0.12, c_months=16, c_draw=0.55, c_costs=65000,
    exit_cap=0.0750, lu_mktg=85000,
    sf=[0.35,1.75,2.40,4.35,0.48,0.12], per_stall=[1225,375,620,185],
    dd=[14000,22000,4000,35000,18000,28000,195000,18000,85000,18000,22000,12000],
    infra=dict(demo=95000, basin=385000, entry=195000, fence_rate=58, gates=155000,
               sec=145000, bldg=265000, util=210000, land_sc=135000))

S["S2"] = dict(common, name="Greenfield, value-engineered, unmanned",
    acres=10.0, yield_pct=0.72, land_ac=175000,
    mix_month=0.80, rate_month=315, occ_month=0.88, rate_night=24, occ_night=0.58,
    anc=0.030, ins=210, staff=0, monitor=52000, snow_ac=8200, rm=235, util=145,
    trash=70, proc=0.015, mktg=85, prof=18000, reserve=195,
    bond=0.000, cont=0.12, c_months=14, c_draw=0.55, c_costs=65000,
    exit_cap=0.0775, lu_mktg=85000,
    sf=[0.35,1.55,2.05,1.95,0.44,0.10], per_stall=[1225,340,0,210],
    dd=[14000,22000,4000,35000,18000,28000,175000,12000,85000,18000,22000,12000],
    infra=dict(demo=95000, basin=355000, entry=175000, fence_rate=52, gates=145000,
               sec=175000, bldg=145000, util=185000, land_sc=105000))

S["S3"] = dict(common, name="Retrofit of an existing paved yard",
    acres=8.0, yield_pct=0.78, land_ac=385000,
    mix_month=0.85, rate_month=325, occ_month=0.90, rate_night=25, occ_night=0.60,
    anc=0.035, ins=220, staff=0, monitor=50000, snow_ac=8800, rm=225, util=150,
    trash=75, proc=0.015, mktg=80, prof=18000, reserve=185,
    bond=0.000, cont=0.15, c_months=10, c_draw=0.60, c_costs=60000,
    exit_cap=0.0750, lu_mktg=75000,
    sf=[0.05,0.20,0.15,1.85,0.12,0.12], per_stall=[1225,300,310,210],
    dd=[12000,14000,4500,95000,6000,22000,85000,12000,55000,12000,10000,4000],
    infra=dict(demo=165000, basin=120000, entry=110000, fence_rate=52, gates=145000,
               sec=165000, bldg=155000, util=95000, land_sc=65000))


def run(p):
    o = {}
    o["stalls"] = st = math.floor(p["acres"] * 43560 * p["yield_pct"] / p["sf_stall"])
    o["yard_sf"] = ysf = st * p["sf_stall"]
    o["yard_ac"] = ysf / 43560
    o["perim"] = perim = round(4 * math.sqrt(p["acres"] * 43560))
    o["density"] = st / p["acres"]

    # ---- variable hard
    o["sf_sub"] = sfs = sum(p["sf"])
    o["hv"] = hv = sfs * ysf + sum(p["per_stall"]) * st
    o["var_hard_stall"] = hv / st
    # ---- fixed hard
    inf = p["infra"]
    o["hf"] = hf = (inf["demo"] + inf["basin"] + inf["entry"] + perim * inf["fence_rate"]
                    + inf["gates"] + inf["sec"] + inf["bldg"] + inf["util"] + inf["land_sc"])
    o["ht"] = ht = hf + hv
    o["vshare"] = vs = hv / ht
    o["soft"] = soft = ht * (p["cm"] + p["test"] + p["brisk"] + p["bond"])
    o["cont"] = cont = (ht + soft) * p["cont"]
    o["constr"] = constr = ht + soft + cont
    o["land"] = land = p["land_ac"] * p["acres"]
    o["land_sub"] = land_sub = land * (1 + p["close_pct"])
    o["dd"] = dd = sum(p["dd"])
    o["impr_basis"] = impr = constr + dd
    o["preloan"] = pre = constr + land_sub + dd
    cloan = pre * p["c_ltc"]
    o["fin"] = fin = (cloan * p["c_orig"] + cloan * p["c_rate"] * p["c_draw"] * p["c_months"] / 12
                      + p["c_costs"] + land * p["assess"] * p["mill"] / 1000 * p["c_months"] / 12)
    o["cap_basis"] = cap = pre + fin

    # ---- revenue
    st_m = round(st * p["mix_month"])
    st_t = st - st_m
    gpr_m = st_m * p["rate_month"] * 12
    gpr_t = st_t * p["rate_night"] * 365
    gpr = gpr_m + gpr_t
    vac = gpr_m * (1 - p["occ_month"]) + gpr_t * (1 - p["occ_night"])
    park = (gpr - vac) * (1 - p["credit"])
    egi = park * (1 + p["anc"])
    o.update(st_m=st_m, st_t=st_t, gpr=gpr, park=park, egi=egi,
             rev_stall=egi / st / 12, rev_ac=egi / p["acres"])

    # ---- opex
    tax = (land * p["tv_land"] + impr * p["tv_impr"]) * p["assess"] * p["mill"] / 1000
    ofix = (tax + p["ins"] * st + p["staff"] + p["monitor"] + p["snow_ac"] * o["yard_ac"]
            + p["rm"] * st + p["util"] * st + p["trash"] * st + p["mktg"] * st
            + p["prof"] + p["reserve"] * st)
    ovar = egi * p["mgmt_pct"] + park * p["proc"]
    opex = ofix + ovar
    noi = egi - opex
    o.update(tax=tax, ofix=ofix, ovar=ovar, opex=opex, noi=noi,
             opex_ratio=opex / egi, opex_stall=opex / st / 12,
             ovar_pct=ovar / egi, noi_stall=noi / st)

    # ---- lease-up reserve closes the cost stack
    o["lu"] = lu = opex * p["lu_months"] / 12 + p["lu_mktg"]
    o["total"] = total = cap + lu
    o["alloc_v"] = av = hv + (soft + cont) * vs
    o["alloc_f"] = af = total - av
    o.update(cps_v=av / st, cps_f=af / st, cps_t=total / st,
             cps_land=land_sub / st, fpct=af / total, per_ac=total / p["acres"])

    # ---- debt
    i = p["p_rate"] / 12
    n = p["p_amort"] * 12
    k = (i / (1 - (1 + i) ** -n)) * 12
    val = noi / p["exit_cap"]
    l_ltc = total * p["p_ltc"]
    l_ltv = val * p["p_ltv"]
    l_dscr = noi / (p["p_dscr"] * k)
    loan = max(0, min(l_ltc, l_ltv, l_dscr))
    bind = "DSCR" if loan == l_dscr else ("LTV" if loan == l_ltv else "LTC")
    ds65 = l_ltc * k
    o.update(k=k, val=val, yoc=noi / total, profit=val - total, margin=(val - total) / total,
             spread=(noi / total - p["exit_cap"]) * 10000,
             l_ltc=l_ltc, l_ltv=l_ltv, l_dscr=l_dscr, loan=loan, bind=bind,
             ds65=ds65, dscr65=noi / ds65, dy=noi / l_ltc,
             eq=total - loan, ds=loan * k,
             dscr=(noi / (loan * k)) if loan > 0 else 0)
    req_noi = ds65 * p["p_dscr"]
    req_egi = (req_noi + ofix) / (1 - o["ovar_pct"])
    req_rev = req_egi / st / 12
    max_cost = noi / (p["p_dscr"] * p["p_ltc"] * k)
    o.update(req_noi=req_noi, noi_gap=noi - req_noi, req_rev=req_rev,
             rev_gap=req_rev / o["rev_stall"] - 1,
             max_cost=max_cost, max_cps=max_cost / st,
             max_land=(max_cost - (total - land_sub)) / (p["acres"] * (1 + p["close_pct"])),
             be_occ=((ds65 + ofix) / (1 - o["ovar_pct"])) / egi)
    return o


R = {k: run(v) for k, v in S.items()}

W = 16
def row(label, key, fmt="{:,.0f}"):
    print(f"{label:<46}" + "".join(fmt.format(R[s][key]).rjust(W) for s in ["S1", "S2", "S3"]))

print("=" * 94)
print(f"{'BLOOMFIELD CT TRUCK PARKING - MODEL OUTPUT':<46}" + "".join(s.rjust(W) for s in ["S1","S2","S3"]))
print("=" * 94)
print(f"{'':<46}" + "".join(S[s]['name'][:15].rjust(W) for s in ["S1","S2","S3"]))
print("-" * 94)
print()
for lbl, k, f in [
    ("Stalls", "stalls", "{:,.0f}"),
    ("Density (stalls/gross acre)", "density", "{:,.1f}"),
    ("Paved yard SF", "yard_sf", "{:,.0f}"),
    ("--- CAPEX ---", None, None),
    ("Variable hard cost", "hv", "${:,.0f}"),
    ("Fixed hard cost", "hf", "${:,.0f}"),
    ("Total hard cost", "ht", "${:,.0f}"),
    ("Soft loadings", "soft", "${:,.0f}"),
    ("Contingency", "cont", "${:,.0f}"),
    ("Land + closing", "land_sub", "${:,.0f}"),
    ("Pre-development", "dd", "${:,.0f}"),
    ("Financing & carry", "fin", "${:,.0f}"),
    ("Lease-up reserve", "lu", "${:,.0f}"),
    ("TOTAL PROJECT COST", "total", "${:,.0f}"),
    ("  Fixed capex", "alloc_f", "${:,.0f}"),
    ("  Variable capex", "alloc_v", "${:,.0f}"),
    ("FIXED COST PER STALL", "cps_f", "${:,.0f}"),
    ("VARIABLE COST PER STALL", "cps_v", "${:,.0f}"),
    ("ALL-IN COST PER STALL", "cps_t", "${:,.0f}"),
    ("  land per stall", "cps_land", "${:,.0f}"),
    ("  fixed share of cost", "fpct", "{:.1%}"),
    ("Cost per gross acre", "per_ac", "${:,.0f}"),
    ("--- OPERATIONS ---", None, None),
    ("EGI", "egi", "${:,.0f}"),
    ("Blended rev / stall / month", "rev_stall", "${:,.0f}"),
    ("Revenue per gross acre", "rev_ac", "${:,.0f}"),
    ("Real estate taxes", "tax", "${:,.0f}"),
    ("Total opex", "opex", "${:,.0f}"),
    ("  opex ratio", "opex_ratio", "{:.1%}"),
    ("  opex / stall / month", "opex_stall", "${:,.0f}"),
    ("NET OPERATING INCOME", "noi", "${:,.0f}"),
    ("  NOI per stall / yr", "noi_stall", "${:,.0f}"),
    ("YIELD ON COST", "yoc", "{:.2%}"),
    ("Value at exit cap", "val", "${:,.0f}"),
    ("Development profit / (loss)", "profit", "${:,.0f}"),
    ("  margin on cost", "margin", "{:.1%}"),
    ("  spread to exit cap (bps)", "spread", "{:,.0f}"),
    ("--- DEBT ---", None, None),
    ("Annual debt constant", "k", "{:.2%}"),
    ("Loan at 65% LTC", "l_ltc", "${:,.0f}"),
    ("Debt service at 65% LTC", "ds65", "${:,.0f}"),
    ("DSCR AT 65% LTC", "dscr65", "{:.2f}x"),
    ("Debt yield at 65% LTC", "dy", "{:.1%}"),
    ("Supportable loan", "loan", "${:,.0f}"),
    ("Required equity", "eq", "${:,.0f}"),
    ("--- BREAK-EVENS (1.25x DSCR) ---", None, None),
    ("NOI required", "req_noi", "${:,.0f}"),
    ("NOI shortfall", "noi_gap", "${:,.0f}"),
    ("Required rev / stall / month", "req_rev", "${:,.0f}"),
    ("  rate gap", "rev_gap", "{:+.1%}"),
    ("Max supportable cost / stall", "max_cps", "${:,.0f}"),
    ("Max supportable land $/acre", "max_land", "${:,.0f}"),
    ("Break-even occupancy", "be_occ", "{:.1%}"),
]:
    if k is None:
        print(f"\n{lbl}")
        continue
    print(f"{lbl:<46}" + "".join(f.format(R[s][k]).rjust(W) for s in ["S1", "S2", "S3"]))
print()
for s in ["S1","S2","S3"]:
    print(f"{s}: {S[s]['name']}  |  binding loan constraint = {R[s]['bind']}")
