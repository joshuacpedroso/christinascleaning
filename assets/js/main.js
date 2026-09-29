(() => {
  "use strict";

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const STAR = '<svg viewBox="0 0 24 24"><path d="M12 0c.6 6.6 5.4 11.4 12 12-6.6.6-11.4 5.4-12 12-.6-6.6-5.4-11.4-12-12C6.6 11.4 11.4 6.6 12 0Z"/></svg>';

  /* ---------- Loader ---------- */
  const finishLoading = () => {
    if (document.body.classList.contains("is-loaded")) return;
    document.body.classList.add("is-loaded");
    document.body.classList.remove("is-loading");
  };
  const skipIntro = reduceMotion || !$(".loader") || document.documentElement.classList.contains("no-loader");
  const minShow = skipIntro ? 0 : 1300;
  try { sessionStorage.setItem("ccs-intro", "1"); } catch (e) { /* storage unavailable */ }
  const start = performance.now();
  window.addEventListener("load", () => {
    setTimeout(finishLoading, Math.max(0, minShow - (performance.now() - start)));
  });
  setTimeout(finishLoading, skipIntro ? 600 : 3500); // safety net on slow connections

  /* ---------- Year ---------- */
  const year = $("#year");
  if (year) year.textContent = new Date().getFullYear();

  /* ---------- Header ---------- */
  const header = $(".header");
  const mobileBar = $(".mobile-bar");
  const hero = $(".hero");
  const onScroll = () => {
    const y = window.scrollY;
    header.classList.toggle("is-scrolled", y > 30);
    if (mobileBar && hero) mobileBar.classList.toggle("is-visible", y > hero.offsetHeight * 0.6);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- Mobile nav ---------- */
  const burger = $("#burger");
  const nav = $("#nav");
  const setNav = (open) => {
    document.documentElement.classList.toggle("nav-open", open);
    burger.setAttribute("aria-expanded", String(open));
    burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    document.body.style.overflow = open ? "hidden" : "";
    if (open) nav.style.setProperty("--nav-top", header.getBoundingClientRect().bottom + "px");
  };
  burger.addEventListener("click", () => setNav(!document.documentElement.classList.contains("nav-open")));
  $$("a", nav).forEach((a) => a.addEventListener("click", () => setNav(false)));
  window.addEventListener("keydown", (e) => { if (e.key === "Escape") setNav(false); });

  /* ---------- Active nav link ---------- */
  const navLinks = $$('.nav a[href^="#"]');
  const sections = navLinks.map((a) => $(a.getAttribute("href"))).filter(Boolean);
  if ("IntersectionObserver" in window) {
    const navIO = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        navLinks.forEach((a) => a.classList.toggle("is-active", a.getAttribute("href") === "#" + en.target.id));
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    sections.forEach((s) => navIO.observe(s));
  }

  /* ---------- Reveal on scroll ---------- */
  const revealEls = $$("[data-reveal]");
  if (!("IntersectionObserver" in window) || reduceMotion) {
    revealEls.forEach((el) => el.classList.add("is-in"));
  } else {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    revealEls.forEach((el) => io.observe(el));
  }

  /* ---------- Hero sparkles canvas ---------- */
  const canvas = $("#sparkles");
  if (canvas && !reduceMotion) {
    const ctx = canvas.getContext("2d");
    let w = 0, h = 0, dpr = 1, particles = [], running = true, raf;
    const mouse = { x: -9999, y: -9999 };
    const colors = ["243,220,170", "255,255,255", "246,198,222", "217,178,111"];

    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.offsetWidth; h = canvas.offsetHeight;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const count = Math.round(Math.min(90, (w * h) / 14000));
      particles = Array.from({ length: count }, () => spawn(true));
    };
    const spawn = (anywhere) => ({
      x: Math.random() * w,
      y: anywhere ? Math.random() * h : h + 10,
      r: Math.random() * 1.8 + 0.4,
      vy: -(Math.random() * 0.25 + 0.05),
      vx: (Math.random() - 0.5) * 0.15,
      t: Math.random() * Math.PI * 2,
      ts: Math.random() * 0.03 + 0.01,
      c: colors[(Math.random() * colors.length) | 0],
      star: Math.random() < 0.18,
    });
    const drawStar = (x, y, s, a, c) => {
      ctx.save();
      ctx.translate(x, y);
      ctx.fillStyle = `rgba(${c},${a})`;
      ctx.shadowColor = `rgba(${c},${a})`;
      ctx.shadowBlur = 8;
      ctx.beginPath();
      ctx.moveTo(0, -s);
      ctx.quadraticCurveTo(0, 0, s, 0);
      ctx.quadraticCurveTo(0, 0, 0, s);
      ctx.quadraticCurveTo(0, 0, -s, 0);
      ctx.quadraticCurveTo(0, 0, 0, -s);
      ctx.fill();
      ctx.restore();
    };
    const tick = () => {
      ctx.clearRect(0, 0, w, h);
      for (const p of particles) {
        p.t += p.ts;
        p.x += p.vx; p.y += p.vy;
        const dx = p.x - mouse.x, dy = p.y - mouse.y, d2 = dx * dx + dy * dy;
        if (d2 < 14400) { const f = (1 - d2 / 14400) * 1.2; p.x += (dx / 120) * f; p.y += (dy / 120) * f; }
        if (p.y < -10 || p.x < -10 || p.x > w + 10) Object.assign(p, spawn(false));
        const a = 0.25 + Math.abs(Math.sin(p.t)) * 0.75;
        if (p.star) drawStar(p.x, p.y, p.r * 3.2 * (0.6 + Math.abs(Math.sin(p.t)) * 0.6), a, p.c);
        else { ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fillStyle = `rgba(${p.c},${a * 0.8})`; ctx.fill(); }
      }
      if (running) raf = requestAnimationFrame(tick);
    };
    resize();
    tick();
    window.addEventListener("resize", () => { cancelAnimationFrame(raf); resize(); if (running) tick(); });
    hero.addEventListener("pointermove", (e) => { const r = canvas.getBoundingClientRect(); mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top; });
    hero.addEventListener("pointerleave", () => { mouse.x = mouse.y = -9999; });
    new IntersectionObserver(([en]) => {
      const vis = en.isIntersecting;
      if (vis && !running) { running = true; tick(); }
      if (!vis) { running = false; cancelAnimationFrame(raf); }
    }).observe(hero);
  }

  /* ---------- Sparkle burst helper ---------- */
  const burst = (parent, x, y, n = 3, spread = 60) => {
    if (reduceMotion) return;
    for (let i = 0; i < n; i++) {
      const s = document.createElement("span");
      s.className = "spark";
      s.innerHTML = STAR;
      const size = 8 + Math.random() * 14;
      s.style.width = s.style.height = size + "px";
      s.style.left = x + "px";
      s.style.top = y + "px";
      s.style.setProperty("--dx", (Math.random() * spread - spread * 0.2).toFixed(1) + "px");
      s.style.setProperty("--dy", (Math.random() * spread - spread / 2).toFixed(1) + "px");
      s.style.setProperty("--s", (0.3 + Math.random() * 0.5).toFixed(2));
      parent.appendChild(s);
      setTimeout(() => s.remove(), 950);
    }
  };

  /* ---------- Before / After compare ---------- */
  $$("[data-compare]").forEach((el) => {
    let pos = 50, dragging = false, lastBurst = 0, autoplayed = false, anim = null;

    const set = (p, sparkle) => {
      pos = Math.max(0, Math.min(100, p));
      el.style.setProperty("--pos", pos + "%");
      el.setAttribute("aria-valuenow", String(Math.round(pos)));
      el.classList.toggle("hide-before", pos < 12);
      el.classList.toggle("hide-after", pos > 88);
      if (sparkle) {
        const now = performance.now();
        if (now - lastBurst > 45) {
          lastBurst = now;
          const r = el.getBoundingClientRect();
          burst(el, (pos / 100) * r.width, Math.random() * r.height, 2, 70);
        }
      }
    };
    const fromEvent = (e) => {
      const r = el.getBoundingClientRect();
      return ((e.clientX - r.left) / r.width) * 100;
    };
    const stopAnim = () => { if (anim) { cancelAnimationFrame(anim); anim = null; } };

    el.addEventListener("pointerdown", (e) => {
      stopAnim();
      dragging = true;
      el.classList.add("is-dragging");
      el.setPointerCapture(e.pointerId);
      set(fromEvent(e), true);
    });
    el.addEventListener("pointermove", (e) => {
      if (dragging) { set(fromEvent(e), true); return; }
      if (finePointer && !anim) set(fromEvent(e), true);
    });
    const end = () => { dragging = false; el.classList.remove("is-dragging"); };
    el.addEventListener("pointerup", end);
    el.addEventListener("pointercancel", end);
    el.addEventListener("keydown", (e) => {
      const step = e.shiftKey ? 20 : 5;
      if (e.key === "ArrowLeft" || e.key === "ArrowDown") { e.preventDefault(); stopAnim(); set(pos - step, true); }
      if (e.key === "ArrowRight" || e.key === "ArrowUp") { e.preventDefault(); stopAnim(); set(pos + step, true); }
      if (e.key === "Home") { e.preventDefault(); set(0); }
      if (e.key === "End") { e.preventDefault(); set(100); }
    });

    // Cinematic auto-sweep: before -> after (with sparkles) -> settle in the middle
    const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
    const keyframes = [[0, 94], [1500, 6], [2300, 6], [3200, 50]];
    const sweep = () => {
      if (reduceMotion) return;
      const t0 = performance.now();
      const frame = (now) => {
        const t = now - t0;
        let i = 0;
        while (i < keyframes.length - 2 && t > keyframes[i + 1][0]) i++;
        const [ta, pa] = keyframes[i], [tb, pb] = keyframes[i + 1];
        const k = Math.min(1, Math.max(0, (t - ta) / (tb - ta)));
        set(pa + (pb - pa) * ease(k), i === 0 && k > 0.05 && k < 0.95);
        if (t < keyframes[keyframes.length - 1][0]) anim = requestAnimationFrame(frame);
        else anim = null;
      };
      anim = requestAnimationFrame(frame);
    };

    set(reduceMotion ? 50 : 94);
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver(([en]) => {
        if (en.isIntersecting && !autoplayed) {
          autoplayed = true;
          io.disconnect();
          setTimeout(sweep, 350 + Math.random() * 300);
        }
      }, { threshold: 0.55 });
      io.observe(el);
    } else set(50);
  });

  /* ---------- Tilt + spotlight cards ---------- */
  if (finePointer && !reduceMotion) {
    $$(".tilt").forEach((card) => {
      card.addEventListener("pointermove", (e) => {
        const r = card.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
        card.style.setProperty("--mx", px * 100 + "%");
        card.style.setProperty("--my", py * 100 + "%");
        card.style.transform = `perspective(900px) rotateX(${(0.5 - py) * 8}deg) rotateY(${(px - 0.5) * 10}deg) translateY(-6px)`;
      });
      card.addEventListener("pointerleave", () => { card.style.transform = ""; });
    });

    /* Magnetic buttons */
    $$(".magnetic").forEach((btn) => {
      btn.addEventListener("pointermove", (e) => {
        const r = btn.getBoundingClientRect();
        const x = e.clientX - r.left - r.width / 2, y = e.clientY - r.top - r.height / 2;
        btn.style.transform = `translate(${x * 0.18}px, ${y * 0.28}px)`;
      });
      btn.addEventListener("pointerleave", () => { btn.style.transform = ""; });
    });

    /* Cursor sparkle trail */
    let lastTrail = 0;
    window.addEventListener("pointermove", (e) => {
      const now = performance.now();
      if (now - lastTrail < 55) return;
      lastTrail = now;
      const s = document.createElement("span");
      s.className = "trail";
      s.innerHTML = STAR;
      const size = 6 + Math.random() * 8;
      s.style.width = s.style.height = size + "px";
      s.style.left = e.clientX + (Math.random() * 10 - 5) + "px";
      s.style.top = e.clientY + (Math.random() * 10 - 5) + "px";
      document.body.appendChild(s);
      setTimeout(() => s.remove(), 820);
    }, { passive: true });
  }

  /* ---------- Process line progress ---------- */
  const steps = $("#steps");
  const line = steps && $(".steps__line", steps);
  if (line) {
    const upd = () => {
      const r = steps.getBoundingClientRect();
      const vh = window.innerHeight;
      const p = Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (vh * 0.55)));
      line.style.setProperty("--progress", p.toFixed(3));
    };
    window.addEventListener("scroll", upd, { passive: true });
    upd();
  }

  /* ---------- Service links prefill the form ---------- */
  const form = $("#quote-form");
  const serviceSelect = form && form.elements.service;
  $$("[data-service]").forEach((a) => {
    a.addEventListener("click", () => {
      if (!serviceSelect) return;
      serviceSelect.value = a.dataset.service;
      setTimeout(() => form.elements.name.focus({ preventScroll: true }), 900);
    });
  });

  /* ---------- Form ---------- */
  if (form) {
    if (form.dataset.defaultService && serviceSelect) serviceSelect.value = form.dataset.defaultService;
    const errorBox = $(".form__error", form);
    const success = $(".form__success");
    const phone = form.elements.phone;

    phone.addEventListener("input", () => {
      const d = phone.value.replace(/\D/g, "").replace(/^1/, "").slice(0, 10);
      let out = d;
      if (d.length > 6) out = `(${d.slice(0, 3)}) ${d.slice(3, 6)}-${d.slice(6)}`;
      else if (d.length > 3) out = `(${d.slice(0, 3)}) ${d.slice(3)}`;
      else if (d.length > 0) out = `(${d}`;
      phone.value = out;
    });

    const sqft = form.elements.sqft;
    if (sqft) {
      sqft.addEventListener("input", () => {
        const d = sqft.value.replace(/\D/g, "").slice(0, 6);
        sqft.value = d ? Number(d).toLocaleString("en-US") : "";
      });
    }

    const validators = {
      name: (v) => v.trim().length >= 2,
      phone: (v) => v.replace(/\D/g, "").length >= 10,
      email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()),
      zip: (v) => /^\d{5}(-?\d{4})?$/.test(v.trim()),
      service: (v) => v !== "",
    };
    const check = (name) => {
      const input = form.elements[name];
      const ok = validators[name](input.value);
      input.closest(".field").classList.toggle("is-invalid", !ok);
      return ok;
    };
    Object.keys(validators).forEach((n) => {
      const input = form.elements[n];
      input.addEventListener("blur", () => { if (input.value) check(n); });
      input.addEventListener("input", () => input.closest(".field").classList.remove("is-invalid"));
      input.addEventListener("change", () => input.closest(".field").classList.remove("is-invalid"));
    });

    const showError = (html) => { errorBox.innerHTML = html; errorBox.hidden = false; };

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      errorBox.hidden = true;
      const bad = Object.keys(validators).filter((n) => !check(n));
      if (bad.length) {
        form.elements[bad[0]].focus();
        showError("Please check the highlighted fields.");
        return;
      }
      if (form.elements._honey.value) return; // bot

      const data = Object.fromEntries(new FormData(form).entries());
      delete data._honey;
      data.page = document.title + " (" + location.pathname + ")";
      form.classList.add("is-sending");
      try {
        const res = await fetch(form.dataset.endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(data),
        });
        const json = await res.json().catch(() => ({}));
        if (!res.ok || json.success === false || json.success === "false") throw new Error(json.message || "Request failed");
        form.hidden = true;
        success.hidden = false;
        const card = $(".quote__card");
        const r = card.getBoundingClientRect();
        burst(card, r.width / 2, 90, 14, 180);
      } catch (err) {
        showError('Sorry, something went wrong sending your request. Please call <a href="tel:+14432106133">(443) 210-6133</a> or email <a href="mailto:christinascleaningservices4@gmail.com">christinascleaningservices4@gmail.com</a>.');
      } finally {
        form.classList.remove("is-sending");
      }
    });
  }
})();
