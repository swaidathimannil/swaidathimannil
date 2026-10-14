const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const code = fs.readFileSync(path.join(__dirname, "../script.js"), "utf8");

function setup({
  saved = null,
  light = false,
  blocked = false,
  clipboard = "success",
} = {}) {
  const elements = {};
  for (const name of [
    ".theme-toggle",
    'meta[name="theme-color"]',
    "#year",
    ".copy-link",
    ".copy-status",
  ]) {
    elements[name] = {
      hidden: true,
      attrs: {},
      listeners: {},
      textContent: "",
      setAttribute(k, v) {
        this.attrs[k] = v;
      },
      addEventListener(k, v) {
        this.listeners[k] = v;
      },
    };
  }
  const root = { dataset: {} };
  const store = {};
  let copied;
  const media = {
    matches: light,
    addEventListener(_, fn) {
      this.onChange = fn;
    },
  };
  vm.runInNewContext(code, {
    document: {
      documentElement: root,
      querySelector: (name) => elements[name],
    },
    window: { matchMedia: () => media, isSecureContext: true },
    localStorage: {
      getItem() {
        if (blocked) throw Error("blocked");
        return saved;
      },
      setItem(k, v) {
        if (blocked) throw Error("blocked");
        store[k] = v;
      },
    },
    navigator:
      clipboard === "missing"
        ? {}
        : {
            clipboard: {
              async writeText(value) {
                if (clipboard === "denied") throw Error("denied");
                copied = value;
              },
            },
          },
    Date,
  });
  return {
    elements,
    root,
    store,
    media,
    get copied() {
      return copied;
    },
  };
}

test("follows system theme and updates theme metadata", () => {
  const s = setup({ light: true });
  assert.equal(s.root.dataset.theme, "light");
  assert.equal(s.elements['meta[name="theme-color"]'].attrs.content, "#f5f4ec");
  s.media.onChange({ matches: false });
  assert.equal(s.root.dataset.theme, "dark");
});
test("saved choice overrides system and toggle persists", () => {
  const s = setup({ saved: "dark", light: true });
  assert.equal(s.root.dataset.theme, "dark");
  s.elements[".theme-toggle"].listeners.click();
  assert.equal(s.root.dataset.theme, "light");
  assert.equal(s.store["swaid-theme"], "light");
  assert.equal(
    s.elements[".theme-toggle"].attrs["aria-label"],
    "Switch to dark theme",
  );
  s.media.onChange({ matches: false });
  assert.equal(s.root.dataset.theme, "light");
});
test("blocked storage does not break theme switching", () => {
  const s = setup({ blocked: true });
  s.elements[".theme-toggle"].listeners.click();
  assert.equal(s.root.dataset.theme, "light");
});
test("ignores invalid stored themes", () => {
  assert.equal(
    setup({ saved: "unexpected", light: true }).root.dataset.theme,
    "light",
  );
});
test("copies the actual GitHub profile and announces success", async () => {
  const s = setup();
  assert.equal(s.elements[".copy-link"].hidden, false);
  await s.elements[".copy-link"].listeners.click();
  assert.equal(s.copied, "https://github.com/swaidathimannil");
  assert.equal(s.elements[".copy-status"].textContent, "Profile link copied.");
});
test("clipboard failures show an actionable fallback", async () => {
  const s = setup({ clipboard: "denied" });
  await s.elements[".copy-link"].listeners.click();
  assert.match(s.elements[".copy-status"].textContent, /Use the GitHub link/);
});
test("hides copy control if clipboard is unavailable", () => {
  assert.equal(
    setup({ clipboard: "missing" }).elements[".copy-link"].hidden,
    true,
  );
});
test("uses current year", () => {
  assert.equal(setup().elements["#year"].textContent, new Date().getFullYear());
});
