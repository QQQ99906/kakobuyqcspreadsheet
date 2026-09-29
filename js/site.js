window.SK = window.SK || {};

SK.origin = "https://kakobuyqcspreadsheet.com";
SK.root = (() => {
  const el = document.querySelector('script[src*="js/site.js"]');
  const src = el ? (el.getAttribute("src") || "") : "";
  if (src && !/^https?:\/\//i.test(src) && !src.startsWith("/")) {
    return src.replace(/js\/site\.js(\?.*)?$/, "");
  }
  const path = location.pathname || "/";
  const sub = path.match(/^(\/kakobuyqcspreadsheet\/)/);
  if (sub) return sub[1];
  if (src.startsWith("/")) return "/";
  if (/^https?:\/\//i.test(src)) {
    try {
      return new URL(src).pathname.replace(/js\/site\.js(\?.*)?$/, "");
    } catch (_) {}
  }
  return src.replace(/js\/site\.js(\?.*)?$/, "");
})();
SK.asset = (path) => {
  const clean = String(path || "").replace(/^\//, "");
  const loc = location.pathname || "";
  if (loc.indexOf("/kakobuyqcspreadsheet") === 0) return "/kakobuyqcspreadsheet/" + clean;
  return SK.root + clean;
};
if (!document.querySelector('script[src*="js/analytics.js"]')) {
  const analytics = document.createElement("script");
  analytics.src = SK.asset("js/analytics.js");
  document.head.appendChild(analytics);
}

SK.pwa = SK.pwa || { deferred: null };
if (typeof SK.pwa.deferred === "undefined") SK.pwa.deferred = null;
SK.pwaStandalone = () =>
  window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
SK.injectPwaHead = () => {
  if (document.querySelector('link[rel="manifest"]')) return;
  const tags = [
    ["link", { rel: "manifest", href: SK.asset("manifest.json?v=pwa12") }],
    ["meta", { name: "theme-color", content: "#FB2840" }],
    ["meta", { name: "mobile-web-app-capable", content: "yes" }],
    ["meta", { name: "apple-mobile-web-app-capable", content: "yes" }],
    ["meta", { name: "apple-mobile-web-app-status-bar-style", content: "default" }],
    ["meta", { name: "apple-mobile-web-app-title", content: "KakoBuy Spreadsheet" }],
    ["meta", { name: "application-name", content: "KakoBuy Spreadsheet" }],
    ["link", { rel: "apple-touch-icon", href: SK.asset("img/apple-touch-icon.png"), sizes: "180x180" }],
  ];
  tags.forEach(([tag, attrs]) => {
    const el = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
    document.head.appendChild(el);
  });
};
SK.injectPwaHead();
SK.injectTrustHead = () => {
  [
    ["privacy-policy", "/privacy.html"],
    ["terms-of-service", "/terms.html"],
    ["author", "/about.html"],
  ].forEach(([rel, href]) => {
    if (document.querySelector(`link[rel="${rel}"]`)) return;
    const el = document.createElement("link");
    el.setAttribute("rel", rel);
    el.setAttribute("href", href);
    document.head.appendChild(el);
  });
};
SK.injectTrustHead();
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch(() => {});
}
window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  SK.pwa.deferred = e;
  SK.refreshPwaUi();
});
window.addEventListener("appinstalled", () => {
  SK.pwa.deferred = null;
  try { localStorage.setItem("sk-pwa-installed", "1"); } catch (_) {}
  SK.track("pwa_installed");
  SK.refreshPwaUi();
});
SK.pwaDismissed = () => {
  try {
    const t = Number(localStorage.getItem("sk-pwa-dismiss-v2") || 0);
    return t && Date.now() - t < 30 * 24 * 60 * 60 * 1000;
  } catch (_) { return false; }
};
SK.pwaInstalledFlag = () => {
  try { return localStorage.getItem("sk-pwa-installed") === "1"; } catch (_) { return false; }
};
SK.pwaIos = () =>
  (/iphone|ipad|ipod/i.test(navigator.userAgent) && !window.MSStream) ||
  (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
SK.pwaAndroid = () => /android/i.test(navigator.userAgent);
SK.showInstallGuide = () => {
  const guide = document.getElementById("ios-guide");
  const title = document.getElementById("pwa-guide-title");
  const gif = document.getElementById("pwa-guide-gif");
  const steps = document.getElementById("pwa-guide-steps");
  if (!guide || !gif || !steps) return;
  let data;
  if (SK.pwaIos()) {
    data = {
      title: "Add to Home Screen",
      src: SK.asset("img/ios-a2hs.gif"),
      alt: "Safari: tap Share, then Add to Home Screen",
      steps: [
        "Tap <b>Share</b> or the <b>•••</b> button",
        "Tap <b>Add to Home Screen</b>",
        "Tap <b>Add</b>",
      ],
    };
  } else if (SK.pwaAndroid()) {
    data = {
      title: "Install app",
      src: SK.asset("img/android-a2hs.gif"),
      alt: "Chrome: tap menu, then Install app",
      steps: [
        "Tap the <b>⋮</b> menu at the top right",
        "Tap <b>Install app</b> or <b>Add to Home screen</b>",
        "Tap <b>Install</b>",
      ],
    };
  } else {
    data = {
      title: "Install on this computer",
      src: SK.asset("img/icon-512.png"),
      alt: "KakoBuy icon",
      steps: [
        "In <b>Chrome</b> or <b>Edge</b>, click the install icon in the address bar",
        "Or click <b>Add</b> when the system prompt appears",
        "Safari: <b>File → Add to Dock</b>",
      ],
    };
  }
  if (title) title.textContent = data.title;
  gif.src = data.src;
  gif.alt = data.alt;
  steps.innerHTML = data.steps.map((s) => `<li>${s}</li>`).join("");
  guide.classList.add("is-on");
};
SK.pwaChromium = () =>
  /Chrome|Edg|Chromium/i.test(navigator.userAgent) && !/iPhone|iPad|CriOS|EdgiOS/i.test(navigator.userAgent);
SK.waitForInstallPrompt = async (ms) => {
  const start = Date.now();
  while (!SK.pwa.deferred && Date.now() - start < ms) {
    await new Promise((r) => setTimeout(r, 120));
  }
  return SK.pwa.deferred;
};
SK.installPwa = async (source) => {
  const from = source || "unknown";
  SK.track("pwa_install_click", { source: from, page_path: location.pathname });
  const addBtn = document.getElementById("pwa-add");
  const headerBtn = document.getElementById("pwa-header-install");
  const prev = addBtn ? addBtn.textContent : "";
  const prevH = headerBtn ? headerBtn.textContent : "";
  if (addBtn) addBtn.textContent = "…";
  if (headerBtn) headerBtn.textContent = "…";
  const dp = await SK.waitForInstallPrompt(SK.pwaChromium() ? 2800 : 400);
  if (addBtn) addBtn.textContent = prev || "Add";
  if (headerBtn) headerBtn.textContent = prevH || SK.t("addDesktop");
  if (dp && typeof dp.prompt === "function") {
    try {
      dp.prompt();
      const choice = await dp.userChoice.catch(() => ({ outcome: "dismissed" }));
      SK.pwa.deferred = null;
      if (choice && choice.outcome === "accepted") {
        try { localStorage.setItem("sk-pwa-installed", "1"); } catch (_) {}
        SK.track("pwa_install_accepted", { source: from, page_path: location.pathname });
        const guide = document.getElementById("ios-guide");
        if (guide) guide.classList.remove("is-on");
        const banner = document.getElementById("pwa-banner");
        if (banner) banner.classList.add("is-off");
        const headerBtn = document.getElementById("pwa-header-install");
        if (headerBtn) headerBtn.classList.add("is-off");
      } else {
        SK.track("pwa_install_dismissed", { source: from, page_path: location.pathname });
      }
      SK.refreshPwaUi();
      return;
    } catch (_) {
      SK.pwa.deferred = null;
    }
  }
  SK.track("pwa_guide_shown", { source: from, page_path: location.pathname });
  SK.showInstallGuide();
};
SK.refreshPwaUi = () => {
  const banner = document.getElementById("pwa-banner");
  const headerBtn = document.getElementById("pwa-header-install");
  const hide = SK.pwaStandalone();
  if (headerBtn) headerBtn.classList.toggle("is-off", hide);
  if (banner) banner.classList.toggle("is-off", hide);
};
SK.mountPwa = () => {
  let banner = document.getElementById("pwa-banner");
  let guide = document.getElementById("ios-guide");
  const iconSrc = SK.asset("img/icon-192.png");
  const guideSrc = SK.asset("img/ios-a2hs.gif");
  if (!banner) {
    banner = document.createElement("div");
    banner.id = "pwa-banner";
    banner.className = "pwa-banner";
    banner.innerHTML = `
      <img src="${iconSrc}" alt="" width="44" height="44" />
      <p>Add to home screen<span>Tap Add to install</span></p>
      <button type="button" class="btn btn-solid" id="pwa-add">Add</button>
      <button type="button" class="pwa-dismiss" id="pwa-dismiss" aria-label="Not now">×</button>
    `;
    document.body.appendChild(banner);
  } else {
    const img = banner.querySelector("img");
    if (img) img.src = iconSrc;
  }
  if (!guide) {
    guide = document.createElement("aside");
    guide.id = "ios-guide";
    guide.className = "ios-guide";
    guide.innerHTML = `
      <div class="ios-guide-top">
        <p id="pwa-guide-title">Add to Home Screen</p>
        <button type="button" class="pwa-dismiss" id="ios-guide-dismiss" aria-label="Close">×</button>
      </div>
      <img id="pwa-guide-gif" src="${guideSrc}" alt="Add to Home Screen" width="420" height="280" />
      <ol id="pwa-guide-steps"></ol>
    `;
    document.body.appendChild(guide);
  } else {
    const gif = document.getElementById("pwa-guide-gif");
    if (gif && (!gif.getAttribute("src") || gif.getAttribute("src").startsWith("/img/"))) {
      gif.src = guideSrc;
    }
  }
  const addBtn = document.getElementById("pwa-add");
  if (addBtn && !addBtn.dataset.bound) {
    addBtn.dataset.bound = "1";
    addBtn.addEventListener("click", (e) => {
      e.preventDefault();
      SK.installPwa("banner");
    });
  }
  const dismissBtn = document.getElementById("pwa-dismiss");
  if (dismissBtn && !dismissBtn.dataset.bound) {
    dismissBtn.dataset.bound = "1";
    dismissBtn.addEventListener("click", () => {
      banner.classList.add("is-off");
      const headerBtn = document.getElementById("pwa-header-install");
      if (headerBtn) headerBtn.classList.add("is-off");
      SK.track("pwa_dismiss");
    });
  }
  const closeGuide = document.getElementById("ios-guide-dismiss");
  if (closeGuide && !closeGuide.dataset.bound) {
    closeGuide.dataset.bound = "1";
    closeGuide.addEventListener("click", () => {
      guide.classList.remove("is-on");
      SK.track("pwa_guide_dismiss");
    });
  }
  SK.refreshPwaUi();
};
SK.itemName = (value) => String(value || "").replace(/\s+/g, " ").trim().slice(0, 100);
SK.gaItem = (p) => {
  if (!p) return [];
  return [{
    item_id: String(p.id || ""),
    item_name: SK.itemName(p.title),
    item_category: p.category || "",
    price: Number(p.price) || 0,
    quantity: 1,
  }];
};
SK._trackQueue = SK._trackQueue || [];
SK.track = (name, params) => {
  const payload = Object.assign({ transport_type: "beacon" }, params || {});
  const send = () => {
    try {
      if (typeof gtag !== "function") return false;
      gtag("event", name, payload);
    } catch (_) {}
    return true;
  };
  if (send()) return;
  SK._trackQueue.push(send);
  if (SK._trackFlush) return;
  SK._trackFlush = setInterval(() => {
    if (typeof gtag !== "function") return;
    const queue = SK._trackQueue.splice(0);
    clearInterval(SK._trackFlush);
    SK._trackFlush = null;
    queue.forEach((fn) => fn());
  }, 50);
  setTimeout(() => {
    if (!SK._trackFlush) return;
    clearInterval(SK._trackFlush);
    SK._trackFlush = null;
  }, 8000);
};
document.addEventListener("click", (e) => {
  const a = e.target.closest("a[href*='kakobuy.com'], a[href*='ikako.vip']");
  if (!a) return;
  const href = a.href || "";
  if (/\/register/i.test(href) || /ikako\.vip\/r\//i.test(href)) {
    SK.track("signup_kakobuy", { link_url: href, page_path: location.pathname });
    return;
  }
  const id = document.body.getAttribute("data-item-id") || a.getAttribute("data-buy") || "";
  const list = typeof SK.products === "function" ? SK.products() : [];
  const item = id
    ? list.find((p) => String(p.id) === String(id) || String(p.id).replace(/^p-/, "") === String(id).replace(/^p-/, ""))
    : null;
  if (item) {
    SK.track("buy_kakobuy", {
      agent: "kakobuy",
      item_id: String(item.id),
      item_name: SK.itemName(item.title),
      currency: "USD",
      value: Number(item.price) || 0,
      items: SK.gaItem(item),
      link_url: href,
      page_path: location.pathname,
    });
  } else {
    const titleEl = document.querySelector("#item-root h1, .buy-box h1");
    const priceEl = document.querySelector("#item-root .price, .buy-box .price");
    const title = titleEl ? titleEl.textContent.trim() : "";
    const price = priceEl ? parseFloat(String(priceEl.textContent).replace(/[^0-9.]/g, "")) : 0;
    SK.track("buy_kakobuy", {
      agent: "kakobuy",
      item_id: id || "",
      item_name: SK.itemName(title),
      currency: "USD",
      value: price || 0,
      link_url: href,
      page_path: location.pathname,
    });
  }
});
document.addEventListener("click", (e) => {
  const a = e.target.closest("a[href]");
  if (!a) return;
  let url;
  try {
    url = new URL(a.href, location.href);
  } catch (_) {
    return;
  }
  if (url.origin === location.origin) return;
  if (url.protocol !== "http:" && url.protocol !== "https:") return;
  const params = {
    event_category: "outbound",
    event_label: (a.textContent || a.getAttribute("aria-label") || "link").trim().slice(0, 80),
    link_url: a.href,
    link_domain: url.hostname,
    outbound: true,
    page_path: location.pathname,
  };
  const id = document.body.getAttribute("data-item-id") || a.getAttribute("data-buy") || "";
  const list = typeof SK.products === "function" ? SK.products() : [];
  const item = id
    ? list.find((p) => String(p.id) === String(id) || String(p.id).replace(/^p-/, "") === String(id).replace(/^p-/, ""))
    : null;
  if (item) {
    params.item_id = String(item.id);
    params.item_name = SK.itemName(item.title);
    params.currency = "USD";
    params.value = Number(item.price) || 0;
    params.items = SK.gaItem(item);
  }
  SK.track("click", params);
  SK.track("outbound_click", params);
});
document.addEventListener("click", (e) => {
  const card = e.target.closest("a.card");
  if (!card) return;
  const href = card.getAttribute("href") || "";
  if (!/\/item\//.test(href)) return;
  const idMatch = href.match(/(\d{5,})\/?$/);
  const id = idMatch ? idMatch[1] : "";
  const list = typeof SK.products === "function" ? SK.products() : [];
  const item = id ? list.find((p) => String(p.id).replace(/^p-/, "") === id) : null;
  const title = item ? item.title : ((card.querySelector("h3") || {}).textContent || "");
  const name = SK.itemName(title);
  if (!name) return;
  SK.track("select_item", {
    item_id: String(item ? item.id : id),
    item_name: name,
    item_list_name: document.body.getAttribute("data-page") || "",
    items: item ? SK.gaItem(item) : [{ item_id: String(id), item_name: name, quantity: 1 }],
  });
});
SK.signup = "https://ikako.vip/r/jm98p";
SK.discord = "https://discord.gg/7DRMaMAADv";
SK.aff = "jm98p";

SK.site = {
  name: "kakobuy spreadsheet",
  email: "hello@kakobuyqcspreadsheet.com",
  updated: "21 Sept 2026",
};

SK.pages = [
  { href: "index.html", label: "Home", id: "home" },
  { href: "spreadsheet.html", label: "KakoBuy Spreadsheet", id: "spreadsheet" },
  { href: "articles.html", label: "Articles", id: "articles" },
  { href: "coupons.html", label: "Coupons", id: "coupons" },
  { href: "faq.html", label: "FAQ", id: "faq" },
  { href: "qc.html", label: "QC Images", id: "qc" },
];
SK.langs = [
  { code: "en", label: "EN" },
  { code: "pl", label: "PL" },
  { code: "de", label: "DE" },
];
SK.catSlugs = ["shoes","t-shirts","accessories","hoodies","pants","jackets","jersey","watches","headwear","glasses","sets","bricks","perfume","underwear","other"];
SK.I18N = {
  en: {
    nav_home: "Home", nav_spreadsheet: "KakoBuy Spreadsheet", nav_articles: "Articles",
    nav_coupons: "Coupons", nav_faq: "FAQ", nav_qc: "QC Images",
    popular: "Popular", showing: "Showing {n} finds", addDesktop: "Add to desktop",
    search: "Search", signup: "Sign up for KakoBuy", items: "items",
    cat_shoes: "Designer Shoes", cat_tshirts: "Tees & Jerseys", cat_accessories: "Premium Accessories",
    cat_hoodies: "Verified Hoodies", cat_pants: "Pants", cat_jackets: "Jackets & Outerwear",
    cat_jersey: "Jerseys", cat_watches: "Watches & Jewelry", cat_headwear: "Hats & Caps",
    cat_glasses: "Sunglasses", cat_sets: "Sets", cat_bricks: "Bricks & Toys",
    cat_perfume: "Perfume", cat_underwear: "Underwear", cat_other: "Other finds",
  },
  pl: {
    nav_home: "Strona główna", nav_spreadsheet: "KakoBuy Spreadsheet", nav_articles: "Artykuły",
    nav_coupons: "Kupony", nav_faq: "FAQ", nav_qc: "Zdjęcia QC",
    popular: "Popularne", showing: "Wyświetlono {n} pozycji", addDesktop: "Dodaj na pulpit",
    search: "Szukaj", signup: "Załóż konto KakoBuy", items: "pozycji",
    cat_shoes: "Buty designerskie", cat_tshirts: "Koszulki i jersey", cat_accessories: "Akcesoria",
    cat_hoodies: "Bluzy", cat_pants: "Spodnie", cat_jackets: "Kurtki",
    cat_jersey: "Jersey", cat_watches: "Zegarki i biżuteria", cat_headwear: "Czapki",
    cat_glasses: "Okulary", cat_sets: "Komplety", cat_bricks: "Klocki i zabawki",
    cat_perfume: "Perfumy", cat_underwear: "Bielizna", cat_other: "Inne znaleziska",
  },
  de: {
    nav_home: "Start", nav_spreadsheet: "KakoBuy Spreadsheet", nav_articles: "Artikel",
    nav_coupons: "Gutscheine", nav_faq: "FAQ", nav_qc: "QC-Fotos",
    popular: "Beliebt", showing: "{n} Funde angezeigt", addDesktop: "Zum Desktop hinzufügen",
    search: "Suche", signup: "KakoBuy-Konto eröffnen", items: "Funde",
    cat_shoes: "Designer-Schuhe", cat_tshirts: "Shirts & Jerseys", cat_accessories: "Accessoires",
    cat_hoodies: "Hoodies", cat_pants: "Hosen", cat_jackets: "Jacken",
    cat_jersey: "Trikots", cat_watches: "Uhren & Schmuck", cat_headwear: "Mützen & Caps",
    cat_glasses: "Sonnenbrillen", cat_sets: "Sets", cat_bricks: "Steine & Spielzeug",
    cat_perfume: "Parfum", cat_underwear: "Unterwäsche", cat_other: "Weitere Funde",
  },
};
SK.currentLang = () => {
  const path = location.pathname || "";
  if (path === "/pl.html" || path === "/pl" || path.startsWith("/pl/")) return "pl";
  if (path === "/de.html" || path === "/de" || path.startsWith("/de/")) return "de";
  const body = document.body && document.body.getAttribute("data-lang");
  if (body === "pl" || body === "de") return body;
  const htmlLang = (document.documentElement.getAttribute("lang") || "").slice(0, 2).toLowerCase();
  if (htmlLang === "pl" || htmlLang === "de") return htmlLang;
  return "en";
};
SK.t = (key, vars) => {
  const pack = SK.I18N[SK.currentLang()] || SK.I18N.en;
  let s = pack[key] || SK.I18N.en[key] || key;
  if (vars) Object.keys(vars).forEach((k) => { s = s.replace("{" + k + "}", vars[k]); });
  return s;
};
SK.homeHref = () => (SK.currentLang() === "en" ? SK.asset("index.html") : SK.asset(SK.currentLang() + ".html"));
SK.langHref = (code) => {
  let path = location.pathname || "/";
  path = path.replace(/^\/kakobuyqcspreadsheet(?=\/|$)/, "") || "/";
  if (path === "/pl.html" || path === "/de.html" || path === "/" || path === "/index.html" || path === "/pl" || path === "/de") {
    if (code === "en") return SK.asset("index.html");
    return SK.asset(code + ".html");
  }
  const stripped = path.replace(/^\/(pl|de)(?=\/)/, "") || "/";
  const item = stripped.match(/^\/item\/([^/]+)\/?$/);
  if (item) return SK.asset((code === "en" ? "" : code + "/") + "item/" + item[1] + "/");
  const cat = stripped.match(/^\/([a-z0-9-]+)\/?$/);
  if (cat && SK.catSlugs.indexOf(cat[1]) !== -1) {
    return SK.asset((code === "en" ? "" : code + "/") + cat[1] + "/");
  }
  if (code === "en") return SK.asset("index.html");
  return SK.asset(code + ".html");
};
SK.langSwitchHtml = () => {
  const cur = SK.currentLang();
  return `<nav class="lang-switch" aria-label="Language">${SK.langs.map((l) =>
    `<a href="${SK.langHref(l.code)}" hreflang="${l.code}" lang="${l.code}"${l.code === cur ? ' class="is-on" aria-current="true"' : ""}>${l.label}</a>`
  ).join("")}</nav>`;
};

SK.categories = [
  { slug: "shoes", label: "Designer Shoes", emoji: "🥾", count: "745+", hot: true },
  { slug: "t-shirts", label: "Tees & Jerseys", emoji: "🎽", count: "640+", hot: true },
  { slug: "accessories", label: "Premium Accessories", emoji: "🕶️", count: "690+" },
  { slug: "hoodies", label: "Verified Hoodies", emoji: "⭐", count: "360+", hot: true },
  { slug: "pants", label: "Pants", emoji: "🩳", count: "390+" },
  { slug: "jackets", label: "Jackets & Outerwear", emoji: "🧥", count: "250+" },
  { slug: "jersey", label: "Jerseys", emoji: "⚽", count: "300+" },
  { slug: "watches", label: "Watches & Jewelry", emoji: "⌚", count: "120+" },
];

SK.money = (n) => "$" + Number(n || 0).toFixed(2);

SK.listing = (sourceUrl) => {
  const url = String(sourceUrl || "");
  const weidian = url.match(/itemID=(\d+)/i);
  if (weidian || /weidian\.com/i.test(url)) {
    const id = weidian ? weidian[1] : "";
    const raw = id ? `https://weidian.com/item.html?itemID=${id}` : url;
    return { id, channel: "weidian", url: raw };
  }
  return { id: "", channel: "weidian", url };
};

SK.kakobuyUrl = (sourceUrl) => {
  const L = SK.listing(sourceUrl);
  if (L.channel === "weidian" && L.id) {
    return `https://www.kakobuy.com/item/details?url=https%3A%2F%2Fweidian.com%2Fitem.html%3FitemID%3D${L.id}&affcode=${SK.aff}`;
  }
  return `https://www.kakobuy.com/item/details?url=${encodeURIComponent(L.url)}&affcode=${SK.aff}`;
};

SK.slugify = (text) => String(text || "")
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, "-")
  .replace(/^-+|-+$/g, "")
  .replace(/-+/g, "-")
  .slice(0, 60);
SK.itemSlug = (p) => {
  if (p && p.slug) return p.slug;
  const id = String((p && p.id) || "").replace(/^p-/, "");
  const base = SK.slugify(p && p.title);
  return (base ? base + "-" : "") + id;
};
SK.itemHref = (p) => {
  const loc = SK.currentLang();
  const hasLocale = loc === "en" || (p && (p.popular || p.featured));
  const pre = hasLocale && loc !== "en" ? loc + "/" : "";
  return SK.asset(pre + "item/" + SK.itemSlug(p) + "/");
};
SK.catHref = (slug) => {
  if (!slug) return SK.asset("spreadsheet.html");
  const loc = SK.currentLang();
  const pre = loc === "en" ? "" : loc + "/";
  return SK.asset(pre + encodeURIComponent(slug) + "/");
};
SK.catLabel = (slug) => {
  const map = {
    shoes: "cat_shoes", "t-shirts": "cat_tshirts", accessories: "cat_accessories",
    hoodies: "cat_hoodies", pants: "cat_pants", jackets: "cat_jackets",
    jersey: "cat_jersey", watches: "cat_watches", headwear: "cat_headwear",
    glasses: "cat_glasses", sets: "cat_sets", bricks: "cat_bricks",
    perfume: "cat_perfume", underwear: "cat_underwear", other: "cat_other",
  };
  return SK.t(map[slug] || "cat_other");
};

SK.products = () => (SK.catalog && SK.catalog.products) || [];

SK.card = (p) => {
  const tags = [
    p.popular ? `<span class="pill">${SK.t("popular")}</span>` : "",
  ].filter(Boolean).join("");
  return `<a class="card" href="${SK.itemHref(p)}">
    <div class="card-media">
      <img src="${SK.asset(p.image)}" alt="${escapeHtml(p.title)}" width="400" height="400" loading="lazy" decoding="async" />
      ${tags ? `<span class="card-tags">${tags}</span>` : ""}
      <span class="price-chip">${SK.money(p.price)}</span>
    </div>
    <div class="card-body">
      <h3>${escapeHtml(p.title)}</h3>
      <div class="seller-row">
        <span>${escapeHtml(p.sellerName || "Verified seller")}</span>
        ${p.sales ? `<span>${p.sales}k</span>` : ""}
      </div>
    </div>
  </a>`;
};

function escapeHtml(s) {
  return String(s || "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

SK.mountChrome = (page) => {
  const promo = document.getElementById("promo");
  if (promo) {
    promo.innerHTML = `<a class="promo-track" href="${SK.signup}" target="_blank" rel="noopener"><img src="${SK.asset("img/promo-banner.png")}" alt="Kakobuy Exclusive: ¥3000 FREE +20% OFF Shipping" /></a>`;
  }

  const header = document.getElementById("site-header");
  if (header) {
    const links = SK.pages.map((p) => {
      const href = p.id === "home" ? SK.homeHref() : SK.asset(p.href);
      return `<a class="${p.id === page ? "is-on" : ""}" href="${href}">${SK.t("nav_" + p.id)}</a>`;
    }).join("");
    header.innerHTML = `<div class="wrap header-row">
      <div class="header-left">
        <a class="brand" href="${SK.homeHref()}">
          <span class="brand-mark"><img src="${SK.asset("img/logo-k.png")}" alt="" width="26" height="32" /></span>
          <span class="brand-copy"><strong><span>kakobuy</span> spreadsheet</strong></span>
        </a>
        <a class="btn btn-discord" href="${SK.discord}" target="_blank" rel="noopener" aria-label="Discord">
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19.27 5.33C17.94 4.71 16.5 4.26 15 4a.09.09 0 0 0-.07.03c-.18.33-.39.76-.53 1.09a16.09 16.09 0 0 0-4.8 0c-.14-.34-.35-.76-.54-1.09-.01-.02-.04-.03-.07-.03-1.5.26-2.93.71-4.27 1.33-.01 0-.02.01-.03.02-2.72 4.07-3.47 8.03-3.1 11.95 0 .02.01.04.03.05 1.8 1.32 3.53 2.12 5.24 2.65.03.01.06 0 .07-.02.4-.55.76-1.13 1.07-1.74.02-.04 0-.08-.04-.09-.57-.22-1.11-.48-1.64-.78-.04-.02-.04-.08-.01-.11.11-.08.22-.17.33-.25.02-.01.05-.01.07 0 3.44 1.57 7.15 1.57 10.55 0 .02-.01.05-.01.07 0 .11.09.22.17.33.26.04.03.04.09-.01.11-.52.31-1.07.56-1.64.78-.04.01-.05.06-.04.09.32.61.68 1.19 1.07 1.74.02.02.06.03.09.02 1.72-.53 3.45-1.33 5.25-2.65.02-.01.03-.03.03-.05.44-4.53-.73-8.46-3.1-11.95-.01-.01-.02-.02-.04-.02zM8.52 14.91c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12 0 1.17-.84 2.12-1.89 2.12zm6.97 0c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12 0 1.17-.83 2.12-1.89 2.12z"/></svg>
        </a>
      </div>
      <nav class="nav-links">${links}</nav>
      <div class="header-cta">
        <button class="btn btn-ghost pwa-header-btn" type="button" id="pwa-header-install">${SK.t("addDesktop")}</button>
        <div class="header-search">
          <button class="btn btn-solid" type="button" id="search-open" aria-label="${SK.t("search")}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="16" height="16"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
            ${SK.t("search")}
          </button>
          <div class="search-pop" id="search-pop" hidden>
            <input id="header-search" type="search" placeholder="Search shoes, hoodies, brands…" autocomplete="off" />
            <div class="search-hits" id="search-hits"></div>
          </div>
        </div>
        <button class="menu-btn" data-open="nav" aria-label="Menu">☰</button>
      </div>
    </div>
    <div class="header-lang">${SK.langSwitchHtml()}</div>`;
  }

  const mobile = document.getElementById("mobile-nav");
  if (mobile) {
    mobile.innerHTML = SK.langSwitchHtml() + SK.pages.map((p) => {
      const href = p.id === "home" ? SK.homeHref() : SK.asset(p.href);
      return `<a href="${href}">${SK.t("nav_" + p.id)}</a>`;
    }).join("") + `<a href="${SK.signup}" target="_blank" rel="noopener">${SK.t("signup")}</a>`;
  }

  const footer = document.getElementById("site-footer");
  if (footer) {
    footer.innerHTML = `<div class="wrap">
      <div class="footer-grid">
        <div class="footer-col">
          <a class="brand" href="${SK.homeHref()}">
            <span class="brand-copy"><strong><span>kakobuy</span> spreadsheet</strong></span>
          </a>
          <p>Independently curated list of 4,000+ KakoBuy replica links.</p>
        </div>
        <div class="footer-col">
          <h3>Site</h3>
          <a href="${SK.asset("spreadsheet.html")}">Browse spreadsheet</a>
          <a href="${SK.asset("coupons.html")}">Coupons</a>
          <a href="${SK.asset("qc.html")}">QC photos</a>
          <a href="${SK.asset("articles.html")}">Articles</a>
          <a href="${SK.signup}" target="_blank" rel="noopener">Official KakoBuy</a>
          <a href="${SK.discord}" target="_blank" rel="noopener">Join Discord</a>
        </div>
        <div class="footer-col">
          <h3>Guides</h3>
          <a href="${SK.asset("faq.html")}">FAQ</a>
          <a href="${SK.asset("articles/is-kakobuy-legit.html")}">Is KakoBuy legit?</a>
          <a href="${SK.asset("articles/shipping-customs.html")}">Shipping &amp; customs</a>
          <a href="${SK.asset("articles/kakobuy-vs-cnfans.html")}">KakoBuy vs CNFans</a>
          <a href="${SK.asset("pl.html")}">Polska</a>
          <a href="${SK.asset("de.html")}">Deutschland</a>
        </div>
        <div class="footer-col">
          <h3>Trust</h3>
          <a href="${SK.asset("about.html")}">About</a>
          <a href="${SK.asset("contact.html")}">Contact</a>
          <a href="${SK.asset("privacy.html")}">Privacy policy</a>
          <a href="${SK.asset("disclaimer.html")}">Disclaimer</a>
          <a href="${SK.asset("terms.html")}">Terms</a>
          <a href="mailto:${SK.site.email}">${SK.site.email}</a>
        </div>
      </div>
      <div class="legal">
        <p><strong>Affiliate disclosure.</strong> This site earns a small referral commission when you order through a KakoBuy link. Browsing is free. No paywall.</p>
        <p>
          <a href="${SK.asset("about.html")}">About</a> ·
          <a href="${SK.asset("contact.html")}">Contact</a> ·
          <a href="${SK.asset("privacy.html")}">Privacy</a> ·
          <a href="${SK.asset("disclaimer.html")}">Disclaimer</a> ·
          <a href="${SK.asset("terms.html")}">Terms</a>
        </p>
        <p>© 2026 Spreadsheet Kakobuy. All rights reserved. Available worldwide · <a href="${SK.asset("pl.html")}">Polski</a> · <a href="${SK.asset("de.html")}">Deutsch</a></p>
      </div>
    </div>`;
  }

  const overlay = document.getElementById("overlay");
  const openBtn = document.querySelector("[data-open=nav]");
  const closeNav = () => {
    if (mobile) mobile.classList.remove("is-on");
    if (overlay) overlay.classList.remove("is-on");
  };
  if (openBtn && mobile) {
    openBtn.addEventListener("click", () => {
      mobile.classList.add("is-on");
      if (overlay) overlay.classList.add("is-on");
    });
  }
  if (overlay) overlay.addEventListener("click", closeNav);
  SK.bindHeaderSearch();
  const headerInstall = document.getElementById("pwa-header-install");
  if (headerInstall && !headerInstall.dataset.bound) {
    headerInstall.dataset.bound = "1";
    headerInstall.addEventListener("click", () => {
      SK.track("add_to_desktop", {
        button_id: "pwa-header-install",
        button_text: headerInstall.textContent.trim(),
        page_path: location.pathname,
      });
      SK.installPwa("header");
    });
  }
};

SK.searchTerms = () => {
  if (SK._terms) return SK._terms;
  const count = new Map();
  const add = (raw) => {
    const t = String(raw || "").replace(/[^\w\s&+-]/g, " ").replace(/\s+/g, " ").trim();
    if (t.length < 2 || /^\d+$/.test(t)) return;
    const key = t.toLowerCase();
    count.set(key, (count.get(key) || 0) + 1);
  };
  SK.products().forEach((p) => {
    add(p.collection);
    add(p.category);
    add(`${p.collection || ""} ${p.category || ""}`);
    const words = String(p.title || "").split(/[\s,/|]+/).filter((w) => w.length > 2);
    words.forEach(add);
    for (let i = 0; i < words.length - 1; i++) add(`${words[i]} ${words[i + 1]}`);
  });
  (SK.categories || []).forEach((c) => add(c.label));
  SK._terms = [...count.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .map(([t]) => t);
  return SK._terms;
};

SK.suggest = (q, limit) => {
  const s = String(q || "").trim().toLowerCase();
  if (!s) return [];
  const terms = SK.searchTerms();
  const starts = [];
  const contains = [];
  for (let i = 0; i < terms.length; i++) {
    const t = terms[i];
    if (t === s) continue;
    if (t.startsWith(s)) starts.push(t);
    else if (t.includes(s)) contains.push(t);
    if (starts.length >= limit) break;
  }
  return [s, ...starts, ...contains].filter((t, i, arr) => arr.indexOf(t) === i).slice(0, limit);
};

SK.bindHeaderSearch = () => {
  const open = document.getElementById("search-open");
  const pop = document.getElementById("search-pop");
  const input = document.getElementById("header-search");
  const hits = document.getElementById("search-hits");
  if (!open || !pop || !input || !hits) return;
  let active = -1;

  const go = (q) => {
    const s = String(q || "").trim();
    if (s) location.href = SK.asset("spreadsheet.html") + "?q=" + encodeURIComponent(s);
  };
  const close = () => { pop.hidden = true; active = -1; };
  const mark = () => {
    hits.querySelectorAll(".search-suggest").forEach((el, i) => {
      el.classList.toggle("is-on", i === active);
    });
  };
  const render = (q) => {
    const s = String(q || "").trim().toLowerCase();
    active = -1;
    if (!s) {
      hits.innerHTML = `<p class="search-empty">Type a brand, item, or category.</p>`;
      return;
    }
    const list = SK.suggest(s, 8);
    if (!list.length) {
      hits.innerHTML = `<p class="search-empty">No suggestions.</p>`;
      return;
    }
    hits.innerHTML = list.map((term) => {
      const i = term.toLowerCase().indexOf(s);
      const label = i >= 0
        ? `${escapeHtml(term.slice(0, i))}<b>${escapeHtml(term.slice(i, i + s.length))}</b>${escapeHtml(term.slice(i + s.length))}`
        : escapeHtml(term);
      return `<button type="button" class="search-suggest" data-q="${escapeHtml(term)}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
        <span>${label}</span>
      </button>`;
    }).join("");
    hits.querySelectorAll(".search-suggest").forEach((btn) => {
      btn.addEventListener("mousedown", (e) => {
        e.preventDefault();
        go(btn.getAttribute("data-q"));
      });
    });
  };

  open.addEventListener("click", (e) => {
    e.stopPropagation();
    if (pop.hidden) {
      pop.hidden = false;
      input.focus();
      render(input.value);
    } else close();
  });
  input.addEventListener("input", () => render(input.value));
  input.addEventListener("keydown", (e) => {
    const items = [...hits.querySelectorAll(".search-suggest")];
    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (!items.length) return;
      active = (active + 1) % items.length;
      mark();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (!items.length) return;
      active = (active - 1 + items.length) % items.length;
      mark();
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (active >= 0 && items[active]) go(items[active].getAttribute("data-q"));
      else go(input.value);
    } else if (e.key === "Escape") close();
  });
  pop.addEventListener("click", (e) => e.stopPropagation());
  document.addEventListener("click", () => close());
};

SK.mountFaqs = (list, target) => {
  const el = document.getElementById(target || "faq-list");
  if (!el) return;
  el.innerHTML = list.map((f, i) =>
    `<article class="faq-item${i === 0 ? " is-open" : ""}">
      <button type="button">${escapeHtml(f.q)} <span>+</span></button>
      <p>${escapeHtml(f.a)}</p>
    </article>`
  ).join("");
  el.querySelectorAll(".faq-item button").forEach((btn) => {
    btn.addEventListener("click", () => btn.parentElement.classList.toggle("is-open"));
  });
};

SK.faqs = {
  en: [
    { q: "What is the KakoBuy Spreadsheet?", a: "It is an independently maintained qualityreps list of 4,000+ Kakobuy replicas. Each entry links to a Taobao, Weidian or 1688 seller through KakoBuy's referral system and includes QC photos when available." },
    { q: "Is it free?", a: "Yes. No signup, no paywall. The site earns a small referral commission when you place an order through a link — this is disclosed on every page." },
    { q: "How often is it updated?", a: "New finds are added several times per week. The last full review of the list was on 21 September 2026. Dead or wrong links can be reported by email." },
    { q: "Are the products authentic?", a: "Most items listed are replica products. They are not produced or authorised by the original brand owners. Buying replicas may be illegal in your country — check before ordering. QC photos help you see what will ship before you commit." },
    { q: "How does shipping to Europe work?", a: "Typical transit times: DHL Express 7–14 working days, EMS 10–18 working days, Sea Mail 30–45 days. EU customs can inspect any package and may apply VAT plus a handling fee on packages over €150. We never promise customs-free delivery." },
    { q: "How do I get 20% off shipping?", a: "Open the Coupons page, copy code FINDS20, then paste it in the coupon field when you pay for international shipping on KakoBuy. It takes 20% off the shipping fee." },
  ],
  pl: [
    { q: "Czy KakoBuy Spreadsheet działa w Polsce?", a: "Tak. Większość naszych użytkowników jest z Polski. Wysyłka EMS lub DHL do Polski trwa zwykle 10–18 dni roboczych. Cła i VAT mogą zostać naliczone — nie obiecujemy, że paczki przejdą bez kontroli." },
    { q: "Czy lista jest darmowa?", a: "Tak. Bez rejestracji i paywalla. Serwis zarabia małą prowizję, gdy złożysz zamówienie przez link polecający." },
    { q: "Jak wygląda cło?", a: "Polski urząd celny może sprawdzić każdą paczkę. Towary z logo marek bywają zatrzymywane. Podajemy realistyczne czasy, nie obietnice." },
  ],
  de: [
    { q: "Wie funktioniert der Versand nach Deutschland?", a: "DHL Express 7–14 Werktage, EMS 12–18 Werktage. Seit ICS2 (2023) prüft der deutsche Zoll Pakete aus China routinemäßig. Bei Markenprodukten kann das Paket beschlagnahmt werden." },
    { q: "Ist die Liste kostenlos?", a: "Ja. Keine Anmeldung, keine Paywall. Die Seite verdient eine kleine Provision, wenn du über einen Link bestellst." },
    { q: "Ist KakoBuy seriös?", a: "KakoBuy ist ein etablierter Einkaufsagent: er kauft, lagert, fotografiert (QC) und verschickt. Diese Seite verkauft nichts selbst." },
  ],
};

document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.getAttribute("data-page") || "home";
  SK.mountChrome(page);
  SK.mountPwa();
});
