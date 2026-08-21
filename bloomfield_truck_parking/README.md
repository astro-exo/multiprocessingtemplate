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
