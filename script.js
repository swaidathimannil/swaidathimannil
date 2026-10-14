"use strict";

const root = document.documentElement;
const themeButton = document.querySelector(".theme-toggle");
const themeMeta = document.querySelector('meta[name="theme-color"]');
const themePreference = window.matchMedia("(prefers-color-scheme: light)");
let explicitTheme = null;
try {
  const saved = localStorage.getItem("swaid-theme");
  if (saved === "light" || saved === "dark") explicitTheme = saved;
} catch {
  /* Storage may be unavailable in private browsing. */
}

function applyTheme(theme) {
  root.dataset.theme = theme;
  themeButton.setAttribute(
    "aria-label",
    `Switch to ${theme === "dark" ? "light" : "dark"} theme`,
  );
  themeMeta.setAttribute("content", theme === "dark" ? "#151714" : "#f5f4ec");
}
applyTheme(explicitTheme || (themePreference.matches ? "light" : "dark"));
themeButton.hidden = false;
themeButton.addEventListener("click", () => {
  explicitTheme = root.dataset.theme === "dark" ? "light" : "dark";
  applyTheme(explicitTheme);
  try {
    localStorage.setItem("swaid-theme", explicitTheme);
  } catch {
    /* Optional persistence. */
  }
});
themePreference.addEventListener("change", (event) => {
  if (!explicitTheme) applyTheme(event.matches ? "light" : "dark");
});

document.querySelector("#year").textContent = new Date().getFullYear();
const copyButton = document.querySelector(".copy-link");
const copyStatus = document.querySelector(".copy-status");
if (navigator.clipboard && window.isSecureContext) {
  copyButton.hidden = false;
  copyButton.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText("https://github.com/swaidathimannil");
      copyStatus.textContent = "Profile link copied.";
    } catch {
      copyStatus.textContent = "Could not copy. Use the GitHub link above.";
    }
  });
}
