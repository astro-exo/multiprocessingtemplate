# Bloomfield, CT — Truck Parking Development

Capex (fixed and variable) → cost per stall → NOI → DSCR.

## What's here

| File | What it is |
|---|---|
| `Bloomfield_Truck_Parking_Model.xlsx` | The underwriting model. 11 tabs, ~1,200 live formulas, three scenarios side by side. Change anything on `Assumptions` and the whole workbook repoints. |
| `build_model.py` | Generates the workbook. Every input lives here, so the model is reproducible and diffable. |
| `verify.py` | Independent pure-Python replication of the same math. Used to cross-check the spreadsheet and to source every number quoted below. |
| `deal_box.py` | Lever sweeps: rate × land price, density, site scale, and the bracketed viable case. |
| `verify_workbook.py` | Evaluates every formula in the workbook and diffs the Summary tab against `verify.py`. Exits non-zero on any Excel error or mismatch. |
| `construction_scale.py` | Economies of scale in yard construction: cost-behaviour decomposition, the scale curve, specification levers and non-land fixed-cost scaling. |

Rebuild with `python3 build_model.py`, then check it with `python3 verify_workbook.py`.

**On recalculation.** The workbook ships with formulas but no cached values, and is
flagged `fullCalcOnLoad`, so Excel, LibreOffice or Sheets computes every cell the moment
it opens. Values could not be baked in here because LibreOffice is non-functional in this
container — it fails to recalculate even a four-formula test workbook — so the usual
`recalc.py` route was unavailable. `verify_workbook.py` substitutes for it, evaluating all
2,424 formula cells with the pure-Python `formulas` engine (`pip install formulas`). Latest
run: **2,424 cells evaluated, zero formula errors, 69 Summary cells matched against the
independent Python model with zero mismatches.**

## Scenarios

| | S1 | S2 | S3 |
|---|---|---|---|
| | Greenfield, full-depth asphalt, staffed | Greenfield, value-engineered, unmanned | Retrofit of an existing paved yard |
| Site | 10.0 ac raw industrial @ $175k/ac | 10.0 ac raw industrial @ $175k/ac | 8.0 ac improved yard @ $385k/ac |
| Surface | 5" bituminous over 12" base, $9.45/SF | Paved aisles + compacted millings stalls, $6.44/SF | Mill & 2" overlay + patching, $2.49/SF |
| Stalls | 216 | 216 | 187 |

## Headline result

| | S1 | S2 | S3 |
|---|---|---|---|
| Total project cost | $9,349,120 | $7,534,492 | $6,743,422 |
| **Fixed cost per stall** | **$24,160** | **$21,813** | **$29,232** |
| **Variable cost per stall** | **$19,123** | **$13,069** | **$6,829** |
| **All-in cost per stall** | **$43,283** | **$34,882** | **$36,061** |
| Fixed share of capital cost | 55.8% | 62.5% | 81.1% |
| Effective gross income | $914,019 | $801,405 | $721,563 |
| Operating expenses | $663,646 | $472,611 | $443,492 |
| Opex ratio | 72.6% | 59.0% | 61.5% |
| **NOI** | **$250,373** | **$328,793** | **$278,071** |
| NOI per stall | $1,159 | $1,522 | $1,487 |
| Yield on cost | 2.68% | 4.36% | 4.12% |
| **DSCR at 65% LTC** | **0.48x** | **0.77x** | **0.73x** |
| Debt yield | 4.1% | 6.7% | 6.3% |

**None of the three clears a 1.25x DSCR.** They are not close: S2, the best of them,
covers 0.77x. That is the finding, not a modeling artifact — it survives every
reasonable flex of the individual inputs.

## Why, in one line

A 1.25x DSCR at 65% LTC and an 8.67% mortgage constant needs a **7.05% yield on cost**,
which means **all-in cost per stall must be no more than about 14.2x NOI per stall.**

| | cost/stall | NOI/stall | ratio | needs |
|---|---|---|---|---|
| S1 | $43,283 | $1,159 | 37.3x | ≤ 14.2x |
| S2 | $34,882 | $1,522 | 22.9x | ≤ 14.2x |
| S3 | $36,061 | $1,487 | 24.3x | ≤ 14.2x |

Connecticut land, Connecticut heavy-duty paving, a 34.40 mill rate on a 70%
assessment ratio, and Hartford-metro parking rates of roughly $310–350 per stall
per month simply do not meet in the middle at a 10-acre program.

## What would have to change

**Scale and density, not rate.** Fixed site costs are 56–81% of capital cost, so the
strongest lever is spreading them over more stalls. Holding rate at $350/month and
land at $120k/acre:

| Gross acres | Stalls | Fixed/stall | Variable/stall | All-in/stall | DSCR | YoC |
|---|---|---|---|---|---|---|
| 4 | 86 | $35,900 | $13,069 | $48,969 | 0.48x | 2.72% |
| 6 | 129 | $26,595 | $13,069 | $39,664 | 0.76x | 4.29% |
| 8 | 173 | $21,801 | $13,069 | $34,870 | 0.96x | 5.41% |
| 10 | 216 | $19,022 | $13,069 | $32,091 | 1.10x | 6.19% |
| **14** | **302** | **$15,822** | **$13,069** | **$28,891** | **1.29x** | **7.30%** |
| 20 | 432 | $13,372 | $13,069 | $26,441 | 1.48x | 8.33% |
| 30 | 648 | $11,464 | $13,069 | $24,532 | 1.65x | 9.29% |

Density does the same work from the other direction — at $350/month and $120k/acre
on a 10-acre site:

| SF/stall | Yard efficiency | Stalls | Cost/stall | NOI/stall | cost:NOI | DSCR | YoC |
|---|---|---|---|---|---|---|---|
| 1,650 | 66% | 174 | $37,971 | $1,799 | 21.1x | 0.84x | 4.74% |
| 1,450 | 72% | 216 | $32,091 | $1,987 | 16.2x | 1.10x | 6.19% |
| 1,300 | 76% | 254 | $28,238 | $2,116 | 13.3x | 1.33x | 7.49% |
| 1,150 | 80% | 303 | $24,599 | $2,236 | 11.0x | 1.61x | 9.09% |

Bracketing a 14-acre high-density program:

| Case | Stalls | $/stall | NOI | YoC | DSCR | cost:NOI |
|---|---|---|---|---|---|---|
| Conservative — $150k/ac, 1,450 SF/stall, $340/mo, 88% occ | 302 | $30,420 | $602,353 | 6.56% | 1.16x | 15.3x |
| **Moderate — $120k/ac, 1,300 SF/stall, $365/mo, 90% occ** | **347** | **$25,813** | **$844,548** | **9.43%** | **1.67x** | **10.6x** |
| Aggressive — $95k/ac, 1,300 SF/stall, $395/mo, 92% occ | 356 | $24,416 | $1,090,772 | 12.55% | 2.23x | 8.0x |

The moderate case is the honest target. Note that it clears on **four** simultaneous
conditions, none of which is free: a 14-acre site, land at $120k/acre (below the
$175k/acre used in the base case), 26 stalls per gross acre, and $365/month — above
today's Hartford-metro asking rates.

## The deal box

DSCR at 65% LTC for the value-engineered program, across rate and land basis:

| Rate $/mo | $0/ac | $40k/ac | $80k/ac | $120k/ac | $160k/ac | $200k/ac |
|---|---|---|---|---|---|---|
| $300 | 1.06x | 0.96x | 0.87x | 0.79x | 0.72x | 0.65x |
| $325 | 1.26x | 1.14x | 1.03x | 0.94x | 0.86x | 0.79x |
| $350 | 1.45x | 1.31x | 1.20x | 1.10x | 1.01x | 0.93x |
| $375 | 1.64x | 1.49x | 1.37x | 1.25x | 1.16x | 1.07x |
| $400 | 1.83x | 1.67x | 1.53x | 1.41x | 1.30x | 1.21x |
| $425 | 2.02x | 1.85x | 1.70x | 1.56x | 1.45x | 1.34x |
| $450 | 2.22x | 2.03x | 1.86x | 1.72x | 1.59x | 1.48x |

At the modeled $315/month, no land price clears — **not even free land.** The rate has
to move first; land basis alone cannot rescue the deal.

## Economies of scale in construction

The scenario tables price yard construction as a flat rate per SF, which hides where the
money goes. `construction_scale.py` and the `Construction_Scale` workbook tab split the
section into how each dollar behaves.

| Cost behaviour | $/SF | Share | $/stall |
|---|---|---|---|
| Mobilisation — fixed per contract | $0.31 | 3.3% | $450 |
| Production — labour & equipment hours | $3.88 | 41.1% | $5,626 |
| **Material — tonnage in the ground** | **$5.26** | **55.7%** | **$7,627** |
| Total | $9.45 | 100% | $13,702 |

**Volume is a weak lever.** Material is 56% of the section, and at 216 stalls the job already
buys 30,885 tons — the best volume tier available. Tripling the yard from 7 to 20 acres takes
only **4.9%** off construction cost per stall.

| Paved acres | Stalls | $/SF | $/stall | vs base |
|---|---|---|---|---|
| 3 | 90 | $10.23 | $14,840 | +8.3% |
| 7.19 | 216 | $9.45 | $13,702 | base |
| 15 | 451 | $9.09 | $13,186 | −3.8% |
| 30 | 901 | $8.85 | $12,825 | −6.4% |

**Specification is the strong lever.** Ranked by impact per stall:

| Lever | $/stall | % of yard |
|---|---|---|
| Hybrid surface — paved aisles, millings stalls | −$3,988 | −29.1% |
| Thinner HMA in stall areas only (5″→4″) | −$863 | −6.3% |
| Balanced cut/fill — no import, no export | −$652 | −4.8% |
| On-site crush & reuse of demo concrete | −$507 | −3.7% |
| 25% RAP content in the HMA mix | −$474 | −3.5% |
| Geogrid — aggregate base 12″→8″ | −$449 | −3.3% |
| Millings for the lower 6″ of base | −$294 | −2.1% |
| ADD: concrete landing-gear pads | +$672 | +4.9% |

Stacked into packages, at the 216-stall base area:

| Package | Yard $/SF | Yard $/stall | Cut |
|---|---|---|---|
| Base heavy-duty section (S1) | $9.45 | $13,702 | — |
| A — value-engineer, keep full pavement | $8.16 | $11,834 | 13.6% |
| B — A + thinner stall section + pads | $8.03 | $11,643 | 15.0% |
| C — hybrid surface (S2) | $6.70 | $9,715 | 29.1% |
| D — hybrid + all compatible levers | $6.08 | $8,812 | 35.7% |

**The larger prize is not the paving contract.** At 216 stalls S2 carries $21,813/stall of
fixed cost, only $8,280 of which is land. The remaining $13,533 exceeds the entire yard
construction bill of $9,338/stall — and most of it does not grow with the site:

| Behaviour | $ at 216 stalls | $/stall |
|---|---|---|
| Flat per site (entitlement, utilities, security, entry, gatehouse, gates, demo) | $1,365,000 | $7,394 |
| Grows with perimeter (√area) — fence, buffer landscaping | $242,280 | $1,312 |
| Grows with impervious area — stormwater | $355,000 | $1,923 |

Going from 216 to 600 stalls cuts non-land fixed cost per stall by **49.5%** — an order of
magnitude more than anything available in the paving contract.

Everything except land, $/stall:

| Package | 150 | 216 | 300 | 450 | 600 |
|---|---|---|---|---|---|
| Base section | $29,965 | $26,107 | $23,584 | $21,343 | $20,174 |
| C — hybrid (S2) | $25,978 | $22,119 | $19,596 | $17,356 | $16,186 |
| D — hybrid + all levers | $25,075 | $21,216 | $18,693 | $16,453 | $15,283 |

Worst to best is a 49% spread — roughly two-thirds programme size, one-third specification.

**What does not scale:** stormwater tracks impervious area exactly; asphalt haul radius is a
hard constraint (HMA must be placed hot, so a plant beyond ~45 minutes raises cost at any
size); lighting and stall electrical scale linearly with stall count; bonding, builder's risk
and CM are percentages of hard cost. Phasing *reverses* the mobilisation economy — each phase
re-mobilises every trade, roughly $97,000 a time.

## Risks that sit outside the model

1. **Entitlement is the gating item.** Bloomfield's Town Plan & Zoning Commission has
   treated outdoor storage as a use that is *not* permitted as a principal use —
   approved as an accessory use by special permit, with a ZBA variance otherwise
   required. A standalone commercial truck-parking yard likely needs a zoning text
   amendment or a variance, not just site-plan approval. Budget 12–18 months and treat
   the land contract as option-and-entitle, never a hard close.
2. **Property taxes.** Modeled on an assessor factor applied to cost basis. A CT
   assessor may instead use the income approach. Grid 4 on the `Sensitivity` tab spans
   the full range; it is the largest single soft spot in the model.
3. **Rate risk.** Hartford-metro marketplace data shows $81–106/month, but for 12–35 ft
   spaces, not secured 53 ft stalls. The $315–340/month used here is an inference from
   the national $150–500/month band for full tractor-trailer configurations, not an
   observed Bloomfield comp. **Verify with live asks before committing capital.**
4. **Public supply.** CTDOT is spending $31M to add 180+ spaces by roughly 2030, taking
   public capacity from ~420 to ~600 — at no charge to drivers. That is a real
   competitive ceiling on private pricing.
5. **Ledge and unsuitable soils** are the largest greenfield cost shock in this part of
   Connecticut and are covered only by the general contingency. Bore before you buy.
6. **Environmental.** CT's Release-Based Remediation program replaced the Transfer Act.
   The $95,000 allowance on S3 is an allowance, not a budget.

## Recommendation

Do not pursue a 10-acre greenfield build at $175k/acre. Two paths are worth real work:

- **Scale up.** Find 14+ acres at or below $120k/acre with a layout that yields 25+
  stalls per gross acre. That is the only configuration that clears a lender's test on
  its own economics.
- **Buy income, don't build it.** An existing paved yard bought at a basis that
  supports $21,000/stall of all-in cost (see `Debt_DSCR`, maximum supportable cost per
  stall) works where new construction does not — but note S3 as modeled fails because
  $385k/acre for improved land is too rich. The residual land value at a 1.25x DSCR is
  **$42,818/acre** for the retrofit case.

Either way, the first spend should be a rate survey of secured 53 ft stalls within
15 miles and a zoning pre-application meeting with Bloomfield TPZ — both cheap, and
both capable of killing the deal before any land is optioned.
