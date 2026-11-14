// Wunschliste – Bearbeiten-Panel für Home Assistant (läuft im iframe, Daten über WebSocket)
const CSS = ":root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}html{scroll-padding-top:env(safe-area-inset-top,0px)}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;}img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}\n\n/* Layout: one calm column, price bands as sections, each wish a row with price and shop on the right. Winter-frost ground, deep blue accent. */\n:root{\n  --bg:#f2f4f7; --surface:#ffffff; --ink:#24243a; --muted:#646a7e; --line:#dde1e9;\n  --accent:#2b5ea7; --accent-soft:#e2ebf7; --taken:#8a8f9f; --taken-bg:#eceef2; --ok:#2f7a5b;\n  --display:\"Fraunces\", Georgia, \"Times New Roman\", serif;\n  --body:\"Figtree\", system-ui, -apple-system, \"Segoe UI\", sans-serif;\n}\n@media (prefers-color-scheme: dark){:root:not([data-theme=\"light\"]){\n  --bg:#16171f; --surface:#1f2029; --ink:#ebebf2; --muted:#a2a6b8; --line:#30323f;\n  --accent:#8db4ee; --accent-soft:#1d2a3e; --taken:#7d8193; --taken-bg:#262732; --ok:#72c9a1; color-scheme:dark}}\n:root[data-theme=\"dark\"]{\n  --bg:#16171f; --surface:#1f2029; --ink:#ebebf2; --muted:#a2a6b8; --line:#30323f;\n  --accent:#8db4ee; --accent-soft:#1d2a3e; --taken:#7d8193; --taken-bg:#262732; --ok:#72c9a1; color-scheme:dark}\nbody{background:var(--bg);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.5}\n.wrap{max-width:820px;margin:0 auto;padding-block:32px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:flex;flex-direction:column;gap:28px}\nheader{display:flex;flex-direction:column;gap:10px}\n.eyebrow{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);font-weight:600}\nh1{font-family:var(--display);font-weight:650;font-size:clamp(30px,6vw,44px);line-height:1.1;margin:0;text-wrap:balance}\n.intro{color:var(--muted);max-width:62ch;margin:0}\n.facts{display:flex;flex-wrap:wrap;gap:8px;margin-top:4px}\n.fact{font-size:13px;border:1px solid var(--line);border-radius:999px;padding:3px 10px;color:var(--muted);background:var(--surface)}\n.fact b{color:var(--ink);font-weight:600}\n.howto{background:var(--accent-soft);border-radius:10px;padding:12px 14px;font-size:14px;max-width:62ch}\n.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center}\n.chip{font:inherit;font-size:14px;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:999px;padding:5px 12px;cursor:pointer}\n.chip[aria-pressed=\"true\"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}\n.chip:focus-visible,.btn:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:2px solid var(--accent);outline-offset:2px}\n.toggle{display:flex;gap:6px;align-items:center;font-size:14px;color:var(--muted);margin-left:auto}\nsection.band{display:flex;flex-direction:column;gap:10px}\n.band h2{font-family:var(--display);font-weight:500;font-size:22px;margin:0;display:flex;align-items:baseline;gap:10px}\n.band h2 small{font-family:var(--body);font-size:13px;color:var(--muted);font-weight:400}\n.band-intro{margin:0;color:var(--muted);font-size:14px;max-width:62ch}\nsection.band.zeit{background:var(--accent-soft);border-radius:14px;padding:16px}\nsection.band.zeit h2{color:var(--accent)}\nsection.band.zeit .band-intro{color:var(--ink)}\nsection.band.zeit .price{color:var(--accent);font-weight:500;font-size:13px}\nul.items{list-style:none;margin:0;padding:0;background:var(--surface);border:1px solid var(--line);border-radius:12px}\nli.item{display:grid;grid-template-columns:1fr auto;gap:4px 16px;padding:14px 16px;border-top:1px solid var(--line)}\nli.item:first-child{border-top:0}\n.main{min-width:0;display:flex;flex-direction:column;gap:3px}\n.name{font-weight:600;font-size:15.5px}\n.note{color:var(--muted);font-size:14px}\n.meta{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center;font-size:13px;color:var(--muted)}\n.theme{font-size:11.5px;letter-spacing:.06em;text-transform:uppercase}\n.side{display:flex;flex-direction:column;align-items:flex-end;gap:6px;text-align:right}\n.price{font-variant-numeric:tabular-nums;font-weight:600;white-space:nowrap}\n.links{display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end}\na.shop{color:var(--accent);font-weight:600;font-size:14px;text-decoration:none;white-space:nowrap}\na.shop:hover{text-decoration:underline}\na.alt{color:var(--muted);font-size:13px;white-space:nowrap}\n.pill{font-size:12px;font-weight:600;border-radius:999px;padding:2px 9px;background:var(--taken-bg);color:var(--taken);white-space:nowrap}\nli.taken .name{color:var(--taken);text-decoration:line-through;text-decoration-thickness:1px}\nli.taken .note{opacity:.7}\n.edit{grid-column:1 / -1;display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding-top:6px}\n.btn{font:inherit;font-size:13px;border:1px solid var(--line);background:var(--bg);color:var(--ink);border-radius:8px;padding:4px 10px;cursor:pointer}\n.btn.primary{background:var(--accent);border-color:var(--accent);color:var(--surface)}\n.btn.danger{color:var(--accent)}\n.btn:disabled{opacity:.5;cursor:default}\n.empty{padding:16px;color:var(--muted);font-size:14px}\nform.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px}\nform.grid label{display:flex;flex-direction:column;gap:4px;font-size:13px;color:var(--muted);min-width:0}\nform.grid .wide{grid-column:1 / -1}\ninput,select,textarea{font:inherit;font-size:14px;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:7px 9px;min-width:0}\n.formbar{grid-column:1 / -1;display:flex;gap:8px;justify-content:flex-end}\n.editbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:14px;color:var(--muted)}\n.status{font-size:13px;color:var(--ok)}\n.status.err{color:var(--accent)}\nfooter{color:var(--muted);font-size:13px;max-width:62ch}\n@media (max-width:520px){\n  li.item{grid-template-columns:1fr}\n  .side{align-items:flex-start;text-align:left;flex-direction:row;flex-wrap:wrap;gap:8px 12px}\n  .links{justify-content:flex-start}\n  form.grid{grid-template-columns:1fr}\n  .toggle{margin-left:0}\n}\n@media (prefers-reduced-motion:no-preference){.chip,.btn{transition:background .15s,color .15s}}\n\ntextarea{resize:vertical}\n.btn[aria-pressed=\"true\"]{background:var(--accent-soft);border-color:var(--accent)}\nwunschliste-panel{display:block}\n";

const BANDS = [
  {key:"zeit", label:"Zeit statt Geld", min:0, max:0},
  {key:"u20", label:"Unter 20 €", min:0, max:20},
  {key:"u50", label:"20 bis 50 €", min:20, max:50},
  {key:"u100", label:"50 bis 100 €", min:50, max:100},
  {key:"o100", label:"Über 100 €", min:100, max:1e9}
];
const THEMES = ["Pflege","Schlafen","Essen","Baden","Spielen","Kleidung","Unterwegs","Gesundheit","Zeit & Gutscheine","Sonstiges"];

function el(tag, attrs, kids) {
  const n = document.createElement(tag);
  if (attrs) for (const k in attrs) { const v = attrs[k]; if (v == null || v === false) continue;
    if (k.slice(0, 2) === "on") n.addEventListener(k.slice(2), v); else n.setAttribute(k, v === true ? "" : v); }
  (kids || []).forEach(c => { if (c != null) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
  return n;
}
function bandOf(p) { if (!(p > 0)) return "zeit"; for (let i = 1; i < BANDS.length; i++) { const b = BANDS[i]; if (p < b.max && p >= b.min) return b.key; } return "o100"; }
function euro(p) { return !(p > 0) ? "kostet nur Zeit" : "ca. " + (Math.round(p * 100) / 100).toLocaleString("de-DE") + " €"; }
function safeUrl(u) { return /^https?:\/\//i.test(u || "") ? u : null; }
function errText(e) { return (e && (e.message || e.code)) || "unbekannter Fehler"; }

class WunschlistePanel extends HTMLElement {
  constructor() {
    super();
    this.ui = {band:"all", hideTaken:false, adding:false, editing:null, reserving:null, deleting:null, busy:false, msg:"", err:false, showSettings:false, showImport:false};
    this.data = null;
    this.publicUrl = "";
  }
  set hass(h) {
    const first = !this._hass;
    this._hass = h;
    if (first && this.isConnected) this._start();
  }
  set panel(p) { this._panel = p; }
  set narrow(v) {} set route(v) {}
  connectedCallback() { if (this._hass && !this._started) this._start(); }
  disconnectedCallback() { if (this._unsub) { this._unsub(); this._unsub = null; } this._started = false; }

  async _start() {
    if (this._started) return;
    this._started = true;
    if (!document.getElementById("wl-css")) {
      const st = document.createElement("style"); st.id = "wl-css"; st.textContent = CSS; document.head.appendChild(st);
    }
    if (!document.getElementById("wl-fonts")) {
      const l = document.createElement("link"); l.id = "wl-fonts"; l.rel = "stylesheet";
      l.href = "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,650&family=Figtree:wght@400;500;600&display=swap";
      document.head.appendChild(l);
    }
    if (!document.querySelector("meta[name=viewport]")) { const m = document.createElement("meta"); m.name = "viewport"; m.content = "width=device-width,initial-scale=1,viewport-fit=cover"; document.head.appendChild(m); }
    this.app = el("div", {"class":"wrap"}); this.textContent = ""; this.appendChild(this.app);
    this._resolvePublicUrl();
    await this._load();
    try {
      this._unsub = await this._hass.connection.subscribeMessage(() => this._load(), {type:"wunschliste/subscribe"});
    } catch (e) { /* Live-Aktualisierung ist optional */ }
  }

  async _resolvePublicUrl() {
    const path = (this._panel && this._panel.config && this._panel.config.public_path) || "/geschenkliste";
    let base = (this._hass.config && this._hass.config.external_url) || "";
    try {
      const c = await this._hass.callWS({type:"cloud/status"});
      if (c && c.remote_enabled && c.remote_domain) base = "https://" + c.remote_domain;
    } catch (e) { /* keine Nabu Casa Cloud */ }
    if (!base) base = window.location.origin;
    this.publicUrl = base.replace(/\/$/, "") + path;
    this.publicIsLocal = !/^https:/.test(this.publicUrl) || /\/\/(localhost|127\.|192\.168\.|10\.|homeassistant\.local)/.test(this.publicUrl);
    this.render();
  }

  async _load() {
    try { this.data = await this._hass.callWS({type:"wunschliste/get"}); }
    catch (e) { this.ui.msg = "Konnte die Liste nicht laden: " + errText(e); this.ui.err = true; }
    this.render();
  }

  async _ws(msg, okMsg) {
    this.ui.busy = true; this.ui.msg = "Wird gespeichert …"; this.ui.err = false; this.render();
    try {
      const r = await this._hass.callWS(msg);
      this.ui.msg = okMsg || "Gespeichert."; this.ui.err = false;
      await this._load();
      return r;
    } catch (e) {
      this.ui.msg = "Hat nicht geklappt: " + errText(e); this.ui.err = true;
      return null;
    } finally { this.ui.busy = false; this.render(); }
  }

  itemForm(item, onSubmit, onCancel) {
    const f = el("form", {"class":"grid"});
    const k = item.id || "neu";
    const nameI = el("input", {id:"f-name-" + k, required:true, maxlength:"200", value:item.name || "", placeholder:"z. B. Spieluhr"});
    const priceI = el("input", {id:"f-price-" + k, type:"number", min:"0", step:"0.01", inputmode:"decimal", value:item.price != null ? String(item.price) : "", placeholder:"0 für Zeit/Gefallen"});
    const themeS = el("select", {id:"f-theme-" + k}, THEMES.map(t => el("option", {value:t, selected:t === (item.theme || "Sonstiges")}, [t])));
    const shopI = el("input", {id:"f-shop-" + k, maxlength:"80", value:item.shop || "", placeholder:"z. B. dm, Amazon"});
    const urlI = el("input", {id:"f-url-" + k, type:"url", value:item.url || "", placeholder:"https://…"});
    const noteI = el("input", {id:"f-note-" + k, maxlength:"500", value:item.note || "", placeholder:"Größe, Farbe, Hinweis"});
    f.append(
      el("label", {"class":"wide"}, ["Was wünscht ihr euch?", nameI]),
      el("label", null, ["Ungefährer Preis in €", priceI]),
      el("label", null, ["Thema", themeS]),
      el("label", null, ["Shop", shopI]),
      el("label", null, ["Link zum Produkt", urlI]),
      el("label", {"class":"wide"}, ["Hinweis für Schenkende", noteI]),
      el("div", {"class":"formbar"}, [
        el("button", {type:"button", "class":"btn", onclick:onCancel}, ["Abbrechen"]),
        el("button", {type:"submit", "class":"btn primary", disabled:this.ui.busy}, [item.id ? "Änderung speichern" : "Zur Liste hinzufügen"])
      ])
    );
    f.addEventListener("submit", e => {
      e.preventDefault();
      const name = nameI.value.trim(); if (!name) return;
      onSubmit({name, price:Math.max(0, parseFloat(priceI.value) || 0), theme:themeS.value, shop:shopI.value.trim(), url:urlI.value.trim(), note:noteI.value.trim()});
    });
    setTimeout(() => { if (!item.id) nameI.focus(); }, 0);
    return f;
  }

  itemRow(it) {
    const ui = this.ui, taken = !!it.reservedBy;
    if (ui.editing === it.id) {
      return el("li", {"class":"item"}, [el("div", {style:"grid-column:1 / -1"}, [this.itemForm(it, v => {
        ui.editing = null; this._ws({type:"wunschliste/item_save", item:Object.assign({}, it, v)});
      }, () => { ui.editing = null; this.render(); })])]);
    }
    const url = safeUrl(it.url);
    const side = el("div", {"class":"side"}, [
      el("span", {"class":"price"}, [euro(it.price)]),
      taken ? el("span", {"class":"pill", title:it.selfReserved ? "Über die öffentliche Seite selbst eingetragen" : null}, ["Vergeben: " + it.reservedBy + (it.selfReserved ? " (selbst)" : "")]) : null,
      url && !taken ? el("div", {"class":"links"}, [el("a", {"class":"shop", href:url, target:"_blank", rel:"noopener noreferrer"}, ["Bei " + (it.shop || "Shop") + " ansehen"])]) : null
    ]);
    const helpers = (it.helpers || []).length ? el("div", {"class":"edit"}, [el("span", null, ["Übernimmt:"])].concat(it.helpers.map((name, idx) =>
      el("span", {"class":"pill"}, [name + " ", el("button", {"class":"btn", style:"padding:0 6px;border:0;background:none", title:"Zusage entfernen", "aria-label":"Zusage von " + name + " entfernen", disabled:ui.busy,
        onclick:() => this._ws({type:"wunschliste/helper_remove", item_id:it.id, index:idx}, "Zusage entfernt.")}, ["×"])])))) : null;
    const bar = el("div", {"class":"edit"});
    if (ui.reserving === it.id) {
      const who = el("input", {id:"f-who-" + it.id, maxlength:"100", placeholder:"Wer schenkt das?", "aria-label":"Wer schenkt das?"});
      const go = () => { ui.reserving = null; this._ws({type:"wunschliste/item_save", item:Object.assign({}, it, {reservedBy:who.value.trim() || "jemand"})}, "Als vergeben markiert."); };
      who.addEventListener("keydown", e => { if (e.key === "Enter") go(); });
      bar.append(who,
        el("button", {"class":"btn primary", disabled:ui.busy, onclick:go}, ["Vergeben"]),
        el("button", {"class":"btn", onclick:() => { ui.reserving = null; this.render(); }}, ["Abbrechen"]));
      setTimeout(() => who.focus(), 0);
    } else if (ui.deleting === it.id) {
      bar.append(el("span", null, ["Wirklich löschen?"]),
        el("button", {"class":"btn danger", disabled:ui.busy, onclick:() => { ui.deleting = null; this._ws({type:"wunschliste/item_delete", item_id:it.id}, "Gelöscht."); }}, ["Ja, löschen"]),
        el("button", {"class":"btn", onclick:() => { ui.deleting = null; this.render(); }}, ["Behalten"]));
    } else {
      bar.append(
        taken ? el("button", {"class":"btn", disabled:ui.busy, onclick:() => this._ws({type:"wunschliste/item_save", item:Object.assign({}, it, {reservedBy:""})}, "Wieder frei.")}, ["Wieder freigeben"])
              : el("button", {"class":"btn", disabled:ui.busy, onclick:() => { ui.reserving = it.id; ui.deleting = null; this.render(); }}, ["Als vergeben markieren"]),
        el("button", {"class":"btn", disabled:ui.busy, onclick:() => { ui.editing = it.id; this.render(); }}, ["Ändern"]),
        el("button", {"class":"btn danger", disabled:ui.busy, onclick:() => { ui.deleting = it.id; ui.reserving = null; this.render(); }}, ["Löschen"]));
    }
    return el("li", {"class":"item" + (taken ? " taken" : "")}, [
      el("div", {"class":"main"}, [
        el("span", {"class":"theme", style:"color:var(--muted)"}, [it.theme || ""]),
        el("span", {"class":"name"}, [it.name]),
        it.note ? el("span", {"class":"note"}, [it.note]) : null
      ]),
      side, helpers, bar
    ]);
  }

  settingsForm() {
    const s = this.data.settings || {};
    const f = el("form", {"class":"grid"});
    const fields = {
      title: el("input", {id:"s-title", maxlength:"120", value:s.title || ""}),
      etDate: el("input", {id:"s-et", type:"date", value:s.etDate || ""}),
      sizes: el("input", {id:"s-sizes", maxlength:"40", value:s.sizes || "", placeholder:"z. B. Gr. 56–68"}),
      intro: el("textarea", {id:"s-intro", rows:"3", maxlength:"1000"}, [s.intro || ""]),
      howto: el("textarea", {id:"s-howto", rows:"3", maxlength:"1000"}, [s.howto || ""])
    };
    f.append(
      el("label", {"class":"wide"}, ["Überschrift", fields.title]),
      el("label", null, ["Errechneter Termin", fields.etDate]),
      el("label", null, ["Kleidergrößen", fields.sizes]),
      el("label", {"class":"wide"}, ["Einleitung", fields.intro]),
      el("label", {"class":"wide"}, ["So geht’s (Hinweis zum Reservieren)", fields.howto]),
      el("div", {"class":"formbar"}, [
        el("button", {type:"button", "class":"btn", onclick:() => { this.ui.showSettings = false; this.render(); }}, ["Schließen"]),
        el("button", {type:"submit", "class":"btn primary", disabled:this.ui.busy}, ["Speichern"])
      ])
    );
    f.addEventListener("submit", e => {
      e.preventDefault();
      const v = {}; for (const k in fields) v[k] = fields[k].value.trim();
      this.ui.showSettings = false;
      this._ws({type:"wunschliste/settings", settings:v}, "Einstellungen gespeichert.");
    });
    return f;
  }

  importBox() {
    const box = el("div", {"class":"grid"});
    const file = el("input", {type:"file", accept:"application/json,.json", id:"imp-file"});
    const replace = el("input", {type:"checkbox", id:"imp-replace"});
    box.append(
      el("p", {"class":"wide note", style:"margin:0"}, ["Exportieren speichert die ganze Liste als Datei, inklusive der Namen. Beim Importieren werden Wünsche mit gleicher ID ersetzt und neue ergänzt."]),
      el("div", {"class":"wide", style:"display:flex;flex-wrap:wrap;gap:8px"}, [
        el("button", {type:"button", "class":"btn", onclick:() => this._export()}, ["Als Datei exportieren"])
      ]),
      el("label", {"class":"wide"}, ["Liste importieren (JSON-Datei)", file]),
      el("label", {"class":"toggle wide", "for":"imp-replace", style:"margin-left:0"}, [replace, "Bisherige Wünsche vorher löschen"]),
      el("div", {"class":"formbar"}, [
        el("button", {type:"button", "class":"btn", onclick:() => { this.ui.showImport = false; this.render(); }}, ["Schließen"]),
        el("button", {type:"button", "class":"btn primary", disabled:this.ui.busy, onclick:async () => {
          const fl = file.files && file.files[0];
          if (!fl) { this.ui.msg = "Bitte zuerst eine Datei auswählen."; this.ui.err = true; this.render(); return; }
          let data;
          try { data = JSON.parse(await fl.text()); } catch (e) { this.ui.msg = "Die Datei ist kein gültiges JSON."; this.ui.err = true; this.render(); return; }
          this.ui.showImport = false;
          const r = await this._ws({type:"wunschliste/import", data, replace:replace.checked}, "Importiert.");
          if (r) { this.ui.msg = r.count + " Wünsche importiert."; this.render(); }
        }}, ["Importieren"])
      ])
    );
    return box;
  }

  _export() {
    const blob = new Blob([JSON.stringify({settings:this.data.settings, items:this.data.items}, null, 2)], {type:"application/json"});
    const a = el("a", {href:URL.createObjectURL(blob), download:"wunschliste-" + new Date().toISOString().slice(0, 10) + ".json"});
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 5000);
  }

  render() {
    if (!this.app) return;
    const ui = this.ui, app = this.app;
    const focusId = document.activeElement && document.activeElement.id;
    app.textContent = "";
    const items = (this.data && this.data.items) || [];
    const free = items.filter(i => !i.reservedBy).length;

    const linkBox = el("div", {"class":"howto"}, [
      el("b", null, ["Öffentlicher Link für Familie und Freunde"]), el("br"),
      this.publicUrl ? el("a", {href:this.publicUrl, target:"_blank", rel:"noopener", "class":"shop", style:"word-break:break-all;white-space:normal"}, [this.publicUrl]) : "wird ermittelt …",
      el("br"),
      this.publicUrl ? el("button", {"class":"btn", style:"margin-top:6px", onclick:async () => {
        try { await navigator.clipboard.writeText(this.publicUrl); ui.msg = "Link kopiert."; ui.err = false; }
        catch (e) { ui.msg = "Kopieren ging nicht, bitte den Link markieren."; ui.err = true; }
        this.render();
      }}, ["Link kopieren"]) : null,
      this.publicIsLocal ? el("p", {"class":"note", style:"margin:6px 0 0"}, ["Das ist eine Adresse aus deinem Heimnetz. Damit andere die Seite sehen, muss Home Assistant von außen erreichbar sein (z. B. Nabu Casa oder eigene Domain)."]) : null
    ]);

    app.append(el("header", null, [
      el("span", {"class":"eyebrow"}, ["Wunschliste bearbeiten"]),
      el("h1", null, [(this.data && this.data.settings && this.data.settings.title) || "Wunschliste"]),
      el("div", {"class":"facts"}, [
        el("span", {"class":"fact"}, [el("b", null, [String(free)]), " von " + items.length + " Wünschen noch frei"])
      ]),
      linkBox
    ]));

    app.append(el("div", {"class":"editbar"}, [
      !ui.adding ? el("button", {"class":"btn primary", onclick:() => { ui.adding = true; this.render(); }}, ["Wunsch hinzufügen"]) : null,
      el("button", {"class":"btn", "aria-pressed":ui.showSettings ? "true" : "false", onclick:() => { ui.showSettings = !ui.showSettings; this.render(); }}, ["Texte und Termin"]),
      el("button", {"class":"btn", "aria-pressed":ui.showImport ? "true" : "false", onclick:() => { ui.showImport = !ui.showImport; this.render(); }}, ["Import / Export"]),
      ui.msg ? el("span", {"class":"status" + (ui.err ? " err" : ""), role:"status"}, [ui.msg]) : null
    ]));
    if (!this.data) { app.append(el("p", {"class":"note"}, ["Liste wird geladen …"])); return; }
    if (ui.showSettings) app.append(this.settingsForm());
    if (ui.showImport) app.append(this.importBox());
    if (ui.adding) app.append(this.itemForm({}, v => { ui.adding = false; this._ws({type:"wunschliste/item_save", item:Object.assign(v, {reservedBy:""})}, "Hinzugefügt."); }, () => { ui.adding = false; this.render(); }));

    const controls = el("div", {"class":"controls", role:"group", "aria-label":"Preisklasse"});
    [{key:"all", label:"Alle"}].concat(BANDS).forEach(b => {
      controls.appendChild(el("button", {id:"band-" + b.key, "class":"chip", "aria-pressed":ui.band === b.key ? "true" : "false", onclick:() => { ui.band = b.key; this.render(); }}, [b.label]));
    });
    const cb = el("input", {type:"checkbox", id:"hide-taken", checked:ui.hideTaken, onchange:() => { ui.hideTaken = cb.checked; this.render(); }});
    controls.appendChild(el("label", {"class":"toggle", "for":"hide-taken"}, [cb, "Vergebenes ausblenden"]));
    app.append(controls);

    if (!items.length) app.append(el("p", {"class":"howto"}, ["Noch keine Wünsche. Füg den ersten hinzu oder importiere eine Liste unter „Import / Export“."]));
    BANDS.forEach(b => {
      if (ui.band !== "all" && ui.band !== b.key) return;
      const all = items.filter(i => bandOf(i.price || 0) === b.key);
      if (!all.length && ui.band === "all") return;
      const shown = all.filter(i => !(ui.hideTaken && i.reservedBy));
      shown.sort((a, c) => (!!a.reservedBy - !!c.reservedBy) || ((a.price || 0) - (c.price || 0)));
      const freeN = all.filter(i => !i.reservedBy).length;
      app.append(el("section", {"class":"band" + (b.key === "zeit" ? " zeit" : ""), "aria-label":b.label}, [
        el("h2", null, [b.label, el("small", null, [freeN + " frei von " + all.length])]),
        el("ul", {"class":"items"}, shown.length ? shown.map(it => this.itemRow(it)) : [el("li", {"class":"empty"}, [all.length ? "Alles in dieser Preisklasse ist schon vergeben." : "Hier steht noch nichts."])])
      ]));
    });
    if (focusId) { const f = document.getElementById(focusId); if (f) f.focus(); }
  }
}
if (!customElements.get("wunschliste-panel")) customElements.define("wunschliste-panel", WunschlistePanel);
