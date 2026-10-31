# PlateLab Audit & Growth Plan

Oct 30, 2026 · @Andrei

## Summary

PlateLab's core loop works and feels good, but the data can't be trusted yet, and that is the first thing to fix before investing in growth. The dataset was machine-extracted from Wikipedia by gpt-4o-mini on 15 Feb 2026 (the JSON says so) and never reviewed. The renderer also presents missing data as facts.

What I tested: the live site on desktop and a 375 px phone viewport, light and dark mode, all 44 country panels, the full `plate_formats.json`, every plate image, the page source and the network traffic. Data claims were spot-checked against Wikipedia, national transport agencies and plate reference sites.

The five things that matter most:

1. **"Unknown" and missing values are shown as data.** Typeface reads "Unknown" for 35 of 44 countries, and an empty forbidden-combinations field is printed as "None" for 29 countries, which states something false.
2. **Several headline formats are wrong or contradict the site itself.** Slovenia's pattern doesn't match its own plate image, the Netherlands shows a superseded sidecode, Germany's pattern contradicts its own explanation, and Portugal is listed with no EU strip.
3. **Stale facts.** Prices are quoted in kuna, lats and lev, three currencies replaced by the euro.
4. **The basics for sharing and discovery are missing:** no meta description, no preview image, no favicon, no robots.txt or sitemap, no per-country URLs.
5. **There is nothing to come back for yet.** The second tab (Workbench) is an empty placeholder, and there is no game, search, or account.

Recommended order: fix the renderer and the top-traffic countries' data (week 1–2), ship the sharing and SEO basics (week 2), then add a daily quiz and per-country pages before trying any monetization.

## Bugs and UX issues

I found 20 issues on the live site; the top three distort what users read, the rest are interaction, accessibility and polish problems. Each was reproduced in the browser or confirmed in the page source.

| # | Issue | Where / evidence | Severity | Fix |
| --- | --- | --- | --- | --- |
| 1 | "Unknown" and "Not available" render as real values | `isVal()` only filters null, "null" and "". Typeface shows "Unknown" for 35 countries, vanity plates for 8 | High | Treat "Unknown" as empty and hide the field |
| 2 | Missing forbidden combinations print "None" | `buildPanelHTML` falls back to the literal "None" for 29 countries (e.g. Moldova, Germany) | High | Hide the section, or say "No data yet" |
| 3 | Prices and years are styled as plate codes | `tagCodes()` regex wraps any 3–4 digit number: Croatia "270", Sweden "6900" and "570", Latvia "2006" | High | Only chip tokens from a whitelist of example codes, or mark them up in the data |
| 4 | Mixed tokens not chipped | Sweden: "AAA" is chipped, "00A" is not | Low | Allow mixed letter/digit tokens |
| 5 | Escape doesn't close the panel | No `keydown` listener in the script | Medium | Close on Escape, return focus to the map |
| 6 | Map not usable by keyboard or screen reader | Country paths have no `tabindex`, role or label; close button is a bare "×" with no `aria-label` | Medium | Add `tabindex="0"`, `role="button"`, `aria-label` per country; label the close button |
| 7 | Page zoom is blocked | Viewport meta has `maximum-scale=1.0, user-scalable=no` | Medium | Remove both (WCAG 1.4.4) |
| 8 | Map moves under the pointer | Opening a panel re-centres and zooms the map (`centerOnCountry`); closing animates back. Twice in testing, a click landed on Serbia instead of the intended country | Medium | Ignore clicks during the animation, or don't zoom when the country is already visible |
| 9 | Portugal exists twice in the map | 45 shapes for 44 countries; two paths share `id="PT"`. `getElementById` only returns the first, so highlighting and centring can miss the other | Medium | Merge into one path or use a group with one id |
| 10 | Flag emoji in "Learn more about …" button | Built from the ISO code. Windows shows letters ("MD"), and Kosovo (XK) has no flag emoji anywhere | Low | Use small SVG flags, or drop the flag |
| 11 | Plate images are heavy | Rasters up to 772 KB for a \~400 px preview: MK 772, LU 744, CH 653, LI 601, SI 543, SE 533, XK 530, GB 457, IS 403 KB. About 6.5 MB if a user hovers everything | Medium | Convert to 800 px WebP/AVIF (\~30–60 KB each), lazy-load |
| 12 | Inconsistent image style | Most are flat illustrations; Sweden, Switzerland and others are angled photos | Low | Standardise on flat, front-on images |
| 13 | Workbench tab is empty | Only "Plate customization coming soon..." | Medium | Hide it, or turn it into a teaser with a waitlist |
| 14 | Low-contrast map | Dark grey countries on near-black; small countries (LI, AD, LU) are hard to hit | Medium | Raise contrast, add a hover outline, add a country search/list |
| 15 | Awkward fit on tall screens | On a portrait desktop pane the map uses about half the width and Turkey is clipped on the right | Low | Fit the viewBox to the container's aspect ratio |
| 16 | Title says "Worldwide" | Only 44 European countries are covered | Medium | "Explore European license plates" until other regions ship |
| 17 | No favicon | `/favicon.ico` returns 404 | Low | Add icon set and web manifest |
| 18 | Default Vercel 404 | Any wrong URL shows plain-text "NOT\_FOUND" | Low | Branded 404 with a link back to the map |
| 19 | Data injected as raw HTML | Panel HTML is built with template strings and `innerHTML`, unescaped | Low now | Escape values before community edits or user input arrive |
| 20 | Pattern box handles alternates inconsistently | Armenia and Sweden list two lines; the Netherlands (7 formats in use) shows one | Low | Support a list of patterns with labels ("cars", "since 2024") |

What works well and should be kept: the hover preview with a real plate image, the clean monospace look, persistent light/dark mode and accent colour, touch pan and pinch-zoom on phones, and fast load (a single 125 KB HTML file, page ready in under 50 ms on a warm cache).

## Data audit

Roughly a third of the 44 entries have at least one wrong, outdated or self-contradicting field, and most have gaps. The cause is systemic: `plate_formats.json` was generated by gpt-4o-mini from Wikipedia on 15 Feb 2026, with no human review, so extraction errors and Wikipedia's own stale passages both pass straight through.

### Systemic problems

| Problem | Scale | Example | Fix |
| --- | --- | --- | --- |
| One pattern for variable formats | DE, PL, BG, IE, HR, NL, SI | Germany shows `AA-AA-0000`; its own explanation says 1–3 letters, 1–2 letters, 1–4 digits | Allow ranges (`A{1,3}-A{1,2} 0{1,4}`) or several labelled patterns |
| Missing values | Typeface missing for 35, forbidden list for 29, vanity for 8 | Netherlands typeface "Unknown" (it's the well-documented Kenteken font) | Research top-traffic countries by hand; hide the rest |
| Fields mixed up | Forbidden field holds alphabet rules for AT, BG, CZ, GB, PL, RO, RS | Austria: "forbidden" = "The letter Q is excluded" | Separate `excluded_letters` from `banned_combinations` |
| Outdated currencies | 3 countries | Croatia in kuna, Latvia in lats, Bulgaria in lev | Convert to euro, add an `as_of` date to every price |
| "Year introduced" means different things | Most entries | Germany 1956 (system), Liechtenstein 1924, Netherlands 2021 (latest design) | Split into `system_since` and `current_design_since` |
| Filler explanations | NL, EE, GE and others | NL: "typically follows a structure of letters and numbers in two parts" | Rewrite by hand: what each block means |
| Inconsistent units | Finland | "118 × 442 mm" is height × width; every other entry is width × height | Normalise to width × height |
| No sources per field | All | Only the Wikipedia article is linked | Store a source URL and a `verified_at` date per country |

### Country-by-country findings

**Confirmed** means checked against a source, the site's own plate image, or an internal contradiction. **Verify** means likely wrong from my knowledge, but check before editing.

| Country | Field | What the site says | Problem | Status |
| --- | --- | --- | --- | --- |
| Netherlands | Format | `A-000-AA`, introduced 2021 | Superseded. New cars have been issued `AAA-00-A` (sidecode 11) since 4 June 2024 ([Alpina](https://www.alpina.nl/en/car-insurance/registration-mark/last-license-plate/)); Wikipedia lists 7 formats in use ([Wikipedia](https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_the_Netherlands)) | Confirmed |
| Netherlands | Explanation | Generic filler sentence | Should explain sidecodes: format changes when a series runs out | Confirmed |
| Netherlands | Alphabet | Vowels restricted "to avoid profane language" | Vowels aren't used at all; reasoning overstated | Verify |
| Netherlands | Typeface | Unknown | Kenteken font | Verify |
| Slovenia | Format | `AA-0000-AA` | Contradicts the site's own image (LJ 898-KP). Real format: region code, municipal crest, then 5 characters with a dash, e.g. LJ 60-CFB ([openvan.camp](https://openvan.camp/en/license-plates/slovenia)) | Confirmed |
| Portugal | Side strip | None | Blue EU band with "P" on the left; only the yellow date band on the right was dropped in 2020 ([Wikipedia](https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Portugal)) | Confirmed |
| Germany | Format | `AA-AA-0000` | Contradicts its own explanation; real plates have no dash after the area code | Confirmed |
| Germany | Forbidden | None (null) | Well-known bans: NS, SS, SA, KZ, HJ and regional variants | Verify |
| Germany | Vanity | Unknown | Custom plates (Wunschkennzeichen) are widely available for a small fee | Verify |
| Slovakia | Explanation | "two-letter district code" | Slovakia moved to a state-wide numbering scheme in January 2023, no longer regional ([Wikipedia mirror](https://wiki.krisyotam.com/content/wikipedia_en_all_nopic_2026-03/Slovak_car_registration_plates)) | Confirmed |
| Czechia | Format | `0AA 0000`, "digit and two letters = region" | Real format is digit, region letter, letter-or-digit, 4 digits (e.g. 1A2 3456); only the letter marks the region. Name should be "Czechia" | Verify |
| Lithuania | Explanation | "no space between them" | Contradicts the pattern `AAA 000`, which has a space | Confirmed |
| Latvia | Typeface | "Austria" | Not a typeface; extraction error | Confirmed |
| Latvia | Vanity | Price in lats (LVL), "since 2006" | Latvia uses the euro since 2014 | Confirmed |
| Croatia | Vanity | 2,000 kuna | Croatia uses the euro since 2023 | Confirmed |
| Bulgaria | Vanity | BGN 7,000 | Bulgaria adopted the euro on 1 Jan 2026 | Verify |
| Bulgaria | Format | `AA 0000 AA` | Province code is 1 or 2 letters (Sofia is CA, Burgas is A) | Confirmed |
| Austria | Forbidden | "The letter Q is excluded" | Alphabet rule in the wrong field | Confirmed |
| Estonia | Vanity | Not available | The Transport Administration sells chosen plates for €300 ([fee list](https://dokumendiregistrid.karlerss.com/dokumendid/363938/kiri)); personalised plates also exist | Verify |
| Estonia | Explanation | Numbers "denote the registration number" | Circular; no real information | Confirmed |
| Ireland | Format | `000-AA-000000` | Year is 2 or 3 digits, county 1 or 2 letters, sequence 1–6 digits | Confirmed |
| France | Forbidden | "KK, PD, PQ, QQ, WC may have been avoided... but are included now" | Muddled sentence; also mixes in the I/O/U alphabet rule | Confirmed |
| France | Side strip | Lists the right-hand region band | That's a separate band, not the side strip | Confirmed |
| United Kingdom | Side strip | None | UK identifier (optionally with Union flag) has been allowed since 2021 | Verify |
| United Kingdom | Forbidden | "I, Q, Z" | Alphabet rule in the wrong field | Confirmed |
| Finland | Dimensions | 118 × 442 mm | Matches Wikipedia, but in height × width order unlike everyone else | Confirmed |
| Armenia | Side strip | "Silver identifier band on the right side of the flag and code" | Garbled sentence | Confirmed |
| Albania | Strip contents | "Year of registration and regional code" | Regional codes were dropped with the 2011 format | Verify |
| Georgia | Explanation | First letters are region or vehicle type | Georgian serials are not regional | Verify |
| North Macedonia | Side strip | "Blue EU band" | Not an EU member; it's a national blue band with NMK | Verify |
| Kosovo | Alphabet | "letters A to Q" | Unclear and likely wrong | Verify |
| Liechtenstein | Vanity | "CHF 500, only through online auctions" | Source unclear | Verify |
| Montenegro | Vanity | "any letter-number combination" | Overstated; rules apply | Verify |
| Belarus | Alphabet | 11 listed letters | List looks incomplete (no M) | Verify |
| Serbia, Romania, Poland | Forbidden | Alphabet rules | Wrong field | Confirmed |

Checked and fine, contrary to my first impression: Iceland (`AAA 00` in Helvetica Neue is current), Sweden (last digit still sets the tax month), Slovenia's 520 × 120 mm size.

## Coverage gaps

The site covers 44 European countries while its title promises the world. The map and the dataset contain exactly the same set, so the missing places can't even be clicked.

| Group | Missing | Note |
| --- | --- | --- |
| Sovereign states in Europe | Malta, Monaco, San Marino, Vatican City, Azerbaijan, Russia | Microstates need a zoomed inset or a list, they're too small for the map. Russia's omission may be deliberate; if so, say so |
| Transcontinental | Kazakhstan | Optional |
| Territories with their own plates | Åland, Faroe Islands, Gibraltar, Jersey, Guernsey, Isle of Man | Plate collectors care about these a lot; Åland ("ÅL") is a favourite |
| Disputed / unrecognised | Northern Cyprus, Transnistria, Abkhazia | Sensitive; label neutrally if added |
| Other regions | Everything outside Europe | The title says "Worldwide" |

Short term, change the title and meta to "European license plates". Long term, the US states and Canadian provinces are the biggest audience for plate content, followed by Japan and Australia.

## Quick wins

These 32 items each take under a day, most under an hour, and together fix trust, sharing and accessibility. They're sorted by impact within each group.

### Data display (do first)

- [ ] Hide any field whose value is "Unknown", "Not available", null or empty
- [ ] Replace the "None" fallback for forbidden combinations with hiding the section
- [ ] Restrict `tagCodes()` so prices, years and percentages are never styled as plate codes
- [ ] Show a small "Data last checked: \<date>" line and a "Report an error" link in every panel
- [ ] Label each panel "Passenger cars" so readers know which plate type is shown

### Data content

- [ ] Fix the confirmed errors in the Data audit table (about 25 field edits)
- [ ] Hand-check the 10 countries most visitors will open first: NL, DE, GB, FR, IT, ES, BE, PL, SE, NO
- [ ] Convert kuna, lats and lev prices to euro
- [ ] Move alphabet rules out of the forbidden-combinations field
- [ ] Rename "Czech Republic" to "Czechia"

### Interaction and accessibility

- [ ] Close the panel with Escape and return focus to the country
- [ ] Make countries focusable with Tab and openable with Enter, each with an `aria-label`
- [ ] Add `aria-label="Close"` to the × button and trap focus inside the open panel
- [ ] Remove `maximum-scale=1.0, user-scalable=no` from the viewport tag
- [ ] Ignore clicks while the map is animating
- [ ] Merge the duplicate Portugal path
- [ ] Add a country search box (type "lie" → Liechtenstein) and an A–Z list for microstates
- [ ] Raise map contrast and add a visible hover outline
- [ ] Hide the Workbench tab, or replace it with a teaser and an email signup

### Sharing and SEO

- [ ] Add a meta description and Open Graph / Twitter card tags with a preview image (a grid of plates)
- [ ] Add a favicon, apple-touch-icon and web manifest
- [ ] Add one `<h1>` ("European license plates, country by country")
- [ ] Change the title from "Worldwide" to "Europe"
- [ ] Give every country its own URL (`/nl` or at least `#nl`) and update the URL when a panel opens
- [ ] Add robots.txt and sitemap.xml once country URLs exist
- [ ] Add a branded 404 page

### Performance

- [ ] Convert plate images to 800 px WebP or AVIF; the nine largest files total about 5 MB
- [ ] Lazy-load images on first hover instead of preloading
- [ ] Use small SVG flags instead of emoji flags (fixes Windows and Kosovo)

### Trust, legal and measurement

- [ ] Credit Wikimedia Commons image authors and licences (many plate images are CC BY-SA, which requires attribution)
- [ ] Add an About page: who made it, where the data comes from, how to suggest fixes
- [ ] Add privacy-friendly analytics (Vercel Analytics, Plausible or Umami); there is none today, so you can't see which countries people open

## Stickiness ideas

The strongest bet is a daily plate-guessing game: it gives people a reason to return every day, it's shareable, and it reuses the data and images you already have. Reference content alone won't hold people; [openvan.camp](https://openvan.camp/en/license-plates/slovenia) already offers formats, region codes and a plate generator, and [licenseplatemania.com](https://licenseplatemania.com/landenpaginas/portugal.htm) and Olav's Plates have decades of collector depth. PlateLab's edge is the interactive map and a modern, playful feel, so lean into play.

### Games (the return-visit engine)

1. **Daily plate ("Plateldle")**: one plate a day, guess the country in up to 6 tries, with hints that reveal the strip, the colours, then a region code. Wordle-style shareable result grid, streaks stored locally.
2. **Region code challenge**: "Which city is MB?" (Maribor), "Where is HH?" (Hamburg). Germany alone has 400+ codes; this is endless content.
3. **Timed map quiz**: plate appears, click the country on the map. Leaderboard per week.
4. **Odd one out**: four plates, one is fake or from a different country.
5. **Difficulty tiers**: easy (EU countries by strip code), hard (non-EU, special plates, old formats), expert (region codes).
6. **GeoGuessr training mode**: GeoGuessr players actively study plates ("plate meta"); a focused trainer with blurred, partial or distant plates speaks directly to them.

### Tools people bookmark

7. **Plate decoder**: type `RA KL 8136` or upload a photo, get "Germany, Rastatt district" with confidence and explanation.
8. **Region code lookup**: per-country searchable tables (DE, AT, PL, CZ, HR, RS, SI, BG, RO, NO, GB memory tags, IE counties).
9. **Compare mode**: two to four countries side by side: format, colours, size, strip, typeface.
10. **History timeline**: a slider per country showing how plates changed (the Netherlands' sidecodes 1–13 are a great showcase).
11. **Special plates gallery**: diplomatic, military, taxi, export, historic, temporary, by country.
12. **Road-trip companion**: "plates you'll see on the A2 to Italy", plate bingo cards for kids, a printable "spot the country" sheet.

### Collection and community

13. **Spotter log**: tick off countries and regions you've seen in real life; a map fills in as your collection grows. Badges for 10, 25, all 44.
14. **Photo submissions**: users upload spotted plates (with plates blurred or partially masked for privacy) to build a better image library.
15. **Suggest an edit** on every field, reviewed before publishing. Turns data errors into engagement.
16. **Weekly "Plate of the week" email or X post**: one interesting plate fact. Feeds social and the newsletter list.

### Workbench (the creative hook)

17. **Plate maker for fun formats**: design a plate in any country's style for a name, team or wedding date, download as PNG or wallpaper. Must be clearly a novelty: fake country strips or a "NOT A REAL PLATE" mark, no exact real registration layouts that could be printed and fitted to a car.
18. **Shareable creations gallery**: "Most liked this week".

### Distribution features

19. **Per-country landing pages** (`/germany-license-plates`) with the full data, region table and quiz link. This is where search traffic comes from.
20. **Embeddable widget** for travel blogs: "What do plates in Croatia look like?"
21. **Open dataset on GitHub** with a clear licence. Earns links from developers, collectors and Wikipedia editors.
22. **Localisation**: Dutch, German, Polish first; people search plate questions in their own language.

## Revenue

Revenue should follow audience, so the order is: build a returning audience with the quiz and country pages, then add merch and affiliate links, then test a small paid tier and B2B data. Display ads alone on a niche reference site rarely earn more than pocket money; the bigger opportunities are products people would buy anyway and data businesses need.

### Options, ranked by fit

| # | Model | How it works for PlateLab | Fit | Needs | When |
| --- | --- | --- | --- | --- | --- |
| 1 | Merch and prints | "License plates of Europe" posters, a plate-style name sign, stickers, mugs, a quiz card deck. Print-on-demand (Printful, Gelato), no stock | High: visual, giftable, on-brand | Good images you own the rights to (redraw them, don't sell Wikimedia images) | Month 2 |
| 2 | Travel affiliate | Country pages and road-trip guides link to toll vignettes (AT, CH, CZ, SK, HU, SI, BG, RO), car rental, eSIMs, and cross-border driving rules | High: matches "driving to Croatia" intent | Country pages with real traffic | Month 2–3 |
| 3 | Premium game pass | Ad-free, unlimited practice, expert packs (region codes, old formats), stats, GeoGuessr trainer. A few euros a month or a one-off unlock | Medium–high if the game takes off | A game people play daily first | Month 3+ |
| 4 | API and data licensing | Clean, verified plate formats, regex validators and region-code tables as JSON/API. Buyers: car rental and fleet software, parking and toll operators, insurers, marketplaces validating listings, games | High value per customer, low volume | Verified data with sources and update dates | Month 4+ |
| 5 | Sponsorships | Plate manufacturers, private-plate dealers, driving schools, car-import services, GeoGuessr content creators sponsor a country page or the daily quiz | Medium | Audience numbers to show | When traffic is meaningful |
| 6 | Education packs | Printable geography worksheets and classroom quiz mode for schools and road-trip families | Medium | The quiz | Month 3+ |
| 7 | Private plate affiliate (UK first) | UK personalised plates are a large market; link to registered dealers from a "what does my plate say" tool | Medium, UK only | UK content depth | Later |
| 8 | Display ads | Carbon Ads or a privacy-friendly network on reference pages, never on the game | Low | Large traffic | Last, optional |
| 9 | Donations | Ko-fi / Buy Me a Coffee in the footer | Low but zero effort | Nothing | Now |

### Guardrails

- **No road-usable plates.** Selling or generating exact replicas of real registration layouts helps plate cloning and is illegal to fit in most countries. Keep the plate maker clearly novelty (fake strips, "NOT A REAL PLATE" mark, or non-standard sizes) and don't sell physical plates in official formats.
- **Image rights.** Wikimedia images can't simply be resold. Redraw plates as your own SVGs; that also fixes the inconsistent style and the image weight.
- **Data claims.** If you sell data, every field needs a source and a verified date; the current dataset is not sellable as is.
- **Privacy.** Any user photo of a real plate is personal data in the EU. Blur or crop the serial before publishing, or only accept the country strip.

### What to measure

- Daily active players and 7-day return rate for the quiz
- Share rate of quiz results
- Country panels opened per visit, top 10 countries
- Search impressions and clicks per country page
- Newsletter signups, merch conversion, affiliate clicks

## Roadmap

The 90 days split into three phases, and each one only starts when the previous gate is met; revenue experiments come last because they need trustworthy data and returning visitors.

&#91;embedded content: 90-day roadmap · 3 phases, 2 gates\]

Phase 1 is almost entirely the Quick wins list above. If the quiz doesn't bring people back by the end of phase 2, try the region-code challenge or the GeoGuessr trainer before moving to revenue.

## Sources

- [Vehicle registration plates of the Netherlands (Wikipedia)](https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_the_Netherlands)
- [Last license plate issued, sidecode 11 since June 2024 (Alpina)](https://www.alpina.nl/en/car-insurance/registration-mark/last-license-plate/)
- [Vehicle registration plates of Portugal (Wikipedia)](https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Portugal)
- [Vehicle registration plates of Finland (Wikipedia)](https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Finland)
- [Vehicle registration plates of Slovenia (Wikipedia)](https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Slovenia)
- [Slovenia license plates (openvan.camp)](https://openvan.camp/en/license-plates/slovenia)
- [Vehicle registration plates of Slovakia (Wikipedia mirror, 2026)](https://wiki.krisyotam.com/content/wikipedia_en_all_nopic_2026-03/Slovak_car_registration_plates)
- [Vehicle registration plates of Iceland (Wikipedia)](https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Iceland)
- [Vehicle tax payment month (Swedish Transport Agency)](https://transportstyrelsen.se/en/road/vehicles/taxes-and-fees/vehicle-tax)
- [Estonian Transport Administration fee list](https://dokumendiregistrid.karlerss.com/dokumendid/363938/kiri)
- [Portugal plates reference (licenseplatemania.com)](https://licenseplatemania.com/landenpaginas/portugal.htm)
- Live site and dataset: [platelab.vercel.app](https://platelab.vercel.app), `/dataset/metadata/plate_formats.json`, tested 30 Oct 2026
