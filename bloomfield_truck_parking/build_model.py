"""
Bloomfield, CT Truck Parking - Development Underwriting Model
Builds a fully-formula-driven XLSX: fixed vs. variable capex -> cost per stall -> NOI -> DSCR.

Three scenarios modeled side by side in columns C / D / E:
  S1  Greenfield, full-depth heavy-duty asphalt, staffed (institutional spec)
  S2  Greenfield, value-engineered (paved aisles + compacted millings stalls, unmanned)
  S3  Retrofit / conversion of an existing paved industrial yard

Run:  python3 build_model.py   then  python3 <xlsx-skill>/scripts/recalc.py Bloomfield_Truck_Parking_Model.xlsx
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

F = "Arial"
BLUE = Font(name=F, size=10, color="0000FF")            # hardcoded input
BLACK = Font(name=F, size=10)                            # formula
GREEN = Font(name=F, size=10, color="008000")            # link to another sheet
BOLD = Font(name=F, size=10, bold=True)
BOLDB = Font(name=F, size=10, bold=True, color="0000FF")
TITLE = Font(name=F, size=14, bold=True, color="1F3864")
SUB = Font(name=F, size=10, italic=True, color="595959")
SECT = Font(name=F, size=10, bold=True, color="FFFFFF")
NOTE = Font(name=F, size=8, italic=True, color="7F7F7F")
HDR = Font(name=F, size=10, bold=True, color="FFFFFF")

FILL_SECT = PatternFill("solid", fgColor="1F3864")
FILL_HDR = PatternFill("solid", fgColor="2F5597")
FILL_KEY = PatternFill("solid", fgColor="FFFF00")
FILL_TOT = PatternFill("solid", fgColor="D9E2F3")
FILL_OUT = PatternFill("solid", fgColor="E2EFDA")
FILL_ALT = PatternFill("solid", fgColor="F2F2F2")

THIN = Side(style="thin", color="BFBFBF")
TOPB = Border(top=Side(style="thin", color="404040"))
BOXB = Border(top=THIN, bottom=THIN, left=THIN, right=THIN)

M0 = '$#,##0;($#,##0);"-"'
M2 = '$#,##0.00;($#,##0.00);"-"'
M0S = '$#,##0.0,,"M";($#,##0.0,,"M");"-"'
P1 = '0.0%;(0.0%);"-"'
P2 = '0.00%;(0.00%);"-"'
N0 = '#,##0;(#,##0);"-"'
N1 = '#,##0.0;(#,##0.0);"-"'
N2 = '#,##0.00;(#,##0.00);"-"'
X2 = '0.00"x"'
TXT = '@'

SC = ["C", "D", "E"]  # scenario columns

wb = Workbook()


def sheet(name, widths):
    ws = wb.create_sheet(name)
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.sheet_view.showGridLines = False
    return ws


def title(ws, t, sub=None):
    ws["A1"] = t
    ws["A1"].font = TITLE
    if sub:
        ws["A2"] = sub
        ws["A2"].font = SUB


def section(ws, row, text, last_col="G"):
    for col in range(1, ws.max_column + 1 if ws.max_column > 1 else 8):
        pass
    ws.cell(row=row, column=1, value=text).font = SECT
    for c in range(1, ord(last_col) - 64 + 1):
        ws.cell(row=row, column=c).fill = FILL_SECT
        ws.cell(row=row, column=c).font = SECT
    return row + 1


def hdrrow(ws, row, labels, last_col="G"):
    for i, l in enumerate(labels, start=1):
        c = ws.cell(row=row, column=i, value=l)
        c.font = HDR
        c.fill = FILL_HDR
        c.alignment = Alignment(horizontal="center" if i >= 3 else "left", wrap_text=True, vertical="center")
    ws.row_dimensions[row].height = 30
    return row + 1


def line(ws, row, label, unit, vals, fmt=M0, font=BLUE, note=None, bold=False, fill=None, indent=0):
    """vals: list of 3 (value or formula string) for scenario cols C/D/E."""
    c = ws.cell(row=row, column=1, value=label)
    c.font = BOLD if bold else Font(name=F, size=10)
    c.alignment = Alignment(indent=indent)
    u = ws.cell(row=row, column=2, value=unit)
    u.font = Font(name=F, size=9, color="595959")
    for i, v in enumerate(vals):
        cell = ws.cell(row=row, column=3 + i, value=v)
        cell.number_format = fmt
        cell.font = (BOLD if bold and font is BLACK else (BOLDB if bold and font is BLUE else font))
        if fill:
            cell.fill = fill
    if note:
        n = ws.cell(row=row, column=6, value=note)
        n.font = NOTE
        n.alignment = Alignment(wrap_text=True, vertical="top")
    if fill:
        ws.cell(row=row, column=1).fill = fill
        ws.cell(row=row, column=2).fill = fill
    return row + 1


# =====================================================================
# ASSUMPTIONS
# =====================================================================
A = sheet("Assumptions", [46, 17, 15, 15, 15, 62])
title(A, "Bloomfield, CT  |  Truck Parking Development  -  Assumptions",
      "Blue = hardcoded input / scenario lever.  Black = formula.  Yellow fill = key assumption to pressure-test.")
r = 4
r = hdrrow(A, r, ["Assumption", "Unit / Basis",
                  "S1  Greenfield Full Asphalt",
                  "S2  Greenfield Value-Eng.",
                  "S3  Retrofit Existing Yard", "Basis / Source"])
AR = {}

r = section(A, r, "1.  SITE & PROGRAM")
AR["acres"] = r
r = line(A, r, "Gross site area", "acres", [10.00, 10.00, 8.00], N2,
         note="Target: I-1 / PID industrial parcel, Bloomfield (Blue Hills Ave / Tobey Rd / Douglas St corridor), ~10 min to I-91 via Rts 218/291.")
AR["yield_pct"] = r
r = line(A, r, "Net yard efficiency (paveable / gross)", "% of gross", [0.72, 0.72, 0.78], P1,
         note="Deductions: front/side setbacks, landscape buffer, stormwater basin, wetland buffer, entry drive, auto parking. S3 higher - already improved.", fill=FILL_KEY)
AR["sf_stall"] = r
r = line(A, r, "Paved area per stall (incl. drive aisle)", "SF / stall", [1450, 1450, 1450], N0,
         note="12' x 75' stall = 900 SF + half of a 75' back-in aisle (450 SF) + 100 SF cross-lanes/tapers.", fill=FILL_KEY)
AR["stalls"] = r
r = line(A, r, "Truck stalls (53' tractor-trailer)", "stalls", 
         [f"=ROUNDDOWN(${c}${AR['acres']}*43560*${c}${AR['yield_pct']}/${c}${AR['sf_stall']},0)" for c in SC],
         N0, font=BLACK, bold=True, note="Implied density shown below; industry rule of thumb is 20-25 stalls per gross acre.")
AR["stalls_ac"] = r
r = line(A, r, "   Implied density", "stalls / gross acre",
         [f"=${c}${AR['stalls']}/${c}${AR['acres']}" for c in SC], N1, font=BLACK, indent=1)
AR["yard_sf"] = r
r = line(A, r, "Paved yard area", "SF",
         [f"=${c}${AR['stalls']}*${c}${AR['sf_stall']}" for c in SC], N0, font=BLACK)
AR["yard_ac"] = r
r = line(A, r, "Paved yard area", "acres",
         [f"=${c}${AR['yard_sf']}/43560" for c in SC], N2, font=BLACK)
AR["perim"] = r
r = line(A, r, "Perimeter fence length", "LF",
         [f"=ROUND(4*SQRT(${c}${AR['acres']}*43560),0)" for c in SC], N0, font=BLACK,
         note="Square-site approximation: 4 x SQRT(site SF). Irregular parcels run 10-25% longer.")

r = section(A, r, "2.  LAND / SITE ACQUISITION")
AR["land_ac"] = r
r = line(A, r, "Land price", "$ / acre", [175000, 175000, 385000], M0,
         note="Hartford-metro industrial land. Raw unentitled Bloomfield acreage $100-200k/ac; already-paved improved yard (S3) $325-450k/ac. CT industrial land avg ~$110k/ac (LandSearch).", fill=FILL_KEY)
AR["land_cost"] = r
r = line(A, r, "Land / acquisition cost", "$",
         [f"=${c}${AR['land_ac']}*${c}${AR['acres']}" for c in SC], M0, font=BLACK, bold=True)
AR["close_pct"] = r
r = line(A, r, "Acquisition closing costs", "% of price", [0.022, 0.022, 0.022], P1,
         note="CT conveyance tax, title, survey update, buyer legal, broker cost share.")

r = section(A, r, "3.  REVENUE")
AR["mix_month"] = r
r = line(A, r, "Stalls sold as monthly reserved", "% of stalls", [0.80, 0.80, 0.85], P1,
         note="Bloomfield is an off-highway 'home-base / drop-lot' market, not a highway truck stop. Monthly contracts dominate; balance sold transient.", fill=FILL_KEY)
AR["rate_month"] = r
r = line(A, r, "Monthly reserved rate", "$ / stall / month", [340, 315, 325], M0,
         note="Secured, lit, gated 53' stall. Northeast private lots run $150-500/mo; Hartford metro is the low end of that band. S1 premium for full pave + staffing.", fill=FILL_KEY)
AR["occ_month"] = r
r = line(A, r, "Stabilized occupancy - monthly stalls", "%", [0.90, 0.88, 0.90], P1,
         note="Tech-enabled operators report 92-98% at stabilization; 88-90% underwritten.")
AR["rate_night"] = r
r = line(A, r, "Transient rate", "$ / stall / night", [26, 24, 25], M0,
         note="Chain travel centers charge $12-25/night for reserved parking; secured off-highway lots price at the top of that band.")
AR["occ_night"] = r
r = line(A, r, "Stabilized utilization - transient stalls", "% of nights", [0.62, 0.58, 0.60], P1)
AR["anc_pct"] = r
r = line(A, r, "Ancillary revenue", "% of parking EGI", [0.050, 0.030, 0.035], P1,
         note="Reefer/APU plug-in fees, unpowered trailer storage, vendor space rent (mobile repair/tire), vending, wash bay referral. S1 has driver services building.")
AR["credit"] = r
r = line(A, r, "Credit loss / bad debt", "% of gross rent", [0.020, 0.020, 0.020], P1,
         note="Owner-operator credit is thin; prepay + card-on-file mitigates.")
AR["growth_rev"] = r
r = line(A, r, "Revenue growth", "% p.a.", [0.030, 0.030, 0.030], P1)

r = section(A, r, "4.  OPERATING EXPENSES  (Year-1 stabilized dollars)")
AR["mill"] = r
r = line(A, r, "Bloomfield mill rate", "mills", [34.40, 34.40, 34.40], N2,
         note="2025 Grand List adopted mill rate for real & personal property (Town of Bloomfield); year 2 of a 4-year revaluation phase-in. FY26 budget forum projected ~34.03.", fill=FILL_KEY)
AR["assess"] = r
r = line(A, r, "CT assessment ratio", "% of market value", [0.70, 0.70, 0.70], P1,
         note="Statutory: CT assesses at 70% of fair market value.")
AR["tv_land"] = r
r = line(A, r, "Assessor value - land", "% of land cost", [1.00, 1.00, 1.00], P1)
AR["tv_impr"] = r
r = line(A, r, "Assessor value - improvements", "% of improvement cost", [0.45, 0.45, 0.45], P1,
         note="LARGEST SINGLE MODELING UNCERTAINTY. Site improvements (paving, fence, lighting) are typically assessed well below cost, but a CT assessor can also value on the income approach. Sensitized on the Sensitivity tab.", fill=FILL_KEY)
AR["ins_stall"] = r
r = line(A, r, "Insurance - GL, property, garagekeepers", "$ / stall / yr", [230, 210, 220], M0,
         note="Garagekeepers legal liability is the coverage IOS truck-parking operators must carry beyond standard GL.")
AR["staff"] = r
r = line(A, r, "On-site staffing / attendant", "$ / yr", [165000, 0, 0], M0,
         note="S1 assumes 16 hr/day attended gate. S2/S3 are unmanned, tech-gated.")
AR["monitor"] = r
r = line(A, r, "Remote monitoring + roving patrol", "$ / yr", [42000, 52000, 50000], M0,
         note="Unmanned sites carry a heavier monitoring/patrol contract.")
AR["snow_ac"] = r
r = line(A, r, "Snow & ice management", "$ / paved acre / yr", [8800, 8200, 8800], M0,
         note="CT: ~18-22 plow events/season plus salting on a large yard. Real cost driver in this climate; gravel stalls (S2) plow slightly cheaper but rut.", fill=FILL_KEY)
AR["rm_stall"] = r
r = line(A, r, "Repairs, maintenance, sweeping, striping", "$ / stall / yr", [210, 235, 225], M0,
         note="S2 higher: millings surface needs annual regrading and dust control.")
AR["util_stall"] = r
r = line(A, r, "Utilities - lighting, water, sewer, telecom", "$ / stall / yr", [165, 145, 150], M0)
AR["trash_stall"] = r
r = line(A, r, "Trash, restrooms, janitorial", "$ / stall / yr", [95, 70, 75], M0)
AR["mgmt_pct"] = r
r = line(A, r, "Property management fee", "% of EGI", [0.040, 0.040, 0.040], P1)
AR["proc_pct"] = r
r = line(A, r, "Payment processing + reservation platform", "% of parking revenue", [0.020, 0.015, 0.015], P1,
         note="Monthly ACH ~1%; card/transient 2.9% + platform fee. Blended by revenue mix.")
AR["mktg_stall"] = r
r = line(A, r, "Marketing & leasing", "$ / stall / yr", [75, 85, 80], M0)
AR["prof"] = r
r = line(A, r, "Professional fees, legal, accounting, admin", "$ / yr", [22000, 18000, 18000], M0)
AR["reserve_stall"] = r
r = line(A, r, "Replacement reserve (pavement / equipment)", "$ / stall / yr", [165, 195, 185], M0,
         note="Deducted before NOI for DSCR purposes - lenders size to a reserve-burdened NOI.")
AR["growth_opex"] = r
r = line(A, r, "Opex growth", "% p.a.", [0.030, 0.030, 0.030], P1)

r = section(A, r, "5.  DEVELOPMENT SOFT-COST LOADINGS  (% of hard cost)")
AR["cm_pct"] = r
r = line(A, r, "Construction management / owner's rep", "% of hard", [0.030, 0.030, 0.030], P1)
AR["test_pct"] = r
r = line(A, r, "Testing, inspection, materials QA", "% of hard", [0.009, 0.009, 0.009], P1)
AR["brisk_pct"] = r
r = line(A, r, "Builder's risk & GL during construction", "% of hard", [0.011, 0.011, 0.011], P1)
AR["bond_pct"] = r
r = line(A, r, "Performance / payment bonds", "% of hard", [0.010, 0.000, 0.000], P1,
         note="S1 institutional spec only.")
AR["cont_pct"] = r
r = line(A, r, "Contingency", "% of hard + soft", [0.12, 0.12, 0.15], P1,
         note="S3 carries 15%: retrofit of an existing yard has subsurface and pavement-condition unknowns.", fill=FILL_KEY)

r = section(A, r, "6.  FINANCING")
AR["c_ltc"] = r
r = line(A, r, "Construction loan - loan to cost", "%", [0.60, 0.60, 0.60], P1)
AR["c_rate"] = r
r = line(A, r, "Construction loan - interest rate", "%", [0.0825, 0.0825, 0.0825], P1,
         note="SOFR + ~325 bps. 2026 industrial bridge quotes 7.5%-9.5%.")
AR["c_months"] = r
r = line(A, r, "Construction + lease-up carry period", "months", [16, 14, 10], N0)
AR["c_draw"] = r
r = line(A, r, "Average draw balance", "% of loan", [0.55, 0.55, 0.60], P1)
AR["c_orig"] = r
r = line(A, r, "Construction loan origination", "% of loan", [0.010, 0.010, 0.010], P1)
AR["c_costs"] = r
r = line(A, r, "Lender costs - appraisal, environmental, legal, title", "$", [65000, 65000, 60000], M0)
AR["p_ltc"] = r
r = line(A, r, "Permanent loan - max loan to cost", "%", [0.65, 0.65, 0.65], P1)
AR["p_ltv"] = r
r = line(A, r, "Permanent loan - max loan to value", "%", [0.65, 0.65, 0.65], P1)
AR["p_rate"] = r
r = line(A, r, "Permanent loan - interest rate", "%", [0.0725, 0.0725, 0.0725], P1,
         note="2026 commercial mortgage quotes start ~5.74%; IOS/truck parking is a niche collateral type and prices wider - 7.00-7.75% is realistic.", fill=FILL_KEY)
AR["p_amort"] = r
r = line(A, r, "Permanent loan - amortization", "years", [25, 25, 25], N0)
AR["p_dscr"] = r
r = line(A, r, "Minimum DSCR (sizing constraint)", "x", [1.25, 1.25, 1.25], X2,
         note="Standard lender floor is 1.25x; non-core collateral such as IOS/truck parking is frequently sized to 1.30-1.40x.", fill=FILL_KEY)
AR["exit_cap"] = r
r = line(A, r, "Stabilized / exit cap rate", "%", [0.0750, 0.0775, 0.0750], P1,
         note="2026 IOS: 6.00-6.75% institutional primary, 6.75-7.75% secondary. Hartford is secondary; truck parking prices wider than leased IOS.", fill=FILL_KEY)
AR["lu_months"] = r
r = line(A, r, "Lease-up opex reserve", "months of opex", [6, 6, 6], N0)
AR["lu_mktg"] = r
r = line(A, r, "Launch marketing / pre-leasing budget", "$", [85000, 85000, 75000], M0)

AR["_end"] = r

def aref(key, col):
    return f"Assumptions!${col}${AR[key]}"


# =====================================================================
# CAPEX - VARIABLE  (scales with stall count / paved yard area)
# =====================================================================
V = sheet("Capex_Variable", [46, 17, 15, 15, 15, 62])
title(V, "Variable Capex  -  costs that scale directly with stall count",
      "Unit costs are blue inputs. Everything here grows one-for-one with the size of the paved yard, so it sets the MARGINAL cost of a stall.")
r = 4
r = hdrrow(V, r, ["Cost item", "Unit", "S1  Greenfield Full Asphalt", "S2  Greenfield Value-Eng.",
                  "S3  Retrofit Existing Yard", "Basis / Source"])
VR = {}

r = section(V, r, "A.  YARD CONSTRUCTION  ($ per SF of paved yard)")
VR["clear"] = r
r = line(V, r, "Clearing, grubbing, erosion & sediment control", "$ / SF", [0.35, 0.35, 0.05], M2)
VR["earth"] = r
r = line(V, r, "Mass grading & earthwork (balanced site)", "$ / SF", [1.75, 1.55, 0.20], M2,
         note="Assumes a cut/fill-balanced site with no rock or unsuitable-soil export. Ledge or peat is the single biggest greenfield cost shock in this part of CT.")
VR["base"] = r
r = line(V, r, "Subgrade prep, geotextile, 12\" processed aggregate base", "$ / SF", [2.40, 2.05, 0.15], M2,
         note="Heavy-duty truck section: 10-12\"+ of aggregate base under the wearing course.")
VR["surf"] = r
r = line(V, r, "Surface course", "$ / SF", [4.35, 1.95, 1.85], M2,
         note="S1: 5\" bituminous (3\" binder + 2\" wearing). S2: paved aisles (~32% of area) blended with compacted millings/crushed stone stalls. S3: mill & 2\" overlay + full-depth patching. CT commercial asphalt $4-11/SF; heavy-duty truck sections $7-12/SF; CT construction costs run ~1.32x national.", fill=FILL_KEY)
VR["storm"] = r
r = line(V, r, "Storm conveyance within yard (catch basins, piping)", "$ / SF", [0.48, 0.44, 0.12], M2)
VR["stripe"] = r
r = line(V, r, "Striping, wheel stops, bollards", "$ / SF", [0.12, 0.10, 0.12], M2)
VR["sf_sub"] = r
r = line(V, r, "Subtotal - yard construction", "$ / SF",
         [f"=SUM({c}{VR['clear']}:{c}{VR['stripe']})" for c in SC], M2, font=BLACK, bold=True, fill=FILL_TOT)
VR["sf_tot"] = r
r = line(V, r, "Yard construction - total", "$",
         [f"={c}{VR['sf_sub']}*{aref('yard_sf', c)}" for c in SC], M0, font=BLACK, bold=True)

r += 1
r = section(V, r, "B.  PER-STALL DISCRETE ITEMS  ($ per stall)")
VR["light"] = r
r = line(V, r, "Yard lighting - LED on 30' poles", "$ / stall", [1225, 1225, 1225], M0,
         note="1 pole per 8 stalls at ~$9,800 installed (pole, fixture, base, conduit, wire).")
VR["elec"] = r
r = line(V, r, "Yard electrical distribution, conduit, panels", "$ / stall", [375, 340, 300], M0)
VR["reefer"] = r
r = line(V, r, "Reefer / APU power pedestals (30A)", "$ / stall", [620, 0, 310], M0,
         note="$3,100 per pedestal on 20% of stalls (S1) / 10% (S3). Reefer plug-ins are the highest-margin ancillary line but add electrical service load.")
VR["cam"] = r
r = line(V, r, "Camera coverage & analytics - incremental", "$ / stall", [185, 210, 210], M0,
         note="Head-end / NVR is a fixed cost; this is the marginal camera density per added row of stalls.")
VR["st_sub"] = r
r = line(V, r, "Subtotal - per-stall items", "$ / stall",
         [f"=SUM({c}{VR['light']}:{c}{VR['cam']})" for c in SC], M0, font=BLACK, bold=True, fill=FILL_TOT)
VR["st_tot"] = r
r = line(V, r, "Per-stall items - total", "$",
         [f"={c}{VR['st_sub']}*{aref('stalls', c)}" for c in SC], M0, font=BLACK, bold=True)

r += 1
VR["hard"] = r
r = line(V, r, "TOTAL VARIABLE HARD COST", "$",
         [f"={c}{VR['sf_tot']}+{c}{VR['st_tot']}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_OUT)
VR["per_stall"] = r
r = line(V, r, "   Variable hard cost per stall", "$ / stall",
         [f"={c}{VR['hard']}/{aref('stalls', c)}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_OUT, indent=1)
ws = V
ws.cell(row=r + 1, column=1, value="Note: soft-cost loadings and contingency are allocated pro-rata between fixed and variable on the Cost_Per_Stall tab; this page is hard cost only.").font = NOTE


# =====================================================================
# CAPEX - FIXED  (site-level threshold costs, independent of stall count)
# =====================================================================
X = sheet("Capex_Fixed", [46, 17, 15, 15, 15, 62])
title(X, "Fixed Capex  -  site-level threshold costs",
      "These are incurred to open the gate at all. They do NOT scale with stall count, which is why density and site size drive this deal.")
r = 4
r = hdrrow(X, r, ["Cost item", "Unit", "S1  Greenfield Full Asphalt", "S2  Greenfield Value-Eng.",
                  "S3  Retrofit Existing Yard", "Basis / Source"])
XR = {}

r = section(X, r, "A.  LAND / ACQUISITION")
XR["land"] = r
r = line(X, r, "Land / site purchase price", "$",
         [f"={aref('land_cost', c)}" for c in SC], M0, font=GREEN, bold=True)
XR["close"] = r
r = line(X, r, "Acquisition closing costs", "$",
         [f"={c}{XR['land']}*{aref('close_pct', c)}" for c in SC], M0, font=BLACK)
XR["land_sub"] = r
r = line(X, r, "Subtotal - acquisition", "$",
         [f"=SUM({c}{XR['land']}:{c}{XR['close']})" for c in SC], M0, font=BLACK, bold=True, fill=FILL_TOT)

r += 1
r = section(X, r, "B.  PRE-DEVELOPMENT, DESIGN & ENTITLEMENT")
XR["survey"] = r
r = line(X, r, "ALTA / topographic survey", "$", [14000, 14000, 12000], M0)
XR["geo"] = r
r = line(X, r, "Geotechnical investigation (borings, pavement design)", "$", [22000, 22000, 14000], M0)
XR["ph1"] = r
r = line(X, r, "Phase I ESA", "$", [4000, 4000, 4500], M0)
XR["ph2"] = r
r = line(X, r, "Phase II ESA / LEP remediation allowance", "$", [35000, 35000, 95000], M0,
         note="CT's Transfer Act has been replaced by the Release-Based Remediation program. A previously-industrial paved yard (S3) carries real recognized-environmental-condition risk - this is an allowance, not a budget.", fill=FILL_KEY)
XR["wet"] = r
r = line(X, r, "Wetlands delineation & IWWA permitting", "$", [18000, 18000, 6000], M0,
         note="Bloomfield Inland Wetlands & Watercourses Agency. Much of the town's remaining industrial acreage carries wetland or watercourse constraints.")
XR["traffic"] = r
r = line(X, r, "Traffic impact study", "$", [28000, 28000, 22000], M0,
         note="A 150-250 stall facility generates enough heavy-vehicle trips to trigger a full TIS and likely CT OSTA review.")
XR["civil"] = r
r = line(X, r, "Civil engineering & site design", "$", [195000, 175000, 85000], M0)
XR["arch"] = r
r = line(X, r, "Architectural - gatehouse / driver services", "$", [18000, 12000, 12000], M0)
XR["legal"] = r
r = line(X, r, "Land-use counsel & entitlement", "$", [85000, 85000, 55000], M0,
         note="ENTITLEMENT IS THE GATING RISK. Bloomfield TPZ has treated outdoor storage as a non-permitted principal use - approved only as an accessory use by special permit, with a ZBA variance otherwise required. A standalone commercial truck-parking yard likely needs a zoning text amendment or variance, not just site-plan approval.", fill=FILL_KEY)
XR["fees"] = r
r = line(X, r, "Municipal application & review fees", "$", [18000, 18000, 12000], M0)
XR["deep"] = r
r = line(X, r, "CT DEEP stormwater GP registration + SWPPP", "$", [22000, 22000, 10000], M0)
XR["drive"] = r
r = line(X, r, "Driveway / encroachment permits", "$", [12000, 12000, 4000], M0)
XR["dd_sub"] = r
r = line(X, r, "Subtotal - pre-development", "$",
         [f"=SUM({c}{XR['survey']}:{c}{XR['drive']})" for c in SC], M0, font=BLACK, bold=True, fill=FILL_TOT)

r += 1
r = section(X, r, "C.  SITE INFRASTRUCTURE  (hard cost, non-stall)")
XR["demo"] = r
r = line(X, r, "Demolition & clearing outside the yard", "$", [95000, 95000, 165000], M0,
         note="S3 assumes demolition of an obsolete building on the existing yard.")
XR["basin"] = r
r = line(X, r, "Stormwater basin, water-quality units, outlet control", "$", [385000, 355000, 120000], M0,
         note="Truck yards are a regulated industrial stormwater activity in CT - treatment train plus spill controls, not just detention.", fill=FILL_KEY)
XR["entry"] = r
r = line(X, r, "Site entry, apron, turn lane, sight-line work", "$", [195000, 175000, 110000], M0)
XR["fence"] = r
r = line(X, r, "Perimeter fence - 8' chain link, slats, barbed arm", "$",
         [f"={aref('perim', SC[i])}*{v}" for i, v in enumerate([58, 52, 52])], M0, font=BLACK,
         note="$52-58 per LF installed on the perimeter LF calculated on the Assumptions tab.")
XR["gates"] = r
r = line(X, r, "Automated gates, operators, LPR / RFID access control", "$", [155000, 145000, 145000], M0)
XR["sec"] = r
r = line(X, r, "Security head-end - NVR, analytics, network, lighting controls", "$", [145000, 175000, 165000], M0,
         note="Unmanned sites (S2/S3) invest more in technology to substitute for staff.")
XR["gate_bldg"] = r
r = line(X, r, "Gatehouse / driver services building + restrooms", "$", [265000, 145000, 155000], M0)
XR["util"] = r
r = line(X, r, "Utility service - electric & transformer, water, sewer/septic, fiber", "$", [210000, 185000, 95000], M0)
XR["land_sc"] = r
r = line(X, r, "Landscaping, buffer plantings, signage, ADA auto parking", "$", [135000, 105000, 65000], M0)
XR["infra_sub"] = r
r = line(X, r, "TOTAL FIXED HARD COST", "$",
         [f"=SUM({c}{XR['demo']}:{c}{XR['land_sc']})" for c in SC], M0, font=BLACK, bold=True, fill=FILL_OUT)


def vref(key, col):
    return f"Capex_Variable!${col}${VR[key]}"


def xref(key, col):
    return f"Capex_Fixed!${col}${XR[key]}"


# =====================================================================
# COST PER STALL  (consolidation: hard -> soft -> contingency -> all-in)
# =====================================================================
C = sheet("Cost_Per_Stall", [46, 17, 15, 15, 15, 62])
title(C, "All-In Development Cost  ->  Cost Per Stall",
      "Soft-cost loadings and contingency are allocated pro-rata between fixed and variable by share of hard cost.")
r = 4
r = hdrrow(C, r, ["", "Unit", "S1  Greenfield Full Asphalt", "S2  Greenfield Value-Eng.",
                  "S3  Retrofit Existing Yard", "Note"])
CR = {}

r = section(C, r, "A.  HARD COSTS")
CR["hf"] = r
r = line(C, r, "Fixed hard cost - site infrastructure", "$",
         [f"={xref('infra_sub', c)}" for c in SC], M0, font=GREEN)
CR["hv"] = r
r = line(C, r, "Variable hard cost - yard & stalls", "$",
         [f"={vref('hard', c)}" for c in SC], M0, font=GREEN)
CR["ht"] = r
r = line(C, r, "Total hard cost", "$",
         [f"={c}{CR['hf']}+{c}{CR['hv']}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_TOT)
CR["vshare"] = r
r = line(C, r, "   Variable share of hard cost", "%",
         [f"={c}{CR['hv']}/{c}{CR['ht']}" for c in SC], P1, font=BLACK, indent=1)

r += 1
r = section(C, r, "B.  SOFT-COST LOADINGS & CONTINGENCY")
CR["cm"] = r
r = line(C, r, "Construction management / owner's rep", "$",
         [f"={c}{CR['ht']}*{aref('cm_pct', c)}" for c in SC], M0, font=BLACK)
CR["test"] = r
r = line(C, r, "Testing, inspection, materials QA", "$",
         [f"={c}{CR['ht']}*{aref('test_pct', c)}" for c in SC], M0, font=BLACK)
CR["brisk"] = r
r = line(C, r, "Builder's risk & GL during construction", "$",
         [f"={c}{CR['ht']}*{aref('brisk_pct', c)}" for c in SC], M0, font=BLACK)
CR["bond"] = r
r = line(C, r, "Performance / payment bonds", "$",
         [f"={c}{CR['ht']}*{aref('bond_pct', c)}" for c in SC], M0, font=BLACK)
CR["soft"] = r
r = line(C, r, "Subtotal - soft-cost loadings", "$",
         [f"=SUM({c}{CR['cm']}:{c}{CR['bond']})" for c in SC], M0, font=BLACK, bold=True)
CR["cont"] = r
r = line(C, r, "Contingency", "$",
         [f"=({c}{CR['ht']}+{c}{CR['soft']})*{aref('cont_pct', c)}" for c in SC], M0, font=BLACK)
CR["constr"] = r
r = line(C, r, "TOTAL CONSTRUCTION COST", "$",
         [f"={c}{CR['ht']}+{c}{CR['soft']}+{c}{CR['cont']}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_TOT)

r += 1
r = section(C, r, "C.  LAND, PRE-DEVELOPMENT & FINANCING  (100% fixed)")
CR["land"] = r
r = line(C, r, "Land & acquisition costs", "$",
         [f"={xref('land_sub', c)}" for c in SC], M0, font=GREEN)
CR["dd"] = r
r = line(C, r, "Pre-development, design & entitlement", "$",
         [f"={xref('dd_sub', c)}" for c in SC], M0, font=GREEN)
CR["impr_basis"] = r
r = line(C, r, "Improvement cost basis (for tax assessment)", "$",
         [f"={c}{CR['constr']}+{c}{CR['dd']}" for c in SC], M0, font=BLACK, indent=1,
         note="Assessor's improvement basis = construction + pre-development. Land assessed separately.")
CR["preloan"] = r
r = line(C, r, "Project cost before financing", "$",
         [f"={c}{CR['constr']}+{c}{CR['land']}+{c}{CR['dd']}" for c in SC], M0, font=BLACK, bold=True)
CR["cloan"] = r
r = line(C, r, "Construction loan amount", "$",
         [f"={c}{CR['preloan']}*{aref('c_ltc', c)}" for c in SC], M0, font=BLACK)
CR["corig"] = r
r = line(C, r, "Construction loan origination fee", "$",
         [f"={c}{CR['cloan']}*{aref('c_orig', c)}" for c in SC], M0, font=BLACK)
CR["cint"] = r
r = line(C, r, "Construction period interest", "$",
         [f"={c}{CR['cloan']}*{aref('c_rate', c)}*{aref('c_draw', c)}*{aref('c_months', c)}/12" for c in SC],
         M0, font=BLACK)
CR["clend"] = r
r = line(C, r, "Lender costs - appraisal, environmental, legal, title", "$",
         [f"={aref('c_costs', c)}" for c in SC], M0, font=GREEN)
CR["ctax"] = r
r = line(C, r, "Real estate taxes during construction", "$",
         [f"={xref('land', c)}*{aref('assess', c)}*{aref('mill', c)}/1000*{aref('c_months', c)}/12" for c in SC],
         M0, font=BLACK)
CR["fin"] = r
r = line(C, r, "Subtotal - financing & carry", "$",
         [f"=SUM({c}{CR['corig']}:{c}{CR['ctax']})" for c in SC], M0, font=BLACK, bold=True)

CR["cap_basis"] = r
r = line(C, r, "Capitalized cost before lease-up reserve", "$",
         [f"={c}{CR['preloan']}+{c}{CR['fin']}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_TOT)

r += 1
r = section(C, r, "D.  LEASE-UP RESERVE")
CR["lu_opex"] = r      # filled after Revenue_NOI is built
r = line(C, r, "Operating reserve during lease-up", "$", [None, None, None], M0, font=BLACK,
         note="Months of stabilized opex carried until the yard fills. Truck-parking assets typically need up to 36 months to reach stabilized occupancy.")
CR["lu_mktg"] = r
r = line(C, r, "Launch marketing / pre-leasing", "$",
         [f"={aref('lu_mktg', c)}" for c in SC], M0, font=GREEN)
CR["lu_sub"] = r
r = line(C, r, "Subtotal - lease-up reserve", "$",
         [f"=SUM({c}{CR['lu_opex']}:{c}{CR['lu_mktg']})" for c in SC], M0, font=BLACK, bold=True)

r += 1
CR["total"] = r
r = line(C, r, "TOTAL PROJECT COST", "$",
         [f"={c}{CR['cap_basis']}+{c}{CR['lu_sub']}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_OUT)

r += 1
r = section(C, r, "E.  FIXED vs. VARIABLE  ->  COST PER STALL")
CR["alloc_v"] = r
r = line(C, r, "VARIABLE capex (hard + allocated soft & contingency)", "$",
         [f"={c}{CR['hv']}+({c}{CR['soft']}+{c}{CR['cont']})*{c}{CR['vshare']}" for c in SC],
         M0, font=BLACK, bold=True)
CR["alloc_f"] = r
r = line(C, r, "FIXED capex (everything else)", "$",
         [f"={c}{CR['total']}-{c}{CR['alloc_v']}" for c in SC], M0, font=BLACK, bold=True)
CR["stalls"] = r
r = line(C, r, "Stalls", "stalls",
         [f"={aref('stalls', c)}" for c in SC], N0, font=GREEN)
CR["cps_v"] = r
r = line(C, r, "Variable cost per stall", "$ / stall",
         [f"={c}{CR['alloc_v']}/{c}{CR['stalls']}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_OUT,
         note="The MARGINAL cost of adding one more stall to an already-entitled site. This is the number that should drive the site-layout decision.")
CR["cps_f"] = r
r = line(C, r, "Fixed cost per stall", "$ / stall",
         [f"={c}{CR['alloc_f']}/{c}{CR['stalls']}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_OUT,
         note="Site-level costs spread over the stall count. Falls as density rises - the single biggest lever on cost per stall.")
CR["cps_t"] = r
r = line(C, r, "ALL-IN COST PER STALL", "$ / stall",
         [f"={c}{CR['total']}/{c}{CR['stalls']}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_OUT)
CR["cps_land"] = r
r = line(C, r, "   of which: land", "$ / stall",
         [f"={c}{CR['land']}/{c}{CR['stalls']}" for c in SC], M0, font=BLACK, indent=1)
CR["fpct"] = r
r = line(C, r, "   Fixed share of all-in cost", "%",
         [f"={c}{CR['alloc_f']}/{c}{CR['total']}" for c in SC], P1, font=BLACK, indent=1)
CR["per_ac"] = r
r = line(C, r, "All-in cost per gross acre", "$ / acre",
         [f"={c}{CR['total']}/{aref('acres', c)}" for c in SC], M0, font=BLACK)


# =====================================================================
# REVENUE & NOI  (stabilized)
# =====================================================================
N = sheet("Revenue_NOI", [46, 17, 15, 15, 15, 62])
title(N, "Stabilized Revenue, Operating Expenses & NOI",
      "Year-1-stabilized dollars. Reserves are deducted before NOI because lenders size debt to a reserve-burdened NOI.")
r = 4
r = hdrrow(N, r, ["", "Unit", "S1  Greenfield Full Asphalt", "S2  Greenfield Value-Eng.",
                  "S3  Retrofit Existing Yard", "Note"])
NR = {}

r = section(N, r, "A.  REVENUE")
NR["st_m"] = r
r = line(N, r, "Stalls - monthly reserved", "stalls",
         [f"=ROUND({aref('stalls', c)}*{aref('mix_month', c)},0)" for c in SC], N0, font=BLACK)
NR["st_t"] = r
r = line(N, r, "Stalls - transient / nightly", "stalls",
         [f"={aref('stalls', c)}-{c}{NR['st_m']}" for c in SC], N0, font=BLACK)
NR["gpr_m"] = r
r = line(N, r, "Gross potential rent - monthly stalls", "$ / yr",
         [f"={c}{NR['st_m']}*{aref('rate_month', c)}*12" for c in SC], M0, font=BLACK)
NR["gpr_t"] = r
r = line(N, r, "Gross potential rent - transient stalls", "$ / yr",
         [f"={c}{NR['st_t']}*{aref('rate_night', c)}*365" for c in SC], M0, font=BLACK)
NR["gpr"] = r
r = line(N, r, "Gross potential rent", "$ / yr",
         [f"={c}{NR['gpr_m']}+{c}{NR['gpr_t']}" for c in SC], M0, font=BLACK, bold=True)
NR["vac"] = r
r = line(N, r, "Less: vacancy / unutilized nights", "$ / yr",
         [f"=-({c}{NR['gpr_m']}*(1-{aref('occ_month', c)})+{c}{NR['gpr_t']}*(1-{aref('occ_night', c)}))"
          for c in SC], M0, font=BLACK)
NR["cred"] = r
r = line(N, r, "Less: credit loss / bad debt", "$ / yr",
         [f"=-({c}{NR['gpr']}+{c}{NR['vac']})*{aref('credit', c)}" for c in SC], M0, font=BLACK)
NR["park"] = r
r = line(N, r, "Net parking revenue", "$ / yr",
         [f"=SUM({c}{NR['gpr']}:{c}{NR['cred']})" for c in SC], M0, font=BLACK, bold=True)
NR["anc"] = r
r = line(N, r, "Ancillary revenue", "$ / yr",
         [f"={c}{NR['park']}*{aref('anc_pct', c)}" for c in SC], M0, font=BLACK)
NR["egi"] = r
r = line(N, r, "EFFECTIVE GROSS INCOME", "$ / yr",
         [f"={c}{NR['park']}+{c}{NR['anc']}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_TOT)
NR["rev_stall"] = r
r = line(N, r, "   Blended revenue per stall per month", "$ / stall / mo",
         [f"={c}{NR['egi']}/{aref('stalls', c)}/12" for c in SC], M0, font=BLACK, indent=1, fill=FILL_TOT)
NR["rev_ac"] = r
r = line(N, r, "   Revenue per gross acre", "$ / acre / yr",
         [f"={c}{NR['egi']}/{aref('acres', c)}" for c in SC], M0, font=BLACK, indent=1,
         note="Cross-check: bulk NNN truck-yard leases in Hartford metro trade around $35,000-55,000 per acre per year. A per-stall retail operation must beat that to justify the operating overhead.")

r += 1
r = section(N, r, "B.  OPERATING EXPENSES")
NR["tax"] = r
r = line(N, r, "Real estate taxes", "$ / yr",
         [f"=({xref('land', c)}*{aref('tv_land', c)}+Cost_Per_Stall!${c}${CR['impr_basis']}*{aref('tv_impr', c)})"
          f"*{aref('assess', c)}*{aref('mill', c)}/1000" for c in SC], M0, font=BLACK,
         note="(Land x land factor + improvements x improvement factor) x 70% assessment ratio x mill rate / 1000.", fill=FILL_KEY)
NR["ins"] = r
r = line(N, r, "Insurance", "$ / yr",
         [f"={aref('ins_stall', c)}*{aref('stalls', c)}" for c in SC], M0, font=BLACK)
NR["staff"] = r
r = line(N, r, "On-site staffing", "$ / yr", [f"={aref('staff', c)}" for c in SC], M0, font=GREEN)
NR["mon"] = r
r = line(N, r, "Remote monitoring & patrol", "$ / yr", [f"={aref('monitor', c)}" for c in SC], M0, font=GREEN)
NR["snow"] = r
r = line(N, r, "Snow & ice management", "$ / yr",
         [f"={aref('snow_ac', c)}*{aref('yard_ac', c)}" for c in SC], M0, font=BLACK)
NR["rm"] = r
r = line(N, r, "Repairs & maintenance", "$ / yr",
         [f"={aref('rm_stall', c)}*{aref('stalls', c)}" for c in SC], M0, font=BLACK)
NR["util"] = r
r = line(N, r, "Utilities", "$ / yr",
         [f"={aref('util_stall', c)}*{aref('stalls', c)}" for c in SC], M0, font=BLACK)
NR["trash"] = r
r = line(N, r, "Trash, restrooms, janitorial", "$ / yr",
         [f"={aref('trash_stall', c)}*{aref('stalls', c)}" for c in SC], M0, font=BLACK)
NR["mktg"] = r
r = line(N, r, "Marketing & leasing", "$ / yr",
         [f"={aref('mktg_stall', c)}*{aref('stalls', c)}" for c in SC], M0, font=BLACK)
NR["prof"] = r
r = line(N, r, "Professional fees, legal, accounting, admin", "$ / yr",
         [f"={aref('prof', c)}" for c in SC], M0, font=GREEN)
NR["res"] = r
r = line(N, r, "Replacement reserve", "$ / yr",
         [f"={aref('reserve_stall', c)}*{aref('stalls', c)}" for c in SC], M0, font=BLACK)
NR["opex_fix"] = r
r = line(N, r, "Subtotal - revenue-independent opex", "$ / yr",
         [f"=SUM({c}{NR['tax']}:{c}{NR['res']})" for c in SC], M0, font=BLACK, bold=True, fill=FILL_TOT,
         note="Does not move with occupancy - drives the operating leverage in this asset class.")
NR["mgmt"] = r
r = line(N, r, "Property management fee", "$ / yr",
         [f"={c}{NR['egi']}*{aref('mgmt_pct', c)}" for c in SC], M0, font=BLACK)
NR["proc"] = r
r = line(N, r, "Payment processing & reservation platform", "$ / yr",
         [f"={c}{NR['park']}*{aref('proc_pct', c)}" for c in SC], M0, font=BLACK)
NR["opex_var"] = r
r = line(N, r, "Subtotal - revenue-linked opex", "$ / yr",
         [f"={c}{NR['mgmt']}+{c}{NR['proc']}" for c in SC], M0, font=BLACK, bold=True)
NR["opex"] = r
r = line(N, r, "TOTAL OPERATING EXPENSES", "$ / yr",
         [f"={c}{NR['opex_fix']}+{c}{NR['opex_var']}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_TOT)
NR["opex_ratio"] = r
r = line(N, r, "   Opex ratio", "% of EGI",
         [f"={c}{NR['opex']}/{c}{NR['egi']}" for c in SC], P1, font=BLACK, indent=1)
NR["opex_stall"] = r
r = line(N, r, "   Opex per stall per month", "$ / stall / mo",
         [f"={c}{NR['opex']}/{aref('stalls', c)}/12" for c in SC], M0, font=BLACK, indent=1)
NR["opex_vpct"] = r
r = line(N, r, "   Revenue-linked opex as % of EGI", "%",
         [f"={c}{NR['opex_var']}/{c}{NR['egi']}" for c in SC], P2, font=BLACK, indent=1)

r += 1
NR["noi"] = r
r = line(N, r, "NET OPERATING INCOME (after reserves)", "$ / yr",
         [f"={c}{NR['egi']}-{c}{NR['opex']}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_OUT)
NR["noi_br"] = r
r = line(N, r, "NOI before replacement reserves", "$ / yr",
         [f"={c}{NR['noi']}+{c}{NR['res']}" for c in SC], M0, font=BLACK, bold=True)
NR["noi_stall"] = r
r = line(N, r, "   NOI per stall", "$ / stall / yr",
         [f"={c}{NR['noi']}/{aref('stalls', c)}" for c in SC], M0, font=BLACK, indent=1)
NR["yoc"] = r
r = line(N, r, "YIELD ON COST  (NOI / total project cost)", "%",
         [f"={c}{NR['noi']}/Cost_Per_Stall!${c}${CR['total']}" for c in SC], P2, font=BLACK, bold=True, fill=FILL_OUT)
NR["val"] = r
r = line(N, r, "Stabilized value at exit cap", "$",
         [f"={c}{NR['noi']}/{aref('exit_cap', c)}" for c in SC], M0, font=BLACK, bold=True)
NR["profit"] = r
r = line(N, r, "Development profit / (loss)", "$",
         [f"={c}{NR['val']}-Cost_Per_Stall!${c}${CR['total']}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_OUT)
NR["margin"] = r
r = line(N, r, "   Development margin", "% of cost",
         [f"={c}{NR['profit']}/Cost_Per_Stall!${c}${CR['total']}" for c in SC], P1, font=BLACK, indent=1)
NR["spread"] = r
r = line(N, r, "   Spread to exit cap (yield on cost - cap rate)", "bps",
         [f"=({c}{NR['yoc']}-{aref('exit_cap', c)})*10000" for c in SC], N0, font=BLACK, indent=1,
         note="Merchant-build rule of thumb: you want 150-250 bps of spread over the exit cap to justify development risk.")

# ---- now backfill the lease-up reserve on Cost_Per_Stall (no circular reference:
#      Revenue_NOI's tax line depends only on 'impr_basis', which sits above this row)
for i, c in enumerate(SC):
    cell = C.cell(row=CR["lu_opex"], column=3 + i,
                  value=f"=Revenue_NOI!${c}${NR['opex']}*{aref('lu_months', c)}/12")
    cell.number_format = M0
    cell.font = BLACK


def nref(key, col):
    return f"Revenue_NOI!${col}${NR[key]}"


def cref(key, col):
    return f"Cost_Per_Stall!${col}${CR[key]}"


# =====================================================================
# DEBT & DSCR
# =====================================================================
D = sheet("Debt_DSCR", [46, 17, 15, 15, 15, 62])
title(D, "Debt Sizing, DSCR & Break-Evens",
      "Permanent debt sized to the LESSER of loan-to-cost, loan-to-value and the minimum-DSCR constraint.")
r = 4
r = hdrrow(D, r, ["", "Unit", "S1  Greenfield Full Asphalt", "S2  Greenfield Value-Eng.",
                  "S3  Retrofit Existing Yard", "Note"])
DR = {}

r = section(D, r, "A.  LOAN SIZING")
DR["cost"] = r
r = line(D, r, "Total project cost", "$", [f"={cref('total', c)}" for c in SC], M0, font=GREEN)
DR["noi"] = r
r = line(D, r, "Stabilized NOI", "$ / yr", [f"={nref('noi', c)}" for c in SC], M0, font=GREEN)
DR["val"] = r
r = line(D, r, "Stabilized value", "$", [f"={nref('val', c)}" for c in SC], M0, font=GREEN)
DR["k"] = r
r = line(D, r, "Annual debt constant", "%",
         [f"=-PMT({aref('p_rate', c)}/12,{aref('p_amort', c)}*12,1)*12" for c in SC], P2, font=BLACK,
         note="Mortgage constant = annualized payment on $1 of principal.")
DR["l_ltc"] = r
r = line(D, r, "Loan by max loan-to-cost", "$",
         [f"={c}{DR['cost']}*{aref('p_ltc', c)}" for c in SC], M0, font=BLACK)
DR["l_ltv"] = r
r = line(D, r, "Loan by max loan-to-value", "$",
         [f"={c}{DR['val']}*{aref('p_ltv', c)}" for c in SC], M0, font=BLACK)
DR["l_dscr"] = r
r = line(D, r, "Loan by minimum DSCR", "$",
         [f"={c}{DR['noi']}/({aref('p_dscr', c)}*{c}{DR['k']})" for c in SC], M0, font=BLACK)
DR["loan"] = r
r = line(D, r, "SUPPORTABLE LOAN", "$",
         [f"=MAX(0,MIN({c}{DR['l_ltc']},{c}{DR['l_ltv']},{c}{DR['l_dscr']}))" for c in SC],
         M0, font=BLACK, bold=True, fill=FILL_OUT)
DR["bind"] = r
r = line(D, r, "Binding constraint", "",
         [f'=IF({c}{DR["loan"]}={c}{DR["l_dscr"]},"DSCR",IF({c}{DR["loan"]}={c}{DR["l_ltv"]},"LTV","LTC"))'
          for c in SC], TXT, font=BLACK)
DR["ltc_act"] = r
r = line(D, r, "   Actual loan to cost", "%",
         [f"={c}{DR['loan']}/{c}{DR['cost']}" for c in SC], P1, font=BLACK, indent=1)
DR["eq"] = r
r = line(D, r, "Required equity", "$",
         [f"={c}{DR['cost']}-{c}{DR['loan']}" for c in SC], M0, font=BLACK, bold=True)
DR["eqs"] = r
r = line(D, r, "   Equity per stall", "$ / stall",
         [f"={c}{DR['eq']}/{aref('stalls', c)}" for c in SC], M0, font=BLACK, indent=1)

r += 1
r = section(D, r, "B.  DEBT SERVICE COVERAGE")
DR["ds"] = r
r = line(D, r, "Annual debt service - at supportable loan", "$ / yr",
         [f"={c}{DR['loan']}*{c}{DR['k']}" for c in SC], M0, font=BLACK)
DR["dscr"] = r
r = line(D, r, "DSCR - at supportable loan", "x",
         [f"=IF({c}{DR['ds']}=0,0,{c}{DR['noi']}/{c}{DR['ds']})" for c in SC], X2, font=BLACK, bold=True, fill=FILL_OUT)
DR["ds65"] = r
r = line(D, r, "Annual debt service - if funded at max LTC", "$ / yr",
         [f"={c}{DR['l_ltc']}*{c}{DR['k']}" for c in SC], M0, font=BLACK)
DR["dscr65"] = r
r = line(D, r, "DSCR - if funded at max LTC", "x",
         [f"={c}{DR['noi']}/{c}{DR['ds65']}" for c in SC], X2, font=BLACK, bold=True, fill=FILL_OUT,
         note="THE HEADLINE TEST. This is the coverage a lender would actually see on a request for the target leverage.")
DR["test"] = r
r = line(D, r, "Passes minimum DSCR at target leverage?", "",
         [f'=IF({c}{DR["dscr65"]}>={aref("p_dscr", c)},"PASS","FAIL")' for c in SC], TXT, font=BLACK, bold=True)
DR["dy"] = r
r = line(D, r, "Debt yield - at max LTC loan", "%",
         [f"={c}{DR['noi']}/{c}{DR['l_ltc']}" for c in SC], P1, font=BLACK,
         note="Lenders on non-core collateral generally want a 10%+ debt yield.")
DR["cf"] = r
r = line(D, r, "Cash flow after debt service (supportable loan)", "$ / yr",
         [f"={c}{DR['noi']}-{c}{DR['ds']}" for c in SC], M0, font=BLACK)
DR["coc"] = r
r = line(D, r, "Cash-on-cash return on equity", "%",
         [f"=IF({c}{DR['eq']}<=0,0,{c}{DR['cf']}/{c}{DR['eq']})" for c in SC], P1, font=BLACK, bold=True)

r += 1
r = section(D, r, "C.  BREAK-EVENS  (what the deal needs in order to clear a 1.25x DSCR at target leverage)")
DR["req_noi"] = r
r = line(D, r, "NOI required for minimum DSCR at max LTC", "$ / yr",
         [f"={c}{DR['ds65']}*{aref('p_dscr', c)}" for c in SC], M0, font=BLACK)
DR["noi_gap"] = r
r = line(D, r, "NOI surplus / (shortfall)", "$ / yr",
         [f"={c}{DR['noi']}-{c}{DR['req_noi']}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_OUT)
DR["req_egi"] = r
r = line(D, r, "EGI required", "$ / yr",
         [f"=({c}{DR['req_noi']}+{nref('opex_fix', c)})/(1-{nref('opex_vpct', c)})" for c in SC], M0, font=BLACK)
DR["req_rev"] = r
r = line(D, r, "Required blended revenue per stall per month", "$ / stall / mo",
         [f"={c}{DR['req_egi']}/{aref('stalls', c)}/12" for c in SC], M0, font=BLACK, bold=True, fill=FILL_OUT)
DR["act_rev"] = r
r = line(D, r, "   vs. modeled blended revenue per stall per month", "$ / stall / mo",
         [f"={nref('rev_stall', c)}" for c in SC], M0, font=GREEN, indent=1)
DR["rev_gap"] = r
r = line(D, r, "   Rate gap", "%",
         [f"={c}{DR['req_rev']}/{c}{DR['act_rev']}-1" for c in SC], P1, font=BLACK, indent=1, bold=True)
DR["max_cost"] = r
r = line(D, r, "Maximum supportable project cost", "$",
         [f"={c}{DR['noi']}/({aref('p_dscr', c)}*{aref('p_ltc', c)}*{c}{DR['k']})" for c in SC], M0, font=BLACK,
         note="Approximate - holds NOI constant, so it ignores the small property-tax feedback from a lower cost basis.")
DR["max_cps"] = r
r = line(D, r, "Maximum supportable cost per stall", "$ / stall",
         [f"={c}{DR['max_cost']}/{aref('stalls', c)}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_OUT)
DR["act_cps"] = r
r = line(D, r, "   vs. modeled all-in cost per stall", "$ / stall",
         [f"={cref('cps_t', c)}" for c in SC], M0, font=GREEN, indent=1)
DR["max_land"] = r
r = line(D, r, "Maximum supportable land price", "$ / acre",
         [f"=({c}{DR['max_cost']}-({c}{DR['cost']}-{cref('land', c)}))/({aref('acres', c)}*(1+{aref('close_pct', c)}))"
          for c in SC], M0, font=BLACK, bold=True, fill=FILL_OUT,
         note="Residual land value at a 1.25x DSCR. Compare to the $175k/acre (raw) and $385k/acre (improved) inputs.")
DR["be_occ"] = r
r = line(D, r, "Break-even occupancy (1.00x DSCR, max LTC loan)", "% of stabilized",
         [f"=({c}{DR['ds65']}+{nref('opex_fix', c)})/(1-{nref('opex_vpct', c)})/{nref('egi', c)}" for c in SC],
         P1, font=BLACK, bold=True,
         note="Share of stabilized EGI needed just to cover opex and debt service.")


# =====================================================================
# 10-YEAR PRO FORMA  (selected scenario)
# =====================================================================
P = sheet("ProForma_10yr", [42, 13] + [12] * 11)
title(P, "10-Year Operating Pro Forma  -  selected scenario",
      "Change the scenario selector in cell C3 (1 = S1, 2 = S2, 3 = S3). Everything below repoints automatically.")
P["A3"] = "SCENARIO SELECTOR  ->"
P["A3"].font = BOLD
P["C3"] = 2
P["C3"].font = BOLDB
P["C3"].fill = FILL_KEY
P["C3"].number_format = N0
P["C3"].border = BOXB
P["D3"] = '=CHOOSE($C$3,"S1  Greenfield, full-depth asphalt, staffed","S2  Greenfield, value-engineered, unmanned","S3  Retrofit of an existing paved yard")'
P["D3"].font = Font(name=F, size=10, bold=True, color="1F3864")


def sel(sheetname, rowmap, key):
    return f"INDEX({sheetname}!$C${rowmap[key]}:$E${rowmap[key]},$C$3)"


PR = {}
r = 5
r = section(P, r, "SELECTED SCENARIO INPUTS", last_col="M")


def pline(row, label, unit, formula, fmt, font=BLACK, note=None, bold=False, fill=None):
    P.cell(row=row, column=1, value=label).font = BOLD if bold else Font(name=F, size=10)
    P.cell(row=row, column=2, value=unit).font = Font(name=F, size=9, color="595959")
    c = P.cell(row=row, column=3, value=formula)
    c.number_format = fmt
    c.font = font if not bold else BOLD
    if fill:
        c.fill = fill
    if note:
        n = P.cell(row=row, column=5, value=note)
        n.font = NOTE
    return row + 1


PR["stalls"] = r
r = pline(r, "Stalls", "stalls", "=" + sel("Assumptions", AR, "stalls"), N0)
PR["egi"] = r
r = pline(r, "Stabilized EGI", "$ / yr", "=" + sel("Revenue_NOI", NR, "egi"), M0)
PR["ofix"] = r
r = pline(r, "Revenue-independent opex", "$ / yr", "=" + sel("Revenue_NOI", NR, "opex_fix"), M0)
PR["ovar"] = r
r = pline(r, "Revenue-linked opex", "% of EGI", "=" + sel("Revenue_NOI", NR, "opex_vpct"), P2)
PR["grev"] = r
r = pline(r, "Revenue growth", "% p.a.", "=" + sel("Assumptions", AR, "growth_rev"), P1)
PR["gopx"] = r
r = pline(r, "Opex growth", "% p.a.", "=" + sel("Assumptions", AR, "growth_opex"), P1)
PR["cost"] = r
r = pline(r, "Total project cost", "$", "=" + sel("Cost_Per_Stall", CR, "total"), M0)
PR["loan"] = r
r = pline(r, "Permanent loan (at max LTC)", "$", "=" + sel("Debt_DSCR", DR, "l_ltc"), M0)
PR["k"] = r
r = pline(r, "Annual debt constant", "%", "=" + sel("Debt_DSCR", DR, "k"), P2)
PR["ds"] = r
r = pline(r, "Annual debt service", "$ / yr", f"=$C${PR['loan']}*$C${PR['k']}", M0)
PR["cap"] = r
r = pline(r, "Exit cap rate", "%", "=" + sel("Assumptions", AR, "exit_cap"), P1)
PR["eq"] = r
r = pline(r, "Equity at close", "$", f"=$C${PR['cost']}-$C${PR['loan']}", M0)
PR["cost_sale"] = r
r = pline(r, "Cost of sale", "% of value", 0.02, P1, font=BLUE)

r += 1
r = section(P, r, "LEASE-UP RAMP  (occupancy as a % of stabilized)", last_col="M")
PR["ramp"] = r
P.cell(row=r, column=1, value="Occupancy ramp - Years 1 / 2 / 3+").font = Font(name=F, size=10)
P.cell(row=r, column=2, value="% of stabilized").font = Font(name=F, size=9, color="595959")
for i, v in enumerate([0.45, 0.78, 1.00]):
    c = P.cell(row=r, column=3 + i, value=v)
    c.number_format = P1
    c.font = BLUE
    c.fill = FILL_KEY
P.cell(row=r, column=6, value="Industry guidance: 70% occupancy is a typical stabilization target, reached within ~36 months. Tech-enabled operators report 92-98% once mature.").font = NOTE
r += 2

r = section(P, r, "OPERATING PRO FORMA", last_col="M")
hr = r
P.cell(row=hr, column=1, value="Year").font = HDR
P.cell(row=hr, column=1).fill = FILL_HDR
P.cell(row=hr, column=2, value="").fill = FILL_HDR
for y in range(1, 11):
    c = P.cell(row=hr, column=2 + y, value=str(y))
    c.font = HDR
    c.fill = FILL_HDR
    c.alignment = Alignment(horizontal="center")
    c.number_format = TXT
r = hr + 1

rows = [
    ("Occupancy - % of stabilized", P1,
     lambda y: (f"=$C${PR['ramp']}" if y == 1 else (f"=$D${PR['ramp']}" if y == 2 else f"=$E${PR['ramp']}"))),
    ("Effective gross income", M0,
     lambda y: f"=$C${PR['egi']}*{get_column_letter(2+y)}{{OCC}}*(1+$C${PR['grev']})^{y-1}"),
    ("Revenue-independent opex", M0,
     lambda y: f"=-$C${PR['ofix']}*(1+$C${PR['gopx']})^{y-1}"),
    ("Revenue-linked opex", M0,
     lambda y: f"=-{get_column_letter(2+y)}{{EGI}}*$C${PR['ovar']}"),
    ("Total operating expenses", M0,
     lambda y: f"=SUM({get_column_letter(2+y)}{{OFIX}}:{get_column_letter(2+y)}{{OVAR}})"),
    ("NET OPERATING INCOME", M0,
     lambda y: f"={get_column_letter(2+y)}{{EGI}}+{get_column_letter(2+y)}{{OTOT}}"),
    ("Debt service", M0, lambda y: f"=-$C${PR['ds']}"),
    ("Cash flow after debt service", M0,
     lambda y: f"={get_column_letter(2+y)}{{NOI}}+{get_column_letter(2+y)}{{DS}}"),
    ("DSCR", X2,
     lambda y: f"=IF($C${PR['ds']}=0,0,{get_column_letter(2+y)}{{NOI}}/$C${PR['ds']})"),
    ("Debt yield", P1,
     lambda y: f"=IF($C${PR['loan']}=0,0,{get_column_letter(2+y)}{{NOI}}/$C${PR['loan']})"),
    ("Yield on cost", P2,
     lambda y: f"={get_column_letter(2+y)}{{NOI}}/$C${PR['cost']}"),
]
row_at = {}
for i, (label, fmt, _) in enumerate(rows):
    row_at[label] = r + i
keymap = {
    "{OCC}": row_at["Occupancy - % of stabilized"],
    "{EGI}": row_at["Effective gross income"],
    "{OFIX}": row_at["Revenue-independent opex"],
    "{OVAR}": row_at["Revenue-linked opex"],
    "{OTOT}": row_at["Total operating expenses"],
    "{NOI}": row_at["NET OPERATING INCOME"],
    "{DS}": row_at["Debt service"],
}
for label, fmt, fn in rows:
    rr = row_at[label]
    strong = label.isupper() or label == "DSCR"
    c0 = P.cell(row=rr, column=1, value=label)
    c0.font = BOLD if strong else Font(name=F, size=10)
    for y in range(1, 11):
        f_ = fn(y)
        for k, v in keymap.items():
            f_ = f_.replace(k, str(v))
        cell = P.cell(row=rr, column=2 + y, value=f_)
        cell.number_format = fmt
        cell.font = BOLD if strong else BLACK
        if strong:
            cell.fill = FILL_OUT
    if label == "NET OPERATING INCOME":
        for y in range(1, 11):
            P.cell(row=rr, column=2 + y).border = TOPB

r = max(row_at.values()) + 2
PR["rev"] = r
P.cell(row=r, column=1, value="Reversion - Year 10 (value at exit cap, net of sale costs)").font = BOLD
cell = P.cell(row=r, column=12,
              value=f"=L{row_at['NET OPERATING INCOME']}*(1+$C${PR['grev']})/$C${PR['cap']}*(1-$C${PR['cost_sale']})")
cell.number_format = M0
cell.font = BOLD
cell.fill = FILL_OUT
r += 1
PR["debt_bal"] = r
P.cell(row=r, column=1, value="Less: loan balance at Year 10").font = Font(name=F, size=10)
_pr = sel("Assumptions", AR, "p_rate")
_pa = sel("Assumptions", AR, "p_amort")
cell = P.cell(row=r, column=12,
              value=f"=-$C${PR['loan']}*(1-(1+{_pr}/12)^-({_pa}*12-120))/(1-(1+{_pr}/12)^-({_pa}*12))")
cell.number_format = M0
cell.font = BLACK
r += 1
PR["net_rev"] = r
P.cell(row=r, column=1, value="Net sale proceeds to equity").font = BOLD
cell = P.cell(row=r, column=12, value=f"=L{PR['rev']}+L{PR['debt_bal']}")
cell.number_format = M0
cell.font = BOLD
cell.fill = FILL_OUT
r += 2

PR["ecf0"] = r
P.cell(row=r, column=1, value="Equity cash flow").font = BOLD
for y in range(0, 11):
    col = 2 + y
    if y == 0:
        f_ = f"=-$C${PR['eq']}"
    elif y == 10:
        f_ = f"={get_column_letter(col)}{row_at['Cash flow after debt service']}+L{PR['net_rev']}"
    else:
        f_ = f"={get_column_letter(col)}{row_at['Cash flow after debt service']}"
    cell = P.cell(row=r, column=col, value=f_)
    cell.number_format = M0
    cell.font = BOLD
    cell.fill = FILL_OUT
r += 1
PR["irr"] = r
P.cell(row=r, column=1, value="Levered equity IRR (10-yr hold)").font = BOLD
cell = P.cell(row=r, column=3, value=f'=IFERROR(IRR(B{PR["ecf0"]}:L{PR["ecf0"]}),"n/m")')
cell.number_format = P1
cell.font = BOLD
cell.fill = FILL_OUT
r += 1
PR["em"] = r
P.cell(row=r, column=1, value="Equity multiple").font = BOLD
cell = P.cell(row=r, column=3,
              value=f'=IFERROR(SUM(C{PR["ecf0"]}:L{PR["ecf0"]})/$C${PR["eq"]}+1,"n/m")')
cell.number_format = X2
cell.font = BOLD


# =====================================================================
# SENSITIVITY
# =====================================================================
S = sheet("Sensitivity", [30, 14] + [13] * 9)
title(S, "Sensitivity Analysis  -  where the deal breaks and what fixes it",
      "Grids are exact re-solves of the same math, not approximations, except where noted. Selector in C3.")
S["A3"] = "SCENARIO SELECTOR  ->"
S["A3"].font = BOLD
S["C3"] = 2
S["C3"].font = BOLDB
S["C3"].fill = FILL_KEY
S["C3"].number_format = N0
S["C3"].border = BOXB
S["D3"] = '=CHOOSE($C$3,"S1  Greenfield, full-depth asphalt, staffed","S2  Greenfield, value-engineered, unmanned","S3  Retrofit of an existing paved yard")'
S["D3"].font = Font(name=F, size=10, bold=True, color="1F3864")

r = 5
r = section(S, r, "SELECTED SCENARIO DRIVERS", last_col="K")
SR = {}


def sline(row, label, formula, fmt, font=BLACK):
    S.cell(row=row, column=1, value=label).font = Font(name=F, size=10)
    c = S.cell(row=row, column=3, value=formula)
    c.number_format = fmt
    c.font = font
    return row + 1


for key, label, src, fmt in [
    ("stalls", "Stalls", ("Assumptions", AR, "stalls"), N0),
    ("ofix", "Revenue-independent opex ($/yr)", ("Revenue_NOI", NR, "opex_fix"), M0),
    ("otax", "   of which real estate taxes", ("Revenue_NOI", NR, "tax"), M0),
    ("ovar", "Revenue-linked opex (% of EGI)", ("Revenue_NOI", NR, "opex_vpct"), P2),
    ("k", "Annual debt constant", ("Debt_DSCR", DR, "k"), P2),
    ("ltc", "Target loan to cost", ("Assumptions", AR, "p_ltc"), P1),
    ("mindscr", "Minimum DSCR", ("Assumptions", AR, "p_dscr"), X2),
    ("cap", "Exit cap rate", ("Assumptions", AR, "exit_cap"), P1),
    ("acres", "Gross acres", ("Assumptions", AR, "acres"), N2),
    ("close", "Acquisition closing costs (%)", ("Assumptions", AR, "close_pct"), P1),
    ("sfst", "Paved SF per stall", ("Assumptions", AR, "sf_stall"), N0),
    ("disc", "Per-stall discrete items ($/stall)", ("Capex_Variable", VR, "st_sub"), M0),
    ("hv", "Variable hard cost ($)", ("Cost_Per_Stall", CR, "hv"), M0),
    ("allocv", "Variable all-in cost ($)", ("Cost_Per_Stall", CR, "alloc_v"), M0),
    ("allocf", "Fixed all-in cost ($)", ("Cost_Per_Stall", CR, "alloc_f"), M0),
    ("landsub", "Land + closing ($)", ("Cost_Per_Stall", CR, "land"), M0),
    ("landcost", "Land price ($)", ("Capex_Fixed", XR, "land"), M0),
    ("impr", "Improvement basis for assessment ($)", ("Cost_Per_Stall", CR, "impr_basis"), M0),
    ("assess", "CT assessment ratio", ("Assumptions", AR, "assess"), P1),
    ("mill", "Mill rate", ("Assumptions", AR, "mill"), N2),
    ("tvland", "Assessor factor - land", ("Assumptions", AR, "tv_land"), P1),
    ("cpst", "All-in cost per stall ($)", ("Cost_Per_Stall", CR, "cps_t"), M0),
    ("revst", "Blended revenue per stall / month ($)", ("Revenue_NOI", NR, "rev_stall"), M0),
]:
    SR[key] = r
    r = sline(r, label, "=" + sel(src[0], src[1], src[2]), fmt, GREEN)

SR["markup"] = r
r = sline(r, "Soft-cost + contingency markup on variable hard", f"=$C${SR['allocv']}/$C${SR['hv']}", X2)
SR["fexland"] = r
r = sline(r, "Fixed all-in cost excluding land", f"=$C${SR['allocf']}-$C${SR['landsub']}", M0)
SR["ofixnotax"] = r
r = sline(r, "Revenue-independent opex excluding taxes", f"=$C${SR['ofix']}-$C${SR['otax']}", M0)


def grid(row, heading, note, row_hdr, col_hdr, rvals, cvals, cellf, fmt, rfmt, cfmt):
    """cellf(rowref, colref) -> formula body without leading '='."""
    row = section(S, row, heading, last_col="K")
    S.cell(row=row, column=1, value=note).font = NOTE
    S.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    S.row_dimensions[row].height = 26
    row += 1
    hr = row
    c = S.cell(row=hr, column=2, value=row_hdr)
    c.font = HDR
    c.fill = FILL_HDR
    c.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
    S.row_dimensions[hr].height = 30
    S.cell(row=hr - 1, column=3, value=col_hdr).font = Font(name=F, size=9, bold=True, color="1F3864")
    for j, cv in enumerate(cvals):
        cc = S.cell(row=hr, column=3 + j, value=cv)
        cc.number_format = cfmt
        cc.font = HDR
        cc.fill = FILL_HDR
        cc.alignment = Alignment(horizontal="center")
    for i, rv in enumerate(rvals):
        rr = hr + 1 + i
        rc = S.cell(row=rr, column=2, value=rv)
        rc.number_format = rfmt
        rc.font = BOLD
        rc.fill = FILL_TOT
        for j in range(len(cvals)):
            colL = get_column_letter(3 + j)
            cell = S.cell(row=rr, column=3 + j, value="=" + cellf(f"$B{rr}", f"{colL}${hr}"))
            cell.number_format = fmt
            cell.font = BLACK
            cell.border = BOXB
    return hr + 1 + len(rvals) + 2


r += 2
rate_vals = [250, 275, 300, 325, 350, 375, 400, 425, 450, 500]
cost_vals = [18000, 22000, 26000, 30000, 34000, 38000, 42000]

r = grid(r, "GRID 1  |  DSCR at target leverage",
         "DSCR = NOI / debt service, where the loan is the target loan-to-cost applied to the cost-per-stall in the column header. Shaded band below 1.25x is a decline.",
         "Blended revenue $ / stall / month", "All-in cost per stall  ->",
         rate_vals, cost_vals,
         lambda R, Cc: (f"({R}*12*$C${SR['stalls']}*(1-$C${SR['ovar']})-$C${SR['ofix']})"
                        f"/($C${SR['ltc']}*{Cc}*$C${SR['stalls']}*$C${SR['k']})"),
         X2, M0, M0)

r = grid(r, "GRID 2  |  Yield on cost  (unlevered NOI / total project cost)",
         "Merchant developers generally need 150-250 bps of yield-on-cost above the exit cap rate. At a 7.75% exit cap that means roughly a 9.25-10.25% yield on cost.",
         "Blended revenue $ / stall / month", "All-in cost per stall  ->",
         rate_vals, cost_vals,
         lambda R, Cc: (f"({R}*12*$C${SR['stalls']}*(1-$C${SR['ovar']})-$C${SR['ofix']})"
                        f"/({Cc}*$C${SR['stalls']})"),
         P2, M0, M0)

land_vals = [0, 50000, 100000, 150000, 200000, 250000, 300000, 385000]
pave_vals = [1.50, 2.50, 4.00, 5.50, 7.00, 8.50, 10.00]
r = grid(r, "GRID 3  |  All-in cost per stall",
         "Land price vs. yard construction cost. Approximate: holds fixed site costs and the soft-cost markup constant, and ignores the small financing-cost feedback from a different land basis.",
         "Land price $ / acre", "Yard construction $ / SF of paved yard  ->",
         land_vals, pave_vals,
         lambda R, Cc: (f"({R}*$C${SR['acres']}*(1+$C${SR['close']})+$C${SR['fexland']})/$C${SR['stalls']}"
                        f"+({Cc}*$C${SR['sfst']}+$C${SR['disc']})*$C${SR['markup']}"),
         M0, M0, M2)

assess_vals = [0.20, 0.30, 0.40, 0.45, 0.55, 0.65, 0.80, 1.00]
r = grid(r, "GRID 4  |  DSCR sensitivity to the property-tax assessment",
         "The improvement assessment factor is the largest single soft spot in this model. Bloomfield's 34.40 mill rate on a CT 70% assessment ratio makes taxes a first-order driver, not a rounding item.",
         "Assessor factor on improvements", "Blended revenue $ / stall / month  ->",
         assess_vals, [275, 300, 325, 350, 375, 400, 450],
         lambda R, Cc: (f"({Cc}*12*$C${SR['stalls']}*(1-$C${SR['ovar']})-$C${SR['ofixnotax']}"
                        f"-(($C${SR['landcost']}*$C${SR['tvland']}+$C${SR['impr']}*{R})*$C${SR['assess']}*$C${SR['mill']}/1000))"
                        f"/($C${SR['ltc']}*$C${SR['cpst']}*$C${SR['stalls']}*$C${SR['k']})"),
         X2, P1, M0)


# =====================================================================
# SUMMARY
# =====================================================================
U = wb["Sheet"]
wb.remove(U)
U = wb.create_sheet("Summary", 0)
for i, w in enumerate([46, 15, 16, 16, 16, 44], start=1):
    U.column_dimensions[get_column_letter(i)].width = w
U.sheet_view.showGridLines = False
title(U, "Bloomfield, CT  -  Truck Parking Development",
      "Fixed & variable capex  ->  cost per stall  ->  NOI  ->  DSCR.  All figures are formula-driven from the Assumptions tab.")
r = 4
r = hdrrow(U, r, ["Metric", "Unit", "S1  Greenfield Full Asphalt", "S2  Greenfield Value-Eng.",
                  "S3  Retrofit Existing Yard", "Comment"])

r = section(U, r, "PROGRAM")
r = line(U, r, "Gross site area", "acres", [f"={aref('acres', c)}" for c in SC], N2, font=GREEN)
r = line(U, r, "Truck stalls", "stalls", [f"={aref('stalls', c)}" for c in SC], N0, font=GREEN, bold=True)
r = line(U, r, "Density", "stalls / acre", [f"={aref('stalls_ac', c)}" for c in SC], N1, font=GREEN)

r = section(U, r, "CAPITAL COST")
r = line(U, r, "Fixed capex", "$", [f"={cref('alloc_f', c)}" for c in SC], M0, font=GREEN)
r = line(U, r, "Variable capex", "$", [f"={cref('alloc_v', c)}" for c in SC], M0, font=GREEN)
r = line(U, r, "TOTAL PROJECT COST", "$", [f"={cref('total', c)}" for c in SC], M0, font=BLACK, bold=True, fill=FILL_TOT)
r = line(U, r, "Fixed cost per stall", "$ / stall", [f"={cref('cps_f', c)}" for c in SC], M0, font=GREEN)
r = line(U, r, "Variable cost per stall", "$ / stall", [f"={cref('cps_v', c)}" for c in SC], M0, font=GREEN)
r = line(U, r, "ALL-IN COST PER STALL", "$ / stall", [f"={cref('cps_t', c)}" for c in SC], M0,
         font=BLACK, bold=True, fill=FILL_OUT,
         note="Fixed costs dominate - see the fixed-share line below. Density is therefore the strongest single lever on this number.")
r = line(U, r, "   Fixed share of all-in cost", "%", [f"={cref('fpct', c)}" for c in SC], P1, font=GREEN, indent=1)
r = line(U, r, "   Land per stall", "$ / stall", [f"={cref('cps_land', c)}" for c in SC], M0, font=GREEN, indent=1)

r = section(U, r, "STABILIZED OPERATIONS")
r = line(U, r, "Effective gross income", "$ / yr", [f"={nref('egi', c)}" for c in SC], M0, font=GREEN)
r = line(U, r, "Blended revenue per stall", "$ / stall / mo", [f"={nref('rev_stall', c)}" for c in SC], M0, font=GREEN)
r = line(U, r, "Operating expenses", "$ / yr", [f"={nref('opex', c)}" for c in SC], M0, font=GREEN)
r = line(U, r, "   Opex ratio", "% of EGI", [f"={nref('opex_ratio', c)}" for c in SC], P1, font=GREEN, indent=1)
r = line(U, r, "   Real estate taxes", "$ / yr", [f"={nref('tax', c)}" for c in SC], M0, font=GREEN, indent=1)
r = line(U, r, "NET OPERATING INCOME", "$ / yr", [f"={nref('noi', c)}" for c in SC], M0,
         font=BLACK, bold=True, fill=FILL_OUT)
r = line(U, r, "   NOI per stall", "$ / stall / yr", [f"={nref('noi_stall', c)}" for c in SC], M0, font=GREEN, indent=1)
r = line(U, r, "YIELD ON COST", "%", [f"={nref('yoc', c)}" for c in SC], P2, font=BLACK, bold=True, fill=FILL_OUT)
r = line(U, r, "Stabilized value at exit cap", "$", [f"={nref('val', c)}" for c in SC], M0, font=GREEN)
r = line(U, r, "Development profit / (loss)", "$", [f"={nref('profit', c)}" for c in SC], M0, font=BLACK, bold=True)

r = section(U, r, "FINANCING & COVERAGE")
r = line(U, r, "Loan at target 65% LTC", "$", [f"=Debt_DSCR!${c}${DR['l_ltc']}" for c in SC], M0, font=GREEN)
r = line(U, r, "Annual debt service", "$ / yr", [f"=Debt_DSCR!${c}${DR['ds65']}" for c in SC], M0, font=GREEN)
r = line(U, r, "DSCR AT TARGET LEVERAGE", "x", [f"=Debt_DSCR!${c}${DR['dscr65']}" for c in SC], X2,
         font=BLACK, bold=True, fill=FILL_OUT, note="Test is 1.25x. See Debt_DSCR tab for the sized loan.")
r = line(U, r, "Pass / fail vs. 1.25x", "", [f"=Debt_DSCR!${c}${DR['test']}" for c in SC], TXT, font=BLACK, bold=True)
r = line(U, r, "Debt yield", "%", [f"=Debt_DSCR!${c}${DR['dy']}" for c in SC], P1, font=GREEN)
r = line(U, r, "Supportable loan (lesser of LTC / LTV / DSCR)", "$", [f"=Debt_DSCR!${c}${DR['loan']}" for c in SC], M0, font=GREEN)
r = line(U, r, "Required equity", "$", [f"=Debt_DSCR!${c}${DR['eq']}" for c in SC], M0, font=GREEN)

r = section(U, r, "WHAT THE DEAL NEEDS  (break-evens at 1.25x DSCR, 65% LTC)")
r = line(U, r, "Required blended revenue per stall", "$ / stall / mo",
         [f"=Debt_DSCR!${c}${DR['req_rev']}" for c in SC], M0, font=GREEN, bold=True)
r = line(U, r, "   Modeled blended revenue per stall", "$ / stall / mo",
         [f"={nref('rev_stall', c)}" for c in SC], M0, font=GREEN, indent=1)
r = line(U, r, "   Rate gap", "%", [f"=Debt_DSCR!${c}${DR['rev_gap']}" for c in SC], P1, font=GREEN, indent=1, bold=True)
r = line(U, r, "Maximum supportable cost per stall", "$ / stall",
         [f"=Debt_DSCR!${c}${DR['max_cps']}" for c in SC], M0, font=GREEN, bold=True)
r = line(U, r, "Maximum supportable land price", "$ / acre",
         [f"=Debt_DSCR!${c}${DR['max_land']}" for c in SC], M0, font=GREEN, bold=True,
         note="Residual land value. Negative means the improvements alone cost more than the income can carry.")
r = line(U, r, "Break-even occupancy", "% of stabilized",
         [f"=Debt_DSCR!${c}${DR['be_occ']}" for c in SC], P1, font=GREEN)

r += 1
U.cell(row=r, column=1, value="LEGEND").font = BOLD
r += 1
for txt, fnt in [
    ("Blue text = hardcoded input or scenario lever. Edit these on the Assumptions tab.", BLUE),
    ("Black text = formula calculated on this sheet.", BLACK),
    ("Green text = link pulled from another tab.", GREEN),
    ("Yellow fill = key assumption that materially moves the answer; pressure-test it first.", BLACK),
]:
    c = U.cell(row=r, column=1, value=txt)
    c.font = fnt
    if "Yellow" in txt:
        c.fill = FILL_KEY
    r += 1


# =====================================================================
# SOURCES & NOTES
# =====================================================================
Z = sheet("Sources_Notes", [34, 96, 60])
title(Z, "Sources, Benchmarks & Modeling Notes",
      "Every hardcoded number in this model traces to one of the benchmarks below, to a stated engineering calculation, or to a labeled judgment call.")
r = 4
Z.cell(row=r, column=1, value="Topic").font = HDR
Z.cell(row=r, column=2, value="What it establishes").font = HDR
Z.cell(row=r, column=3, value="Source").font = HDR
for cc in range(1, 4):
    Z.cell(row=r, column=cc).fill = FILL_HDR
r += 1

SOURCES = [
    ("CT truck parking demand",
     "CT has roughly 1,238 truck parking spaces; 92% of demand concentrates on I-95, I-84, I-91 and I-395, mostly overnight; demand projected to grow 18% by 2040. Establishes that the shortage is real and structural.",
     "CTDOT statewide truck parking study / CT Freight Plan - portal.ct.gov/dot"),
    ("Public supply expansion",
     "$31M CTDOT program adds 180+ spaces at Middletown, Madison, Southington, Southbury and Vernon by ~2030, taking public capacity from ~420 to ~600. Implies ~$172k per space at public prevailing-wage pricing, and is the competitive backdrop for any private facility.",
     "CTDOT press release (2024); Hartford Business Journal; CCJ"),
    ("Development cost - rule of thumb",
     "$100k-$200k per acre for new truck parking construction excluding land; standard yield 25 trucks/acre; implies $4,000-$8,000 per stall. Used as a low-cost-market floor, NOT as the Connecticut number.",
     "Truck Parking Club - Cost of Building a Truck Parking Lot"),
    ("Surface parking cost - national",
     "$4,500-$6,800 per completed surface space in 2026 including paving, drainage, striping, lighting, signage and basic technology.",
     "Wins Parking - Parking Lot Construction Cost Guide (2026)"),
    ("Paving cost - heavy duty",
     "Commercial asphalt $4-$10/SF; heavy-duty truck sections $7-$12+/SF (4-6\" asphalt over 10-12\"+ aggregate base). CT specifically $4-$11/SF, with CT construction costs ~1.32x the national average.",
     "Asphalt Coatings Co.; The Pavement Group; CostFlowAI CT calculator"),
    ("Stall geometry",
     "A tractor-trailer stall is ~14' x 75'; a trailer-only stall ~14' x 55'. Model uses 12' x 75' plus half of a 75' back-in aisle = 1,450 SF per stall all-in.",
     "Truck Parking Club; standard AASHTO/industry layout practice"),
    ("Parking rates - national bands",
     "$12-$25 per night at chain travel centers; $50-$150/month for bobtails and box trucks at private lots; $150-$500+/month for full tractor-trailer configurations, regionally dependent.",
     "RecNation - How Much Is Truck Parking"),
    ("Parking rates - Hartford metro",
     "Hartford ~$81/month average for 22' tractor spaces; East Hartford ~$96; West Hartford ~$106 (12-35' spaces). These are small-vehicle spaces, so they set a FLOOR, not the 53' secured rate. Model uses $315-$340/month for a secured, lit, gated 53' stall.",
     "Neighbor.com marketplace listings, Hartford / East Hartford / West Hartford"),
    ("Occupancy & stabilization",
     "70% occupancy is a typical stabilization target, generally reached within ~36 months; professionally managed, tech-enabled facilities report 92-98%. Model underwrites 88-90% stabilized with a 45% / 78% / 100% ramp.",
     "Truck Parking Club development materials; Truckspace"),
    ("IOS cap rates",
     "2026: 6.00-6.75% for stabilized institutional IOS in primary markets; 6.75-7.75% in secondary markets; broader range 6.5-9.0%. IOS prices 25-75 bps wide of comparable industrial. Hartford is secondary.",
     "Matthews 2026 IOS Sector Update; Commercial Lending Solutions"),
    ("Debt terms",
     "Commercial mortgage rates start ~5.74% (Aug 2026); industrial bridge 7.5-9.5%; DSCR floors 1.25x for core, 1.30-1.40x for other property types; 25-year amortization available.",
     "Select Commercial; PeerSense; Commercial Lending USA"),
    ("Bloomfield mill rate",
     "2025 Grand List adopted mill rate 34.40 for real and personal property (year 2 of a 4-year revaluation phase-in). FY2026 budget forum projected ~34.03. CT assesses at 70% of fair market value.",
     "Town of Bloomfield - Town's Mill Rate / Assessor / FY2026 Budget Forum"),
    ("Bloomfield zoning",
     "Bloomfield TPZ has treated outdoor storage as a use that is NOT permitted as a principal use - approved as an accessory use by special permit, with a ZBA variance otherwise required. A standalone commercial truck-parking yard would likely need a text amendment or variance. This is the gating risk on the whole deal.",
     "Bloomfield Town Plan & Zoning Commission meeting minutes (2025-2026)"),
    ("Bloomfield industrial land",
     "CT industrial land averages ~$110k/acre across 31 listed properties; a Bloomfield flex industrial property (23,825 SF on 2.51 acres) traded at $1.86M in July 2026. Model uses $175k/acre raw and $385k/acre for an already-paved improved yard.",
     "LandSearch CT industrial; Hartford Business Journal"),
    ("Bloomfield industrial context",
     "Active industrial corridor along Blue Hills Ave / Cottage Grove Rd; a 74,520 SF warehouse and distribution center was proposed on 8.7 acres at 59-69 Douglas St near Routes 218/187 with easy I-91 access. Confirms both freight demand and the availability of comparable parcels.",
     "Hartford Business Journal; Sentry Commercial / LoopNet listings"),
    ("Insurance",
     "IOS truck-parking operators need garagekeepers legal liability in addition to standard GL and property - a coverage line that does not appear in a generic parking-lot pro forma.",
     "CNS Insurance; InsuranceHub - insurance for truck parking lots"),
]
for topic, what, src in SOURCES:
    Z.cell(row=r, column=1, value=topic).font = BOLD
    a = Z.cell(row=r, column=2, value=what)
    a.font = Font(name=F, size=9)
    a.alignment = Alignment(wrap_text=True, vertical="top")
    b = Z.cell(row=r, column=3, value=src)
    b.font = Font(name=F, size=9, italic=True, color="595959")
    b.alignment = Alignment(wrap_text=True, vertical="top")
    Z.cell(row=r, column=1).alignment = Alignment(vertical="top", wrap_text=True)
    Z.row_dimensions[r].height = 46
    r += 1

r += 1
Z.cell(row=r, column=1, value="MODELING NOTES & KNOWN LIMITATIONS").font = BOLD
r += 1
NOTES = [
    "Stall count is derived, not asserted: gross acres x 43,560 x net yard efficiency / 1,450 SF per stall. Change any of the three and the whole model repoints.",
    "Fixed vs. variable split: variable = yard construction ($/SF of paved area) plus per-stall discrete items (lighting, electrical, pedestals, camera density). Everything else - land, entitlement, stormwater basin, gatehouse, fence, gates, security head-end, utilities, financing, lease-up reserve - is fixed. Soft-cost loadings and contingency are allocated pro-rata by share of hard cost.",
    "Property taxes are modeled on an assessor factor applied to cost basis, not on an income-approach valuation. A CT assessor may use either. Grid 4 on the Sensitivity tab shows the full range of outcomes; this is the single largest soft spot in the model.",
    "There is no circular reference: the lease-up reserve depends on stabilized opex, and opex depends on the capitalized cost BEFORE the reserve. Do not repoint the tax formula at total project cost or the workbook will become circular.",
    "Break-even solves hold NOI constant, so the maximum supportable cost and maximum land price ignore the second-order property-tax relief from a lower cost basis. Both are therefore mildly conservative.",
    "No revenue is assumed from a truck wash, fuel, a repair bay or a convenience store. Those are separate businesses with their own capex and are the usual way a highway-adjacent truck stop closes an economics gap - Bloomfield's off-highway location makes them harder to justify.",
    "Environmental risk is carried as an allowance, not a budget. CT's Release-Based Remediation program replaced the Transfer Act; a previously-industrial paved yard (S3) can carry remediation exposure well beyond the $95,000 allowance shown.",
    "Ledge and unsuitable soils are the largest single greenfield cost shock in this part of Connecticut and are covered only by the general contingency. A geotechnical investigation should precede any hard commitment on land.",
]
for n in NOTES:
    c = Z.cell(row=r, column=1, value="- " + n)
    c.font = Font(name=F, size=9)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    Z.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
    Z.row_dimensions[r].height = 40
    r += 1

# =====================================================================
# SCALE & DENSITY  (the dominant lever: fixed costs spread over stalls)
# =====================================================================
G = sheet("Scale_Density", [34, 14] + [12] * 8)
title(G, "Scale & Density  -  the dominant lever on cost per stall",
      "Fixed site costs are 56-81% of this deal's capital cost, so cost per stall falls fast with site size and stall density. Selector in C3.")
G["A3"] = "SCENARIO SELECTOR  ->"
G["A3"].font = BOLD
G["C3"] = 2
G["C3"].font = BOLDB
G["C3"].fill = FILL_KEY
G["C3"].number_format = N0
G["C3"].border = BOXB
G["D3"] = '=CHOOSE($C$3,"S1  Greenfield, full-depth asphalt, staffed","S2  Greenfield, value-engineered, unmanned","S3  Retrofit of an existing paved yard")'
G["D3"].font = Font(name=F, size=10, bold=True, color="1F3864")

r = 5
r = section(G, r, "SELECTED SCENARIO DRIVERS", last_col="J")
GR = {}


def gline(row, label, formula, fmt, font=BLACK, note=None):
    G.cell(row=row, column=1, value=label).font = Font(name=F, size=10)
    c = G.cell(row=row, column=3, value=formula)
    c.number_format = fmt
    c.font = font
    if note:
        n = G.cell(row=row, column=5, value=note)
        n.font = NOTE
    return row + 1


for key, label, src, fmt in [
    ("acres0", "Base gross acres", ("Assumptions", AR, "acres"), N2),
    ("yieldp", "Net yard efficiency", ("Assumptions", AR, "yield_pct"), P1),
    ("landac", "Land price ($/acre)", ("Assumptions", AR, "land_ac"), M0),
    ("close", "Acquisition closing costs", ("Assumptions", AR, "close_pct"), P1),
    ("persf", "Yard construction ($/SF)", ("Capex_Variable", VR, "sf_sub"), M2),
    ("disc", "Per-stall discrete items ($/stall)", ("Capex_Variable", VR, "st_sub"), M0),
    ("hv0", "Base variable hard cost ($)", ("Cost_Per_Stall", CR, "hv"), M0),
    ("allocv0", "Base variable all-in cost ($)", ("Cost_Per_Stall", CR, "alloc_v"), M0),
    ("allocf0", "Base fixed all-in cost ($)", ("Cost_Per_Stall", CR, "alloc_f"), M0),
    ("landsub0", "Base land + closing ($)", ("Cost_Per_Stall", CR, "land"), M0),
    ("ins", "Insurance ($/stall/yr)", ("Assumptions", AR, "ins_stall"), M0),
    ("rm", "Repairs & maintenance ($/stall/yr)", ("Assumptions", AR, "rm_stall"), M0),
    ("util", "Utilities ($/stall/yr)", ("Assumptions", AR, "util_stall"), M0),
    ("trash", "Trash & restrooms ($/stall/yr)", ("Assumptions", AR, "trash_stall"), M0),
    ("mktg", "Marketing ($/stall/yr)", ("Assumptions", AR, "mktg_stall"), M0),
    ("resv", "Replacement reserve ($/stall/yr)", ("Assumptions", AR, "reserve_stall"), M0),
    ("snowac", "Snow & ice ($/paved acre/yr)", ("Assumptions", AR, "snow_ac"), M0),
    ("staff", "On-site staffing ($/yr)", ("Assumptions", AR, "staff"), M0),
    ("mon", "Remote monitoring ($/yr)", ("Assumptions", AR, "monitor"), M0),
    ("prof", "Professional fees ($/yr)", ("Assumptions", AR, "prof"), M0),
    ("ovar", "Revenue-linked opex (% of EGI)", ("Revenue_NOI", NR, "opex_vpct"), P2),
    ("assess", "CT assessment ratio", ("Assumptions", AR, "assess"), P1),
    ("mill", "Mill rate", ("Assumptions", AR, "mill"), N2),
    ("tvimpr", "Assessor factor - improvements", ("Assumptions", AR, "tv_impr"), P1),
    ("ltc", "Target loan to cost", ("Assumptions", AR, "p_ltc"), P1),
    ("k", "Annual debt constant", ("Debt_DSCR", DR, "k"), P2),
]:
    GR[key] = r
    r = gline(r, label, "=" + sel(src[0], src[1], src[2]), fmt, GREEN)

GR["markup"] = r
r = gline(r, "Soft + contingency markup on variable hard", f"=$C${GR['allocv0']}/$C${GR['hv0']}", X2)
GR["fexland"] = r
r = gline(r, "Base fixed all-in cost excluding land", f"=$C${GR['allocf0']}-$C${GR['landsub0']}", M0)
GR["scalepct"] = r
G.cell(row=r, column=1, value="Share of non-land fixed cost that scales with site area").font = Font(name=F, size=10)
c = G.cell(row=r, column=3, value=0.40)
c.number_format = P1
c.font = BLUE
c.fill = FILL_KEY
G.cell(row=r, column=5, value="Stormwater, perimeter fence, entry work and mass E&S scale with acreage; entitlement, gatehouse, gates, security head-end and design do not.").font = NOTE
r += 1
GR["fflat"] = r
r = gline(r, "   Fixed cost - flat component ($)", f"=$C${GR['fexland']}*(1-$C${GR['scalepct']})", M0)
GR["fperac"] = r
r = gline(r, "   Fixed cost - per gross acre ($)", f"=$C${GR['fexland']}*$C${GR['scalepct']}/$C${GR['acres0']}", M0)
GR["rev"] = r
G.cell(row=r, column=1, value="Blended revenue per stall per month").font = BOLD
c = G.cell(row=r, column=3, value="=" + sel("Revenue_NOI", NR, "rev_stall"))
c.number_format = M0
c.font = GREEN
G.cell(row=r, column=5, value="Overwrite with a hardcoded rate to test a different pricing assumption across the whole grid.").font = NOTE
r += 1
GR["opst"] = r
r = gline(r, "Per-stall opex ($/stall/yr)",
          f"=$C${GR['ins']}+$C${GR['rm']}+$C${GR['util']}+$C${GR['trash']}+$C${GR['mktg']}+$C${GR['resv']}", M0)
GR["opflat"] = r
r = gline(r, "Flat opex ($/yr)", f"=$C${GR['staff']}+$C${GR['mon']}+$C${GR['prof']}", M0)
GR["snowsf"] = r
r = gline(r, "Snow & ice ($/paved SF/yr)", f"=$C${GR['snowac']}/43560", M2)

acres_vals = [4, 6, 8, 10, 12, 14, 18, 24, 30]
sf_vals = [1650, 1500, 1400, 1300, 1200, 1100]


def ggrid(row, heading, note, cellf, fmt, extra=None):
    row = section(G, row, heading, last_col="J")
    G.cell(row=row, column=1, value=note).font = NOTE
    G.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    G.row_dimensions[row].height = 26
    row += 1
    G.cell(row=row - 1, column=3, value="Paved SF per stall (density)  ->").font = Font(name=F, size=9, bold=True, color="1F3864")
    hr = row
    c = G.cell(row=hr, column=2, value="Gross acres")
    c.font = HDR
    c.fill = FILL_HDR
    c.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
    G.row_dimensions[hr].height = 28
    for j, cv in enumerate(sf_vals):
        cc = G.cell(row=hr, column=3 + j, value=cv)
        cc.number_format = N0
        cc.font = HDR
        cc.fill = FILL_HDR
        cc.alignment = Alignment(horizontal="center")
    for i, rv in enumerate(acres_vals):
        rr = hr + 1 + i
        rc = G.cell(row=rr, column=2, value=rv)
        rc.number_format = N0
        rc.font = BOLD
        rc.fill = FILL_TOT
        for j in range(len(sf_vals)):
            colL = get_column_letter(3 + j)
            cell = G.cell(row=rr, column=3 + j, value="=" + cellf(f"$B{rr}", f"{colL}${hr}", rr, colL, hr))
            cell.number_format = fmt
            cell.font = BLACK
            cell.border = BOXB
    return hr, hr + 1 + len(acres_vals) + 2


r += 1
# --- stall count grid
hr_st, r = ggrid(r, "GRID A  |  Stall count",
    "stalls = gross acres x 43,560 x net yard efficiency / paved SF per stall. Below about 1,200 SF per stall the layout needs blind-side backing or shared aisles - confirm against a real site plan before underwriting it.",
    lambda A, Fc, rr, cl, hr: f"ROUNDDOWN({A}*43560*$C${GR['yieldp']}/{Fc},0)", N0)

# --- cost per stall grid  (references Grid A one row-for-row via ROW() offset)
hr_cps, r = ggrid(r, "GRID B  |  All-in cost per stall",
    "Land and the acreage-scaled share of fixed cost, spread over the stall count from Grid A. Variable cost per stall is exact.",
    lambda A, Fc, rr, cl, hr: (
        f"IF({cl}{hr_st + (rr - hr)}=0,0,"
        f"({A}*$C${GR['landac']}*(1+$C${GR['close']})+$C${GR['fflat']}+$C${GR['fperac']}*{A})"
        f"/{cl}{hr_st + (rr - hr)}"
        f"+({Fc}*$C${GR['persf']}+$C${GR['disc']})*$C${GR['markup']})"), M0)

# --- NOI grid
hr_noi, r = ggrid(r, "GRID C  |  Stabilized NOI",
    "Revenue = blended $/stall/month x stalls x 12, net of revenue-linked opex. Costs = per-stall opex + snow per paved SF + flat opex + property tax computed on this grid's own cost basis.",
    lambda A, Fc, rr, cl, hr: (
        f"{cl}{hr_st + (rr - hr)}*$C${GR['rev']}*12*(1-$C${GR['ovar']})"
        f"-{cl}{hr_st + (rr - hr)}*$C${GR['opst']}"
        f"-{cl}{hr_st + (rr - hr)}*{Fc}*$C${GR['snowsf']}"
        f"-$C${GR['opflat']}"
        f"-(({A}*$C${GR['landac']}+({cl}{hr_cps + (rr - hr)}*{cl}{hr_st + (rr - hr)}"
        f"-{A}*$C${GR['landac']}*(1+$C${GR['close']}))*$C${GR['tvimpr']})*$C${GR['assess']}*$C${GR['mill']}/1000)"), M0)

# --- DSCR grid
hr_d, r = ggrid(r, "GRID D  |  DSCR at target leverage",
    "DSCR = Grid C NOI / (target loan-to-cost x Grid B cost per stall x Grid A stalls x annual debt constant). 1.25x is the lender test.",
    lambda A, Fc, rr, cl, hr: (
        f"IF({cl}{hr_cps + (rr - hr)}*{cl}{hr_st + (rr - hr)}=0,0,"
        f"{cl}{hr_noi + (rr - hr)}/($C${GR['ltc']}*{cl}{hr_cps + (rr - hr)}"
        f"*{cl}{hr_st + (rr - hr)}*$C${GR['k']}))"), X2)

# --- yield on cost grid
hr_y, r = ggrid(r, "GRID E  |  Yield on cost",
    "NOI divided by total project cost. Needs to clear the exit cap rate by 150-250 bps to justify merchant development risk.",
    lambda A, Fc, rr, cl, hr: (
        f"IF({cl}{hr_cps + (rr - hr)}*{cl}{hr_st + (rr - hr)}=0,0,"
        f"{cl}{hr_noi + (rr - hr)}/({cl}{hr_cps + (rr - hr)}"
        f"*{cl}{hr_st + (rr - hr)}))"), P2)

for ws in wb.worksheets:
    ws.freeze_panes = "A5"
wb["ProForma_10yr"].freeze_panes = "C5"
wb["Sensitivity"].freeze_panes = "C5"
wb["Scale_Density"].freeze_panes = "C5"
wb.move_sheet("Sources_Notes", offset=0)

# LibreOffice is unavailable in this environment, so no cached values can be baked in.
# Force a full recalculation the moment the file is opened, in Excel or anywhere else.
wb.calculation.fullCalcOnLoad = True

OUT = "/home/user/multiprocessingtemplate/bloomfield_truck_parking/Bloomfield_Truck_Parking_Model.xlsx"
wb.save(OUT)
print("saved", OUT)
