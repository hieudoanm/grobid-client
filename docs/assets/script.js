/*
 * pagify default theme — progressive enhancement.
 *
 * Every feature here is an upgrade to markup that already works without
 * JavaScript. If this file fails to load, the site still reads, navigates and
 * prints. No framework, no build step, no dependencies.
 *
 * Search lives in search.js; this file owns the theme, the mobile drawer and the
 * content upgrades.
 */

(function () {
  "use strict";

  var STORAGE_KEY = "pagify:theme";

  /* --- Theme ---------------------------------------------------------- */

  var media = window.matchMedia("(prefers-color-scheme: dark)");

  function storedTheme() {
    try {
      return window.localStorage.getItem(STORAGE_KEY);
    } catch (error) {
      return null;
    }
  }

  function storeTheme(theme) {
    try {
      window.localStorage.setItem(STORAGE_KEY, theme);
    } catch (error) {
      /* Private browsing: the theme simply does not persist. */
    }
  }

  function preferredTheme() {
    var stored = storedTheme();
    if (stored === "dark" || stored === "light") {
      return stored;
    }
    return media.matches ? "dark" : "light";
  }

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    var toggle = document.querySelector("[data-theme-toggle]");
    if (toggle) {
      toggle.setAttribute("aria-pressed", String(theme === "dark"));
      // Use emoji for sun/moon
      toggle.textContent = theme === "dark" ? "☀️" : "🌙";
    }
  }

  function initTheme() {
    applyTheme(preferredTheme());

    var toggle = document.querySelector("[data-theme-toggle]");
    if (toggle) {
      toggle.addEventListener("click", function () {
        var next =
          document.documentElement.dataset.theme === "dark" ? "light" : "dark";
        applyTheme(next);
        storeTheme(next);
      });
    }

    media.addEventListener("change", function (event) {
      if (!storedTheme()) {
        applyTheme(event.matches ? "dark" : "light");
      }
    });
  }

  /* --- Mobile navigation ---------------------------------------------- */

  function initNav() {
    var toggle = document.querySelector("[data-nav-toggle]");
    var sidebar = document.getElementById("sidebar");
    if (!toggle || !sidebar) {
      return;
    }

    function setOpen(open) {
      document.documentElement.toggleAttribute("data-nav-open", open);
      toggle.setAttribute("aria-expanded", String(open));
    }

    toggle.addEventListener("click", function () {
      setOpen(!document.documentElement.hasAttribute("data-nav-open"));
    });

    sidebar.addEventListener("click", function (event) {
      if (event.target.closest("a")) {
        setOpen(false);
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        setOpen(false);
      }
    });
  }

  /* --- Content upgrades ------------------------------------------------ */

  /*
   * Goldmark marks code blocks with a language class and wraps tables in
   * nothing at all. Both need structure the stylesheet can target, and the
   * copy button needs somewhere to live, so the markup is added here rather
   * than in the renderer: it is presentational, and the page reads fine
   * without it.
   */

  function enhanceCodeBlocks() {
    var blocks = document.querySelectorAll(".markdown pre > code");
    Array.prototype.forEach.call(blocks, function (code, index) {
      if (code.parentElement.parentElement.classList.contains("code")) {
        return;
      }

      var wrapper = document.createElement("div");
      wrapper.className = "code";
      code.parentElement.parentNode.replaceChild(wrapper, code.parentElement);
      wrapper.appendChild(code.parentElement);

      var language = detectLanguage(code);
      if (language) {
        var label = document.createElement("span");
        label.className = "code__language";
        label.textContent = language;
        wrapper.appendChild(label);
      }

      wrapper.appendChild(copyButton(code, index));
    });
  }

  function detectLanguage(code) {
    var match = /language-([\w+#-]+)/.exec(code.className || "");
    return match ? match[1] : "";
  }

  function copyButton(code, index) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "code__copy";
    button.textContent = "Copy";
    button.setAttribute("aria-label", "Copy code block " + (index + 1));

    button.addEventListener("click", function () {
      writeClipboard(code.textContent).then(function () {
        button.textContent = "Copied";
        button.setAttribute("data-copied", "");
        window.setTimeout(function () {
          button.removeAttribute("data-copied");
          button.textContent = "Copy";
        }, 1600);
      });
    });
    return button;
  }

  function writeClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    // execCommand is the only option on plain http, which is what a local
    // preview server serves.
    return new Promise(function (resolve) {
      var area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      document.execCommand("copy");
      area.remove();
      resolve();
    });
  }

  function enhanceTables() {
    var tables = document.querySelectorAll(".markdown table");
    Array.prototype.forEach.call(tables, function (table) {
      if (table.parentElement.classList.contains("table")) {
        return;
      }
      var wrapper = document.createElement("div");
      wrapper.className = "table";
      table.parentNode.replaceChild(wrapper, table);
      wrapper.appendChild(table);
    });
  }

  /* --- Boot ------------------------------------------------------------ */

  function init() {
    initTheme();
    initNav();
    enhanceCodeBlocks();
    enhanceTables();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
