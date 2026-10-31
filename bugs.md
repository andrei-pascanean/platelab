# Bugs

Discovered during code + data audit (2026-10-30). Organized by type and priority.

---

## Code Bugs

### BUG-01 — Forbidden Combinations section never hides for null data
**File:** `index.html` — `buildPanelHTML()`  
**Severity:** Medium  
The section always renders. When `forbidden_combinations` is `null` (no restrictions), the code falls to the `else` branch and outputs the text "None". Per the spec in `CLAUDE.md`, `null` means the section should be hidden entirely, the same way Vanity Plates is hidden.  
**Affects:** 29 of 44 countries (all with `null` forbidden_combinations).  
**Fix:** Wrap the entire Forbidden Combinations section in `if (isVal(pf.forbidden_combinations))`.

---

### BUG-02 — `isVal()` doesn't catch the string `"None"`
**File:** `index.html` — `isVal()` + `buildPanelHTML()`  
**Severity:** Medium  
`isVal()` guards against `null`, `"null"`, and `""`, but not the literal string `"None"`. Five countries have `strip_contents: "None"` in the JSON, which passes `isVal()` and renders the word "None" in the Side Strip field instead of hiding the field.  
**Affects:** `CH`, `BA`, `GB`, `LI`, `PT`  
**Fix:** Add `"None"` to the exclusion list in `isVal()`.

---

### BUG-03 — `tagCodes()` false positives on contextual numbers
**File:** `index.html` — `tagCodes()`  
**Severity:** Low  
The regex tags 3–4 digit numbers in explanatory prose, not just plate format codes. The existing currency guard (`€₴£$~kr`) only looks 3 characters before the number, so it misses values like "270 euros" or a standalone year like "2006".  
**Affected fields and text:**
- `HR` vanity: `270` (euros) gets tagged
- `LV` vanity: `2006` (a year) gets tagged
- `ES` format explanation: `9999` (range endpoint) gets tagged
- `CY` format explanation: `001` and `999` (range endpoints) get tagged
- `GR` format explanation: `1000` and `9999` (range endpoints) get tagged

---

## Data Bugs (`plate_formats.json`)

### BUG-04 — GB typeface is a bad AI extraction
**Entry:** `GB`  
**Field:** `typeface`  
**Current value:** `"Mandatory (typeface), a variation of Charles Wright"`  
The AI copied the word "typeface" from a surrounding sentence. The correct value is `"Charles Wright"` (a font specifically designed for UK plates).

---

### BUG-05 — LV typeface value is ambiguous/wrong
**Entry:** `LV`  
**Field:** `typeface`  
**Current value:** `"Austria"`  
"Austria" appears to be a font name in the FE-Schrift family, but as a standalone value it reads like a country name and is almost certainly a misextraction. Needs manual verification against the Latvian plate spec.

---

### BUG-06 — AD strip data is inconsistent
**Entry:** `AD` (Andorra)  
**Fields:** `colors_strip` / `strip_contents`  
**Current values:** `colors_strip: "None"` but `strip_contents: "Coat of arms and country code AND"`  
Andorra plates actually have a left strip with the coat of arms. One of these two fields is wrong. Given that `strip_contents` has real content, `colors_strip` is likely the incorrect field.

---

### BUG-07 — ME format description doesn't match plate image
**Entry:** `ME` (Montenegro)  
**Field:** `format_explanation`  
The explanation describes the first two letters as a municipality code, but the actual plate image does not show `MNE` as described. The format explanation needs to be rewritten to match what's visible on the physical plate.

---

### BUG-08 — CZ format pattern doesn't match plate image
**Entry:** `CZ` (Czech Republic)  
**Field:** `format_pattern`  
**Current value:** `"0AA 0000"`  
The actual plate image shows a number followed by two letters first. The pattern and explanation need to be corrected to match the image.

---

### BUG-09 — SK and HU missing coat of arms in format pattern
**Entries:** `SK` (Slovakia), `HU` (Hungary)  
**Field:** `format_pattern`  
Austria (`AT`) correctly uses the `∇` symbol to represent the provincial emblem in its format pattern (e.g., `AA ∇ 000 AA`). Slovakia and Hungary also display a coat of arms on their plates but their format patterns omit the `∇`. Both entries should be updated to include it.

---

### BUG-10 — BA format explanation doesn't describe the actual format
**Entry:** `BA` (Bosnia and Herzegovina)  
**Field:** `format_explanation`  
**Pattern:** `A00-A-000`  
The explanation describes the positions generically without clarifying what any component represents (no geographic origin, no series logic). It needs a complete rewrite to describe the actual format structure.

---

### BUG-11 — PT alphabet entry is factually incorrect
**Entry:** `PT` (Portugal)  
**Field:** `alphabet`  
The current text states that W, Y, and K are not part of the Portuguese alphabet. This is incorrect — Portugal officially added W, K, and Y to its standard alphabet. The entry needs to be corrected.

---

### BUG-12 — MD region code data is outdated
**Entry:** `MD` (Moldova)  
**Fields:** `format_explanation` / `alphabet`  
The entry states that `C` and `K` are used for the Chișinău region code. This is no longer accurate for current Moldovan plates and should be removed or updated to reflect the current system.

---

## Incomplete Data (gaps, not bugs)

### GAP-01 — 39 of 44 countries have `typeface: "Unknown"`
Only `AM`, `CY`, `DE`, `GB`, `IS`, `LV`, `MD`, `RO`, `SI` have typeface data. Currently hidden in the UI by `isVal()`, which is correct behavior, but it's a significant content gap.

### GAP-02 — 8 countries have `vanity_plates: "Unknown"`
`AD`, `AL`, `AM`, `BA`, `BY`, `CY`, `DE`, `MD` — also currently hidden in the UI. These are mostly smaller or non-EU countries where Wikipedia data was sparse.

---

## Unreachable Assets

### NOTE-01 — 17 plate images in `plateMap` have no SVG country
These ISOs have images stored and referenced in `plateMap` but have no matching `<path id="...">` in the SVG, so they can never be opened via the map. They represent territories, dependencies, and unrecognized states not drawn on the SVG:  
`ABH`, `AX`, `AZ`, `FO`, `GBA`, `GBG`, `GBJ`, `GBM`, `GBZ`, `MC`, `MT`, `PMR`, `RSO`, `RU`, `SM`, `TRNC`, `VA`  
Not a bug per se, but the images and format data for these are sitting unused.
