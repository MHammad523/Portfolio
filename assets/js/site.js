/**
 * site.js — progressive-enhancement interactivity only.
 * All content is already present in the static HTML (baked in by build.py
 * from data/resume.json) so the page works, reads, and indexes correctly
 * even with JavaScript disabled. This file just adds the nice-to-haves:
 * theme toggle, mobile nav, smooth active-link tracking, scroll reveals,
 * a typewriter effect, animated counters/rings, portfolio filtering, and
 * a lightweight custom lightbox.
 */
(function () {
  "use strict";

  /* ---------------- Theme toggle ---------------- */
  const root = document.documentElement;
  const themeBtn = document.getElementById("theme-toggle");

  function setThemeIcon(theme) {
    if (!themeBtn) return;
    const icon = themeBtn.querySelector("i");
    if (icon) icon.className = theme === "light" ? "bi bi-moon-stars" : "bi bi-sun";
    themeBtn.setAttribute("aria-label", theme === "light" ? "Switch to dark mode" : "Switch to light mode");
  }
  setThemeIcon(root.getAttribute("data-theme") || "dark");

  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
      setThemeIcon(next);
    });
  }

  /* ---------------- Mobile nav ---------------- */
  const navToggle = document.getElementById("nav-toggle");
  const mainNav = document.querySelector(".main-nav");
  if (navToggle && mainNav) {
    navToggle.addEventListener("click", () => {
      const open = mainNav.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
      navToggle.querySelector("i").className = open ? "bi bi-x-lg" : "bi bi-list";
    });
    mainNav.querySelectorAll("a").forEach((a) =>
      a.addEventListener("click", () => {
        mainNav.classList.remove("open");
        navToggle.setAttribute("aria-expanded", "false");
        navToggle.querySelector("i").className = "bi bi-list";
      })
    );
  }

  /* ---------------- Header shadow + active nav link on scroll ---------------- */
  const header = document.querySelector(".site-header");
  const navLinks = document.querySelectorAll(".main-nav a[href^='#']");
  const sections = Array.from(navLinks)
    .map((a) => document.querySelector(a.getAttribute("href")))
    .filter(Boolean);

  function onScroll() {
    if (header) header.classList.toggle("scrolled", window.scrollY > 12);
    const pos = window.scrollY + 140;
    let current = sections[0];
    sections.forEach((sec) => {
      if (sec.offsetTop <= pos) current = sec;
    });
    navLinks.forEach((a) => a.classList.toggle("active", current && a.getAttribute("href") === "#" + current.id));
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------------- Scroll reveal ---------------- */
  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in-view");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 }
    );
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add("in-view"));
  }

  /* ---------------- Typewriter hero role text ---------------- */
  const typedEl = document.getElementById("typed-role");
  if (typedEl) {
    let items = [];
    try { items = JSON.parse(typedEl.getAttribute("data-items") || "[]"); } catch (e) {}
    if (items.length) {
      let itemIndex = 0, charIndex = 0, deleting = false;
      const TYPE_SPEED = 65, DELETE_SPEED = 35, HOLD = 1600;
      function tick() {
        const word = items[itemIndex];
        if (!deleting) {
          charIndex++;
          typedEl.textContent = word.slice(0, charIndex);
          if (charIndex === word.length) {
            deleting = true;
            setTimeout(tick, HOLD);
            return;
          }
          setTimeout(tick, TYPE_SPEED);
        } else {
          charIndex--;
          typedEl.textContent = word.slice(0, charIndex);
          if (charIndex === 0) {
            deleting = false;
            itemIndex = (itemIndex + 1) % items.length;
          }
          setTimeout(tick, DELETE_SPEED);
        }
      }
      setTimeout(tick, 500);
    }
  }

  /* ---------------- Animated counters ---------------- */
  const counters = document.querySelectorAll(".stat-num[data-count]");
  if (counters.length && "IntersectionObserver" in window) {
    const counterIO = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const el = entry.target;
          const target = parseInt(el.getAttribute("data-count"), 10) || 0;
          const duration = 1200;
          const start = performance.now();
          function step(now) {
            const p = Math.min(1, (now - start) / duration);
            const eased = 1 - Math.pow(1 - p, 3);
            el.textContent = Math.round(eased * target).toLocaleString();
            if (p < 1) requestAnimationFrame(step);
          }
          requestAnimationFrame(step);
          counterIO.unobserve(el);
        });
      },
      { threshold: 0.4 }
    );
    counters.forEach((el) => counterIO.observe(el));
  }

  /* ---------------- Animated skill rings ---------------- */
  const rings = document.querySelectorAll(".ring[data-val]");
  if (rings.length && "IntersectionObserver" in window) {
    const ringIO = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const el = entry.target;
          requestAnimationFrame(() => {
            el.style.setProperty("--val", el.getAttribute("data-val"));
          });
          ringIO.unobserve(el);
        });
      },
      { threshold: 0.4 }
    );
    rings.forEach((el) => ringIO.observe(el));
  } else {
    rings.forEach((el) => el.style.setProperty("--val", el.getAttribute("data-val")));
  }

  /* ---------------- Portfolio filter ---------------- */
  const pills = document.querySelectorAll(".pill");
  const workCards = document.querySelectorAll(".work-card");
  pills.forEach((pill) => {
    pill.addEventListener("click", () => {
      pills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      const filter = pill.getAttribute("data-filter");
      workCards.forEach((card) => {
        const show = filter === "all" || card.getAttribute("data-cat") === filter;
        card.classList.toggle("hidden", !show);
      });
    });
  });

  /* ---------------- Lightbox ---------------- */
  const lightbox = document.getElementById("lightbox");
  if (lightbox) {
    const lbImg = lightbox.querySelector(".lightbox-img");
    const lbCaption = lightbox.querySelector(".lightbox-caption");
    const btnClose = lightbox.querySelector(".lightbox-close");
    const btnPrev = lightbox.querySelector(".lightbox-prev");
    const btnNext = lightbox.querySelector(".lightbox-next");
    let currentImages = [];
    let currentIndex = 0;
    let currentTitle = "";

    function show(index) {
      currentIndex = (index + currentImages.length) % currentImages.length;
      lbImg.src = currentImages[currentIndex];
      lbImg.alt = currentTitle + " — screenshot " + (currentIndex + 1) + " of " + currentImages.length;
      lbCaption.textContent = `${currentTitle} — ${currentIndex + 1} / ${currentImages.length}`;
    }
    function open(images, title, startIndex) {
      currentImages = images;
      currentTitle = title;
      show(startIndex || 0);
      lightbox.classList.add("open");
      lightbox.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
    }
    function close() {
      lightbox.classList.remove("open");
      lightbox.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
    }

    document.querySelectorAll(".work-thumb[data-images]").forEach((btn) => {
      btn.addEventListener("click", () => {
        let images = [];
        try { images = JSON.parse(btn.getAttribute("data-images") || "[]"); } catch (e) {}
        if (!images.length) return;
        open(images, btn.getAttribute("data-title") || "", 0);
      });
    });

    if (btnClose) btnClose.addEventListener("click", close);
    if (btnPrev) btnPrev.addEventListener("click", () => show(currentIndex - 1));
    if (btnNext) btnNext.addEventListener("click", () => show(currentIndex + 1));
    lightbox.addEventListener("click", (e) => { if (e.target === lightbox) close(); });
    document.addEventListener("keydown", (e) => {
      if (!lightbox.classList.contains("open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(currentIndex - 1);
      if (e.key === "ArrowRight") show(currentIndex + 1);
    });
  }
})();
