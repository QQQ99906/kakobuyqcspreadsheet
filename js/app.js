(() => {
  const byId = (id) => document.getElementById(id);
  const products = () => SK.products();
  const params = new URLSearchParams(location.search);

  const renderGrid = (el, list) => {
    if (!el) return;
    el.innerHTML = list.length
      ? list.map(SK.card).join("")
      : `<p class="empty">No finds in this filter yet. Try another category.</p>`;
  };

  const page = document.body.getAttribute("data-page");

  if (page === "home") {
    const homeIds = [
      "p-7784612683", "p-7727238283", "p-7726672765", "p-7669816767",
      "p-7821936541", "p-7761869227", "p-7727191097", "p-7725792983",
      "p-7729706204", "p-7821210351", "p-7728782536", "p-7728984644",
    ];
    const byIdMap = Object.fromEntries(products().map((p) => [p.id, p]));
    const homeList = homeIds.map((id) => byIdMap[id]).filter(Boolean);
    renderGrid(byId("latest-grid"), homeList);
    const cats = byId("cat-grid");
    if (cats) {
      cats.innerHTML = SK.categories.map((c) =>
        `<a class="cat-tile" href="${SK.catHref(c.slug)}">
          ${c.hot ? `<em class="hot">HOT</em>` : ""}
          <b>${c.emoji}</b>
          <div><h3>${SK.catLabel(c.slug)}</h3><span>${c.count} ${SK.t("items")}</span></div>
        </a>`
      ).join("");
    }
    const faqLang = SK.currentLang();
    SK.mountFaqs(SK.faqs[faqLang] || SK.faqs.en);
    document.querySelectorAll("[data-faq]").forEach((btn) => {
      btn.classList.toggle("is-on", btn.getAttribute("data-faq") === faqLang);
      btn.addEventListener("click", () => {
        document.querySelectorAll("[data-faq]").forEach((b) => b.classList.remove("is-on"));
        btn.classList.add("is-on");
        SK.mountFaqs(SK.faqs[btn.getAttribute("data-faq")] || SK.faqs.en);
      });
    });
  }

  if (page === "spreadsheet" || page === "finds" || page === "category") {
    if (page === "spreadsheet") {
      const jump = params.get("cat");
      if (jump) {
        const rest = new URLSearchParams(params);
        rest.delete("cat");
        const qs = rest.toString();
        location.replace(SK.catHref(jump) + (qs ? "?" + qs : ""));
        return;
      }
    }
    const catSlug = document.body.getAttribute("data-cat") || "";
    const all = page === "finds"
      ? products().filter((p) => p.featured)
      : page === "category"
        ? products().filter((p) => p.category === catSlug)
        : products();
    const grid = byId("catalog-grid");
    const search = byId("catalog-search");
    const cat = byId("catalog-cat");
    const sort = byId("catalog-sort");
    const count = byId("result-count");
    const hasStatic = grid && grid.querySelector(".card");

    if (cat && !cat.querySelector("option[value]:not([value=''])")) {
      const slugs = [...new Set(products().map((p) => p.category).filter(Boolean))].sort();
      slugs.forEach((s) => {
        const opt = document.createElement("option");
        opt.value = s;
        opt.textContent = SK.catLabel(s);
        cat.appendChild(opt);
      });
    }
    if (cat && catSlug) cat.value = catSlug;

    const q0 = params.get("q");
    if (q0 && search) search.value = q0;

    const apply = () => {
      const q = (search && search.value || "").trim().toLowerCase();
      const c = cat && cat.value;
      let list = all.slice();
      if (page !== "category" && c) list = list.filter((p) => p.category === c);
      if (q) list = list.filter((p) => `${p.title} ${p.collection} ${p.sellerName}`.toLowerCase().includes(q));
      const s = sort && sort.value;
      if (s === "price-asc") list.sort((a, b) => a.price - b.price);
      else if (s === "price-desc") list.sort((a, b) => b.price - a.price);
      else if (s === "boosted") list.sort((a, b) => b.boosted - a.boosted);
      if (count) count.textContent = SK.t("showing", { n: list.length });
      renderGrid(grid, list);
    };

    if (cat) {
      cat.addEventListener("change", () => {
        if (cat.value) location.href = SK.catHref(cat.value);
        else location.href = SK.currentLang() === "en" ? SK.asset("spreadsheet.html") : SK.homeHref();
      });
    }
    [search, sort].forEach((el) => el && el.addEventListener("input", apply));
    if (!(hasStatic && !all.length)) apply();
  }

  if (page === "qc") {
    const greenIds = [
      "p-7761975633", "p-7831599461", "p-7772876716", "p-7769857321",
      "p-7770013729", "p-7729721974", "p-7827721991", "p-7677653327",
      "p-7787587202", "p-7769801349", "p-7764410050", "p-7672746969",
      "p-7828602919", "p-7728849946", "p-7784454989", "p-7821293817",
      "p-7829328833", "p-7787599116", "p-7827700263", "p-7769936739",
      "p-7787579356", "p-7833199760", "p-7772925932", "p-7821906551",
      "p-7769896449", "p-7784640585", "p-7830721718", "p-7758821219",
      "p-7784597307", "p-7727513303", "p-7761909183", "p-7784601243",
      "p-7787403312", "p-7831197588", "p-7787693790", "p-7784680099",
      "p-7784597273", "p-7827468849", "p-7830657434", "p-7769951835",
      "p-7829359659", "p-7784666215", "p-7769942661", "p-7655817272",
      "p-7833927528", "p-7787594856", "p-7727560357", "p-7680596822",
    ];
    const map = Object.fromEntries(products().map((p) => [p.id, p]));
    const green = greenIds.map((id) => map[id]).filter(Boolean);
    renderGrid(byId("qc-grid"), green);
  }

  if (page === "coupons") {
    const copied = byId("coupon-copied");
    const copyCode = async (code) => {
      try {
        await navigator.clipboard.writeText(code);
      } catch (_) {
        const tmp = document.createElement("textarea");
        tmp.value = code;
        document.body.appendChild(tmp);
        tmp.select();
        document.execCommand("copy");
        tmp.remove();
      }
      if (copied) {
        copied.hidden = false;
        copied.textContent = "Copied. Enter FINDS20 on the shipping page.";
      }
    };
    document.querySelectorAll("[data-copy]").forEach((btn) => {
      btn.addEventListener("click", () => copyCode(btn.getAttribute("data-copy") || "FINDS20"));
    });
  }

  if (page === "item") {
    const pathSlug = (location.pathname.match(/\/item\/([^/]+)/) || [])[1];
    const id = params.get("id") || document.body.getAttribute("data-item-id");
    const list = products();
    let p = list.find((x) => x.id === id)
      || list.find((x) => x.slug === pathSlug)
      || list.find((x) => SK.itemSlug(x) === pathSlug);
    if (p && params.get("id") && !pathSlug) {
      location.replace(SK.itemHref(p));
      return;
    }
    const bindThumbs = () => {
      const mainImg = byId("item-main");
      const thumbs = byId("item-thumbs");
      if (!thumbs || !mainImg) return;
      thumbs.querySelectorAll("button").forEach((btn) => {
        const thumb = btn.querySelector("img");
        if (thumb) {
          thumb.addEventListener("error", () => {
            btn.classList.add("is-empty");
            btn.removeAttribute("data-src");
            thumb.remove();
          });
        }
        btn.addEventListener("click", () => {
          const src = btn.getAttribute("data-src");
          if (!src) return;
          mainImg.src = src;
          thumbs.querySelectorAll("button").forEach((el) => el.classList.toggle("is-on", el === btn));
        });
      });
    };
    const root = byId("item-root");
    const trackItem = (item) => {
      if (!item || !SK.track) return;
      const name = SK.itemName ? SK.itemName(item.title) : String(item.title || "").slice(0, 100);
      SK.track("view_item", {
        item_id: String(item.id || ""),
        item_name: name,
        currency: "USD",
        value: Number(item.price) || 0,
        items: [{
          item_id: String(item.id || ""),
          item_name: name,
          item_category: item.category || "",
          price: Number(item.price) || 0,
          quantity: 1,
        }],
      });
    };
    if (root && root.querySelector("#item-main")) {
      bindThumbs();
      const h1 = root.querySelector("h1");
      const priceEl = root.querySelector(".price");
      trackItem(p || {
        id: document.body.getAttribute("data-item-id"),
        title: h1 ? h1.textContent.trim() : "",
        price: priceEl ? parseFloat(String(priceEl.textContent).replace(/[^0-9.]/g, "")) : 0,
        category: "",
      });
      return;
    }
    if (!p || !root) return;
    document.title = `${p.title} — KakoBuy Spreadsheet`;
    const crumbs = byId("item-crumbs");
    if (crumbs) {
      crumbs.innerHTML = `<a href="${SK.homeHref()}">${SK.t("nav_home")}</a> / <a href="${SK.catHref(p.category)}">${SK.catLabel(p.category)}</a> / <span>${p.collection || "Find"}</span>`;
    }
    const pid = String(p.id || "").replace(/^p-/, "");
    const mainSrc = SK.asset(p.image);
    const gallery = [mainSrc, SK.asset(`img/products/${pid}-2.webp`), SK.asset(`img/products/${pid}-3.webp`)];
    root.innerHTML = `
      <div class="item-gallery">
        <div class="item-shot"><img id="item-main" src="${mainSrc}" alt="${p.title}" /></div>
        <div class="item-thumbs" id="item-thumbs">
          ${gallery.map((src, i) => `<button type="button" data-src="${src}" class="${i === 0 ? "is-on" : ""}" aria-label="Photo ${i + 1}"><img src="${src}" alt="" /></button>`).join("")}
        </div>
      </div>
      <div class="buy-box">
        <h1>${p.title}</h1>
        <div class="price">${SK.money(p.price)}</div>
        <p>Hand-checked listing. Opens the live KakoBuy product page so you can pick size, pay, and review warehouse QC before shipping.</p>
        <div style="margin-top:22px">
          <a class="btn btn-solid" href="${SK.kakobuyUrl(p.sourceUrl)}" target="_blank" rel="noopener">View on KakoBuy →</a>
          <p class="buy-note">Link uses our KakoBuy referral code. How this site makes money.</p>
        </div>
      </div>`;
    bindThumbs();
    trackItem(p);
    renderGrid(byId("related-grid"), list.filter((x) => x.category === p.category && x.id !== p.id).slice(0, 8));
  }
})();
