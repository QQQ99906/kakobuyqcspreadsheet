#!/usr/bin/env python3
"""Generate Polish and German category + item pages, and wire hreflang."""
from __future__ import annotations

import json
import re
import shutil
import sys
from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_seo import (  # noqa: E402
    ORIGIN,
    RESERVED_SLUGS,
    ROOT,
    TODAY,
    cat_info,
    item_id,
    kakobuy_url,
    load_local_products,
)

CAT_EMOJI = {
    "shoes": "👟",
    "t-shirts": "👕",
    "accessories": "💼",
    "hoodies": "⭐",
    "pants": "👖",
    "jackets": "🧥",
    "jersey": "⚽",
    "watches": "⌚",
    "headwear": "🧢",
    "glasses": "🕶️",
    "sets": "👕",
    "bricks": "🧱",
    "perfume": "🧴",
    "underwear": "🩲",
    "other": "📦",
}

CAT_I18N = {
    "pl": {
        "shoes": ("Buty designerskie", "Lista butów replica KakoBuy — 2026", "Buty replica KakoBuy — {n} pozycji", "{n} butów replica KakoBuy z cenami USD, zdjęciami QC i bezpośrednimi linkami."),
        "t-shirts": ("Koszulki i jersey", "Lista koszulek replica KakoBuy — 2026", "Koszulki replica KakoBuy — {n} pozycji", "{n} koszulek i jersey replica KakoBuy z cenami USD, zdjęciami QC i linkami."),
        "accessories": ("Akcesoria", "Lista akcesoriów replica KakoBuy — 2026", "Akcesoria replica KakoBuy — {n} pozycji", "{n} toreb, pasków i akcesoriów replica KakoBuy z cenami USD i zdjęciami QC."),
        "hoodies": ("Bluzy", "Lista bluz replica KakoBuy — 2026", "Bluzy replica KakoBuy — {n} pozycji", "{n} bluz replica KakoBuy z cenami USD, zdjęciami QC i bezpośrednimi linkami."),
        "pants": ("Spodnie", "Lista spodni replica KakoBuy — 2026", "Spodnie replica KakoBuy — {n} pozycji", "{n} spodni i szortów replica KakoBuy z cenami USD i zdjęciami QC."),
        "jackets": ("Kurtki", "Lista kurtek replica KakoBuy — 2026", "Kurtki replica KakoBuy — {n} pozycji", "{n} kurtek replica KakoBuy z cenami USD, zdjęciami QC i bezpośrednimi linkami."),
        "jersey": ("Jersey", "Lista jersey replica KakoBuy — 2026", "Jersey replica KakoBuy — {n} pozycji", "{n} koszulek piłkarskich replica KakoBuy z cenami USD i zdjęciami QC."),
        "watches": ("Zegarki i biżuteria", "Lista zegarków replica KakoBuy — 2026", "Zegarki replica KakoBuy — {n} pozycji", "{n} zegarków i biżuterii replica KakoBuy z cenami USD i zdjęciami QC."),
        "headwear": ("Czapki", "Lista czapek replica KakoBuy — 2026", "Czapki replica KakoBuy — {n} pozycji", "{n} czapek i beanie replica KakoBuy z cenami USD i zdjęciami QC."),
        "glasses": ("Okulary", "Lista okularów replica KakoBuy — 2026", "Okulary replica KakoBuy — {n} pozycji", "{n} okularów replica KakoBuy z cenami USD i zdjęciami QC."),
        "sets": ("Komplety", "Lista kompletów replica KakoBuy — 2026", "Komplety replica KakoBuy — {n} pozycji", "{n} kompletów replica KakoBuy z cenami USD i zdjęciami QC."),
        "bricks": ("Klocki i zabawki", "Lista klocków KakoBuy — 2026", "Klocki KakoBuy — {n} pozycji", "{n} klocków i zabawek z cenami USD i linkami KakoBuy."),
        "perfume": ("Perfumy", "Lista perfum replica KakoBuy — 2026", "Perfumy replica KakoBuy — {n} pozycji", "{n} perfum replica KakoBuy z cenami USD i linkami."),
        "underwear": ("Bielizna", "Lista bielizny replica KakoBuy — 2026", "Bielizna replica KakoBuy — {n} pozycji", "{n} sztuk bielizny replica KakoBuy z cenami USD i linkami."),
        "other": ("Inne znaleziska", "Więcej znalezisk replica KakoBuy — 2026", "Inne znaleziska KakoBuy — {n} pozycji", "{n} dodatkowych znalezisk replica KakoBuy z cenami USD i zdjęciami QC."),
    },
    "de": {
        "shoes": ("Designer-Schuhe", "Replica-Schuhe Spreadsheet — KakoBuy 2026", "KakoBuy Replica-Schuhe — {n} Funde", "{n} KakoBuy Replica-Schuhe mit USD-Preisen, QC-Fotos und direkten Links."),
        "t-shirts": ("Shirts & Jerseys", "Replica-T-Shirts Spreadsheet — KakoBuy 2026", "KakoBuy Replica-T-Shirts — {n} Funde", "{n} KakoBuy Replica-Shirts und Jerseys mit USD-Preisen, QC-Fotos und Links."),
        "accessories": ("Accessoires", "Replica-Accessoires Spreadsheet — KakoBuy 2026", "KakoBuy Replica-Accessoires — {n} Funde", "{n} KakoBuy Replica-Taschen, Gürtel und Accessoires mit USD-Preisen und QC-Fotos."),
        "hoodies": ("Hoodies", "Replica-Hoodies Spreadsheet — KakoBuy 2026", "KakoBuy Replica-Hoodies — {n} Funde", "{n} KakoBuy Replica-Hoodies mit USD-Preisen, QC-Fotos und direkten Links."),
        "pants": ("Hosen", "Replica-Hosen Spreadsheet — KakoBuy 2026", "KakoBuy Replica-Hosen — {n} Funde", "{n} KakoBuy Replica-Hosen und Shorts mit USD-Preisen und QC-Fotos."),
        "jackets": ("Jacken", "Replica-Jacken Spreadsheet — KakoBuy 2026", "KakoBuy Replica-Jacken — {n} Funde", "{n} KakoBuy Replica-Jacken mit USD-Preisen, QC-Fotos und direkten Links."),
        "jersey": ("Trikots", "Replica-Trikots Spreadsheet — KakoBuy 2026", "KakoBuy Replica-Trikots — {n} Funde", "{n} KakoBuy Replica-Fußballtrikots mit USD-Preisen und QC-Fotos."),
        "watches": ("Uhren & Schmuck", "Replica-Uhren Spreadsheet — KakoBuy 2026", "KakoBuy Replica-Uhren — {n} Funde", "{n} KakoBuy Replica-Uhren und Schmuck mit USD-Preisen und QC-Fotos."),
        "headwear": ("Mützen & Caps", "Replica-Caps Spreadsheet — KakoBuy 2026", "KakoBuy Replica-Caps — {n} Funde", "{n} KakoBuy Replica-Caps und Beanies mit USD-Preisen und QC-Fotos."),
        "glasses": ("Sonnenbrillen", "Replica-Sonnenbrillen Spreadsheet — KakoBuy 2026", "KakoBuy Replica-Sonnenbrillen — {n} Funde", "{n} KakoBuy Replica-Sonnenbrillen mit USD-Preisen und QC-Fotos."),
        "sets": ("Sets", "Replica-Sets Spreadsheet — KakoBuy 2026", "KakoBuy Replica-Sets — {n} Funde", "{n} KakoBuy Replica-Sets mit USD-Preisen und QC-Fotos."),
        "bricks": ("Steine & Spielzeug", "KakoBuy Steine Spreadsheet — 2026", "KakoBuy Steine — {n} Funde", "{n} Steine- und Spielzeug-Funde mit USD-Preisen und KakoBuy-Links."),
        "perfume": ("Parfum", "Replica-Parfum Spreadsheet — KakoBuy 2026", "KakoBuy Replica-Parfum — {n} Funde", "{n} KakoBuy Replica-Düfte mit USD-Preisen und Links."),
        "underwear": ("Unterwäsche", "Replica-Unterwäsche Spreadsheet — KakoBuy 2026", "KakoBuy Replica-Unterwäsche — {n} Funde", "{n} KakoBuy Replica-Unterwäsche mit USD-Preisen und Links."),
        "other": ("Weitere Funde", "Mehr Replica-Funde Spreadsheet — KakoBuy 2026", "Weitere KakoBuy-Funde — {n} Artikel", "{n} weitere KakoBuy Replica-Funde mit USD-Preisen und QC-Fotos."),
    },
}

UI = {
    "pl": {
        "home": "Strona główna",
        "spreadsheet": "Spreadsheet",
        "popular": "Popularne",
        "view": "Zobacz na KakoBuy →",
        "buy": "Sprawdzona oferta replica. Otwiera stronę produktu KakoBuy, aby wybrać rozmiar, zapłacić i sprawdzić zdjęcia QC w magazynie przed wysyłką.",
        "note": "Link zawiera nasz kod polecający KakoBuy. Tak ta strona zarabia.",
        "qc_h2": "Co sprawdzić na zdjęciach QC",
        "qc_1": "Sprawdź zdjęcia QC sprzedawcy, zanim zaakceptujesz paczkę w magazynie KakoBuy.",
        "qc_2": "Porównaj kolor i materiał ze zdjęciami detalicznymi.",
        "qc_3": "Sprawdź metki rozmiarowe i logo pod kątem literówek lub złego ułożenia.",
        "related_h2": "Podobne oferty",
        "related_p": "Ta sama kategoria, inne ogłoszenia.",
        "desc": "{title} — kopia na KakoBuy Spreadsheet. ${price} USD, zdjęcia QC, bezpośredni link KakoBuy.",
        "title_suf": "— KakoBuy Spreadsheet",
        "all_cats": "Wszystkie kategorie",
        "latest": "Najnowsze",
        "price_asc": "Cena: od najniższej",
        "price_desc": "Cena: od najwyższej",
        "showing": "Wyświetlono {n} pozycji",
        "search_ph": "Szukaj: {label}…",
        "signup": "Zarejestruj się i odbierz kupony KakoBuy",
        "updated": "Zaktualizowano {date}.",
        "photo": "Zdjęcie {n}",
        "cats_h2": "Popularne kategorie",
        "cats_p": "Przeglądaj listę po polsku — te same oferty, polskie opisy stron.",
        "items_word": "pozycji",
        "open_sheet": "Otwórz spreadsheet",
    },
    "de": {
        "home": "Start",
        "spreadsheet": "Spreadsheet",
        "popular": "Beliebt",
        "view": "Auf KakoBuy ansehen →",
        "buy": "Geprüfte Replica-Anzeige. Öffnet die KakoBuy-Produktseite, damit du Größe wählst, bezahlst und die Lager-QC prüfst, bevor du versendest.",
        "note": "Der Link enthält unseren KakoBuy-Empfehlungscode. So finanziert sich diese Seite.",
        "qc_h2": "Worauf du in den QC-Fotos achten solltest",
        "qc_1": "Prüfe die QC-Fotos des Verkäufers, bevor du das Paket im KakoBuy-Lager annimmst.",
        "qc_2": "Vergleiche Farbe und Material mit Retail-Bildern.",
        "qc_3": "Kontrolliere Größenetiketten und Logos auf Schreibfehler oder falsche Platzierung.",
        "related_h2": "Ähnliche Funde",
        "related_p": "Gleiche Kategorie, andere Inserate.",
        "desc": "{title} Replik auf KakoBuy Spreadsheet. ${price} USD, QC-Fotos, direkter KakoBuy-Link.",
        "title_suf": "— KakoBuy Spreadsheet",
        "all_cats": "Alle Kategorien",
        "latest": "Neueste",
        "price_asc": "Preis: aufsteigend",
        "price_desc": "Preis: absteigend",
        "showing": "{n} Funde angezeigt",
        "search_ph": "Suche: {label}…",
        "signup": "Bei KakoBuy registrieren und Coupons sichern",
        "updated": "Aktualisiert {date}.",
        "photo": "Foto {n}",
        "cats_h2": "Beliebte Kategorien",
        "cats_p": "Die gleiche Liste auf Deutsch — gleiche Funde, deutsche Seiten.",
        "items_word": "Funde",
        "open_sheet": "Spreadsheet öffnen",
    },
}


def fmt_date(lang: str) -> str:
    d = date.fromisoformat(TODAY)
    if lang == "pl":
        months = "sty lut mar kwi maj cze lip sie wrz paź lis gru".split()
        return f"{d.day} {months[d.month - 1]} {d.year}"
    if lang == "de":
        return d.strftime("%d.%m.%Y")
    return d.strftime("%-d %b %Y")


def loc_cat(lang: str, slug: str, n: int) -> dict:
    row = (CAT_I18N.get(lang) or {}).get(slug)
    if not row:
        info = cat_info(slug, n)
        return info
    label, title, h1, desc = row
    return {
        "slug": slug,
        "label": label,
        "title": title.format(n=n),
        "h1": h1.format(n=n),
        "desc": desc.format(n=n),
        "kw": f"kakobuy, replica, {label}",
    }


def hreflang_item(slug: str) -> str:
    return (
        f'  <link rel="alternate" hreflang="en" href="{ORIGIN}/item/{slug}/" />\n'
        f'  <link rel="alternate" hreflang="pl" href="{ORIGIN}/pl/item/{slug}/" />\n'
        f'  <link rel="alternate" hreflang="de" href="{ORIGIN}/de/item/{slug}/" />\n'
        f'  <link rel="alternate" hreflang="x-default" href="{ORIGIN}/item/{slug}/" />'
    )


def hreflang_cat(slug: str) -> str:
    return (
        f'  <link rel="alternate" hreflang="en" href="{ORIGIN}/{slug}/" />\n'
        f'  <link rel="alternate" hreflang="pl" href="{ORIGIN}/pl/{slug}/" />\n'
        f'  <link rel="alternate" hreflang="de" href="{ORIGIN}/de/{slug}/" />\n'
        f'  <link rel="alternate" hreflang="x-default" href="{ORIGIN}/{slug}/" />'
    )


def thumbs(p: dict, ui: dict) -> str:
    pid = item_id(p)
    imgs = [f"/img/products/{pid}.webp"]
    for n in (2, 3):
        if (ROOT / "img" / "products" / f"{pid}-{n}.webp").exists():
            imgs.append(f"/img/products/{pid}-{n}.webp")
    while len(imgs) < 3:
        imgs.append("")
    bits = []
    for i, src in enumerate(imgs):
        cls = "is-on" if i == 0 else ""
        label = escape(ui["photo"].format(n=i + 1))
        if src:
            bits.append(
                f'<button type="button" data-src="{src}" class="{cls}" aria-label="{label}">'
                f'<img src="{src}" alt="" /></button>'
            )
        else:
            bits.append(f'<button type="button" class="is-empty" aria-label="{label}"></button>')
    return "".join(bits)


LOCALE_ITEM_IDS: set[str] = set()


def item_href(p: dict, lang: str) -> str:
    if p.get("id") in LOCALE_ITEM_IDS:
        return f"/{lang}/item/{p['slug']}/"
    return f"/item/{p['slug']}/"


def card(p: dict, lang: str, ui: dict) -> str:
    pill = f'<span class="pill">{escape(ui["popular"])}</span>' if p.get("popular") else ""
    tags = f'<span class="card-tags">{pill}</span>' if pill else ""
    title = escape(p["title"])
    return (
        f'<a class="card" href="{item_href(p, lang)}">'
        f'<div class="card-media">'
        f'<img src="/{p["image"]}" alt="{title}" width="400" height="400" loading="lazy" decoding="async" />'
        f"{tags}"
        f'<span class="price-chip">${float(p["price"]):.2f}</span>'
        f"</div>"
        f'<div class="card-body"><h3>{title}</h3>'
        f'<div class="seller-row"><span>{escape(p.get("sellerName") or "")}</span></div>'
        f"</div></a>"
    )


def head_common(lang: str) -> str:
    return f"""  <link rel="icon" href="/img/favicon.svg?v=3" type="image/svg+xml" />
  <link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png" />
  <link rel="manifest" href="/manifest.json?v=pwa12" />
  <script src="/js/pwa-boot.js?v=pwa11"></script>
  <meta name="theme-color" content="#FB2840" />
  <meta name="mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-title" content="KakoBuy Spreadsheet" />
  <link rel="apple-touch-icon" href="/img/apple-touch-icon.png" sizes="180x180" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/css/style.css?v=pwa15" />"""


def item_html(p: dict, related: list[dict], lang: str) -> str:
    ui = UI[lang]
    slug = p["slug"]
    url = f"{ORIGIN}/{lang}/item/{slug}/"
    title = p["title"]
    desc = ui["desc"].format(title=title, price=f"{float(p['price']):.2f}")
    img = f"{ORIGIN}/{p['image']}"
    info = loc_cat(lang, p.get("category") or "other", 0)
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": title,
        "image": img,
        "description": desc,
        "inLanguage": lang,
        "brand": {"@type": "Brand", "name": p.get("collection") or "Find"},
        "offers": {
            "@type": "Offer",
            "price": f"{float(p['price']):.2f}",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "url": url,
        },
    }
    buy = kakobuy_url(p.get("sourceUrl") or "")
    related_html = "".join(card(x, lang, ui) for x in related)
    home = f"/{lang}.html"
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)} {escape(ui["title_suf"])}</title>
  <meta name="description" content="{escape(desc)}" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <link rel="canonical" href="{url}" />
{hreflang_item(slug)}
  <meta property="og:type" content="product" />
  <meta property="og:title" content="{escape(title)} {escape(ui["title_suf"])}" />
  <meta property="og:description" content="{escape(desc)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{img}" />
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
{head_common(lang)}
</head>
<body data-page="item" data-lang="{lang}" data-item-id="{escape(str(p['id']))}">
  <div class="promo-bar" id="promo"></div>
  <header class="site-header" id="site-header"></header>
  <div class="overlay" id="overlay"></div>
  <aside class="mobile-nav" id="mobile-nav"></aside>
  <main>
    <section class="section">
      <div class="wrap">
        <div class="crumbs" id="item-crumbs"><a href="{home}">{escape(ui["home"])}</a> / <a href="/{lang}/{escape(p.get("category") or "other")}/">{escape(info["label"])}</a> / <span>{escape(p.get("collection") or "")}</span></div>
        <div class="item-grid" id="item-root">
          <div class="item-gallery">
            <div class="item-shot"><img id="item-main" src="/{p["image"]}" alt="{escape(title)}" /></div>
            <div class="item-thumbs" id="item-thumbs">{thumbs(p, ui)}</div>
          </div>
          <div class="buy-box">
            <h1>{escape(title)}</h1>
            <div class="price">${float(p["price"]):.2f}</div>
            <p>{escape(ui["buy"])}</p>
            <div style="margin-top:22px">
              <a class="btn btn-solid" href="{escape(buy)}" target="_blank" rel="noopener">{escape(ui["view"])}</a>
              <p class="buy-note">{escape(ui["note"])}</p>
            </div>
          </div>
        </div>
        <aside class="qc-tips">
          <h2>{escape(ui["qc_h2"])}</h2>
          <ol>
            <li>{escape(ui["qc_1"])}</li>
            <li>{escape(ui["qc_2"])}</li>
            <li>{escape(ui["qc_3"])}</li>
          </ol>
        </aside>
      </div>
    </section>
    <section class="section soft">
      <div class="wrap">
        <div class="section-head"><div><h2>{escape(ui["related_h2"])}</h2><p>{escape(ui["related_p"])}</p></div></div>
        <div class="product-grid" id="related-grid">{related_html}</div>
      </div>
    </section>
  </main>
  <footer class="site-footer" id="site-footer"></footer>
  <script src="/js/site.js?v=pwa24"></script>
  <script src="/js/app.js?v=pwa17"></script>
</body>
</html>
"""


def category_html(slug: str, items: list[dict], all_slugs: list[str], lang: str) -> str:
    ui = UI[lang]
    n = len(items)
    info = loc_cat(lang, slug, n)
    url = f"{ORIGIN}/{lang}/{slug}/"
    cards = "".join(card(p, lang, ui) for p in items)
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": info["title"],
        "url": url,
        "description": info["desc"],
        "inLanguage": lang,
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": n,
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i,
                    "url": f"{ORIGIN}{item_href(p, lang)}",
                    "name": p["title"],
                }
                for i, p in enumerate(items[:40], 1)
            ],
        },
    }
    options = "".join(
        f'<option value="{escape(s)}"{" selected" if s == slug else ""}>{escape(loc_cat(lang, s, 0)["label"])}</option>'
        for s in all_slugs
        if s not in RESERVED_SLUGS
    )
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(info["title"])}</title>
  <meta name="description" content="{escape(info["desc"])}" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <link rel="canonical" href="{url}" />
{hreflang_cat(slug)}
  <meta property="og:title" content="{escape(info["title"])}" />
  <meta property="og:description" content="{escape(info["desc"])}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{ORIGIN}/img/og.png" />
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
{head_common(lang)}
</head>
<body data-page="category" data-lang="{lang}" data-cat="{escape(slug)}">
  <div class="promo-bar" id="promo"></div>
  <header class="site-header" id="site-header"></header>
  <div class="overlay" id="overlay"></div>
  <aside class="mobile-nav" id="mobile-nav"></aside>
  <main>
    <section class="page-hero">
      <div class="wrap">
        <div class="crumbs"><a href="/{lang}.html">{escape(ui["home"])}</a> / <span>{escape(info["label"])}</span></div>
        <h1>{escape(info["h1"])}</h1>
        <p class="lede">{escape(info["desc"])} {escape(ui["updated"].format(date=fmt_date(lang)))}</p>
      </div>
    </section>
    <section class="section tight">
      <div class="wrap">
        <div class="toolbar">
          <div class="search">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
            <input id="catalog-search" placeholder="{escape(ui["search_ph"].format(label=info["label"].lower()))}" />
          </div>
          <select id="catalog-cat"><option value="">{escape(ui["all_cats"])}</option>{options}</select>
          <select id="catalog-sort">
            <option value="featured">{escape(ui["latest"])}</option>
            <option value="price-asc">{escape(ui["price_asc"])}</option>
            <option value="price-desc">{escape(ui["price_desc"])}</option>
          </select>
        </div>
        <p id="result-count" class="lede" style="margin-bottom:16px">{escape(ui["showing"].format(n=n))}</p>
        <div class="product-grid" id="catalog-grid">{cards}</div>
        <div class="cta-row">
          <a class="btn btn-solid" href="https://ikako.vip/r/jm98p" target="_blank" rel="noopener">{escape(ui["signup"])}</a>
        </div>
      </div>
    </section>
  </main>
  <footer class="site-footer" id="site-footer"></footer>
  <script src="/js/products.js"></script>
  <script src="/js/site.js?v=pwa24"></script>
  <script src="/js/app.js?v=pwa17"></script>
</body>
</html>
"""


def write_locale_pages(products: list[dict]) -> None:
    by_cat = defaultdict(list)
    for p in products:
        slug = p.get("category") or "other"
        if slug in RESERVED_SLUGS:
            continue
        by_cat[slug].append(p)
    slugs = sorted(by_cat.keys())
    for lang in ("pl", "de"):
        for slug, items in by_cat.items():
            folder = ROOT / lang / slug
            if folder.exists():
                shutil.rmtree(folder)
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "index.html").write_text(category_html(slug, items, slugs, lang), encoding="utf-8")
        print(f"  {lang} categories: {len(slugs)}")
        item_root = ROOT / lang / "item"
        if item_root.exists():
            shutil.rmtree(item_root)
        locale_items = [p for p in products if p.get("id") in LOCALE_ITEM_IDS]
        n = 0
        for p in locale_items:
            related = [x for x in by_cat.get(p.get("category") or "other", []) if x["id"] != p["id"]][:8]
            folder = item_root / p["slug"]
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "index.html").write_text(item_html(p, related, lang), encoding="utf-8")
            n += 1
        print(f"  {lang} items: {n}")


def patch_en_hreflang(products: list[dict]) -> None:
    n = 0
    for p in products:
        path = ROOT / "item" / p["slug"] / "index.html"
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        html = re.sub(r'\n  <link rel="alternate" hreflang=[^>]*>', "", html)
        if p.get("id") in LOCALE_ITEM_IDS:
            block = hreflang_item(p["slug"])
            canon = f'<link rel="canonical" href="{ORIGIN}/item/{p["slug"]}/" />'
            if canon in html and f'{ORIGIN}/pl/item/{p["slug"]}/' not in html:
                html = html.replace(canon, canon + "\n" + block, 1)
                n += 1
        path.write_text(html, encoding="utf-8")
    print(f"en item hreflang: {n}")
    cats = {p.get("category") or "other" for p in products} - RESERVED_SLUGS
    c = 0
    for slug in cats:
        path = ROOT / slug / "index.html"
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        if f"{ORIGIN}/pl/{slug}/" in html and "hreflang=\"pl\"" in html:
            continue
        block = hreflang_cat(slug)
        html = re.sub(r'\s*<link rel="alternate" hreflang=[^>]*>', "", html)
        canon = f'<link rel="canonical" href="{ORIGIN}/{slug}/" />'
        if canon in html:
            html = html.replace(canon, canon + "\n" + block, 1)
            path.write_text(html, encoding="utf-8")
            c += 1
    print(f"en category hreflang: {c}")


def patch_landing(products: list[dict]) -> None:
    print("skip landing cats — locale homes share the English layout")


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
        "/about.html",
        "/contact.html",
        "/privacy.html",
        "/disclaimer.html",
        "/terms.html",
    ]
    cats = sorted({p.get("category") or "other" for p in products} - RESERVED_SLUGS)
    urls: list[str] = []

    def loc_url(path: str, extra: str = "") -> str:
        body = f"    <loc>{ORIGIN}{path}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>weekly</changefreq>"
        if extra:
            body += "\n" + extra
        return "  <url>\n" + body + "\n  </url>"

    home_alts = "\n".join(
        [
            f'    <xhtml:link rel="alternate" hreflang="en" href="{ORIGIN}/"/>',
            f'    <xhtml:link rel="alternate" hreflang="pl" href="{ORIGIN}/pl.html"/>',
            f'    <xhtml:link rel="alternate" hreflang="de" href="{ORIGIN}/de.html"/>',
            f'    <xhtml:link rel="alternate" hreflang="x-default" href="{ORIGIN}/"/>',
        ]
    )
    for path in pages:
        extra = home_alts if path in {"/", "/pl.html", "/de.html"} else ""
        urls.append(loc_url(path, extra))
    for slug in cats:
        alts = "\n".join(
            [
                f'    <xhtml:link rel="alternate" hreflang="en" href="{ORIGIN}/{slug}/"/>',
                f'    <xhtml:link rel="alternate" hreflang="pl" href="{ORIGIN}/pl/{slug}/"/>',
                f'    <xhtml:link rel="alternate" hreflang="de" href="{ORIGIN}/de/{slug}/"/>',
                f'    <xhtml:link rel="alternate" hreflang="x-default" href="{ORIGIN}/{slug}/"/>',
            ]
        )
        urls.append(loc_url(f"/{slug}/", alts))
        urls.append(loc_url(f"/pl/{slug}/", alts))
        urls.append(loc_url(f"/de/{slug}/", alts))
    for p in products:
        slug = p["slug"]
        if p.get("id") in LOCALE_ITEM_IDS:
            alts = "\n".join(
                [
                    f'    <xhtml:link rel="alternate" hreflang="en" href="{ORIGIN}/item/{slug}/"/>',
                    f'    <xhtml:link rel="alternate" hreflang="pl" href="{ORIGIN}/pl/item/{slug}/"/>',
                    f'    <xhtml:link rel="alternate" hreflang="de" href="{ORIGIN}/de/item/{slug}/"/>',
                    f'    <xhtml:link rel="alternate" hreflang="x-default" href="{ORIGIN}/item/{slug}/"/>',
                ]
            )
            urls.append(loc_url(f"/item/{slug}/", alts))
            urls.append(loc_url(f"/pl/item/{slug}/", alts))
            urls.append(loc_url(f"/de/item/{slug}/", alts))
        else:
            urls.append(loc_url(f"/item/{slug}/"))
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    print(f"sitemap.xml: {len(urls)} urls")


def main() -> None:
    global LOCALE_ITEM_IDS
    products = load_local_products()
    LOCALE_ITEM_IDS = {p["id"] for p in products if p.get("popular") or p.get("featured")}
    print("products", len(products), "locale items", len(LOCALE_ITEM_IDS))
    write_locale_pages(products)
    patch_en_hreflang(products)
    patch_landing(products)
    write_sitemap(products)
    print("done i18n")


if __name__ == "__main__":
    main()
