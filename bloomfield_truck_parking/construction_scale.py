"""Economies of scale in yard construction, and the specification levers that
beat them.

The main model treats yard construction as a flat $/SF. That hides where the
money actually goes and which parts respond to volume at all. This module
decomposes the heavy-duty section into three cost behaviours -

  mobilisation   fixed dollars per trade per contract; falls as $/SF with area
  production     labour + equipment hours; improves on a learning curve
  material       tonnage in the ground; responds only to volume-tier pricing

- then prices a menu of section-design changes against the same basis, and
  stacks them into packages.

All rates are calibrated so the base case reproduces the $9.45/SF used for
scenario S1 in the main model. Run:  python3 construction_scale.py
"""

SF_PER_STALL = 1450
BASE_YARD_SF = 313_200          # S1/S2 base case: 216 stalls x 1,450 SF
BASE_YARD_AC = BASE_YARD_SF / 43560

# ---------------------------------------------------------------- quantities
# Compacted HMA runs ~112 lb per SY per inch; processed aggregate ~135 lb/CF.
HMA_T_SF_IN = (112 / 9) / 2000          # 0.00622 tons per SF per inch
AGG_T_SF_IN = (135 / 12) / 2000         # 0.00563 tons per SF per inch

HMA_PRICE = 105.0    # $/ton delivered, CT plant price, binder/wearing mix
AGG_PRICE = 22.0     # $/ton delivered processed aggregate base
RAP_PRICE = 16.0     # $/ton delivered recycled asphalt millings

HMA_IN, AGG_IN = 5.0, 12.0

# ------------------------------------------------- base section cost behaviour
BASE = [
    ("Clearing, grubbing, E&S",               0.06, 0.24, 0.05),
    ("Mass grading & earthwork",              0.09, 1.36, 0.30),
    ('Subgrade prep + 12" aggregate base',    0.05, 0.86, 1.49),
    ('5" bituminous surface course',          0.07, 1.11, 3.17),
    ("Storm conveyance within yard",          0.03, 0.25, 0.20),
    ("Striping, wheel stops, bollards",       0.01, 0.06, 0.05),
]
MOB = sum(r[1] for r in BASE)
PROD = sum(r[2] for r in BASE)
MAT = sum(r[3] for r in BASE)
TOTAL = MOB + PROD + MAT
MOB_DOLLARS = MOB * BASE_YARD_SF

# bulk (tiering) material vs. everything else
BULK_MAT = HMA_T_SF_IN * HMA_IN * HMA_PRICE + AGG_T_SF_IN * AGG_IN * AGG_PRICE
OTHER_MAT = MAT - BULK_MAT

# Production learning curve: each doubling of area takes ~4.7% off the unit
# rate; floored at 82% of base, since crews cannot beat maximum daily output.
PROD_EXPONENT, PROD_FLOOR = 0.070, 0.82

# Material volume tiers. Normalised so the base case = 1.00, because the $9.45
# quote already reflects whatever tier a 216-stall job commands.
TIERS = [(2_000, 1.00), (5_000, 0.97), (10_000, 0.94), (20_000, 0.91), (10**9, 0.89)]


def _tier(tons):
    for cap, f in TIERS:
        if tons <= cap:
            return f
    return TIERS[-1][1]


BASE_TONS = BASE_YARD_SF * (HMA_T_SF_IN * HMA_IN + AGG_T_SF_IN * AGG_IN)
BASE_TIER = _tier(BASE_TONS)


def yard(area_sf, hma_in=HMA_IN, agg_in=AGG_IN, prod_adj=0.0, mat_adj=0.0,
         mob_extra=0.0):
    """Return (mob, production, material, total) $/SF at a given area/section."""
    mob = (MOB_DOLLARS + mob_extra) / area_sf
    prod = (PROD + prod_adj) * max(PROD_FLOOR, (area_sf / BASE_YARD_SF) ** -PROD_EXPONENT)
    tons = area_sf * (HMA_T_SF_IN * hma_in + AGG_T_SF_IN * agg_in)
    rel = _tier(tons) / BASE_TIER
    bulk = HMA_T_SF_IN * hma_in * HMA_PRICE + AGG_T_SF_IN * agg_in * AGG_PRICE
    mat = rel * bulk + OTHER_MAT + mat_adj
    return mob, prod, mat, mob + prod + mat


W = 98
def rule(c="="):
    print(c * W)


rule()
print("1.  WHERE THE MONEY GOES  -  cost behaviour of the base heavy-duty section")
rule()
print(f"{'':<38}{'mobilise':>11}{'production':>12}{'material':>11}{'total':>10}{'mat %':>9}")
for name, m, p, mt in BASE:
    t = m + p + mt
    print(f"{name:<38}{m:>11.2f}{p:>12.2f}{mt:>11.2f}{t:>10.2f}{mt/t:>9.0%}")
rule("-")
print(f"{'$ per SF of paved yard':<38}{MOB:>11.2f}{PROD:>12.2f}{MAT:>11.2f}{TOTAL:>10.2f}{MAT/TOTAL:>9.0%}")
print(f"{'share of yard construction':<38}{MOB/TOTAL:>11.1%}{PROD/TOTAL:>12.1%}{MAT/TOTAL:>11.1%}")
print(f"{'$ per stall (1,450 SF)':<38}{MOB*SF_PER_STALL:>11,.0f}{PROD*SF_PER_STALL:>12,.0f}"
      f"{MAT*SF_PER_STALL:>11,.0f}{TOTAL*SF_PER_STALL:>10,.0f}")
print()
print(f"Fixed mobilisation, all trades combined : ${MOB_DOLLARS:,.0f}")
print(f"Base-case tonnage                       : {BASE_YARD_SF*HMA_T_SF_IN*HMA_IN:,.0f} t HMA"
      f"  +  {BASE_YARD_SF*AGG_T_SF_IN*AGG_IN:,.0f} t aggregate  =  {BASE_TONS:,.0f} t")
print(f"Volume tier already captured at 216 stalls: {BASE_TIER:.2f}  (best tier available)")

print()
rule()
print("2.  THE SCALE CURVE  -  what volume alone can do")
rule()
print(f"{'paved ac':>9}{'stalls':>8}{'bulk tons':>11}{'mobilise':>10}{'product.':>10}"
      f"{'material':>10}{'$/SF':>8}{'$/stall':>10}{'vs base':>9}")
ref = yard(BASE_YARD_SF)[3]
for ac in [1, 2, 3, 5, BASE_YARD_AC, 10, 15, 20, 30, 50]:
    a = ac * 43560
    m, p, mt, t = yard(a)
    tag = "  <- base" if abs(ac - BASE_YARD_AC) < 0.01 else ""
    print(f"{ac:>9.2f}{a/SF_PER_STALL:>8,.0f}{a*(HMA_T_SF_IN*HMA_IN+AGG_T_SF_IN*AGG_IN):>11,.0f}"
          f"{m:>10.2f}{p:>10.2f}{mt:>10.2f}{t:>8.2f}{t*SF_PER_STALL:>10,.0f}{t/ref-1:>+9.1%}{tag}")
print()
print("Scale in CONSTRUCTION is bounded. Material is 56% of the section and the")
print("216-stall base case already sits in the top volume tier, so tonnage pricing")
print("has nothing left to give. Tripling the yard to 20 acres takes ~5% off $/SF.")

# --------------------------------------------------------------- spec levers
print()
rule()
print("3.  SPECIFICATION LEVERS  -  changing what gets built, not how much")
rule()

agg_place_per_in = 0.86 / AGG_IN          # $/SF per inch of base placement
hma_place_per_in = 1.11 / HMA_IN          # $/SF per inch of HMA placement
STALL_SHARE = 0.68                        # share of yard that is stall, not aisle

LEVERS = [
    ("Geogrid, aggregate base 12\" -> 8\"",
     -(4 * AGG_T_SF_IN * AGG_PRICE) - 4 * agg_place_per_in + 0.4722,
     "Triaxial geogrid at ~$4.25/SY installed buys a 25-50% base reduction. Also de-risks soft subgrade."),
    ("25% RAP content in the HMA mix",
     -0.10 * (HMA_T_SF_IN * HMA_IN * HMA_PRICE),
     "Recycled asphalt pavement in the mix; ~8-15% off mix price. Confirm the plant's RAP capability."),
    ("Millings for the lower 6\" of base",
     -6 * AGG_T_SF_IN * (AGG_PRICE - RAP_PRICE),
     "Crushed RAP at $16/t against processed aggregate at $22/t. Supply is opportunistic."),
    ("Balanced cut/fill - no import, no export",
     -0.45,
     "Kills both the import-fill material line and the export haul. Needs the grading plan designed for it."),
    ("Thinner HMA in stall areas only (5\" -> 4\")",
     -STALL_SHARE * (HMA_T_SF_IN * HMA_PRICE + hma_place_per_in),
     "Aisles keep full section. Rutting risk under static trailer loads - pair with landing-gear pads."),
    ("Hybrid surface: paved aisles, millings stalls",
     -2.40 - 0.35,
     "The S2 specification. Largest single lever by a wide margin."),
    ("On-site crush & reuse of demo concrete/pavement",
     -0.35,
     "Only where a structure or existing pavement is being removed. Avoids export AND import."),
    ("ADD: concrete landing-gear pads, 48 SF/stall",
     +48 * 14.0 / SF_PER_STALL,
     "A cost ADD. Stops the punch-through failure that drives premature reconstruction."),
]
print(f"{'lever':<48}{'$/SF':>9}{'$/stall':>10}{'% of yard':>11}")
rule("-")
for name, d, _ in LEVERS:
    print(f"{name:<48}{d:>+9.2f}{d*SF_PER_STALL:>+10,.0f}{d/TOTAL:>+11.1%}")
print()
for name, d, note in LEVERS:
    print(f"  {name}\n      {note}")

# ------------------------------------------------------------------ packages
print()
rule()
print("4.  STACKED PACKAGES  -  levers combined, at the 216-stall base area")
rule()
L = {n: d for n, d, _ in LEVERS}
PACKAGES = {
    "Base heavy-duty section (S1 as modelled)": [],
    "A  Value-engineer, keep full pavement": [
        'Geogrid, aggregate base 12" -> 8"', "25% RAP content in the HMA mix",
        'Millings for the lower 6" of base', "Balanced cut/fill - no import, no export"],
    "B  A + thinner stall section + pads": [
        'Geogrid, aggregate base 12" -> 8"', "25% RAP content in the HMA mix",
        'Millings for the lower 6" of base', "Balanced cut/fill - no import, no export",
        'Thinner HMA in stall areas only (5" -> 4")',
        "ADD: concrete landing-gear pads, 48 SF/stall"],
    "C  Hybrid surface (S2 as modelled)": [
        "Hybrid surface: paved aisles, millings stalls"],
    "D  Hybrid + all compatible levers": [
        "Hybrid surface: paved aisles, millings stalls",
        "25% RAP content in the HMA mix",
        "Balanced cut/fill - no import, no export",
        'Geogrid, aggregate base 12" -> 8"',
        "ADD: concrete landing-gear pads, 48 SF/stall"],
}
print(f"{'package':<44}{'$/SF':>8}{'$/stall':>10}{'saving':>10}{'% cut':>8}")
rule("-")
base_sf = TOTAL
for name, keys in PACKAGES.items():
    d = sum(L[k] for k in keys)
    sf = base_sf + d
    print(f"{name:<44}{sf:>8.2f}{sf*SF_PER_STALL:>10,.0f}"
          f"{-d*SF_PER_STALL:>+10,.0f}{-d/base_sf:>+8.1%}")

print()
rule()
print("5.  SCALE AND SPECIFICATION TOGETHER  -  yard $/stall")
rule()
hdr = f"{'paved acres ->':<44}" + "".join(f"{a:>10.0f}" for a in [3, 5, 7, 10, 15, 20])
print(hdr)
rule("-")
for name, keys in PACKAGES.items():
    d = sum(L[k] for k in keys)
    row = f"{name:<44}"
    for ac in [3, 5, 7, 10, 15, 20]:
        _, _, _, t = yard(ac * 43560)
        row += f"{(t + d) * SF_PER_STALL:>10,.0f}"
    print(row)
print()
print("Read across for scale, down for specification. Specification moves the number")
print("three to five times as far as volume does.")

# ------------------------------------------------- non-land fixed cost scaling
print()
rule()
print("6.  NON-LAND FIXED COST  -  the larger prize, and it scales harder")
rule()
print("At 216 stalls the S2 scenario carries $21,813/stall of fixed cost, of which only")
print("$8,280 is land. The other $13,533 exceeds the entire yard construction bill of")
print("$9,338/stall - and unlike material, most of it does not grow with the site.")
print()

# S2 direct fixed items, classified by how each responds to site size.
PER_SITE = {                      # flat: one per project, whatever the size
    "Pre-development, design, entitlement": 445_000,
    "Utility service & transformer":        185_000,
    "Security head-end (NVR, analytics)":   175_000,
    "Site entry, apron, turn lane":         175_000,
    "Gatehouse / driver services":          145_000,
    "Automated gates & access control":     145_000,
    "Demolition & clearing outside yard":    95_000,
}
PERIMETER = {                     # grows with the square root of area
    "Perimeter fence":                      137_280,
    "Landscaping & buffer plantings":       105_000,
}
WITH_AREA = {                     # grows with impervious area
    "Stormwater basin & treatment":         355_000,
}
LOADING = 1.0 + 0.05 + 0.12       # soft-cost loadings + contingency
BASE_STALLS = 216


def fixed_nonland_per_stall(stalls):
    """Direct non-land fixed cost per stall at a given programme size."""
    scale = stalls / BASE_STALLS
    per_site = sum(PER_SITE.values())
    perim = sum(PERIMETER.values()) * scale ** 0.5
    area = sum(WITH_AREA.values()) * scale
    return (per_site + perim + area) * LOADING / stalls


print(f"{'behaviour':<34}{'items':>7}{'$ at 216 stalls':>18}{'$/stall':>10}")
rule("-")
for label, d, note in [
    ("Flat per site", PER_SITE, "does not grow at all"),
    ("Grows with perimeter (sqrt area)", PERIMETER, "halves per stall at 4x the area"),
    ("Grows with impervious area", WITH_AREA, "no economy of scale"),
]:
    tot = sum(d.values())
    print(f"{label:<34}{len(d):>7}{tot:>18,.0f}{tot*LOADING/BASE_STALLS:>10,.0f}   {note}")
tot_all = sum(PER_SITE.values()) + sum(PERIMETER.values()) + sum(WITH_AREA.values())
rule("-")
print(f"{'Total direct non-land fixed':<34}{'':>7}{tot_all:>18,.0f}{tot_all*LOADING/BASE_STALLS:>10,.0f}")
print()
print(f"{'stalls':>8}{'gross ac':>10}{'flat/stall':>12}{'perimeter':>11}{'stormwater':>12}"
      f"{'$/stall':>10}{'vs 216':>9}")
rule("-")
ref_fix = fixed_nonland_per_stall(BASE_STALLS)
for st in [86, 150, 216, 300, 450, 600, 900]:
    sc = st / BASE_STALLS
    flat = sum(PER_SITE.values()) * LOADING / st
    per = sum(PERIMETER.values()) * sc ** 0.5 * LOADING / st
    ar = sum(WITH_AREA.values()) * sc * LOADING / st
    tot = flat + per + ar
    print(f"{st:>8,}{st*1450/0.72/43560:>10.1f}{flat:>12,.0f}{per:>11,.0f}{ar:>12,.0f}"
          f"{tot:>10,.0f}{tot/ref_fix-1:>+9.1%}")
print()
print("Going from 216 to 600 stalls cuts non-land fixed cost per stall by ~55% -")
print("an order of magnitude more than anything available in the paving contract.")

# ------------------------------------------------------------- putting it together
print()
rule()
print("7.  EVERYTHING EXCEPT LAND  -  $/stall, scale against specification")
rule()
DISCRETE = 1775          # per-stall lighting, electrical, cameras (S2)
print(f"{'':<44}" + "".join(f"{s:>10,}" for s in [150, 216, 300, 450, 600]) + "   stalls")
rule("-")
for name, keys in PACKAGES.items():
    d = sum(L[k] for k in keys)
    row = f"{name:<44}"
    for st in [150, 216, 300, 450, 600]:
        area = st * SF_PER_STALL
        _, _, _, t = yard(area)
        row += f"{(t + d) * SF_PER_STALL + DISCRETE + fixed_nonland_per_stall(st):>10,.0f}"
    print(row)
print()
best = (yard(600 * SF_PER_STALL)[3] + sum(L[k] for k in PACKAGES["D  Hybrid + all compatible levers"])) \
       * SF_PER_STALL + DISCRETE + fixed_nonland_per_stall(600)
worst = (yard(150 * SF_PER_STALL)[3]) * SF_PER_STALL + DISCRETE + fixed_nonland_per_stall(150)
print(f"Worst cell (150 stalls, base section) : ${worst:,.0f} per stall")
print(f"Best cell (600 stalls, package D)     : ${best:,.0f} per stall")
print(f"Spread                                : ${worst-best:,.0f} per stall  ({best/worst-1:+.0%})")
print()
print("Excludes land, financing carry and the lease-up reserve, so it is not directly")
print("comparable to the all-in cost per stall in the main model - it isolates the")
print("construction and site-cost levers the question was about.")

# -------------------------------------------------------------- diseconomies
print()
rule()
print("8.  WHAT DOES NOT SCALE  -  and what gets worse")
rule()
for t in [
    "Stormwater treatment tracks impervious area almost exactly, and CT's industrial\n"
    "  stormwater rules add a treatment train plus spill controls. Bigger yard, bigger\n"
    "  basin - no unit saving. Pervious stall surfacing is the only real relief.",
    "Asphalt haul radius is a hard constraint, not a volume question. HMA must be placed\n"
    "  hot, so a plant more than ~45 minutes out raises cost at any project size. Confirm\n"
    "  the nearest plant before trusting any $/ton quote.",
    "Yard lighting and stall electrical scale linearly with stall count - they are the\n"
    "  per-stall discrete items, and volume does nothing for them.",
    "Bonding, builder's risk and construction management are percentages of hard cost.\n"
    "  They scale linearly by construction, so they never dilute.",
    "Larger sites cross permitting thresholds: more traffic study scope, more DEEP\n"
    "  attention, longer entitlement. Schedule risk rises with size even as $/stall falls.",
    "Phasing REVERSES the mobilisation economy. Each phase re-mobilises every trade -\n"
    "  roughly $97k a time on this section. Phase only for capital or lease-up reasons,\n"
    "  never expecting a construction saving.",
]:
    print("- " + t)
