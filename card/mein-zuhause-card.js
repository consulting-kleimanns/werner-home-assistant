/*
 * mein-zuhause-card – Teil von „Werner“ (https://github.com/consulting-kleimanns/werner-home-assistant)
 * Einfache Bildschirme für Senioren: Start, Werner, Energie, Auto, Einstellen.
 * Lizenz: MIT
 *
 * Konfiguration (Beispiel):
 *   type: custom:mein-zuhause-card
 *   screen: start            # start | werner | energie | auto | einstellen
 *   bewohner: Erika          # optional, sonst Vorname der angemeldeten Person
 *   dashboard: mein-zuhause  # URL-Pfad des Dashboards (für die Kacheln)
 *   entities:                # optional: eigene Entity-IDs statt der Vorgaben
 *     netz: sensor.mein_zaehler_leistung
 *     bezug: sensor.mein_zaehler_bezug
 *     weather: weather.forecast_home
 *     person: person.erika
 *     locperm: sensor.erikas_handy_location_permission
 *     steps: sensor.erikas_handy_steps
 *   pv_kwp: 1.5              # Leistung des Balkonkraftwerks für die Sonnen-Schätzung
 *   pv_text: Balkonkraftwerk mit 1,5 kWp und Batterie.
 *   pv_hinweis / batterie_hinweis: Text, solange keine Werte da sind
 *   auto_name: Auto          # z. B. „Kleiner Stromer“
 */
const MZ_VERSION = '0.1.0';
const E_DEFAULT = {
  status: 'input_select.werner_status', pause: 'input_boolean.werner_pausiert', pauseBis: 'input_datetime.werner_pause_bis',
  letzte: 'input_datetime.werner_letzte_aktivitat', netz: 'sensor.werner_hausleistung', bezug: 'sensor.werner_strombezug',
  weather: 'weather.forecast_home', person: 'person.bewohner', iphone: 'device_tracker.bewohner_handy',
  locperm: 'sensor.bewohner_handy_location_permission', steps: 'sensor.bewohner_handy_steps',
  rMorgen: 'input_boolean.werner_regel_morgens_nichts_los', rRuhe: 'input_boolean.werner_regel_tagsuber_lange_still', rNacht: 'input_boolean.werner_regel_nachts_ungewohnlich_aktiv',
  qr: 'image.werner_signal_qr_code', mServer: 'input_text.werner_mail_server', mPort: 'input_number.werner_mail_port', mUser: 'input_text.werner_mail_benutzer', mPass: 'input_text.werner_mail_passwort', mMode: 'input_select.werner_mail_verschluesselung', qrc: 'counter.werner_signal_qr', nMorgen: 'input_number.werner_morgens_bis_uhr', nRuhe: 'input_number.werner_ruhe_stunden', nWarten: 'input_number.werner_wartezeit_minuten'
};
let E = Object.assign({}, E_DEFAULT);
const P = (n, k) => `input_${k === 'weg' ? 'select' : 'text'}.werner_person_${n}_${k}`;

const CSS = `
:host{display:block}
*{box-sizing:border-box}
.wrap{font-family:'Atkinson Hyperlegible',system-ui,sans-serif;color:#1E2421;background:#F5F2EA;padding:20px 18px 110px;display:flex;flex-direction:column;gap:14px;max-width:560px;margin:0 auto}
h1{margin:0;font-size:28px;line-height:1.15}
h1.big{font-size:30px}
.muted{font-size:16px;color:#55605A;line-height:1.4}
.small{font-size:15px;color:#55605A;line-height:1.4}
.card{background:#FFF;border:1px solid #E2DDD1;border-radius:18px;padding:16px;display:flex;flex-direction:column;gap:10px}
.box{border-radius:18px;padding:16px 18px;display:flex;flex-direction:column;gap:6px}
.ok{background:#E3F0E8;border:1px solid #BFD9C9;color:#1F4D38}
.warn{background:#FBEBD6;border:1px solid #E8C79B;color:#6E3B0B}
.err{background:#FBE3E0;border:1px solid #E9B3AD;color:#7A1C15}
.grey{background:#EFEBE2;border:1px solid #C9C3B5;color:#3E4541}
.t-xl{font-size:22px;font-weight:700;line-height:1.25}.t-l{font-size:20px;font-weight:700}.t-m{font-size:18px;font-weight:700}
.txt{font-size:16px;line-height:1.4}
.grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
button{font-family:inherit;cursor:pointer;-webkit-tap-highlight-color:transparent}
.tile{text-align:left;background:#FFF;border:1px solid #E2DDD1;border-radius:18px;padding:16px;display:flex;flex-direction:column;gap:6px;color:#1E2421;min-height:120px}
.tile .l{font-size:15px;color:#55605A}.tile .v{font-size:32px;font-weight:700}.tile .s{font-size:15px;color:#55605A}
.bar{display:block;height:10px;border-radius:5px;background:#E6E1D6;overflow:hidden}.bar>span{display:block;height:10px;background:#2E6B4F}
.pill{align-self:flex-start;min-height:48px;border-radius:24px;padding:0 18px;font-size:16px;font-weight:700}
.pill.ok,.pill.warn,.pill.grey{border-width:1px}.pill.err{border:none;background:#A3261D;color:#FFF}
.ai{text-align:left;background:#1F4E79;border:none;border-radius:18px;padding:16px 18px;display:flex;align-items:center;gap:14px;color:#FFF;min-height:76px;text-decoration:none}
.btn{min-height:56px;border-radius:16px;font-size:17px;font-weight:700;border:1px solid #C9C3B5;background:#FFF;color:#1E2421}
.btn.blue{border:none;background:#1F4E79;color:#FFF}.btn.red{border:none;background:#A3261D;color:#FFF;min-height:60px;font-size:20px}
.btn.green{border:none;background:#2E6B4F;color:#FFF}
.days{display:flex;gap:10px;overflow-x:auto;padding-bottom:4px}
.day{flex-shrink:0;width:100px;white-space:nowrap;min-height:120px;border-radius:16px;padding:10px;display:flex;flex-direction:column;align-items:flex-start;gap:2px;text-align:left;border:1px solid #E2DDD1;background:#FFF;color:#1E2421}
.day.good{background:#FBF1D9;color:#5A3E05}.day.sel{border:3px solid #1F4E79}
.log{display:flex;gap:12px;font-size:16px;align-items:baseline}.log b{width:48px;flex-shrink:0}
.sub{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;background:#E9E4D8;border-radius:16px;padding:5px}
.sub button{min-height:48px;border-radius:12px;border:none;font-size:15px;padding:0 2px;background:transparent;color:#3E4541}
.sub button.on{background:#FFF;color:#12324F;font-weight:700}
.nr{width:38px;height:38px;flex-shrink:0;border-radius:19px;background:#1F4E79;color:#FFF;font-size:18px;font-weight:700;display:flex;align-items:center;justify-content:center}
.ch{min-height:48px;border-radius:12px;border:1px solid #E2DDD1;background:#FFF;color:#55605A;font-size:16px}
.ch.on{border:2px solid #1F4E79;background:#E6EEF6;color:#12324F;font-weight:700}
.row{display:flex;align-items:center;gap:12px}.between{display:flex;align-items:center;justify-content:space-between;gap:10px}
.sw{width:64px;height:38px;flex-shrink:0;border-radius:19px;border:none;padding:4px;display:flex;background:#C9C3B5;justify-content:flex-start}
.sw.on{background:#2E6B4F;justify-content:flex-end}.sw>span{display:block;width:30px;height:30px;border-radius:15px;background:#FFF}
.pm{width:52px;height:52px;border-radius:14px;border:1px solid #E2DDD1;background:#FFF;color:#1E2421;font-size:24px}
.val{flex-grow:1;text-align:center;font-size:20px;font-weight:700}
.badge{align-self:flex-start;font-size:14px;font-weight:700;border-radius:10px;padding:4px 10px}
.badge.ok{border:none}.badge.warn{border:none}.badge.blue{background:#E6EEF6;color:#12324F}.badge.grey{border:none}
.edit{min-height:44px;border-radius:12px;border:1px solid #E2DDD1;background:#FFF;color:#1F4E79;font-size:15px;font-weight:700;padding:0 12px;text-align:left}
.mode{text-align:left;min-height:84px;border-radius:18px;padding:14px 16px;display:flex;flex-direction:column;gap:4px;border:1px solid #E2DDD1;background:#FFF;color:#1E2421}
.mode.on{border:3px solid #1F4E79;background:#E6EEF6;color:#12324F}
.spin{width:44px;height:44px;border-radius:22px;border:5px solid #E2DDD1;border-top-color:#1F4E79;animation:mzspin 1s linear infinite}@keyframes mzspin{to{transform:rotate(360deg)}}
button[disabled]{opacity:.55;cursor:default}
.sheet-bg{position:fixed;inset:0;background:rgba(30,36,33,.6);display:flex;align-items:flex-end;z-index:20}
.sheet{width:100%;max-width:560px;margin:0 auto;background:#FFF;border-radius:26px 26px 0 0;padding:26px 18px 34px;display:flex;flex-direction:column;gap:12px}
`;

const fmtW = (w) => { const n = Number(w); if (isNaN(n)) return '–'; return Math.abs(n) >= 1000 ? (n / 1000).toLocaleString('de-DE', { maximumFractionDigits: 1 }) + ' kW' : Math.round(n) + ' W'; };
const hm = (d) => d.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
const COND = { sunny: 'Sonnig', 'clear-night': 'Klar', partlycloudy: 'Wolkig', cloudy: 'Bedeckt', fog: 'Nebel', rainy: 'Regen', pouring: 'Starkregen', snowy: 'Schnee', 'snowy-rainy': 'Schneeregen', lightning: 'Gewitter', 'lightning-rainy': 'Gewitter', windy: 'Windig', 'windy-variant': 'Windig', hail: 'Hagel', exceptional: 'Unwetter' };
// grobe Sonnenstrom-Schätzung aus Bewölkung und Monat (kWp über die Karten-Option pv_kwp, Vorgabe 1,5)
function sunKwh(f, date, kwp) {
  kwp = kwp || 1.5;
  const m = date.getMonth(); const peakH = [1.6, 2.2, 3.2, 4.2, 5, 5.4, 5.4, 4.8, 3.8, 2.8, 1.8, 1.4][m];
  let cc = f.cloud_coverage; if (cc == null) cc = { sunny: 10, partlycloudy: 50, cloudy: 90, fog: 95 }[f.condition] ?? 85;
  if (/rain|pour|snow|lightning|hail/.test(f.condition || '')) cc = Math.max(cc, 92);
  const k = kwp * peakH * (1 - 0.8 * cc / 100) * 0.85; return { k, good: k >= kwp * peakH * 0.85 * 0.55 };
}

class MeinZuhauseCard extends HTMLElement {
  setConfig(c) { this._c = Object.assign({ screen: 'start' }, c || {}); E = Object.assign({}, E_DEFAULT, this._c.entities || {}); this._ui = this._ui || { day: 0, sub: 'wer', sheet: null }; this._sig = ''; }
  getCardSize() { return 12; }
  getGridOptions() { return { columns: 'full' }; }
  connectedCallback() { this._hideHeader(); }
  disconnectedCallback() { if (this._unsub) { this._unsub.then((u) => u && u()).catch(() => {}); this._unsub = null; } }
  set hass(h) {
    this._h = h;
    if (!this.shadowRoot) { this.attachShadow({ mode: 'open' }); this.shadowRoot.addEventListener('click', (ev) => this._click(ev)); }
    if (!this._unsub && h.states[E.weather] && ['start', 'energie', 'auto'].includes(this._c.screen)) {
      this._unsub = h.connection.subscribeMessage((m) => { this._fc = m.forecast; this._render(true); }, { type: 'weather/subscribe_forecast', forecast_type: 'daily', entity_id: E.weather });
    }
    if (this._c.screen === 'einstellen' && (!this._sigT || Date.now() - this._sigT > 120000)) this._loadSignal();
    if (this._c.screen === 'werner' && (!this._logT || Date.now() - this._logT > 60000)) this._loadLog();
    this._render(false);
  }
  _bn() { return this._c.bewohner || ((this._h && this._h.user && this._h.user.name) || '').split(' ')[0]; }
  _s(id) { const s = this._h && this._h.states[id]; return s ? s.state : undefined; }
  _n(id) { const v = parseFloat(this._s(id)); return isNaN(v) ? null : v; }
  _render(force) {
    const ids = Object.values(E).concat([1, 2, 3].flatMap((n) => ['name', 'weg', 'telefon', 'e_mail', 'kontakt'].map((k) => P(n, k))));
    const sig = ids.map((i) => this._s(i)).join('|') + JSON.stringify(this._ui) + (this._log ? this._log.length : 0) + (this._fc ? this._fc.length : 0) + JSON.stringify(this._sigAcc || null) + (this._mailRes || '') + (this._qrBusy ? 'B' : '') + (this._qrErr ? 'E' : '') + (this._sigBusy ? 'S' : '') + JSON.stringify(this._tests || {});
    if (!force && sig === this._sig) return; this._sig = sig;
    const fn = { start: this._start, werner: this._werner, energie: this._energie, auto: this._auto, einstellen: this._einstellen }[this._c.screen] || this._start;
    let html = fn.call(this);
    if (this._ui.sheet === 'hilfe') html += this._sheetHilfe();
    if (this._ui.sheet === 'info') html += this._sheetInfo();
    this.shadowRoot.innerHTML = `<style>${CSS}</style><div class="wrap">${html}</div>`;
  }
  _hideHeader() {
    if (this._c && this._c.hide_header === false) return;
    setTimeout(() => {
      try {
        if (/[?&](kopf|edit)=1/.test(location.search)) return;
        let n = this; while (n) { if (n.tagName === 'HUI-ROOT') break; n = n.parentNode || n.host; }
        const sr = n && n.shadowRoot; if (!sr || sr.getElementById('mz-hide')) return;
        const st = document.createElement('style'); st.id = 'mz-hide';
        st.textContent = '.header{display:none!important}#view{padding-top:env(safe-area-inset-top)!important;min-height:100vh!important}';
        sr.appendChild(st);
      } catch (e) { /* nicht kritisch */ }
    }, 300);
  }
  /* ---------- Werner-Status ---------- */
  _wv() {
    const st = this._s(E.status) || 'Alles in Ordnung'; const paused = this._s(E.pause) === 'on';
    const la = this._h.states[E.letzte]; let seit = '';
    if (la && la.attributes && la.attributes.timestamp) { const d = new Date(la.attributes.timestamp * 1000); seit = ' Zuletzt aktiv: ' + hm(d) + ' Uhr' + (d.toDateString() === new Date().toDateString() ? '' : ', ' + d.toLocaleDateString('de-DE', { day: 'numeric', month: 'numeric' })) + '.'; }
    const first = (this._s(P(1, 'name')) || '').trim();
    if (paused) { const b = this._h.states[E.pauseBis]; let bis = ''; if (b && b.attributes.timestamp) bis = ' Bis ' + new Date(b.attributes.timestamp * 1000).toLocaleString('de-DE', { weekday: 'long', hour: '2-digit', minute: '2-digit' }) + ' Uhr.'; return { cls: 'grey', pill: 'Werner pausiert', title: 'Werner pausiert', text: 'Zum Beispiel wegen Besuch oder Urlaub. Werner meldet nichts.' + bis }; }
    if (st === 'Fragt nach') return { cls: 'warn', pill: 'Werner fragt nach', title: 'Werner fragt nach', text: 'Bitte bestätigen Sie kurz, dass alles in Ordnung ist.' };
    if (st === 'Vertrauensperson informiert') return { cls: 'err', pill: 'Hilfe ist unterwegs', title: 'Vertrauensperson informiert', text: first ? 'Werner hat ' + first + ' benachrichtigt. Antwortet niemand, geht es in Ihrer Reihenfolge weiter.' : 'Werner empfiehlt den Notruf 112.' };
    if (st === 'Hilfe angefordert') return { cls: 'err', pill: 'Hilfe ist unterwegs', title: 'Hilfe angefordert', text: first ? 'Werner informiert ' + first + '.' : 'Sie haben niemanden eingetragen. Rufen Sie bitte 112 an.' };
    return { cls: 'ok', pill: 'Werner: Alles in Ordnung', title: 'Alles in Ordnung', text: 'Ihr Tag verläuft wie gewohnt.' + seit };
  }
  /* ---------- Wetter-Tipps ---------- */
  _days() {
    const fc = (this._fc || []).slice(0, 5); const names = ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'];
    return fc.map((f, i) => { const d = new Date(f.datetime); const sk = sunKwh(f, d, Number(this._c.pv_kwp) || 1.5); const k = sk.k; return { i, name: i === 0 ? 'Heute' : i === 1 ? 'Morgen' : names[d.getDay()], long: i === 0 ? 'Heute' : i === 1 ? 'Morgen' : d.toLocaleDateString('de-DE', { weekday: 'long' }), weather: COND[f.condition] || f.condition, kwh: k, good: sk.good, t: f.temperature }; });
  }
  _tip(d, best) {
    const k = d.kwh.toLocaleString('de-DE', { maximumFractionDigits: 1 });
    if (d.good) return { cls: 'ok', title: d.long + ' ist ein Sonnentag', text: 'Etwa ' + k + ' kWh Sonnenstrom erwartet. Zwischen 11 und 14 Uhr lohnt sich Waschen, Spülen und Auto laden.' };
    if (best && best.i !== d.i) return { cls: '', title: d.long + ': lohnt sich wenig', text: 'Nur etwa ' + k + ' kWh Sonne. Besser ' + (best.i === 1 ? 'morgen' : 'am ' + best.long) + ' mittags waschen und laden.' };
    return { cls: '', title: d.long + ': wenig Sonne', text: 'Nur etwa ' + k + ' kWh Sonne. In den nächsten Tagen wird es nicht besser – waschen Sie, wann es Ihnen passt.' };
  }
  _bestDay(days) { return days.slice(0, 4).reduce((a, b) => (!a || b.kwh > a.kwh ? b : a), null); }
  /* ---------- Bildschirme ---------- */
  _start() {
    const now = new Date(); const h = now.getHours(); const gruss = h < 11 ? 'Guten Morgen' : h < 18 ? 'Guten Tag' : 'Guten Abend';
    const name = this._c.bewohner || ((this._h.user && this._h.user.name) || '').split(' ')[0];
    const w = this._wv(); const days = this._days(); const best = this._bestDay(days);
    let emp = '';
    if (best) { const t = best.good ? (best.i === 0 ? 'Heute mittags waschen' : 'Waschen lieber ' + (best.i === 1 ? 'morgen' : 'am ' + best.long) + ' ab 11 Uhr') : 'Diese Woche wenig Sonne'; emp = `<section class="box ${best.good ? 'ok' : 'grey'}"><div class="t-xl" style="font-size:21px">${t}</div><div class="txt" style="font-size:17px">${this._tip(best, best).text}</div></section>`; }
    const netz = this._n(E.netz);
    return `<header style="display:flex;flex-direction:column;gap:10px"><div style="font-size:17px;color:#55605A">${now.toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long' })}</div>
<h1 class="big">${gruss}${name ? ', ' + name : ''}</h1><button class="pill ${w.cls}" data-nav="werner">${w.pill}</button></header>${emp}
<div class="grid2">
<button class="tile" data-nav="energie"><span class="l">Balkon liefert</span><span class="v">–</span><span class="s">${this._c.pv_hinweis || 'noch keine Daten'}</span></button>
<button class="tile" data-nav="energie"><span class="l">Batterie</span><span class="v">–</span><span class="bar"><span style="width:0"></span></span></button>
<button class="tile" data-nav="energie"><span class="l">${netz != null && netz < 0 ? 'Ins Netz' : 'Aus dem Netz'}</span><span class="v">${fmtW(netz == null ? NaN : Math.abs(netz))}</span><span class="s">am Zähler</span></button>
<button class="tile" data-nav="auto"><span class="l">${this._c.auto_name || 'Auto'}</span><span class="v" style="font-size:26px">Laden</span><span class="s">Plan und Modus</span><span style="font-size:15px;color:#1F4E79;font-weight:700">Ändern ›</span></button>
</div>
<a class="ai" href="https://claude.ai/new" target="_blank" rel="noopener"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16v11H9l-5 4z"/><path d="M8 10h8M8 13h5"/></svg><span style="display:flex;flex-direction:column;gap:2px"><span style="font-size:19px;font-weight:700">Claude fragen</span><span style="font-size:15px">Sprechen, schreiben oder ein Foto schicken</span></span></a>`;
  }
  _energie() {
    const days = this._days(); const best = this._bestDay(days); const sel = days[this._ui.day] || days[0];
    const netz = this._n(E.netz); const bezug = this._n(E.bezug);
    const tip = sel ? this._tip(sel, best) : null;
    return `<h1>Energie heute</h1><div class="muted">${this._c.pv_text || 'Balkonkraftwerk mit ' + String(Number(this._c.pv_kwp) || 1.5).replace('.', ',') + ' kWp.'}</div>
<div class="grid2">
<div class="card" style="padding:14px;gap:4px"><span class="small">Gerade aus dem Netz</span><span style="font-size:26px;font-weight:700">${fmtW(netz)}</span></div>
<div class="card" style="padding:14px;gap:4px"><span class="small">Zählerstand</span><span style="font-size:26px;font-weight:700">${bezug == null ? '–' : Math.round(bezug).toLocaleString('de-DE') + ' kWh'}</span></div>
<div class="card" style="padding:14px;gap:4px"><span class="small">Vom Balkon</span><span style="font-size:26px;font-weight:700">–</span></div>
<div class="box warn" style="padding:14px;gap:4px;border-radius:16px"><span style="font-size:15px">Batterie</span><span style="font-size:18px;font-weight:700">${this._c.batterie_hinweis || 'noch keine Daten'}</span></div>
</div>
<section style="display:flex;flex-direction:column;gap:10px"><div class="t-l">Die nächsten Tage</div>
<div class="days">${days.map((d) => `<button class="day ${d.good ? 'good' : ''} ${d.i === (sel && sel.i) ? 'sel' : ''}" data-day="${d.i}"><span style="font-size:16px;font-weight:700">${d.name}</span><span style="font-size:14px">${d.weather}</span><span style="font-size:20px;font-weight:700">${d.kwh.toLocaleString('de-DE', { maximumFractionDigits: 1 })} kWh</span><span style="font-size:13px">Sonnenstrom</span></button>`).join('') || '<div class="muted">Vorhersage wird geladen …</div>'}</div>
${tip ? `<div class="box ${tip.cls || 'card'}" style="border-radius:16px;padding:14px 16px;gap:4px"><div class="t-m">${tip.title}</div><div class="txt">${tip.text}</div></div>` : ''}</section>
<section style="display:flex;flex-direction:column;gap:10px"><div class="t-l">Meine Geräte</div>
${[[this._c.auto_name || 'Auto', 'braucht ca. 15 kWh', 'Steuert evcc automatisch', 'blue'], ['Waschmaschine', 'ca. 1 kWh je Wäsche', 'Tipp – Sie schalten selbst ein', 'grey'], ['Spülmaschine', 'ca. 1 kWh', 'Tipp – Sie schalten selbst ein', 'grey']].map((g) => `<div class="card" style="padding:14px;gap:6px"><div class="between" style="align-items:baseline"><span class="t-m">${g[0]}</span><span class="small">${g[1]}</span></div><div class="txt"><b>Beste Zeit:</b> ${best ? (best.good ? (best.i === 0 ? 'heute' : best.i === 1 ? 'morgen' : best.long) + ' 11–14 Uhr' : 'diese Woche egal') : '–'}</div><span class="badge ${g[3]}" style="${g[3] === 'grey' ? 'background:#EFEBE2;color:#3E4541' : ''}">${g[2]}</span></div>`).join('')}
</section><div class="small">Sonnenstrom ist eine grobe Schätzung aus der Wettervorhersage. Jede selbst genutzte Kilowattstunde Sonnenstrom spart Geld.</div>`;
  }
  _auto() {
    return `<h1>${this._c.auto_name || 'Auto'} laden</h1>
<div class="card"><div class="grid2"><div style="display:flex;flex-direction:column;gap:2px"><span class="small">Akku</span><span style="font-size:30px;font-weight:700">–</span></div><div style="display:flex;flex-direction:column;gap:2px"><span class="small">Reicht für ca.</span><span style="font-size:30px;font-weight:700">–</span></div></div>
<span class="bar" style="height:12px"><span style="width:0;background:#1F4E79"></span></span><div class="small">Der Ladestand erscheint, sobald Wallbox und Auto in evcc eingebunden sind.</div></div>
<div class="box warn"><div class="t-m">Laden folgt mit evcc</div><div class="txt">Ist die Wallbox angebunden, wählen Sie hier, bis wann das Auto voll sein soll und wie geladen wird.</div></div>
<div class="muted">So wird die Wallbox laden:</div>
${[['Sonne nutzen, Plan einhalten', 'Lädt mit Sonnenstrom und nur so viel Netzstrom, dass Ihr Plan sicher klappt. Empfohlen.', true], ['Nur mit Sonne', 'Lädt ausschließlich mit Strom vom Balkon. Kostet nichts, dauert lange.'], ['Sofort laden', 'Lädt gleich mit voller Leistung, auch mit Netzstrom.'], ['Pause', 'Das Auto wird nicht geladen.']].map((m) => `<div class="mode ${m[2] ? 'on' : ''}"><span class="t-l">${m[0]}</span><span style="font-size:15px;line-height:1.35">${m[1]}</span></div>`).join('')}
<div class="small">evcc plant das Laden mit der Sonnen-Vorhersage. Fehlt Sonne, lädt evcc rechtzeitig mit Netzstrom nach.</div>`;
  }
  _werner() {
    const w = this._wv(); const paused = this._s(E.pause) === 'on';
    const log = (this._log || []).slice(-8);
    return `<h1>Werner passt auf</h1><section class="box ${w.cls}"><div class="t-xl">${w.title}</div><div class="txt">${w.text}</div></section>
<section class="card"><div class="t-m">Zuletzt bemerkt</div>${log.length ? log.map((e) => `<div class="log"><b>${e.t}</b><span>${e.text}</span></div>`).join('') : '<div class="muted">In den letzten 24 Stunden nichts Besonderes.</div>'}</section>
<button class="edit" style="min-height:52px;font-size:17px;text-align:center" data-act="info">So funktioniert Werner</button>
<div class="small">Werner achtet nur auf den Stromverbrauch im Haus und darauf, ob Ihr iPhone zu Hause ist. Keine Kamera, kein Mikrofon.</div>
<div style="display:flex;flex-direction:column;gap:10px">
<button class="btn green" data-act="ok">Alles gut</button>
<button class="btn ${paused ? 'blue' : ''}" data-act="pause">${paused ? 'Werner wieder einschalten' : 'Werner pausieren (Besuch, Urlaub)'}</button>
${paused ? '<button class="edit" data-more="' + E.pauseBis + '">Pause endet … (ändern)</button>' : ''}
<button class="btn red" data-act="hilfe">Ich brauche Hilfe</button></div>`;
  }
  _sheetHilfe() {
    const first = (this._s(P(1, 'name')) || '').trim();
    return `<div class="sheet-bg" data-act="close"><div class="sheet" role="alertdialog"><div style="font-size:16px;color:#55605A;font-weight:700">Werner</div>
<div style="font-size:27px;font-weight:700;line-height:1.2">Soll Werner Hilfe holen?</div>
<div style="font-size:17px;line-height:1.45">${first ? 'Werner informiert sofort ' + first + ' und dann die nächsten Personen.' : 'Sie haben niemanden eingetragen. Rufen Sie bitte 112 an.'}</div>
<button class="btn red" style="min-height:64px;font-size:21px" data-act="hilfe-ja">Ja, bitte Hilfe holen</button>
<button class="btn" style="min-height:64px" data-act="close">Nein, doch nicht</button></div></div>`;
  }
  _einstellen() {
    const sub = this._ui.sub;
    const tabs = [['wer', 'Wer & wie'], ['wann', 'Wann'], ['sensoren', 'Sensoren'], ['mail', 'E-Mail']].map((t) => `<button class="${sub === t[0] ? 'on' : ''}" data-sub="${t[0]}">${t[1]}</button>`).join('');
    let body = '';
    if (sub === 'wer') {
      const people = [1, 2, 3].map((n) => ({ n, name: (this._s(P(n, 'name')) || '').trim(), weg: this._s(P(n, 'weg')), tel: (this._s(P(n, 'telefon')) || '').trim(), mail: (this._s(P(n, 'e_mail')) || '').trim() }));
      body = this._signalCard() + `<div class="txt">Zuerst fragt Werner <b>immer Sie selbst</b> auf dem iPhone. Antworten Sie nicht, informiert er nacheinander:</div>` + people.map((p) => {
        if (!p.name) return `<button class="edit" style="min-height:56px;border:2px dashed #1F4E79;font-size:17px;text-align:center" data-more="${P(p.n, 'name')}">+ ${p.n}. Person eintragen</button>`;
        const ch = [['Home-Assistant-App', 'HA-App'], ['Signal', 'Signal']];
        const sum = [p.weg && p.weg !== 'Aus' ? (p.weg === 'Home-Assistant-App' ? 'HA-App' : p.weg) : null, p.mail ? 'E-Mail' : null].filter(Boolean).join(' · ') || 'Noch kein Weg gewählt';
        return `<div class="card" style="padding:14px"><div class="row"><span class="nr">${p.n}</span><span style="display:flex;flex-direction:column;gap:2px;min-width:0"><span style="font-size:19px;font-weight:700">${p.name}</span><span class="small">${sum}</span></span></div>
<div class="small">So erreicht Werner diese Person:</div><div class="grid2" style="gap:8px">${ch.map((c) => `<button class="ch ${p.weg === c[0] ? 'on' : ''}" data-weg="${p.n}|${c[0]}">${p.weg === c[0] ? '✓ ' : ''}${c[1]}</button>`).join('')}
<button class="ch ${p.mail ? 'on' : ''}" data-more="${P(p.n, 'e_mail')}">${p.mail ? '✓ ' : ''}E-Mail</button><button class="ch ${p.weg === 'Aus' ? 'on' : ''}" data-weg="${p.n}|Aus">Nicht melden</button></div>
<div class="grid2" style="gap:8px"><button class="edit" data-more="${P(p.n, 'name')}">Name ändern</button><button class="edit" data-more="${P(p.n, 'telefon')}">Handynummer</button></div>
${this._testBlock(p.n)}</div>`;
      }).join('') + `<div class="small">Die Personen brauchen keine neue App. Sie bekommen nur die Meldung und die Uhrzeit – nicht Ihren Tagesablauf.</div>`;
    } else if (sub === 'wann') {
      const r = [
        { b: E.rMorgen, n: E.nMorgen, t: 'Morgens nichts los', x: 'Werner fragt nach, wenn bis zu dieser Uhrzeit noch nichts im Haus passiert ist.', f: (v) => 'bis ' + v + ':00 Uhr' },
        { b: E.rRuhe, n: E.nRuhe, t: 'Tagsüber lange still', x: 'Werner fragt nach, wenn Sie zu Hause sind und so lange nur Grundlast läuft.', f: (v) => v + ' Stunden' },
        { b: E.rNacht, t: 'Nachts ungewöhnlich aktiv', x: 'Werner fragt nach, wenn zwischen 0 und 5 Uhr ungewöhnlich viel passiert.', f: () => 'sofort' },
        { n: E.nWarten, t: 'Wartezeit auf Ihre Antwort', x: 'So lange wartet Werner auf Ihr „Alles gut“, bevor er die erste Person informiert.', f: (v) => v + ' Minuten' }
      ];
      body = r.map((d) => { const on = d.b ? this._s(d.b) === 'on' : true; const v = d.n ? this._n(d.n) : 0; return `<div class="card" style="padding:14px 16px"><div class="between"><span class="t-m" style="line-height:1.25">${d.t}</span>${d.b ? `<button class="sw ${on ? 'on' : ''}" role="switch" aria-checked="${on}" data-toggle="${d.b}"><span></span></button>` : ''}</div>
<div class="txt">${d.x}</div>${d.n ? `<div class="row" style="gap:10px"><button class="pm" data-step="${d.n}|-1">–</button><span class="val">${on ? d.f(v == null ? '–' : Math.round(v)) : 'aus'}</span><button class="pm" data-step="${d.n}|1">+</button></div>` : `<div class="val">${on ? d.f() : 'aus'}</div>`}</div>`; }).join('') + `<div class="small">Ist Ihr iPhone unterwegs oder Werner pausiert, gelten diese Regeln nicht.</div>`;
    } else if (sub === 'mail') {
      body = this._mailCard();
    } else {
      const lp = this._s(E.locperm) || ''; const strom = this._s(E.netz) != null && this._s(E.netz) !== 'unavailable';
      const s = [
        ['Stromverbrauch im Haus', 'Am Zähler gemessen: Wasserkocher, Herd, Fernseher zeigen Ihren Tagesrhythmus.', strom ? 'Vorhanden' : 'Noch nicht verbunden', strom],
        ['Ihr iPhone: zu Hause oder unterwegs', 'Sind Sie unterwegs, schweigt Werner.', /always/i.test(lp) ? 'Vorhanden' : 'Vorhanden – Standort auf „Immer“ stellen', /always/i.test(lp)],
        ['Schritte vom iPhone', 'Zeigt, ob Sie sich bewegen. Nur die Anzahl, kein Ort.', this._s(E.steps) && this._s(E.steps) !== 'unavailable' ? 'Vorhanden' : 'Freigabe „Bewegung & Fitness“ nötig', this._s(E.steps) && this._s(E.steps) !== 'unavailable'],
        ['iPad wird benutzt', 'Wenn Sie das iPad aufwecken, weiß Werner: alles in Ordnung.', 'App auf dem iPad einrichten', false],
        ['Bewegungsmelder (Flur, Bad)', 'Kleine Funksensoren ohne Kamera. Machen Werner deutlich zuverlässiger.', 'Empfohlen – noch nicht vorhanden', false]
      ];
      body = `<div class="txt">Woran Werner Ihren Tag erkennt.</div>` + s.map((x) => `<div class="card" style="padding:14px 16px;gap:6px"><span class="t-m">${x[0]}</span><div style="font-size:15px;line-height:1.4;color:#3E4541">${x[1]}</div><span class="badge ${x[3] ? 'ok' : 'warn'}">${x[2]}</span></div>`).join('') + `<div class="small">Werner nutzt keine Kamera und kein Mikrofon.</div>`;
    }
    return `<h1>Werner einstellen</h1><div class="muted">Sie bestimmen, wer wie und wann informiert wird. Niemand sonst kann das ändern.</div><button class="edit" style="min-height:52px;font-size:17px;text-align:center" data-act="info">So funktioniert Werner</button><div class="sub" role="tablist">${tabs}</div>${body}`;
  }
  _signalCard() {
    if (this._qrBusy) { const cur = this._h.states[E.qr]; if (cur && cur.state !== this._qrBefore) { this._qrBusy = false; this._qrErr = false; } else if (Date.now() - this._qrT > 45000) { this._qrBusy = false; this._qrErr = true; } }
    const acc = this._sigAcc;
    if (acc && acc.length && !this._ui.qr) return `<div class="box ok" style="padding:14px 16px"><div class="t-m">Signal ist verbunden</div><div class="txt">Werner schreibt Ihren Vertrauenspersonen über Ihr Signal-Konto.</div></div>`;
    if (!this._ui.qr) return `<div class="box warn" style="padding:14px 16px;gap:10px"><div class="t-m">${acc === null ? 'Signal wird geprüft …' : 'Signal ist noch nicht verbunden'}</div><div class="txt">Damit Werner Nachrichten über Signal schicken kann, verbinden Sie einmal Ihr Signal mit Werner.</div>${acc === null ? '' : '<button class="btn blue" data-act="qr">Signal verbinden</button>'}</div>`;
    const st = this._h.states[E.qr]; const pic = st && st.attributes.entity_picture;
    const ok = acc && acc.length;
    return `<div class="card" style="gap:12px"><div class="t-m">Signal mit Werner verbinden</div>
${ok ? '<div class="box ok" style="padding:12px 14px"><div class="t-m">Geschafft – Signal ist verbunden</div></div>' : ''}
<div class="txt">Sie brauchen dafür <b>zwei Geräte</b>: diese Seite auf dem <b>iPad</b> und Ihr <b>iPhone</b> zum Scannen.</div>
<ol style="margin:0;padding-left:22px;font-size:16px;line-height:1.5"><li>Öffnen Sie auf dem iPhone die App <b>Signal</b>.</li><li>Tippen Sie oben links auf Ihr Bild, dann auf <b>Einstellungen</b>.</li><li>Tippen Sie auf <b>Verknüpfte Geräte</b> und dann auf <b>Neues Gerät verknüpfen</b>.</li><li>Halten Sie das iPhone über diesen Code.</li><li>Tippen Sie auf <b>Gerät verknüpfen</b>.</li></ol>
<div style="background:#FFF;border:1px solid #E2DDD1;border-radius:16px;padding:12px;align-self:center">${this._qrBusy ? '<div style="width:240px;height:240px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;text-align:center"><div class="spin"></div><div class="txt"><b>Der Code wird erstellt.</b><br>Bitte warten Sie einen Moment.<br>Das dauert bis zu 30 Sekunden.</div></div>' : this._qrErr ? '<div style="width:240px;height:240px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;text-align:center"><div class="t-m" style="color:#7A1C15">Das hat nicht geklappt.</div><div class="txt">Tippen Sie auf „Neuer Code“. Klappt es wieder nicht, fragen Sie Ihre Vertrauensperson.</div></div>' : pic ? `<img src="${pic}&v=${encodeURIComponent(st.state)}" alt="QR-Code zum Verbinden" onerror="(this.getRootNode().host||{_qrFail(){}})._qrFail()" style="width:240px;height:240px;display:block;image-rendering:pixelated">` : '<div class="muted" style="width:240px;height:240px;display:flex;align-items:center;justify-content:center">Code wird erstellt …</div>'}</div>
<div class="small">Der Code gilt nur wenige Minuten. Ist er abgelaufen, tippen Sie auf „Neuer Code“.</div>
<div class="grid2" style="gap:8px"><button class="btn" data-act="qr" ${this._qrBusy ? 'disabled' : ''}>Neuer Code</button><button class="btn green" data-act="qr-check" ${this._sigBusy || this._qrBusy ? 'disabled' : ''}>${this._sigBusy ? 'Wird geprüft …' : ok ? 'Fertig' : 'Ich habe gescannt'}</button></div>
${this._sigChecked && !ok && !this._sigBusy ? '<div class="box warn" style="padding:12px 14px"><div class="txt">Noch nicht verbunden. Haben Sie auf dem iPhone „Gerät verknüpfen“ getippt? Warten Sie kurz und tippen Sie dann noch einmal auf „Ich habe gescannt“.</div></div>' : ''}</div>`;
  }
  _mailCard() {
    const v = (id) => (this._s(id) || '').trim();
    const server = v(E.mServer), user = v(E.mUser), pass = v(E.mPass), mode = v(E.mMode), port = this._n(E.mPort);
    const ready = server && user && pass;
    const presets = [['GMX', 'mail.gmx.net', 587, 'STARTTLS'], ['WEB.DE', 'smtp.web.de', 587, 'STARTTLS'], ['Gmail', 'smtp.gmail.com', 587, 'STARTTLS'], ['T-Online', 'securesmtp.t-online.de', 465, 'SSL/TLS']];
    const cur = presets.find((x) => x[1] === server);
    const to = [1, 2, 3].map((n) => v(P(n, 'e_mail'))).find((m) => m.includes('@'));
    const res = this._mailRes ? JSON.parse(this._mailRes) : null;
    const row = (label, val, id) => `<div class="between" style="border-top:1px solid #EFEBE2;padding-top:10px"><span style="display:flex;flex-direction:column;gap:2px;min-width:0"><span class="small">${label}</span><span style="font-size:17px;font-weight:700;word-break:break-all">${val || '–'}</span></span><button class="edit" data-more="${id}">Ändern</button></div>`;
    return `<div class="txt">Werner schickt Ihren Vertrauenspersonen zusätzlich eine <b>E-Mail</b>. Dafür braucht Werner ein eigenes E-Mail-Postfach. Das richtet am besten eine Vertrauensperson ein.</div>
<div class="box ${ready ? 'ok' : 'warn'}" style="padding:14px 16px"><div class="t-m">${ready ? 'E-Mail ist eingerichtet' : 'E-Mail ist noch nicht eingerichtet'}</div><div class="txt">${ready ? 'Werner sendet von ' + user + '.' : 'Bitte Anbieter wählen und Benutzer und Passwort eintragen.'}</div></div>
<div class="card"><div class="t-m">Anbieter</div><div class="grid2" style="gap:8px">${presets.map((x) => `<button class="ch ${cur && cur[0] === x[0] ? 'on' : ''}" data-preset="${x[1]}|${x[2]}|${x[3]}">${cur && cur[0] === x[0] ? '✓ ' : ''}${x[0]}</button>`).join('')}</div>
${row('Postausgangs-Server (SMTP)', server, E.mServer)}${row('Port', port == null ? '' : String(Math.round(port)), E.mPort)}${row('Verschlüsselung', mode, E.mMode)}${row('Benutzer (E-Mail-Adresse)', user, E.mUser)}${row('Passwort', pass ? '••••••••' : '', E.mPass)}
<div class="small">Bei Gmail ein „App-Passwort“ verwenden. Bei GMX und WEB.DE in den Postfach-Einstellungen „POP3/IMAP/SMTP-Zugriff“ erlauben.</div></div>
<div class="card"><div class="t-m">Test-E-Mail</div><div class="txt">${to ? 'Geht an ' + to + '.' : 'Tragen Sie zuerst bei einer Person eine E-Mail-Adresse ein.'}</div>
${res ? `<div class="box ${res.ok ? 'ok' : 'err'}" style="padding:12px 14px"><div class="txt">${res.text}</div></div>` : ''}
<button class="btn blue" data-act="mailtest" ${ready && to ? '' : 'disabled style="opacity:.5"'}>Test-E-Mail senden</button></div>
<div class="small">Das Passwort ist in Home Assistant gespeichert. Nehmen Sie deshalb ein Postfach, das nur Werner nutzt.</div>`;
  }
  async _mailTest() {
    const to = [1, 2, 3].map((n) => (this._s(P(n, 'e_mail')) || '').trim()).find((m) => m.includes('@'));
    this._mailRes = JSON.stringify({ ok: true, text: 'Wird gesendet …' }); this._render(true);
    try {
      const r = await this._h.callService('shell_command', 'werner_mail_senden', { an: to, betreff: 'Werner: Test-E-Mail', text: 'Hallo,\n\ndas ist eine Test-E-Mail von Werner aus Ihrem Zuhause. Wenn Sie diese E-Mail lesen, funktioniert der Versand.\n\n– Werner' }, undefined, false, true);
      const out = r && r.response; let j = null; try { j = JSON.parse((out.stdout || '').trim()); } catch (e) { /* kein JSON */ }
      this._mailRes = JSON.stringify(j || { ok: out && out.returncode === 0, text: (out && (out.stdout || out.stderr)) || 'Keine Antwort' });
    } catch (e) { this._mailRes = JSON.stringify({ ok: false, text: 'Fehler: ' + (e.message || e) }); }
    this._render(true);
  }
  _testBlock(n) {
    const t = (this._tests || {})[n];
    const busy = t === 'busy';
    const res = Array.isArray(t) ? t.map((x) => `<div class="box ${x.ok ? 'ok' : 'err'}" style="padding:10px 12px;gap:2px"><div style="font-size:15px;font-weight:700">${x.ok ? '✓ ' : '✗ '}${x.k}</div><div style="font-size:15px;line-height:1.35">${x.text}</div></div>`).join('') : '';
    return `<button class="btn" style="min-height:52px;font-size:16px" data-test="${n}" ${busy ? 'disabled' : ''}>${busy ? 'Test läuft …' : 'Test-Nachricht an diese Person senden'}</button>${res}${Array.isArray(t) && t.some((x) => x.ok) ? '<div class="small">Fragen Sie kurz nach, ob die Nachricht angekommen ist.</div>' : ''}`;
  }
  async _testPerson(n) {
    this._tests = this._tests || {};
    if (this._tests[n] === 'busy') return;
    this._tests[n] = 'busy'; this._render(true);
    const v = (k) => (this._s(P(n, k)) || '').trim();
    const name = v('name'), weg = this._s(P(n, 'weg')), tel = v('telefon'), mail = v('e_mail'), geraet = v('kontakt');
    const msg = 'Test von Werner: ' + (this._bn() || 'Ihr Angehöriger') + ' hat Sie als ' + n + '. Vertrauensperson eingetragen. Das ist nur ein Test – es ist alles in Ordnung. Bei einem echten Alarm bekommen Sie eine ähnliche Nachricht.';
    const out = [];
    const svc = (d, s, data) => this._h.callService(d, s, data, undefined, false, true).then((r) => (r && r.response) || {});
    try {
      if (weg === 'Home-Assistant-App') {
        if (!geraet) out.push({ k: 'HA-App', ok: false, text: 'Für diese Person ist kein Gerät hinterlegt.' });
        else { try { await this._h.callService('notify', geraet, { title: 'Werner (Test)', message: msg }); out.push({ k: 'HA-App', ok: true, text: 'An die HA-App von ' + name + ' gesendet.' }); } catch (e) { out.push({ k: 'HA-App', ok: false, text: 'Konnte nicht gesendet werden: ' + (e.message || e) }); } }
      }
      if (weg === 'Signal') {
        if (!tel) out.push({ k: 'Signal', ok: false, text: 'Bitte zuerst eine Handynummer eintragen.' });
        else {
          const acc = await svc('rest_command', 'werner_signal_konten', {}); const abs = Array.isArray(acc.content) ? acc.content[0] : null;
          if (!abs) out.push({ k: 'Signal', ok: false, text: 'Signal ist noch nicht verbunden. Bitte oben „Signal verbinden“ antippen.' });
          else {
            const r = await svc('rest_command', 'werner_signal_senden', { absender: abs, empfaenger: tel, message: msg });
            const ok = r.status >= 200 && r.status < 300;
            out.push({ k: 'Signal', ok, text: ok ? 'Per Signal an ' + tel + ' gesendet.' : 'Signal meldet einen Fehler (' + (r.status || '?') + '). Stimmt die Nummer und nutzt die Person Signal?' });
          }
        }
      }
      if (mail.includes('@')) {
        const r = await svc('shell_command', 'werner_mail_senden', { an: mail, betreff: 'Werner: Test – Sie sind als Vertrauensperson eingetragen', text: 'Hallo ' + name + ',\n\n' + msg + '\n\n– Werner' });
        let j = null; try { j = JSON.parse((r.stdout || '').trim()); } catch (e) { /* kein JSON */ }
        out.push({ k: 'E-Mail', ok: !!(j && j.ok), text: j ? j.text : 'Keine Antwort vom Mail-Versand.' });
      }
      if (!out.length) out.push({ k: 'Kein Weg', ok: false, text: 'Für diese Person ist kein Weg gewählt.' });
    } catch (e) { out.push({ k: 'Fehler', ok: false, text: String(e.message || e) }); }
    this._tests[n] = out; this._render(true);
  }
  _qrFail() { if (!this._qrErr) { this._qrErr = true; this._render(true); } }
  async _loadSignal(manual) {
    this._sigT = Date.now(); if (manual) { this._sigBusy = true; this._render(true); }
    try {
      const r = await this._h.callService('rest_command', 'werner_signal_konten', {}, undefined, false, true);
      const resp = r && r.response; const c = resp && resp.content;
      this._sigAcc = Array.isArray(c) ? c : [];
    } catch (e) { this._sigAcc = this._sigAcc || []; }
    this._sigBusy = false; if (manual) this._sigChecked = true;
    this._render(true);
  }
  _sheetInfo() {
    const w = this._n(E.nWarten) || 10; const first = (this._s(P(1, 'name')) || '').trim();
    const li = (t) => `<li style="margin-bottom:10px">${t}</li>`;
    return `<div class="sheet-bg" data-act="close"><div class="sheet" style="max-height:85vh;overflow-y:auto"><div style="font-size:26px;font-weight:700;line-height:1.2">So funktioniert Werner</div>
<ul style="margin:0;padding-left:22px;font-size:18px;line-height:1.45">
${li('Werner passt auf, ob bei Ihnen <b>alles in Ordnung</b> ist.')}
${li('Werner merkt, wenn Sie <b>Strom</b> verbrauchen. Zum Beispiel beim Wasserkocher, am Herd oder beim Fernseher.')}
${li('Werner merkt auch, ob Ihr <b>iPhone zu Hause</b> ist. Sind Sie unterwegs, ist Werner still.')}
${li('Ist es <b>ungewöhnlich lange still</b>? Oder passiert <b>nachts</b> etwas Ungewöhnliches? Dann fragt Werner <b>zuerst Sie</b>: „Ist alles in Ordnung?“')}
${li('Tippen Sie dann auf <b>„Alles gut“</b>. Damit ist alles erledigt. Niemand wird gestört.')}
${li('Antworten Sie nicht innerhalb von <b>' + Math.round(w) + ' Minuten</b>? Dann schreibt Werner Ihrer Vertrauensperson' + (first ? ' – zuerst <b>' + first + '</b>' : '') + '.')}
${li('Brauchen Sie Hilfe? Tippen Sie auf <b>„Ich brauche Hilfe“</b>. Dann sagt Werner sofort Bescheid.')}
${li('Besuch oder Urlaub? Tippen Sie auf <b>„Werner pausieren“</b>. Dann meldet Werner nichts.')}
${li('Werner hat <b>keine Kamera</b> und <b>kein Mikrofon</b>. Ihre Vertrauenspersonen sehen nur die Meldung – nicht Ihren Tag.')}
${li('Sie bestimmen alles selbst: <b>wer</b>, <b>wie</b> und <b>wann</b>. Das stellen Sie unter „Einstellen“ ein.')}
</ul>
<div class="box err" style="padding:12px 14px"><div class="t-m">Im Notfall rufen Sie bitte 112 an.</div></div>
<button class="btn blue" data-act="close">Verstanden</button></div></div>`;
  }
  /* ---------- Logbuch ---------- */
  async _loadLog() {
    this._logT = Date.now();
    try {
      const start = new Date(); start.setHours(start.getHours() - 24);
      const ent = [E.status, E.pause, E.person, E.letzte].join(',');
      const res = await this._h.callApi('GET', `logbook/${start.toISOString()}?entity=${ent}`);
      const seen = new Set();
      this._log = (res || []).filter((e) => e.message || e.state).map((e) => {
        const d = new Date(e.when); let text = e.message || e.state;
        if (e.entity_id === E.person) text = e.state === 'home' ? 'Sie sind nach Hause gekommen' : e.state === 'not_home' ? 'Sie sind unterwegs – Werner schweigt' : text;
        else if (e.entity_id === E.pause) text = e.state === 'on' ? 'Werner pausiert' : 'Werner wieder eingeschaltet';
        else if (e.entity_id === E.status) text = 'Werner: ' + e.state;
        else if (e.entity_id === E.letzte) return null;
        return { t: hm(d), text, k: hm(d) + text };
      }).filter((x) => x && !seen.has(x.k) && seen.add(x.k));
      this._render(true);
    } catch (err) { this._log = []; }
  }
  /* ---------- Bedienung ---------- */
  _call(d, s, data) { return this._h.callService(d, s, data); }
  _more(id) { this.dispatchEvent(new CustomEvent('hass-more-info', { bubbles: true, composed: true, detail: { entityId: id } })); }
  _click(ev) {
    const el = ev.target.closest('[data-nav],[data-act],[data-day],[data-sub],[data-weg],[data-toggle],[data-step],[data-more],[data-preset],[data-test]');
    if (!el) return;
    const ds = el.dataset;
    if (ds.nav) { history.pushState(null, '', '/' + (this._c.dashboard || 'mein-zuhause') + '/' + ds.nav); window.dispatchEvent(new CustomEvent('location-changed')); return; }
    if (ds.day) { this._ui.day = Number(ds.day); this._render(true); return; }
    if (ds.sub) { this._ui.sub = ds.sub; this._render(true); return; }
    if (ds.test) { this._testPerson(Number(ds.test)); return; }
    if (ds.more) { this._more(ds.more); return; }
    if (ds.preset) { const [sv, pt, md] = ds.preset.split('|'); this._call('input_text', 'set_value', { entity_id: E.mServer, value: sv }); this._call('input_number', 'set_value', { entity_id: E.mPort, value: Number(pt) }); this._call('input_select', 'select_option', { entity_id: E.mMode, option: md }); return; }
    if (ds.weg) { const [n, opt] = ds.weg.split('|'); this._call('input_select', 'select_option', { entity_id: P(n, 'weg'), option: opt }); return; }
    if (ds.toggle) { this._call('input_boolean', 'toggle', { entity_id: ds.toggle }); return; }
    if (ds.step) { const [id, dir] = ds.step.split('|'); this._call('input_number', Number(dir) > 0 ? 'increment' : 'decrement', { entity_id: id }); return; }
    const a = ds.act;
    if (a === 'ok') this._call('script', 'werner_alles_gut', {}).then(() => { this._logT = 0; });
    if (a === 'pause') this._call('input_boolean', 'toggle', { entity_id: E.pause });
    if (a === 'hilfe') { this._ui.sheet = 'hilfe'; this._render(true); }
    if (a === 'mailtest') { this._mailTest(); return; }
    if (a === 'info') { this._ui.sheet = 'info'; this._render(true); }
    if (a === 'qr') {
      if (this._qrBusy) return;
      this._ui.qr = true; this._sigAcc = this._sigAcc || []; this._sigChecked = false;
      const cur = this._h.states[E.qr]; this._qrBefore = cur ? cur.state : ''; this._qrBusy = true; this._qrErr = false; this._qrT = Date.now();
      this._call('counter', 'increment', { entity_id: E.qrc });
      clearTimeout(this._qrTO); this._qrTO = setTimeout(() => this._render(true), 46000);
      this._render(true);
    }
    if (a === 'qr-check') { if (this._sigAcc && this._sigAcc.length && el.textContent.trim() === 'Fertig') { this._ui.qr = false; this._render(true); } else if (!this._sigBusy) this._loadSignal(true); }
    if (a === 'close') { if (el.classList.contains('sheet-bg') && ev.target.closest('.sheet')) return; this._ui.sheet = null; this._render(true); }
    if (a === 'hilfe-ja') { this._ui.sheet = null; this._call('script', 'werner_hilfe', {}); this._render(true); }
  }
}
if (!customElements.get('mein-zuhause-card')) customElements.define('mein-zuhause-card', MeinZuhauseCard);
window.customCards = window.customCards || [];
window.customCards.push({ type: 'mein-zuhause-card', name: 'Mein Zuhause', description: 'Werner: einfache Bildschirme für Senioren (Start, Werner, Energie, Auto, Einstellen)' });
console.info('mein-zuhause-card ' + MZ_VERSION);
