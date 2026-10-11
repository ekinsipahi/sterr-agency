(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.remove("no-js");
  doc.classList.add("js");

  /* ------------------------------------------------------------------
     Tracking — one entry point for GA4 (gtag), GTM (dataLayer) and Meta.
     Event names follow GA4 conventions (snake_case, ≤40 chars).
     ------------------------------------------------------------------ */
  var cfg = window.sterrConfig || {};
  var PIXEL_MAP = { generate_lead: "Lead", whatsapp_click: "Contact", phone_click: "Contact", email_click: "Contact" };

  function track(name, params) {
    params = Object.assign({}, window.sterrPage || {}, params || {});
    window.dataLayer = window.dataLayer || [];
    if (cfg.gtm) {
      window.dataLayer.push(Object.assign({ event: name }, params));
    } else if (cfg.ga4 && window.gtag) {
      window.gtag("event", name, params);
    }
    if (window.fbq && PIXEL_MAP[name]) {
      var fbParams = params.value !== undefined ? { value: params.value, currency: params.currency || "TRY" } : {};
      window.fbq("track", PIXEL_MAP[name], fbParams);
    }
  }
  window.sterrTrack = track;

  function locationOf(el) {
    var marked = el.closest("[data-loc]");
    if (marked) return marked.getAttribute("data-loc");
    if (el.closest(".nav")) return "nav";
    if (el.closest(".footer")) return "footer";
    if (el.closest(".wa-float")) return "floating_button";
    if (el.closest(".cta")) return "cta_band";
    if (el.closest(".plan")) return "pricing";
    if (el.closest(".hero, .page-hero")) return "hero";
    if (el.closest("form")) return "form";
    return "body";
  }

  // Click tracking: calls, WhatsApp, email, CTAs, package selection
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a");
    if (!a) return;
    var href = a.getAttribute("href") || "";
    var base = { link_location: locationOf(a), link_url: href.slice(0, 100) };
    if (href.indexOf("https://wa.me/") === 0) return track("whatsapp_click", base);
    if (href.indexOf("tel:") === 0) return track("phone_click", base);
    if (href.indexOf("mailto:") === 0) return track("email_click", base);
    if (href.indexOf("/basvuru/") !== -1) {
      var pkg = /[?&]paket=([^&]+)/.exec(href);
      if (pkg) return track("package_select", Object.assign(base, { package: decodeURIComponent(pkg[1]) }));
      return track("cta_click", Object.assign(base, { cta_text: (a.textContent || "").trim().slice(0, 60) }));
    }
  });

  /* ---------- Consent banner (Consent Mode v2) ---------- */
  var bar = document.querySelector("[data-consent]");
  function setConsent(state) {
    try { localStorage.setItem("sterr_consent", state); } catch (e) { /* storage blocked */ }
    if (window.gtag) {
      var v = state === "granted" ? "granted" : "denied";
      window.gtag("consent", "update", { ad_storage: v, ad_user_data: v, ad_personalization: v, analytics_storage: v });
    }
    if (state === "granted" && window.sterrLoadPixel) window.sterrLoadPixel();
    if (bar) bar.hidden = true;
  }
  if (bar) {
    if (!window.sterrConsent) bar.hidden = false;
    bar.querySelector("[data-consent-accept]").addEventListener("click", function () { setConsent("granted"); });
    bar.querySelector("[data-consent-deny]").addEventListener("click", function () { setConsent("denied"); });
  }

  /* ---------- Nav ---------- */
  var nav = document.querySelector(".nav");
  if (nav) {
    var onScroll = function () { nav.classList.toggle("is-scrolled", window.scrollY > 8); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    var toggle = nav.querySelector(".nav__toggle");
    if (toggle) toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---------- Reveal on scroll ---------- */
  var items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---------- Thank-you page: generate_lead ---------- */
  var leadData = document.getElementById("lead-event");
  if (leadData) {
    try { track("generate_lead", JSON.parse(leadData.textContent)); } catch (e) { /* malformed */ }
  }

  /* ---------- First-touch attribution (UTM + gclid) ---------- */
  var ATTR = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "gclid"];
  var params = new URLSearchParams(location.search);
  var stored = {};
  try { stored = JSON.parse(localStorage.getItem("sterr_utm") || "{}"); } catch (e) { stored = {}; }
  if (ATTR.some(function (k) { return params.get(k); }) && !stored.utm_source && !stored.gclid) {
    ATTR.forEach(function (k) { stored[k] = params.get(k) || ""; });
    if (stored.gclid && !stored.utm_source) { stored.utm_source = "google"; stored.utm_medium = "cpc"; }
    stored.landing = location.pathname;
    try { localStorage.setItem("sterr_utm", JSON.stringify(stored)); } catch (e) { /* storage blocked */ }
  }

  /* ---------- Language menu + review button ---------- */
  document.addEventListener("click", function (e) {
    document.querySelectorAll(".lang-menu[open]").forEach(function (m) { if (!m.contains(e.target)) m.removeAttribute("open"); });
    var t = e.target.closest("[data-track]");
    if (!t) return;
    var what = t.getAttribute("data-track");
    if (what === "lang-switch") {
      track("language_switch", { language_from: doc.lang, language_to: t.getAttribute("hreflang"), link_location: locationOf(t) });
    } else if (what === "review-cta") {
      track("review_click", { link_location: locationOf(t) });
    }
  });

  /* ---------- Dental tourism inquiry form (16 languages) ---------- */
  var dform = document.querySelector("[data-dental-form]");
  if (dform) {
    ["utm_source", "utm_medium", "utm_campaign", "gclid"].forEach(function (k) {
      var input = dform.querySelector('[name="' + k + '"]');
      if (input && !input.value) input.value = params.get(k) || stored[k] || "";
    });
    var dsrc = dform.querySelector('[name="source_page"]');
    if (dsrc && !dsrc.value) dsrc.value = location.pathname + (stored.landing && stored.landing !== location.pathname ? " ← " + stored.landing : "");
    var dStarted = false;
    dform.addEventListener("focusin", function () {
      if (dStarted) return;
      dStarted = true;
      track("form_start", { form_id: "dental_inquiry", language: doc.lang });
    });
    if (dform.dataset.formErrors) {
      track("lead_form_error", { form_id: "dental_inquiry", error_fields: dform.dataset.formErrors.slice(0, 100) });
    }
  }

  /* ---------- Multi-step application form (funnel) ---------- */
  var form = document.querySelector("[data-steps]");
  if (!form) return;
  ATTR.forEach(function (k) {
    var input = form.querySelector('[name="' + k + '"]');
    if (input && !input.value) input.value = params.get(k) || stored[k] || "";
  });
  var src = form.querySelector('[name="source_page"]');
  if (src && !src.value) src.value = stored.landing || document.referrer || location.pathname;

  var steps = Array.prototype.slice.call(form.querySelectorAll(".fstep"));
  var STEP_NAMES = ["sektor", "hedef", "butce", "icerik_zamanlama", "iletisim"];
  var bars = form.querySelectorAll(".progress span");
  var current = 0;
  var started = false;
  var seenSteps = {};
  var firstError = form.querySelector(".fstep .errorlist");
  if (firstError) current = steps.indexOf(firstError.closest(".fstep"));
  if (form.dataset.formErrors) {
    track("lead_form_error", { form_id: "basvuru", error_fields: form.dataset.formErrors.slice(0, 100) });
  }

  function answer(name) {
    var el = form.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : undefined;
  }

  function show(i) {
    current = Math.max(0, Math.min(i, steps.length - 1));
    steps.forEach(function (s, idx) { s.classList.toggle("is-active", idx === current); });
    bars.forEach(function (b, idx) { b.classList.toggle("is-done", idx <= current); });
    var budgetWarn = form.querySelector("[data-budget-warn]");
    if (budgetWarn) budgetWarn.hidden = answer("budget") !== "lt50";
    if (current > 0 && !seenSteps[current]) {
      seenSteps[current] = true;
      track("lead_form_step", {
        form_id: "basvuru", step_number: current + 1, step_name: STEP_NAMES[current],
        lead_sector: answer("sector"), lead_goal: answer("goal"), lead_budget: answer("budget")
      });
    }
  }

  function valid(step) {
    var ok = true;
    var groups = {};
    step.querySelectorAll("input, select, textarea").forEach(function (el) {
      if (el.type === "radio") { groups[el.name] = true; return; }
      if (!el.checkValidity()) { ok = false; el.reportValidity(); }
    });
    Object.keys(groups).forEach(function (name) {
      if (!step.querySelector('input[name="' + name + '"]:checked')) {
        ok = false;
        var first = step.querySelector('input[name="' + name + '"]');
        if (first) { first.setCustomValidity("Lütfen bir seçenek belirleyin."); first.reportValidity(); first.setCustomValidity(""); }
      }
    });
    return ok;
  }

  form.addEventListener("click", function (e) {
    var next = e.target.closest("[data-next]");
    var prev = e.target.closest("[data-prev]");
    if (next) { e.preventDefault(); if (valid(steps[current])) { show(current + 1); form.scrollIntoView({ behavior: "smooth", block: "start" }); } }
    if (prev) { e.preventDefault(); show(current - 1); }
  });

  form.addEventListener("change", function (e) {
    if (!started) {
      started = true;
      track("lead_form_start", { form_id: "basvuru", package: form.querySelector('[name="package"]').value || "none" });
    }
    if (e.target.type !== "radio") return;
    show(current);
    // Auto-advance on single-question steps (not on the low-budget warning)
    var step = steps[current];
    var names = {};
    step.querySelectorAll('input[type="radio"]').forEach(function (r) { names[r.name] = true; });
    var keys = Object.keys(names);
    if (keys.length === 1 && step.querySelector('input[name="' + keys[0] + '"]:checked') && e.target.value !== "lt50") {
      setTimeout(function () { show(current + 1); }, 260);
    }
  });

  form.addEventListener("submit", function () {
    track("lead_form_submit", { form_id: "basvuru", lead_budget: answer("budget"), lead_sector: answer("sector") });
    var btn = form.querySelector('[type="submit"]');
    if (btn) { btn.disabled = true; btn.textContent = "Gönderiliyor…"; }
  });

  show(current);
})();
