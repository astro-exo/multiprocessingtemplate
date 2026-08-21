# Bloomfield Truck Parking — Analysis Handoff

**Status:** feasibility analysis, self-audited, incomplete by design.
**Purpose of this document:** hand a downstream project everything needed to challenge this
work further, without re-inheriting its weak numbers as facts.
**Bottom line:** the deal as scoped does not work; the reason it does not work is solid; the
recommended fix (buy scale) rests on an assumption that this analysis has since shown to be
probably wrong.

---

## 0. How to use this

Read §1 before using any number. Then:

- **To extend the model** → §2 gives the reduced form. Do not start from the 12-tab workbook;
  start from the identity, which reproduces it exactly.
- **To attack the conclusions** → §6 is the ranked attack surface, and §7 is the list of things
  never modelled at all. §7 is where the largest errors almost certainly live.
- **To reuse numbers** → §3 grades every parameter. Anything graded **F** must be re-derived or
  discarded; do not propagate it.
- **To avoid repeating work** → §4 lists what was already tried and rejected, with reasons.

A machine-readable version of the parameter register and challenge list is in `handoff.json`.

---

## 1. Provenance warning — read before using any number

This analysis was produced without access to primary local market data. That is not a caveat
appended to the end; it is the central fact about its reliability.

| Category | Count | Trust |
|---|---|---|
| **A** — primary source (statute, published rate, meeting minutes) | 2 | Use directly |
| **B** — published secondary source or market report | 3 | Use with attribution |
| **C** — derivable arithmetic, checkable end to end | 3 | Verify the derivation, then use |
| **D** — judgement, defensible but unverified | 7 | Treat as a prior, not a value |
| **F** — invented for the model, no basis | 6 | **Do not propagate** |

The highest-leverage input in the entire model — blended revenue per stall-month, DSCR
elasticity **1.67** — is grade **F**. No verifiable Hartford-area rate for a secured 53 ft
tractor-trailer stall was found. The figure used ($309) is an inference from a national
$150–500 band.

**Everything quantitative downstream of that number inherits its grade.** The DSCR, the
yield on cost, the cost-per-stall thresholds, the site-size recommendation — all of it.

---

## 2. The reduced model

The 12-tab, 1,419-formula workbook collapses **exactly** to one identity. Verified against the
workbook to floating-point precision (max error 2×10⁻¹⁶ across all three scenarios):

```
DSCR  =  [ N(R − c)·12 − F ]  /  [ LTC · k · (N·v + Φ) ]

  N    stalls  =  A · 43,560 · y / s
  R    blended revenue per stall-month
  c    variable operating cost per stall-month
  F    fixed annual operating cost
  v    variable capex per stall
  Φ    fixed capex — land, entitlement, infrastructure, financing, reserves
  k    annual mortgage constant
  LTC  loan to cost
  D    DSCR test level (1.25 conventional)
```

### Three tests, in order

**Test 0 — sign of leverage.** Compare yield on cost to the interest rate. Requires no DSCR
convention, no LTC, no cap rate.

```
YoC = NOI / Cost ;  if YoC < interest rate, leverage is negative
```

**Test 1 — is a marginal unit self-financing?**

```
m = (R − c)·12 − D·LTC·k·v      if m ≤ 0, no scale ever works. Stop.
```

**Test 2 — is the programme big enough for its fixed burden?**

```
B = F + D·LTC·k·Φ               N* = B / m
```

**Ceiling.** Best achievable at infinite scale: `(R − c)·12 / (LTC·k·v)`.

**Inversion.** The required revenue at any programme size:

```
R* = c + [ F + D·LTC·k·(N·v + Φ) ] / 12N
```

### Current parameter values

| | S1 full asphalt | S2 value-engineered | S3 retrofit |
|---|---|---|---|
| N | 216 | 216 | 187 |
| R ($/stall/mo) | 353 | 309 | 322 |
| c ($/stall/mo) | 99.16 | 95.20 | 95.44 |
| F ($/yr) | 406,635 | 225,844 | 229,327 |
| v ($/stall) | 19,123 | 13,069 | 6,829 |
| Φ ($) | 5,218,590 | 4,711,612 | 5,466,396 |
| k | 0.086738 | 0.086738 | 0.086738 |
| **DSCR** | **0.475** | **0.774** | **0.731** |
| m ($/stall/yr) | 1,694 | 1,647 | 2,232 |
| N* needed | 457 | 339 | 275 |
| DSCR ceiling | 2.82× | 3.48× | 7.05× |

---

## 3. Parameter register

Ranked by |elasticity of DSCR|, computed by central difference at ±5%. **An input below 0.1
cannot change the conclusion regardless of how wrong it is.**

| Input | Value | Grade | \|e\| | Provenance |
|---|---|---|---|---|
| Blended revenue $/stall/mo | $309 | **F** | 1.67 | Inferred from a national $150–500 band. No local comp exists. |
| Stabilized occupancy | 88% | D | 1.67 | Contradicts own source (70% typical stabilization target). |
| Paved SF per stall | 1,450 | C | 1.59 | 12′×75′ stall + half a 75′ back-in aisle + 100 SF cross-lanes. Checkable. |
| Net yard efficiency | 72% | D | 1.00 | No site plan behind it. Parcel-specific in reality. |
| Loan to cost | 65% | B | 1.00 | Market standard for the asset class. |
| Monthly / transient mix | 80/20 | D | 0.87 | Judgement about an off-highway location. Untested. |
| Permanent loan rate | 7.25% | B | 0.65 | 2026 quotes start ~5.74%; niche collateral prices wider. |
| Transient rate & utilisation | $24 / 58% | D | 0.63 | Same evidence gap as the monthly rate. |
| Gross site acres | 10.0 | C | 0.61 | A programme choice, not a measurement. |
| Land $/acre | $175,000 | D | 0.38 | No usable comp found. |
| Bloomfield mill rate | 34.40 | **A** | 0.31 | Adopted 2025 Grand List rate, Town of Bloomfield. |
| CT assessment ratio | 70% | **A** | 0.31 | Connecticut statute. |
| Snow & ice $/paved acre | $8,200 | **F** | 0.18 | Never sourced. |
| Assessor factor on improvements | 45% | **F** | 0.17 | Invented. |
| Insurance / R&M / utilities / reserves | various | D | <0.16 | Plausible operating estimates. Individually immaterial. |
| Contingency & soft loadings | 12% / 5% | C | <0.09 | Standard practice. Immaterial to the test. |
| Construction cost-behaviour splits | $0.31/$3.88/$5.26 per SF | **F** | <0.10 | Assigned line by line from judgement. |
| Production learning exponent | 0.070 | **F** | <0.05 | Invented; implied calibration that never happened. |
| Material volume tier table | 5 steps | **F** | <0.05 | Source supported only "5–15% for bulk orders". |
| Exit cap rate | 7.75% | B | **0.00** | Zero elasticity on the financing test. |
| Revenue & opex growth | 3.0% | D | **0.00** | Zero elasticity on the year-one test. |

**Structural note.** Several inputs share an elasticity exactly because they enter
multiplicatively. Rate and occupancy both scale revenue; acres, yield and SF-per-stall all scale
stall count. There are **three independent levers**, not six: revenue per stall, stall count,
and financing terms.

---

## 4. Discard list — do not resurrect

| Item | Why it was discarded |
|---|---|
| Neighbor.com Hartford rates as a rate "floor" | Those listings are **22–35 ft spaces**. A 53 ft secured stall is a different product with different demand and competition. Citing it manufactured an illusion of local grounding. |
| Construction cost-behaviour decomposition | Mobilisation/production/material splits were assigned from judgement then reported to the cent. The headline "material is 56% of the section" rests entirely on invented numbers. Retained only as a labelled illustration. |
| Production learning curve, material tier table | Invented; presented as though calibrated. |
| Snow $8,200/acre, assessor factor 45% | Never sourced. |
| Exit cap rate and "development profit" | Two faults: zero elasticity on the financing test, and conceptually wrong — a per-stall retail parking operation is an **operating business**, not a leased asset, so capitalising its NOI against leased-IOS comps overstates value. |
| Ten-year pro forma with 3% growth | Zero elasticity on the year-one test that decides the deal. |
| "~1,500 live formulas" | Actual count is 1,419. |

---

## 5. Findings, with confidence

| # | Finding | Confidence | Depends on |
|---|---|---|---|
| 1 | **Negative leverage.** Yield on cost (2.68–4.36%) is below the debt rate (7.25%) in all three scenarios. Debt reduces the equity return. | **High** — holds for any plausible rate; needs no DSCR convention | R, and only weakly |
| 2 | **Fixed costs dominate.** 56–81% of capital cost is site-level and does not scale with stall count. | **High** — arithmetic from the cost build | Cost structure only |
| 3 | **Cost:NOI must clear ~14.2×.** At 65% LTC and an 8.674% constant, a 1.25× DSCR needs a 7.05% yield on cost. Scenarios run 22.9–37.3×. | **High** — pure arithmetic | Financing terms |
| 4 | **A marginal stall is self-financing** (m = +$1,647/yr for S2), so scale is not structurally blocked. | Medium | R, c, v |
| 5 | **The retrofit has the highest ceiling** — 7.05× vs 3.48× — because variable capex per stall is a third of the alternatives. | Medium | v |
| 6 | P(clearing 1.25× at 10 acres) = **7.2%**; 50% crossing near **18 acres**. | Low–Medium — priors are mine | All six parameters |
| 7 | **Scale fixes the deal.** | **LOW — see §6.1. Probably wrong as stated.** | An unmeasured demand elasticity |

---

## 6. Challenge register — ranked attack surface

Ordered by (leverage × ignorance). **C-1 is the most important item in this document.**

### C-1 — Occupancy is treated as independent of programme size. It is not.

- **Claim under attack:** "Scale fixes the deal — build 14–18+ acres."
- **The defect:** the model holds stabilized occupancy constant at 88% while stall count
  triples. Occupancy is an *output* of demand vs. supply, not an input independent of size.
- **Magnitude:** Connecticut has ~1,238 truck parking spaces statewide (~420 public, ~818
  private). The financing threshold of **339 stalls is 27% of statewide supply and 41% of
  private supply**. An 18-acre programme (390 stalls) is 48% of private supply. A 30-acre
  programme is 79%.
- **Direction of error:** optimistic. Scale adds stalls faster than it adds capturable demand.
- **Illustrative sensitivity (not calibrated):** a 10% occupancy decay per doubling pushes the
  1.25× crossing past 30 acres. A 20% decay removes the crossing entirely — scale stops being a
  solution at all.
- **What would resolve it:** a catchment demand estimate — truck volumes on I-91/I-84 within
  30 minutes, fleet domiciles in the Hartford MSA, overnight parking deficit from the CTDOT
  study localised to this sub-market.
- **If it fails:** the central recommendation of this analysis is void.

### C-2 — Revenue per stall has no local evidence

- **Claim:** $309 blended, $315 monthly reserved.
- **Elasticity:** 1.67 — the highest in the model.
- **Resolve by:** rate survey of secured 53 ft stalls within 15 miles — operators, brokers, fleet
  managers. Estimated cost: one week.
- **Threshold to test against:** $387/stall/month at 10 acres, $306 at 16 acres.
- **If below ~$300:** no site size in Bloomfield rescues it; the search should move markets.

### C-3 — Only one business model was examined

- **Claim implicit throughout:** this is a per-stall retail parking operation.
- **Never compared:** a bulk NNN lease of the whole yard to a single fleet or 3PL tenant. That
  eliminates the per-stall operating overhead (~$182/stall/month), the lease-up risk, and the
  management intensity — at a lower rent per acre. Hartford-metro bulk yard leases were noted at
  roughly $35,000–55,000/acre/yr but never modelled.
- **Why it matters:** at 10 acres, bulk lease revenue of ~$45k/acre = $450k/yr against modelled
  EGI of $801k — but with an opex ratio nearer 15% than 59%. The NOI comparison is not obvious
  and may favour the simpler structure.

### C-4 — Trailer-only storage was never modelled

- Drop-lot trailer storage uses ~55 ft stalls instead of 75 ft (roughly 25–30% more stalls per
  acre), needs no driver amenities, and carries lower rates. Different point on the same
  frontier; never evaluated.

### C-5 — Will a lender finance this collateral at all?

- The analysis assumes financeability is a *ratio* question. For single-purpose, operating-
  business-like collateral it may be **binary**. If no lender takes it, DSCR is moot and the
  question becomes all-equity return.

### C-6 — Stall geometry assumes uniform double-loaded rows

- The 1,450 SF/stall figure allocates half a drive aisle to every stall. Real layouts have
  perimeter rows, turning bulbs, and often pull-through stalls (far less dense, premium rate).
  Grade C — the arithmetic is checkable, the layout assumption is not verified against a site plan.

### C-7 — Land basis is unsupported

- $175,000/acre with no usable comp. The one Bloomfield transaction located was improved
  property with a building. Elasticity is only 0.38 and no land price alone rescues the deal, so
  this is lower priority than it looks — but it is still a fabricated anchor.

### C-8 — Entitlement risk is binary and unpriced

- Bloomfield TPZ has treated outdoor storage as not permitted as a principal use (source:
  meeting minutes, grade A). A text amendment or variance is likely required. The model carries
  $85,000 of legal cost and a 14-month schedule; it does **not** carry a probability of refusal.
  A 40% chance of never being approved changes the expected value more than most of §3.

---

## 7. Unexamined territory — never modelled at all

Listed because absence is invisible in a model and this is where large errors hide.

1. **Demand.** No catchment analysis, no competitive supply inventory, no seasonality. (See C-1.)
2. **Competitive response.** CTDOT is adding ~180 free public spaces by ~2030. Private entrants
   are not modelled either.
3. **Lease-up duration as a function of size.** A 6-month reserve is assumed regardless of
   programme. Sourced guidance says stabilization can take ~36 months.
4. **Downside floor.** If truck parking fails, the land retains alternative industrial value.
   Never valued — so the analysis overstates downside.
5. **Tax abatement / incentives.** CT municipalities offer industrial development incentives.
   Never investigated.
6. **Interest rate path and refinance risk.** A single fixed 7.25% throughout.
7. **Cargo theft and liability tail.** Garagekeepers coverage is named; exposure is not
   stress-tested. This is a material and growing risk at truck yards.
8. **Phasing option value.** Noted that phasing loses mobilisation economies; never valued as an
   option under uncertainty.
9. **Operator comparables.** No actual operator P&L was obtained. The entire opex stack is
   constructed, not observed.
10. **Environmental.** Carried as a $95,000 allowance on the retrofit. CT's Release-Based
    Remediation program exposure is not bounded.

---

## 8. Known defects in this analysis

Stated plainly so they are not rediscovered as findings.

1. **Occupancy independence** (C-1) — the most serious. Invalidates finding 7.
2. **Six parameters graded F** were used in a model presented with cent-level precision.
3. **Cost-per-stall was chosen as the denominator** without testing whether $/acre — the market
   convention for IOS — would have framed the problem better. It would have made the bulk-lease
   alternative (C-3) visible much earlier.
4. **A cap-rate valuation was applied to an operating business.** Wrong instrument.
5. **Point estimates were reported before distributions.** The distributional answer (7.2%)
   should have been the headline from the start.
6. **No primary local source was obtained for anything except the mill rate, the assessment
   ratio and the zoning posture.** Three grade-A facts in a document of this size is thin.

---

## 9. Reproduction

```
bloomfield_truck_parking/
├── Bloomfield_Truck_Parking_Model.xlsx   12 tabs, 1,419 live formulas, fullCalcOnLoad
├── build_model.py         generates the workbook; every input lives here
├── verify.py              independent pure-Python replication of the workbook
├── verify_workbook.py     evaluates all formulas, diffs vs verify.py, exits non-zero on error
├── framework.py           ★ the identity, its validation, the three tests, the inversion
├── audit_elasticity.py    ranks every input by DSCR elasticity
├── audit_evidence.py      evidence grades + Monte Carlo over the six identity parameters
├── audit_demand.py        the demand-side sanity check (C-1)
├── construction_scale.py  cost-behaviour model — largely grade F, immaterial to DSCR
├── deal_box.py            lever sweeps
├── report.html            long-form feasibility report
├── brief.html             two-page visual brief  (+ .pdf)
├── audit.html             audit and method revision
└── HANDOFF.md             this document  (+ handoff.json)
```

```bash
python3 build_model.py        # regenerate the workbook
python3 verify_workbook.py    # 2,947 cells, 0 formula errors, 69 cells matched
python3 framework.py          # identity validation + the three tests
python3 audit_elasticity.py   # leverage ranking
python3 audit_evidence.py     # grades + Monte Carlo
python3 audit_demand.py       # the demand sanity check
```

**Note on tooling:** LibreOffice is non-functional in the environment this was built in (it fails
on a four-formula test workbook), so the xlsx skill's `recalc.py` could not bake cached values.
The workbook is flagged `fullCalcOnLoad` and `verify_workbook.py` substitutes for recalculation
using the pure-Python `formulas` engine.

---

## 10. Suggested next work, ordered

1. **Rate survey** (C-2). One week. Falsifies or confirms the dominant input. Test against
   $306–387/stall/month.
2. **Catchment demand estimate** (C-1). Determines whether the scale recommendation is valid at
   all. Without this, finding 7 should not be repeated.
3. **Model the bulk-lease alternative** (C-3). May dominate the retail structure and is far
   simpler to underwrite.
4. **Zoning pre-application meeting** (C-8). Converts a binary risk into a known one. Cheap.
5. **Obtain one operator P&L** (§7.9). Replaces a constructed opex stack with an observed one.
6. Only then: revisit site selection and the retrofit-at-scale structure (finding 5).

**Do not** spend further effort on construction cost decomposition, contingency calibration,
cap-rate selection, or the multi-year pro forma. All are demonstrably immaterial to the outcome.
