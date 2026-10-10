#!/usr/bin/env python3
"""Import *商品.xlsx into js/products.js (prepend new finds) and fetch thumbs."""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

import openpyxl
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "img" / "products"
JS = ROOT / "js" / "products.js"
CACHE = ROOT / "scripts" / "pic_urls.json"
WORKERS = 6
UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://weidian.com/",
}

TAG_CAT = {
    "shoes": "shoes",
    "slides": "shoes",
    "sneakers": "shoes",
    "shorts": "pants",
    "pants": "pants",
    "jeans": "pants",
    "t-shirt": "t-shirts",
    "tshirt": "t-shirts",
    "tee": "t-shirts",
    "hoodies": "hoodies",
    "hoodie": "hoodies",
    "sweater": "hoodies",
    "jacket": "jackets",
    "vest": "jackets",
    "coat": "jackets",
    "cap": "headwear",
    "hat": "headwear",
    "beanie": "headwear",
    "suit": "sets",
    "set": "sets",
    "tracksuit": "sets",
    "jersey": "jersey",
    "sunglasses": "glasses",
    "glasses": "glasses",
    "bag": "accessories",
    "belt": "accessories",
    "wallet": "accessories",
    "accessories": "accessories",
    "watch": "watches",
    "electronics": "other",
    "apple": "other",
    "airpods": "other",
    "dress": "other",
    "underwear": "underwear",
}
CAT_SKIP_BRAND = set(TAG_CAT) | {"top trending", "trending", "new", "hot"}


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower())
    s = re.sub(r"^-+|-+$", "", s)
    s = re.sub(r"-+", "-", s)
    return s[:60]


def guess_cat(tags: list[str], title: str) -> str:
    t = (title or "").lower()
    tag_l = [x.lower().strip() for x in tags]
    if re.search(r"\b(lego|bricks?)\b", t):
        return "bricks"
    if re.search(r"\b(sunglasses?|eyewear)\b", t) or "sunglasses" in tag_l:
        return "glasses"
    if re.search(r"\b(watch(?:es)?|rolex)\b", t) or "watch" in tag_l:
        return "watches"
    if re.search(r"\b(perfume|cologne)\b", t):
        return "perfume"
    if any(k in t for k in ("shoe", "sneaker", "slide", "slipper", "jordan")) or "shoes" in tag_l or "slides" in tag_l:
        return "shoes"
    if any(k in t for k in ("jersey", "football")) or "jersey" in tag_l:
        return "jersey"
    if any(k in t for k in ("hoodie", "sweater")) or "hoodies" in tag_l:
        return "hoodies"
    if any(k in t for k in ("cap", "hat", "beanie")) or "cap" in tag_l:
        return "headwear"
    if "suit" in tag_l or re.search(r"\b(tracksuit|suit|set)\b", t):
        return "sets"
    if any(k in t for k in ("jacket", "coat", "vest", "bomber")) or "jacket" in tag_l or "vest" in tag_l:
        return "jackets"
    if any(k in t for k in ("short", "pant", "jean")) or any(x in tag_l for x in ("shorts", "pants", "jeans")):
        return "pants"
    if any(k in t for k in ("tee", "t-shirt", "shirt", "polo")) or "t-shirt" in tag_l:
        return "t-shirts"
    if any(x in tag_l for x in ("bag", "belt", "wallet", "accessories")) or any(k in t for k in ("bag", "wallet", "belt")):
        return "accessories"
    if any(x in tag_l for x in ("electronics", "apple", "airpods")):
        return "other"
    for tag in tag_l:
        if tag in TAG_CAT:
            return TAG_CAT[tag]
    return "other"


def brand_from(tags: list[str], title: str) -> str:
    for tag in tags:
        if tag.lower().strip() not in CAT_SKIP_BRAND:
            return tag.strip()
    parts = re.split(r"\s+", (title or "").strip())
    return parts[0] if parts else "Find"


def load_xlsx(path: Path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    items = []
    seen = set()
    batch = path.stem
    for r in rows[1:]:
        if not r or not r[1]:
            continue
        title = str(r[0] or "Find").strip()
        url = str(r[1]).strip()
        tags = [t.strip() for t in str(r[2] or "").replace("\n", ",").split(",") if t.strip()]
        m = re.search(r"itemID=(\d+)", url, re.I)
        if not m:
            continue
        iid = m.group(1)
        if iid in seen:
            continue
        seen.add(iid)
        items.append(
            {
                "itemId": iid,
                "title": title[:80],
                "url": f"https://weidian.com/item.html?itemID={iid}",
                "tags": tags,
                "category": guess_cat(tags, title),
                "brand": brand_from(tags, title),
                "batch": batch,
            }
        )
    return items


def load_catalog():
    raw = JS.read_text(encoding="utf-8")
    start = raw.index("SK.catalog = ") + len("SK.catalog = ")
    catalog, _ = json.JSONDecoder().raw_decode(raw[start:])
    return catalog


def write_catalog(catalog: dict):
    JS.write_text(
        "window.SK = window.SK || {};\nSK.catalog = "
        + json.dumps(catalog, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def load_cache():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def save_cache(cache):
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")


def local_path(item_id: str):
    dest = OUT / f"{item_id}.webp"
    if dest.exists() and dest.stat().st_size > 800:
        return dest
    return None


def save_webp(blob: bytes, dest: Path, max_side=560, quality=72):
    im = Image.open(BytesIO(blob))
    im.load()
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    elif im.mode == "L":
        im = im.convert("RGB")
    if max(im.size) > max_side:
        im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    buf = BytesIO()
    im.save(buf, format="WEBP", quality=quality, method=4)
    dest.write_bytes(buf.getvalue())


def fetch_detail(item_id: str, cache: dict):
    dest = local_path(item_id)
    img = f"img/products/{item_id}.webp" if dest else ""
    price_cny = None
    pic = cache.get(item_id) or ""

    param = quote(json.dumps({"itemId": str(item_id)}, separators=(",", ":")))
    api = f"https://thor.weidian.com/detail/getItemSkuInfo/1.0?param={param}"
    last = "fail"
    for attempt in range(3):
        try:
            req = Request(api, headers=UA)
            with urlopen(req, timeout=18) as r:
                data = json.loads(r.read().decode("utf-8", "replace"))
            res = data.get("result") or {}
            fen = res.get("itemDiscountLowPrice") or res.get("itemOriginalLowPrice")
            if fen is not None:
                price_cny = float(fen) / 100.0
            if not pic:
                pic = (res.get("itemMainPic") or "").split("?")[0]
            if pic or price_cny is not None:
                break
            last = "empty"
            break
        except Exception as e:
            last = type(e).__name__
            time.sleep(0.5 * (attempt + 1))

    if img:
        return "have", img, price_cny
    if not pic:
        return last, "", price_cny

    pic = pic.replace(".jpg.webp", ".jpg")
    try:
        req = Request(pic + "?w=560&h=560&cp=1", headers=UA)
        with urlopen(req, timeout=18) as r:
            blob = r.read()
        if len(blob) >= 800:
            save_webp(blob, OUT / f"{item_id}.webp")
            return "ok", f"img/products/{item_id}.webp", price_cny
    except Exception as e:
        last = type(e).__name__
    return "remote", pic + "?w=560&h=560&cp=1", price_cny


def usd(cny):
    return round(float(cny) / 7.2, 2) if cny else 0


def to_product(it, image, price_cny):
    base = slugify(it["title"])
    slug = f"{base}-{it['itemId']}" if base else it["itemId"]
    return {
        "id": f"p-{it['itemId']}",
        "title": it["title"],
        "price": usd(price_cny) if price_cny else 0,
        "rating": 4.7,
        "category": it["category"],
        "collection": it["brand"] or "Find",
        "qc": True,
        "featured": True,
        "sourceUrl": it["url"],
        "image": image if image.startswith("img/") else f"img/products/{it['itemId']}.webp",
        "popular": True,
        "sellerName": "Wen Studio",
        "slug": slug,
    }


def main(paths: list[Path]):
    OUT.mkdir(parents=True, exist_ok=True)
    catalog = load_catalog()
    existing = catalog.get("products") or []
    existing_ids = {str(p.get("id") or "") for p in existing}

    new_items = []
    seen = set()
    for path in paths:
        chunk = load_xlsx(path)
        print(f"{path.name}: {len(chunk)}", flush=True)
        for it in chunk:
            if it["itemId"] in seen:
                continue
            seen.add(it["itemId"])
            new_items.append(it)

    todo = [it for it in new_items if f"p-{it['itemId']}" not in existing_ids]
    print(f"unique {len(new_items)} new {len(todo)} existing {len(existing)}", flush=True)
    print("cats", dict(Counter(it["category"] for it in todo)), flush=True)

    cache = load_cache()
    meta = {}

    def work(it):
        st, src, price = fetch_detail(it["itemId"], cache)
        return it["itemId"], st, src, price

    ok = fail = remote = have = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(work, it): it for it in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            iid, st, src, price = fut.result()
            print(f"{i}/{len(todo)} {iid} {st} ¥{price}", flush=True)
            if src:
                meta[iid] = (src, price, st)
                if src.startswith("http"):
                    cache[iid] = src.split("?")[0]
                    remote += 1
                elif st == "have":
                    have += 1
                else:
                    ok += 1
            else:
                fail += 1
            if i % 80 == 0:
                save_cache({k: v for k, v in cache.items() if v})

    save_cache({k: v for k, v in cache.items() if v})

    added = []
    for it in todo:
        row = meta.get(it["itemId"])
        if not row or not row[0]:
            continue
        # Prefer local webp path for site assets
        img = row[0]
        if img.startswith("http"):
            # keep remote only if download failed; still list product
            local = f"img/products/{it['itemId']}.webp"
            if local_path(it["itemId"]):
                img = local
            else:
                continue
        added.append(to_product(it, img, row[1]))

    for p in existing:
        if p.get("featured") or p.get("popular"):
            p["featured"] = False
            p["popular"] = False

    merged = added + existing
    today = date.today()
    catalog["updated"] = today.strftime("%-d %b %Y")
    catalog["count"] = len(merged)
    catalog["countLabel"] = f"{len(merged):,}+" if len(merged) >= 1000 else str(len(merged))
    catalog["products"] = merged
    write_catalog(catalog)
    print(
        f"done ok={ok} have={have} remote={remote} fail={fail} "
        f"added={len(added)} total={len(merged)}",
        flush=True,
    )
    print("added cats", dict(Counter(p["category"] for p in added)), flush=True)


if __name__ == "__main__":
    args = [Path(a) for a in sys.argv[1:]]
    if not args:
        args = sorted(ROOT.glob("*商品.xlsx"))
    if not args:
        raise SystemExit("No xlsx files found")
    main(args)
