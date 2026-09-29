#!/usr/bin/env python3
"""Build catalog, crawlable item pages, sitemap, robots, and OG image for kakobuyqcspreadsheet.com."""
from __future__ import annotations

import json
import os
import re
import shutil
from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

ORIGIN = "https://kakobuyqcspreadsheet.com"
AFF = "jm98p"
TODAY = date.today().isoformat()
ROOT = Path(__file__).resolve().parents[1]
HUNT = ROOT.parent / "kakobuyhunt"
SELLERS = {"wen": "Wen Studio", "li": "LJR-Christine", "other": "Verified seller"}
RESERVED_SLUGS = {
    "item", "img", "js", "css", "scripts", "articles", "coupons", "faq", "qc",
    "pl", "de", "finds", "index",
}
CAT_META = {
    "shoes": {
        "label": "Designer Shoes",
        "title": "Replica Shoes Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica shoes — {n} finds",
        "desc": "{n} Kakobuy replica shoes with USD prices, QC photos, and direct KakoBuy links. QualityReps spreadsheet, free.",
        "kw": "replica shoes, kakobuy sneakers, qualityreps shoes",
    },
    "t-shirts": {
        "label": "Tees & Jerseys",
        "title": "Replica T-Shirts Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica t-shirts — {n} finds",
        "desc": "{n} Kakobuy replica t-shirts and jerseys with USD prices, QC photos, and direct KakoBuy links.",
        "kw": "replica t-shirts, kakobuy tees, qualityreps jerseys",
    },
    "accessories": {
        "label": "Premium Accessories",
        "title": "Replica Accessories Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica accessories — {n} finds",
        "desc": "{n} Kakobuy replica bags, belts, and accessories with USD prices, QC photos, and direct KakoBuy links.",
        "kw": "replica accessories, kakobuy bags, qualityreps",
    },
    "hoodies": {
        "label": "Verified Hoodies",
        "title": "Replica Hoodies Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica hoodies — {n} finds",
        "desc": "{n} Kakobuy replica hoodies with USD prices, QC photos, and direct KakoBuy links. QualityReps spreadsheet.",
        "kw": "replica hoodies, kakobuy hoodie, qualityreps",
    },
    "pants": {
        "label": "Pants",
        "title": "Replica Pants Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica pants — {n} finds",
        "desc": "{n} Kakobuy replica pants and shorts with USD prices, QC photos, and direct KakoBuy links.",
        "kw": "replica pants, kakobuy shorts, qualityreps",
    },
    "jackets": {
        "label": "Jackets & Outerwear",
        "title": "Replica Jackets Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica jackets — {n} finds",
        "desc": "{n} Kakobuy replica jackets and outerwear with USD prices, QC photos, and direct KakoBuy links.",
        "kw": "replica jackets, kakobuy outerwear, qualityreps",
    },
    "jersey": {
        "label": "Jerseys",
        "title": "Replica Jerseys Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica jerseys — {n} finds",
        "desc": "{n} Kakobuy replica football jerseys with USD prices, QC photos, and direct KakoBuy links.",
        "kw": "replica jerseys, kakobuy football shirt, qualityreps",
    },
    "watches": {
        "label": "Watches & Jewelry",
        "title": "Replica Watches Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica watches — {n} finds",
        "desc": "{n} Kakobuy replica watches and jewelry with USD prices, QC photos, and direct KakoBuy links.",
        "kw": "replica watches, kakobuy rolex, qualityreps",
    },
    "headwear": {
        "label": "Hats & Caps",
        "title": "Replica Hats Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica hats — {n} finds",
        "desc": "{n} Kakobuy replica caps, beanies, and hats with USD prices, QC photos, and direct KakoBuy links.",
        "kw": "replica hats, kakobuy cap, qualityreps",
    },
    "glasses": {
        "label": "Sunglasses",
        "title": "Replica Sunglasses Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica sunglasses — {n} finds",
        "desc": "{n} Kakobuy replica sunglasses with USD prices, QC photos, and direct KakoBuy links.",
        "kw": "replica sunglasses, kakobuy glasses, qualityreps",
    },
    "sets": {
        "label": "Sets",
        "title": "Replica Sets Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica sets — {n} finds",
        "desc": "{n} Kakobuy replica matching sets with USD prices, QC photos, and direct KakoBuy links.",
        "kw": "replica sets, kakobuy tracksuit, qualityreps",
    },
    "bricks": {
        "label": "Bricks & Toys",
        "title": "Replica Bricks Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica bricks — {n} finds",
        "desc": "{n} Kakobuy brick and toy finds with USD prices and direct KakoBuy links.",
        "kw": "kakobuy lego, replica bricks, qualityreps",
    },
    "perfume": {
        "label": "Perfume",
        "title": "Replica Perfume Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica perfume — {n} finds",
        "desc": "{n} Kakobuy replica fragrances with USD prices and direct KakoBuy links.",
        "kw": "replica perfume, kakobuy fragrance, qualityreps",
    },
    "underwear": {
        "label": "Underwear",
        "title": "Replica Underwear Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica underwear — {n} finds",
        "desc": "{n} Kakobuy replica underwear finds with USD prices and direct KakoBuy links.",
        "kw": "replica underwear, kakobuy, qualityreps",
    },
    "other": {
        "label": "Other finds",
        "title": "More Replica Finds Spreadsheet — KakoBuy 2026",
        "h1": "More Kakobuy replica finds — {n} items",
        "desc": "{n} extra Kakobuy replica finds with USD prices, QC photos, and direct KakoBuy links.",
        "kw": "replicas, qualityreps, kakobuy spreadsheet",
    },
}


def cat_info(slug: str, n: int) -> dict:
    raw = CAT_META.get(slug) or {
        "label": slug.replace("-", " ").title(),
        "title": f"Replica {slug.replace('-', ' ').title()} Spreadsheet — KakoBuy 2026",
        "h1": "Kakobuy replica {label} — {n} finds",
        "desc": "{n} Kakobuy replica finds in this category with USD prices, QC photos, and direct KakoBuy links.",
        "kw": f"replicas, qualityreps, kakobuy {slug}",
    }
    label = raw["label"]
    return {
        "slug": slug,
        "label": label,
        "title": raw["title"].format(n=n, label=label),
        "h1": raw["h1"].format(n=n, label=label.lower()),
        "desc": raw["desc"].format(n=n, label=label.lower()),
        "kw": raw["kw"],
    }


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower())
    s = re.sub(r"^-+|-+$", "", s)
    s = re.sub(r"-+", "-", s)
    return s[:60]


def item_id(p: dict) -> str:
    return re.sub(r"^p-", "", str(p.get("id") or ""), count=1)


def item_slug(p: dict) -> str:
    if p.get("slug"):
        return str(p["slug"])
    base = slugify(str(p.get("title") or ""))
    num = item_id(p)
    return f"{base}-{num}" if base else num


def kakobuy_url(source_url: str) -> str:
    url = source_url or ""
    weidian = re.search(r"itemID=(\d+)", url, re.I)
    if weidian or "weidian.com" in url.lower():
        if weidian:
            return (
                "https://www.kakobuy.com/item/details?url="
                f"https%3A%2F%2Fweidian.com%2Fitem.html%3FitemID%3D{weidian.group(1)}"
                f"&affcode={AFF}"
            )
    return f"https://www.kakobuy.com/item/details?url={quote(url, safe='')}&affcode={AFF}"


def load_hunt() -> list[dict]:
    raw = (HUNT / "js" / "catalog.js").read_text(encoding="utf-8")
    start = raw.index("KF.products = ") + len("KF.products = ")
    products, _ = json.JSONDecoder().raw_decode(raw[start:])
    return products


def link_or_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        return
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def copy_images(products: list[dict]) -> None:
    src_dir = HUNT / "img" / "products"
    dst_dir = ROOT / "img" / "products"
    dst_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for p in products:
        pid = item_id(p)
        for name in (f"{pid}.webp", f"{pid}-2.webp", f"{pid}-3.webp"):
            src = src_dir / name
            if src.exists():
                link_or_copy(src, dst_dir / name)
                n += 1
    print(f"images linked/copied: {n}")


def write_products(products: list[dict]) -> list[dict]:
    slim = []
    for p in products:
        slug = item_slug(p)
        slim.append({
            "id": p.get("id"),
            "title": p.get("title") or "Find",
            "price": p.get("price") or 0,
            "rating": p.get("rating") or 4.5,
            "category": p.get("category") or "other",
            "collection": p.get("collection") or "Find",
            "qc": bool(p.get("qc")),
            "featured": bool(p.get("featured")),
            "sourceUrl": p.get("sourceUrl") or "",
            "image": f"img/products/{item_id(p)}.webp",
            "popular": bool(p.get("featured") or (p.get("rating") or 0) >= 4.8),
            "sellerName": SELLERS.get(str(p.get("seller") or "other"), "Verified seller"),
            "slug": slug,
        })
    payload = {
        "updated": "21 Sept 2026",
        "countLabel": "4,000+",
        "count": len(slim),
        "products": slim,
    }
    out = ROOT / "js" / "products.js"
    out.write_text(
        "window.SK = window.SK || {};\nSK.catalog = "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(f"products.js: {len(slim)} items, {out.stat().st_size // 1024} KB")
    return slim


def card_html(p: dict, prefix: str) -> str:
    pill = '<span class="pill">Popular</span>' if p.get("popular") else ""
    tags = f'<span class="card-tags">{pill}</span>' if pill else ""
    title = escape(p["title"])
    return (
        f'<a class="card" href="{prefix}item/{p["slug"]}/">'
        f'<div class="card-media">'
        f'<img src="{prefix}{p["image"]}" alt="{title}" width="400" height="400" loading="lazy" decoding="async" />'
        f"{tags}"
        f'<span class="price-chip">${float(p["price"]):.2f}</span>'
        f"</div>"
        f'<div class="card-body"><h3>{title}</h3>'
        f'<div class="seller-row"><span>{escape(p.get("sellerName") or "Verified seller")}</span></div>'
        f"</div></a>"
    )


def thumbs_html(p: dict, prefix: str) -> str:
    pid = item_id(p)
    imgs = [f"img/products/{pid}.webp"]
    for n in (2, 3):
        if (ROOT / "img" / "products" / f"{pid}-{n}.webp").exists():
            imgs.append(f"img/products/{pid}-{n}.webp")
    while len(imgs) < 3:
        imgs.append("")
    bits = []
    for i, src in enumerate(imgs):
        cls = "is-on" if i == 0 else ""
        if src:
            bits.append(
                f'<button type="button" data-src="{prefix}{src}" class="{cls}" aria-label="Photo {i + 1}">'
                f'<img src="{prefix}{src}" alt="" /></button>'
            )
        else:
            bits.append(f'<button type="button" class="is-empty" aria-label="Photo {i + 1}"></button>')
    return "".join(bits)


def item_page(p: dict, related: list[dict]) -> str:
    prefix = "../../"
    slug = p["slug"]
    url = f"{ORIGIN}/item/{slug}/"
    title = p["title"]
    desc = (
        f"{title} replica on KakoBuy Spreadsheet. "
        f"${float(p['price']):.2f} USD, QC photos, direct KakoBuy link. QualityReps find."
    )
    img = f"{ORIGIN}/{p['image']}"
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": title,
        "image": img,
        "description": desc,
        "brand": {"@type": "Brand", "name": p.get("collection") or "Find"},
        "offers": {
            "@type": "Offer",
            "price": f"{float(p['price']):.2f}",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "url": url,
        },
    }
    related_html = "".join(card_html(x, prefix) for x in related)
    buy = kakobuy_url(p.get("sourceUrl") or "")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)} — KakoBuy Spreadsheet Replicas</title>
  <meta name="description" content="{escape(desc)}" />
  <meta name="keywords" content="replicas, qualityreps, Kakobuy Spreadsheet, {escape(title)}" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <link rel="canonical" href="{url}" />
  <meta property="og:type" content="product" />
  <meta property="og:site_name" content="kakobuy spreadsheet" />
  <meta property="og:title" content="{escape(title)} — KakoBuy Spreadsheet" />
  <meta property="og:description" content="{escape(desc)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{img}" />
  <meta name="twitter:card" content="summary_large_image" />
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
  <link rel="icon" href="{prefix}img/favicon.svg?v=3" type="image/svg+xml" />
  <link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png" />
  <link rel="manifest" href="/manifest.json?v=pwa12" />
  <meta name="theme-color" content="#FB2840" />
  <meta name="mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="default" />
  <meta name="apple-mobile-web-app-title" content="KakoBuy Spreadsheet" />
  <meta name="application-name" content="KakoBuy Spreadsheet" />
  <link rel="apple-touch-icon" href="/img/apple-touch-icon.png" sizes="180x180" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{prefix}css/style.css" />
</head>
<body data-page="item" data-item-id="{escape(str(p['id']))}">
  <div class="promo-bar" id="promo"></div>
  <header class="site-header" id="site-header"></header>
  <div class="overlay" id="overlay"></div>
  <aside class="mobile-nav" id="mobile-nav"></aside>
  <main>
    <section class="section">
      <div class="wrap">
        <div class="crumbs" id="item-crumbs"><a href="{prefix}index.html">Home</a> / <a href="{prefix}spreadsheet.html">Spreadsheet</a> / <a href="{prefix}{escape(p.get("category") or "shoes")}/">{escape(cat_info(p.get("category") or "shoes", 0)["label"])}</a> / <span>{escape(p.get("collection") or "Find")}</span></div>
        <div class="item-grid" id="item-root">
          <div class="item-gallery">
            <div class="item-shot"><img id="item-main" src="{prefix}{p['image']}" alt="{escape(title)}" /></div>
            <div class="item-thumbs" id="item-thumbs">{thumbs_html(p, prefix)}</div>
          </div>
          <div class="buy-box">
            <h1>{escape(title)}</h1>
            <div class="price">${float(p['price']):.2f}</div>
            <p>Hand-checked replica listing. Opens the live KakoBuy product page so you can pick size, pay, and review warehouse QC before shipping.</p>
            <div style="margin-top:22px">
              <a class="btn btn-solid" href="{escape(buy)}" target="_blank" rel="noopener">View on KakoBuy →</a>
              <p class="buy-note">Link uses our KakoBuy referral code. How this site makes money.</p>
            </div>
          </div>
        </div>
        <aside class="qc-tips">
          <h2>What to check in the QC photos</h2>
          <ol>
            <li>Check the seller's QC photos before accepting at the KakoBuy warehouse.</li>
            <li>Compare against retail images for color and material accuracy.</li>
            <li>Verify size labels and any logos for spelling or placement issues.</li>
          </ol>
        </aside>
      </div>
    </section>
    <section class="section soft">
      <div class="wrap">
        <div class="section-head"><div><h2>Related finds</h2><p>Same category, other listings.</p></div></div>
        <div class="product-grid" id="related-grid">{related_html}</div>
      </div>
    </section>
  </main>
  <footer class="site-footer" id="site-footer"></footer>
  <script src="{prefix}js/site.js"></script>
  <script src="{prefix}js/app.js"></script>
</body>
</html>
"""


def write_items(products: list[dict]) -> None:
    by_cat = defaultdict(list)
    for p in products:
        by_cat[p["category"]].append(p)
    item_root = ROOT / "item"
    if item_root.exists():
        shutil.rmtree(item_root)
    n = 0
    for p in products:
        related = [x for x in by_cat[p["category"]] if x["id"] != p["id"]][:8]
        folder = item_root / p["slug"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.html").write_text(item_page(p, related), encoding="utf-8")
        n += 1
        if n % 500 == 0:
            print(f"  item pages {n}/{len(products)}")
    print(f"item pages: {n}")


def load_local_products() -> list[dict]:
    raw = (ROOT / "js" / "products.js").read_text(encoding="utf-8")
    start = raw.index("SK.catalog = ") + len("SK.catalog = ")
    catalog, _ = json.JSONDecoder().raw_decode(raw[start:])
    return catalog["products"]


def category_page(slug: str, items: list[dict], all_slugs: list[str] | None = None) -> str:
    n = len(items)
    info = cat_info(slug, n)
    url = f"{ORIGIN}/{slug}/"
    prefix = "../"
    cards = "".join(card_html(p, prefix) for p in items)
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": info["title"],
        "url": url,
        "description": info["desc"],
        "isPartOf": {"@id": f"{ORIGIN}/#website"},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": n,
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i,
                    "url": f"{ORIGIN}/item/{p['slug']}/",
                    "name": p["title"],
                }
                for i, p in enumerate(items[:40], 1)
            ],
        },
    }
    option_slugs = all_slugs or sorted(set(CAT_META) | {slug})
    options = "".join(
        f'<option value="{escape(s)}"{" selected" if s == slug else ""}>{escape(cat_info(s, 0)["label"])}</option>'
        for s in option_slugs
        if s not in RESERVED_SLUGS
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(info["title"])}</title>
  <meta name="description" content="{escape(info["desc"])}" />
  <meta name="keywords" content="replicas, qualityreps, {escape(info["kw"])}" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <link rel="canonical" href="{url}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="kakobuy spreadsheet" />
  <meta property="og:title" content="{escape(info["title"])}" />
  <meta property="og:description" content="{escape(info["desc"])}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{ORIGIN}/img/og.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
  <link rel="icon" href="{prefix}img/favicon.svg?v=3" type="image/svg+xml" />
  <link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png" />
  <link rel="manifest" href="/manifest.json?v=pwa12" />
  <meta name="theme-color" content="#FB2840" />
  <meta name="mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="default" />
  <meta name="apple-mobile-web-app-title" content="KakoBuy Spreadsheet" />
  <meta name="application-name" content="KakoBuy Spreadsheet" />
  <link rel="apple-touch-icon" href="/img/apple-touch-icon.png" sizes="180x180" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{prefix}css/style.css" />
</head>
<body data-page="category" data-cat="{escape(slug)}">
  <div class="promo-bar" id="promo"></div>
  <header class="site-header" id="site-header"></header>
  <div class="overlay" id="overlay"></div>
  <aside class="mobile-nav" id="mobile-nav"></aside>
  <main>
    <section class="page-hero">
      <div class="wrap">
        <div class="crumbs"><a href="{prefix}index.html">Home</a> / <a href="{prefix}spreadsheet.html">Spreadsheet</a> / <span>{escape(info["label"])}</span></div>
        <h1>{escape(info["h1"])}</h1>
        <p class="lede">{escape(info["desc"])} Updated {date.fromisoformat(TODAY).strftime("%-d %b %Y")}.</p>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap">
        <div class="toolbar">
          <div class="search">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
            <input id="catalog-search" placeholder="Search {escape(info["label"].lower())}…" />
          </div>
          <select id="catalog-cat"><option value="">All categories</option>{options}</select>
          <select id="catalog-sort">
            <option value="featured">Latest</option>
            <option value="price-asc">Price: low to high</option>
            <option value="price-desc">Price: high to low</option>
          </select>
        </div>
        <p id="result-count" class="lede" style="margin-bottom:16px">Showing {n} finds</p>
        <div class="product-grid" id="catalog-grid">{cards}</div>
        <div class="cta-row">
          <a class="btn btn-solid" href="https://ikako.vip/r/jm98p" target="_blank" rel="noopener">Sign up for KakoBuy coupons</a>
        </div>
      </div>
    </section>
  </main>
  <footer class="site-footer" id="site-footer"></footer>
  <script src="{prefix}js/products.js"></script>
  <script src="{prefix}js/site.js"></script>
  <script src="{prefix}js/app.js"></script>
</body>
</html>
"""


def write_categories(products: list[dict]) -> list[str]:
    by_cat = defaultdict(list)
    for p in products:
        slug = p.get("category") or "other"
        if slug in RESERVED_SLUGS:
            continue
        by_cat[slug].append(p)
    slugs = sorted(by_cat.keys())
    for slug, items in sorted(by_cat.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        folder = ROOT / slug
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.html").write_text(category_page(slug, items, slugs), encoding="utf-8")
        print(f"  /{slug}/ {len(items)} items")
    print(f"category pages: {len(slugs)}")
    return slugs


def patch_item_crumbs(products: list[dict]) -> None:
    by_id = {str(p.get("id")): p for p in products}
    n = 0
    item_root = ROOT / "item"
    if not item_root.exists():
        return
    for path in item_root.glob("*/index.html"):
        html = path.read_text(encoding="utf-8")
        m = re.search(r'data-item-id="([^"]+)"', html)
        if not m:
            continue
        p = by_id.get(m.group(1))
        if not p:
            continue
        slug = p.get("category") or "shoes"
        label = cat_info(slug, 0)["label"]
        old = (
            '<a href="../../index.html">Home</a> / '
            '<a href="../../spreadsheet.html">Spreadsheet</a> / '
        )
        new = (
            '<a href="../../index.html">Home</a> / '
            '<a href="../../spreadsheet.html">Spreadsheet</a> / '
            f'<a href="../../{slug}/">{escape(label)}</a> / '
        )
        if old in html and f'href="../../{slug}/"' not in html:
            path.write_text(html.replace(old, new, 1), encoding="utf-8")
            n += 1
    print(f"item crumbs patched: {n}")


def write_sitemap(products: list[dict]) -> None:
    pages = [
        "/",
        "/spreadsheet.html",
        "/coupons.html",
        "/faq.html",
        "/qc.html",
        "/articles.html",
        "/pl.html",
        "/de.html",
        "/articles/is-kakobuy-legit.html",
        "/articles/kakobuy-vs-cnfans.html",
        "/articles/shipping-customs.html",
    ]
    alts = [
        '    <xhtml:link rel="alternate" hreflang="en" href="https://kakobuyqcspreadsheet.com/"/>',
        '    <xhtml:link rel="alternate" hreflang="pl" href="https://kakobuyqcspreadsheet.com/pl.html"/>',
        '    <xhtml:link rel="alternate" hreflang="de" href="https://kakobuyqcspreadsheet.com/de.html"/>',
        '    <xhtml:link rel="alternate" hreflang="x-default" href="https://kakobuyqcspreadsheet.com/"/>',
    ]
    locale_paths = {"/", "/pl.html", "/de.html"}
    cats = sorted({p.get("category") or "other" for p in products} - RESERVED_SLUGS)
    urls = []
    for path in pages:
        if path in locale_paths:
            urls.append(
                "  <url>\n"
                f"    <loc>{ORIGIN}{path}</loc>\n"
                f"    <lastmod>{TODAY}</lastmod>\n"
                "    <changefreq>weekly</changefreq>\n"
                + "\n".join(alts)
                + "\n  </url>"
            )
        else:
            urls.append(
                f"  <url><loc>{ORIGIN}{path}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq></url>"
            )
    for slug in cats:
        urls.append(
            f"  <url><loc>{ORIGIN}/{slug}/</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq></url>"
        )
    for p in products:
        urls.append(
            f"  <url><loc>{ORIGIN}/item/{p['slug']}/</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq></url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    print(f"sitemap.xml: {len(urls)} urls")


def write_robots() -> None:
    (ROOT / "robots.txt").write_text(
        f"""User-agent: *
Allow: /
Disallow: /scripts/

Sitemap: {ORIGIN}/sitemap.xml

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /
""",
        encoding="utf-8",
    )
    print("robots.txt")


def write_og() -> None:
    from PIL import Image, ImageDraw, ImageFont

    w, h = 1200, 630
    img = Image.new("RGB", (w, h), "#f6f3ec")
    logo = Image.open(ROOT / "img" / "logo-k.png").convert("RGBA")
    logo = logo.resize((180, 230), Image.Resampling.LANCZOS)
    img.paste(logo, (80, 200), logo)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 64)
        small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 32)
    except OSError:
        font = ImageFont.load_default()
        small = font
    draw.text((300, 230), "kakobuy spreadsheet", fill="#141210", font=font)
    draw.text((300, 320), "4,000+ replicas with QC photos", fill="#f05a00", font=small)
    out = ROOT / "img" / "og.png"
    img.save(out, "PNG", optimize=True)
    print(f"og.png {out.stat().st_size // 1024} KB")


HREFLANG = f"""  <link rel="alternate" hreflang="en" href="{ORIGIN}/" />
  <link rel="alternate" hreflang="pl" href="{ORIGIN}/pl.html" />
  <link rel="alternate" hreflang="de" href="{ORIGIN}/de.html" />
  <link rel="alternate" hreflang="x-default" href="{ORIGIN}/" />"""

SITE_SCHEMA = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "Organization",
            "@id": f"{ORIGIN}/#org",
            "name": "kakobuy spreadsheet",
            "url": f"{ORIGIN}/",
            "logo": f"{ORIGIN}/img/logo-k.png",
            "email": "hello@kakobuyqcspreadsheet.com",
            "sameAs": ["https://discord.gg/7DRMaMAADv"],
        },
        {
            "@type": "WebSite",
            "@id": f"{ORIGIN}/#website",
            "url": f"{ORIGIN}/",
            "name": "KakoBuy Spreadsheet 2026",
            "publisher": {"@id": f"{ORIGIN}/#org"},
            "inLanguage": "en",
            "potentialAction": {
                "@type": "SearchAction",
                "target": f"{ORIGIN}/spreadsheet.html?q={{search_term_string}}",
                "query-input": "required name=search_term_string",
            },
        },
    ],
}


def upsert_head(path: Path, canonical: str, extra: str = "", hreflang: bool = False) -> None:
    html = path.read_text(encoding="utf-8")
    html = re.sub(r'\s*<link rel="canonical"[^>]*>', "", html)
    html = re.sub(r'\s*<link rel="alternate" hreflang=[^>]*>', "", html)
    html = re.sub(r'\s*<meta property="og:url"[^>]*>', "", html)
    html = re.sub(r'\s*<meta property="og:image"[^>]*>', "", html)
    html = re.sub(r'\s*<meta name="twitter:card"[^>]*>', "", html)
    html = re.sub(r'\s*<meta name="robots"[^>]*>', "", html)
    html = re.sub(
        r'\s*<script type="application/ld\+json">.*?</script>',
        "",
        html,
        flags=re.S,
    )
    html = html.replace("https://spreadsheet-kakobuy.com", ORIGIN)
    html = html.replace("10,000+", "4,000+")
    block = [
        f'  <meta name="robots" content="index, follow, max-image-preview:large" />',
        f'  <link rel="canonical" href="{canonical}" />',
        f'  <meta property="og:url" content="{canonical}" />',
        f'  <meta property="og:image" content="{ORIGIN}/img/og.png" />',
        '  <meta name="twitter:card" content="summary_large_image" />',
    ]
    if hreflang:
        block.append(HREFLANG)
    if extra:
        block.append(extra)
    inject = "\n".join(block) + "\n"
    html = html.replace("  <link rel=\"icon\"", inject + "  <link rel=\"icon\"", 1)
    path.write_text(html, encoding="utf-8")


def patch_pages() -> None:
    schema = f'  <script type="application/ld+json">{json.dumps(SITE_SCHEMA, ensure_ascii=False)}</script>'
    pages = {
        "index.html": (f"{ORIGIN}/", True, schema),
        "spreadsheet.html": (f"{ORIGIN}/spreadsheet.html", False, schema),
        "coupons.html": (f"{ORIGIN}/coupons.html", False, ""),
        "faq.html": (f"{ORIGIN}/faq.html", False, ""),
        "qc.html": (f"{ORIGIN}/qc.html", False, ""),
        "articles.html": (f"{ORIGIN}/articles.html", False, ""),
        "pl.html": (f"{ORIGIN}/pl.html", True, schema),
        "de.html": (f"{ORIGIN}/de.html", True, schema),
        "finds.html": (f"{ORIGIN}/finds.html", False, ""),
        "item.html": (f"{ORIGIN}/item.html", False, ""),
        "articles/is-kakobuy-legit.html": (f"{ORIGIN}/articles/is-kakobuy-legit.html", False, ""),
        "articles/kakobuy-vs-cnfans.html": (f"{ORIGIN}/articles/kakobuy-vs-cnfans.html", False, ""),
        "articles/shipping-customs.html": (f"{ORIGIN}/articles/shipping-customs.html", False, ""),
    }
    for rel, (canon, hreflang, extra) in pages.items():
        path = ROOT / rel
        if path.exists():
            upsert_head(path, canon, extra, hreflang)
            print("patched", rel)


def main() -> None:
    print("loading hunt catalog…")
    hunt = load_hunt()
    print("hunt products", len(hunt))
    copy_images(hunt)
    products = write_products(hunt)
    write_items(products)
    write_categories(products)
    patch_item_crumbs(products)
    write_sitemap(products)
    write_robots()
    write_og()
    patch_pages()
    print("done")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "cats":
        products = load_local_products()
        write_categories(products)
        patch_item_crumbs(products)
        write_sitemap(products)
        print("done cats")
    else:
        main()
