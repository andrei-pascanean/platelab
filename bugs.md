# Bugs

Discovered during code + data audit (2026-10-30, updated 2026-10-31). Organized by type and priority.

---

## Code Bugs

### BUG-C1 — `"Unknown"` and `"Not available"` render as real field values
**File:** `index.html` — `isVal()`  
**Severity:** High  
`isVal()` was fixed to catch `"None"`, but `"Unknown"` and `"Not available"` still pass through and render as actual data in the panel. Typeface shows "Unknown" for 35 countries; vanity plates shows "Unknown" for 8. These fields should be hidden, not displayed.  
**Fix:** Add `"Unknown"` and `"Not available"` to the exclusion list in `isVal()`.

---

### BUG-C2 — Escape key doesn't close the panel
**File:** `index.html`  
**Severity:** Medium  
There is no `keydown` listener in the script. Pressing Escape while a country panel is open does nothing. Standard expectation for any overlay or slide-in panel.  
**Fix:** Add a `keydown` listener that calls `closePanel()` when `key === "Escape"` and the panel is open.

---

### BUG-C3 — Portugal has a duplicate SVG path with `id="PT"`
**File:** `index.html` — embedded SVG  
**Severity:** Medium  
There are 45 country paths for 44 countries; two paths share `id="PT"`. `getElementById` only returns the first, so panel highlighting and `centerOnCountry` silently ignore the second shape. Depending on which path is first, clicking part of Portugal may open the panel but not highlight or centre correctly.  
**Fix:** Merge the two paths into one, or keep one `id="PT"` and give the other a non-interactive class.

---

### BUG-C4 — Viewport meta blocks user zoom (WCAG 1.4.4)
**File:** `index.html` — `<meta name="viewport">`  
**Severity:** Medium  
The viewport tag includes `maximum-scale=1.0, user-scalable=no`. This prevents users from pinching to zoom the page on mobile, which violates WCAG 1.4.4 (Resize Text). The map manages its own touch zoom via custom gesture handlers, so these restrictions are not needed for the map to work.  
**Fix:** Remove `maximum-scale=1.0` and `user-scalable=no` from the viewport meta tag.

---

### BUG-C5 — Map clicks during pan/zoom animation land on wrong country
**File:** `index.html`  
**Severity:** Medium  
Opening a panel triggers `centerOnCountry()`, which animates the viewBox. If the user clicks during the animation the click coordinates no longer correspond to the intended country — in testing this opened Serbia when a neighbouring country was targeted.  
**Fix:** Set a flag during `animateViewBox` and ignore country click/tap events until the animation completes.

---

### BUG-C6 — Mixed letter+digit tokens not chipped in format patterns
**File:** `index.html` — `tagCodes()`  
**Severity:** Low  
`tagCodes()` matches `[A-Z]{1,3}` (letters only) or `\d{3,4}` (digits only), but not mixed tokens like `00A`. Sweden's second format pattern `AAA 00A` renders `AAA` chipped and `00A` unchipped, which looks inconsistent given the purpose of the chips.  
**Fix:** Extend the regex to also match mixed alphanumeric tokens in the format `\d{1,2}[A-Z]` and `[A-Z]\d{1,2}`.

---

## Data Bugs (`plate_formats.json`)

### BUG-04 — GB typeface is a bad AI extraction
**Entry:** `GB`  
**Field:** `typeface`  
**Current value:** `"Mandatory (typeface), a variation of Charles Wright"`  
The AI copied the word "typeface" from a surrounding sentence. The correct value is `"Charles Wright"` (a font specifically designed for UK plates).

---

### BUG-05 — LV typeface value is wrong
**Entry:** `LV`  
**Field:** `typeface`  
**Current value:** `"Austria"`  
Confirmed extraction error. Latvia does not use a typeface called "Austria". Needs manual verification against the Latvian plate spec.

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
**Entry:** `CZ` (Czechia)  
**Field:** `format_pattern`  
**Current value:** `"0AA 0000"`  
The actual plate image shows a number followed by two letters first. The pattern and explanation need to be corrected to match the image. Also: the entry name should be updated from "Czech Republic" to "Czechia".

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

### BUG-13 — NL format is outdated
**Entry:** `NL` (Netherlands)  
**Field:** `format_pattern`, `format_explanation`  
**Current value:** `"A-000-AA"` (sidecode 10, introduced 2021)  
Since 4 June 2024 new cars are issued sidecode 11: `AAA-00-A`. The Netherlands has 7 formats currently in use; the entry should reflect the current system. The explanation is also generic filler that doesn't describe the sidecode logic.  
**Source:** [Alpina](https://www.alpina.nl/en/car-insurance/registration-mark/last-license-plate/), [Wikipedia](https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_the_Netherlands)

---

### BUG-14 — SI format pattern wrong
**Entry:** `SI` (Slovenia)  
**Field:** `format_pattern`, `format_explanation`  
**Current value:** `"AA-0000-AA"`  
Contradicts the site's own plate image (`LJ 898-KP`). The real format is a region code, a municipal crest, then 5 characters with a dash (e.g. `LJ 60-CFB`). Pattern and explanation both need rewriting.  
**Source:** [openvan.camp](https://openvan.camp/en/license-plates/slovenia)

---

### BUG-15 — PT side strip is wrong
**Entry:** `PT` (Portugal)  
**Field:** `strip_contents`  
**Current value:** `"None"`  
Portugal has a blue EU band with the country code "P" on the left side. Only the yellow date band on the right was removed in 2020. The side strip is not "None".  
**Source:** [Wikipedia](https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Portugal)

---

### BUG-16 — DE format pattern contradicts its own explanation
**Entry:** `DE` (Germany)  
**Fields:** `format_pattern`, `format_explanation`  
**Current value:** `"AA-AA-0000"`  
The explanation correctly states the format uses 1–3 letters for the area code, 1–2 letters, and 1–4 digits — but the pattern shows a fixed `AA-AA-0000` with a dash after the area code that doesn't exist on real plates. The pattern should reflect the variable-length reality.

---

### BUG-17 — SK explanation is outdated
**Entry:** `SK` (Slovakia)  
**Field:** `format_explanation`  
**Current value:** describes a "two-letter district code"  
Slovakia moved to a state-wide (non-regional) numbering scheme in January 2023. The district code system is no longer used for new registrations.  
**Source:** [Wikipedia mirror](https://wiki.krisyotam.com/content/wikipedia_en_all_nopic_2026-03/Slovak_car_registration_plates)

---

### BUG-18 — LT explanation contradicts the format pattern
**Entry:** `LT` (Lithuania)  
**Field:** `format_explanation`  
**Pattern:** `"AAA 000"`  
The explanation states there is "no space between" the letters and numbers, directly contradicting the pattern which has a space. One of the two is wrong.

---

### BUG-19 — Vanity plate prices quoted in obsolete currencies
**Entries:** `LV` (Latvia), `HR` (Croatia), `BG` (Bulgaria)  
**Field:** `vanity_plates`  
- `LV` quotes a price in Latvian lats (LVL) — Latvia adopted the euro in 2014  
- `HR` quotes a price in Croatian kuna — Croatia adopted the euro in 2023  
- `BG` quotes a price in Bulgarian lev (BGN) — Bulgaria adopted the euro on 1 January 2026  

All three prices should be converted to euros with an approximate current value.

---

### BUG-20 — EE vanity plates incorrectly marked as unavailable
**Entry:** `EE` (Estonia)  
**Field:** `vanity_plates`  
**Current value:** `"Not available"`  
The Estonian Transport Administration sells chosen plate numbers for €300. Personalized plates exist and are available.  
**Source:** [Estonian Transport Administration fee list](https://dokumendiregistrid.karlerss.com/dokumendid/363938/kiri)

---

### BUG-21 — IE format pattern doesn't match the real format
**Entry:** `IE` (Ireland)  
**Field:** `format_pattern`  
**Current value:** `"000-AA-000000"`  
The real format is variable: the year part is 2 or 3 digits (e.g. `13` or `131`), the county code is 1 or 2 letters, and the sequence is 1–6 digits. The fixed pattern overstates precision.

---

### BUG-22 — FI dimensions are in the wrong order
**Entry:** `FI` (Finland)  
**Field:** `dimensions`  
**Current value:** `"118 × 442 mm or 200 × 256 mm"`  
Every other entry uses width × height. Finland's entry appears to use height × width (118 mm tall, 442 mm wide is the standard European plate). Should be `"442 × 118 mm or 256 × 200 mm"` to be consistent.

---

### BUG-23 — MK side strip incorrectly says "EU band"
**Entry:** `MK` (North Macedonia)  
**Field:** `colors_strip`, `strip_contents`  
**Current value:** `"Blue EU band"`  
North Macedonia is not an EU member. The strip is a national blue band with the country code `NMK`, not an EU identifier.

---

### BUG-24 — Alphabet rules placed in the wrong field for multiple countries
**Entries:** `AT`, `GB`, `RS`, `RO`, `PL` (confirmed); likely others  
**Field:** `forbidden_combinations`  
These entries contain rules about which letters are excluded from the alphabet (e.g. AT: "The letter Q is excluded from all sequences"), not actual banned plate combinations. Alphabet restrictions belong in the `alphabet` field. The `forbidden_combinations` field should contain only specific banned sequences (e.g. `SS`, `NS`, `KZ`).

---

### BUG-25 — DE missing well-known forbidden combinations
**Entry:** `DE` (Germany)  
**Field:** `forbidden_combinations`  
**Current value:** `null`  
Germany has well-documented banned combinations due to Nazi associations: `NS`, `SS`, `SA`, `KZ`, `HJ` and several regional variants. The field should not be null.

---

### BUG-26 — FR forbidden combinations field mixes two separate concerns
**Entry:** `FR` (France)  
**Field:** `forbidden_combinations`  
The entry conflates alphabet exclusions (I, O, U not used) with genuinely banned combinations (`SS`, `WW`), and then muddies it further by referencing superseded rules from an older system. These should be separated: excluded letters to `alphabet`, banned combinations to `forbidden_combinations`.

---

## Incomplete Data (gaps, not bugs)

### GAP-01 — 35 of 44 countries have `typeface: "Unknown"` which renders in the panel
The `typeface` field contains the string `"Unknown"` for 35 countries. Because `"Unknown"` passes `isVal()`, it currently renders as actual data in the panel. Once BUG-C1 is fixed (adding "Unknown" to `isVal()`'s exclusion list), these fields will be correctly hidden. Top priority to fill in: `NL` (Kenteken font), `GB` (Charles Wright), `FR`, `DE`, `IT`.

### GAP-02 — 8 countries have `vanity_plates: "Unknown"` which renders in the panel
`AD`, `AL`, `AM`, `BA`, `BY`, `CY`, `DE`, `MD` — same issue as GAP-01. Will be hidden once BUG-C1 is fixed.

---

## Unreachable Assets

### NOTE-01 — 17 plate images in `plateMap` have no SVG country
These ISOs have images stored and referenced in `plateMap` but have no matching `<path id="...">` in the SVG, so they can never be opened via the map. They represent territories, dependencies, and unrecognized states not drawn on the SVG:  
`ABH`, `AX`, `AZ`, `FO`, `GBA`, `GBG`, `GBJ`, `GBM`, `GBZ`, `MC`, `MT`, `PMR`, `RSO`, `RU`, `SM`, `TRNC`, `VA`  
Not a bug per se, but the images and format data for these are sitting unused.
