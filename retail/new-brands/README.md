# New JDM brands (16 Nov 2026)

**Source:** Keith Lynam (JDM, key account manager), email "JDM Brand Suggestions", 16 Nov, with three spreadsheets (saved here). Photos and spec sheets are in JDM's Dropbox; dropbox.com is not reachable from the cloud session.

## Created as DRAFT

There are 35 products with 38 variants. They are not visible to customers yet.

- **BLUETTI**: 13 products
  - power stations: AC50P, AC70P, AC180P, AC200PL, Apex 300, Elite 320, Premium 30/100/200 V2
  - B300K expansion battery
  - SORA 60/130/220W solar panels
  - Collections: `portable-power-stations` or `solar-panels`, plus the new `bluetti`.
- **Easypix**: 12 products
  - Aquapix W3027 (2 colours) and W3048-I Edge (2 colours)
  - Birdycam, Mini Pro XS1, V64 Flip, V48 Pocket
  - GoXtreme Enduro, Reef (yellow), Vision Duo, GS1 gimbal, Floating Grip
  - Collections: the new `easypix`, and `action-cameras` for Aquapix and GoXtreme.
  - Skipped: GoXtreme Reef Blue and GX4 Gimbal, both marked EOL in the sheet.
- **PocketBook**: 11 products
  - Verse Lite, Verse, Verse Pro, Verse Pro Color, Era Color, Era Lite
  - InkPad One, InkPad Color 3, InkPad Eo
  - Verse shell cover (black, flower print) and Era flip cover
  - Collections: the new `e-readers` and `pocketbook`.

## Setup, the same as the other JDM products

- tag "JDM Products"
- SKU = JDM code, barcode = EAN
- inventory tracked, don't sell when out of stock
- price = RRP from the sheet; unit cost = JDM price

## To go live

1. Add photos: the Dropbox folders hold the images; Matteo uploads them, or allows access.
2. Set the products to Active.
3. Make the 4 new collections visible on the Online Store.
4. Add "E-Readers" to the Electronics menu.

## 16 Nov, later

- **Prices:** Matteo keeps the suggested RRP for now; to be discussed later.
- **Matteo re-uploaded the 3 spreadsheets:** identical to the email ones (same checksums), with no photos inside.
- **Photos:** www.dropbox.com and dl.dropboxusercontent.com were added to the environment's allowed hosts. The Dropbox folder download was then blocked by the session's permission check, so no photos yet.
- **JDM EOL list of 15 Nov, archived:**
  - Garmin HRM-Fit (was ACTIVE); redirect `/products/garmin-hrm-fit` → `/collections/heart-rate-monitors`.
  - Igloohome Smart Padlock (was DRAFT).
  - Not in the shop: Knaap AMS01 Space Grey/Matt Black (the Knaap V2 RTD is a different model and stays).
  - Not in the shop: Shokz OpenRun Grey (from the 8 Nov list).

## 16 Nov: completed and live

Matteo: "make sure you have description, picture, SKU, barcode, everything", sourced from the official brand websites.

**Sources** (each host was added to the environment allowlist):
- **BLUETTI:** bluettipower.eu product pages. Images come from checkout.bluettipower.eu/cdn and cdn.shopify.com.
- **PocketBook:** pocketbook.ch catalog. Images from /uploads/.
- **Easypix, Aquapix, GoXtreme:** easypix.com product pages. Images are /media/image/... and named after JDM's product codes.

**What every product has now:**
- an English description written from the official specs: intro, key features and specifications
- 1–7 official photos, each with alt text
- SKU, barcode and cost, as before

**Title fixes:** "Easypix V64 Flip Camera" and "Easypix V48 Pocket Camera" (they were listed as camcorders; the handles are unchanged).

**Now ACTIVE and published to the Online Store:**
- 32 products
- the 4 collections: e-readers, bluetti, easypix and pocketbook

**Still DRAFT:** BLUETTI SORA 60/130/220W panels. They are not on bluettipower.eu; the official page is cl.bluettipower.com, which the session's permission check blocked.

**Stock:** every variant is at 0, so the products show "Sold out" until the JDM stock sync picks up the new SKUs.

**Menu:** "E-Readers" has not been added to the Electronics menu yet.
