/*
 * „Mein Zuhause“ – Oberfläche von Werner (https://github.com/consulting-kleimanns/werner-home-assistant)
 * Einfache Bildschirme für Senioren: Start, Werner, Energie, Auto, Einstellen.
 * Optik nach dem Klickdummy. Lizenz: MIT.
 *
 * Wird von der Integration ausgeliefert:
 *  - als Bereich „Mein Zuhause“ in der Seitenleiste (/werner)
 *  - als Karte für Dashboards:  type: custom:werner-mein-zuhause
 *
 * Die Oberfläche zeigt immer den Bewohner, der angemeldet ist. Administratoren
 * können zwischen den Bewohnern umschalten. Alle Werte kommen aus den Entitäten
 * der Integration; was nicht eingerichtet ist, wird ausgeblendet oder zeigt „–“.
 */
const WERNER_UI_VERSION = '0.7.0';

const C = {
  bg: '#F5F2EA', ink: '#1E2421', muted: '#55605A', line: '#E2DDD1', blue: '#1F4E79', blueBg: '#E6EEF6', blueInk: '#12324F',
  green: '#2E6B4F', red: '#A3261D'
};

const CSS = `
:host{display:block;--wz-font:'Atkinson Hyperlegible',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif}
*{box-sizing:border-box}
button,input,select{font-family:inherit}
button{cursor:pointer;-webkit-tap-highlight-color:transparent}
button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid ${C.blue};outline-offset:2px}
.app{font-family:var(--wz-font);color:${C.ink};background:${C.bg};display:flex;flex-direction:column;position:relative;overflow:hidden;min-height:640px}
:host([panel]) .app{height:100vh;height:100dvh;min-height:0}
main{flex-grow:1;min-height:0;overflow-y:auto;padding:24px 18px 24px;display:flex;flex-direction:column;gap:14px}
.inner{width:100%;max-width:560px;margin:0 auto;display:flex;flex-direction:column;gap:14px}
h1{margin:0;font-size:28px;line-height:1.15}
h1.big{font-size:30px}
.date{font-size:17px;color:${C.muted}}
.muted{font-size:16px;color:${C.muted};line-height:1.4}
.small{font-size:15px;color:${C.muted};line-height:1.4}
.txt{font-size:16px;line-height:1.4}
.t-xl{font-size:22px;font-weight:700;line-height:1.25}.t-l{font-size:20px;font-weight:700}.t-m{font-size:18px;font-weight:700;line-height:1.25}
.card{background:#FFF;border:1px solid ${C.line};border-radius:18px;padding:16px;display:flex;flex-direction:column;gap:10px}
.box{border-radius:18px;padding:16px 18px;display:flex;flex-direction:column;gap:6px}
.ok{background:#E3F0E8;border:1px solid #BFD9C9;color:#1F4D38}
.warn{background:#FBEBD6;border:1px solid #E8C79B;color:#6E3B0B}
.err{background:#FBE3E0;border:1px solid #E9B3AD;color:#7A1C15}
.grey{background:#EFEBE2;border:1px solid #C9C3B5;color:#3E4541}
.info{background:${C.blueBg};border:1px solid #C3D3E6;color:${C.blueInk}}
.grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.tile{text-align:left;background:#FFF;border:1px solid ${C.line};border-radius:18px;padding:16px;display:flex;flex-direction:column;gap:6px;color:${C.ink};min-height:120px}
.tile .l{font-size:15px;color:${C.muted}}.tile .v{font-size:32px;font-weight:700}.tile .s{font-size:15px;color:${C.muted}}
.mini{background:#FFF;border:1px solid ${C.line};border-radius:16px;padding:14px;display:flex;flex-direction:column;gap:4px}
.mini .v{font-size:26px;font-weight:700}
.bar{display:block;height:10px;border-radius:5px;background:#E6E1D6;overflow:hidden}.bar>span{display:block;height:100%;background:${C.green}}
.pill{align-self:flex-start;min-height:48px;border-radius:24px;padding:0 18px;font-size:16px;font-weight:700}
.pill.red{border:none;background:${C.red};color:#FFF}
.btn{min-height:56px;border-radius:16px;font-size:17px;font-weight:700;border:1px solid #C9C3B5;background:#FFF;color:${C.ink};padding:0 14px}
.btn.blue{border:none;background:${C.blue};color:#FFF}
.btn.green{border:none;background:${C.green};color:#FFF}
.btn.red{border:none;background:${C.red};color:#FFF;min-height:60px;font-size:20px}
.btn.redline{border:2px solid ${C.red};background:#FFF;color:${C.red}}
.btn.dashed{border:2px dashed ${C.blue};color:${C.blue};background:#FFF}
.btn[disabled]{opacity:.55;cursor:default}
.days{display:flex;gap:10px;overflow-x:auto;padding-bottom:4px}
.day{flex-shrink:0;width:96px;min-height:120px;border-radius:16px;padding:10px;display:flex;flex-direction:column;align-items:flex-start;gap:2px;text-align:left;border:1px solid ${C.line};background:#FFF;color:${C.ink}}
.day.good{background:#FBF1D9;color:#5A3E05}.day.sel{border:3px solid ${C.blue}}
.log{display:flex;gap:12px;font-size:16px;align-items:baseline}.log b{width:52px;flex-shrink:0}
.sub{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:4px;background:#E9E4D8;border-radius:16px;padding:5px}
.sub button{min-height:48px;border-radius:12px;border:none;font-size:15px;padding:0 2px;background:transparent;color:#3E4541}
.sub button.on{background:#FFF;color:${C.blueInk};font-weight:700}
.nr{width:38px;height:38px;flex-shrink:0;border-radius:19px;background:${C.blue};color:#FFF;font-size:18px;font-weight:700;display:flex;align-items:center;justify-content:center}
.row{display:flex;align-items:center;gap:12px}.between{display:flex;align-items:center;justify-content:space-between;gap:10px}
.chips{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.ch{min-height:48px;border-radius:12px;border:1px solid ${C.line};background:#FFF;color:${C.muted};font-size:16px}
.ch.on{border:2px solid ${C.blue};background:${C.blueBg};color:${C.blueInk};font-weight:700}
.sw{width:64px;height:38px;flex-shrink:0;border-radius:19px;border:none;padding:4px;display:flex;background:#C9C3B5;justify-content:flex-start}
.sw.on{background:${C.green};justify-content:flex-end}.sw>span{display:block;width:30px;height:30px;border-radius:15px;background:#FFF}
.pm{width:52px;height:52px;border-radius:14px;border:1px solid ${C.line};background:#FFF;color:${C.ink};font-size:24px}
.val{flex-grow:1;text-align:center;font-size:20px;font-weight:700}
.badge{align-self:flex-start;font-size:14px;font-weight:700;border-radius:10px;padding:4px 10px}
.badge.ok,.badge.warn,.badge.grey{border:none}
.icon-btn{width:48px;height:48px;border-radius:12px;border:1px solid ${C.line};background:#FFF;color:${C.ink};font-size:20px}
.edit{min-height:52px;border-radius:12px;border:1px solid ${C.line};background:#FFF;color:${C.blue};font-size:16px;font-weight:700;padding:8px 12px}
.link{min-height:48px;padding:0 14px;border-radius:12px;border:1px solid ${C.line};background:#FFF;color:${C.red};font-size:15px}
label.f{display:flex;flex-direction:column;gap:4px;font-size:14px;color:${C.muted}}
label.f input,label.f select{min-height:48px;border:1px solid #C9C3B5;border-radius:12px;padding:0 12px;font-size:16px;color:${C.ink};background:#FBFAF7;width:100%}
.mode{text-align:left;min-height:84px;border-radius:18px;padding:14px 16px;display:flex;flex-direction:column;gap:4px;border:1px solid ${C.line};background:#FFF;color:${C.ink}}
.mode.on{border:3px solid ${C.blue};background:${C.blueBg};color:${C.blueInk}}
nav{flex-shrink:0;padding:8px 6px calc(14px + env(safe-area-inset-bottom));background:#FFF;border-top:1px solid ${C.line};display:grid;gap:4px}
nav button{min-height:62px;border:none;border-radius:14px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;padding:4px 0;background:transparent;color:${C.muted};font-size:13px;line-height:1.1}
nav button.on{background:${C.blueBg};color:${C.blueInk};font-weight:700}
nav .wrapnav{max-width:560px;width:100%;margin:0 auto;display:grid;gap:4px}
.top{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.menu{width:44px;height:44px;border-radius:12px;border:1px solid ${C.line};background:#FFF;color:${C.ink};display:flex;align-items:center;justify-content:center}
.who{min-height:40px;border-radius:20px;border:1px solid ${C.line};background:#FFF;color:${C.muted};font-size:14px;padding:0 14px}
.who.on{border:2px solid ${C.blue};color:${C.blueInk};font-weight:700}
.sheet-bg{position:absolute;inset:0;background:rgba(30,36,33,.6);display:flex;align-items:flex-end;z-index:20}
.sheet{width:100%;max-width:560px;margin:0 auto;max-height:92%;overflow-y:auto;background:#FFF;border-radius:26px 26px 0 0;padding:26px 18px calc(30px + env(safe-area-inset-bottom));display:flex;flex-direction:column;gap:12px}
.sheet ul{margin:0;padding-left:22px;font-size:17px;line-height:1.45;display:flex;flex-direction:column;gap:6px}
.empty{padding:40px 24px;text-align:center}
`;

const ICON = {
  start: '<path d="M3 11l9-7 9 7"></path><path d="M5 10v10h14V10"></path>',
  werner: '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"></path><path d="M9 12l2 2 4-4"></path>',
  energie: '<circle cx="12" cy="12" r="4"></circle><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"></path>',
  auto: '<path d="M5 16l1.5-5h11l1.5 5"></path><rect x="3" y="16" width="18" height="4" rx="1"></rect><path d="M7 20v1M17 20v1"></path>',
  einstellen: '<circle cx="9" cy="8" r="3"></circle><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"></path><circle cx="17" cy="9" r="2.5"></circle><path d="M16 14.2c2.8.4 5 2.8 5 5.8"></path>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"></path>'
};
const svg = (name, size = 26) => `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICON[name]}</svg>`;

const esc = (v) => String(v == null ? '' : v).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const BAD = ['unavailable', 'unknown', '', undefined, null];
const fmtW = (w) => { const n = Number(w); if (!isFinite(n)) return '–'; return Math.abs(n) >= 1000 ? (n / 1000).toLocaleString('de-DE', { maximumFractionDigits: 1 }) + ' kW' : Math.round(n) + ' W'; };
const fmtNum = (v, unit, digits = 0) => { const n = Number(v); if (!isFinite(n)) return '–'; return n.toLocaleString('de-DE', { maximumFractionDigits: digits }) + (unit ? ' ' + unit : ''); };
// Aktueller Wert einer Entität in einfachen Worten – damit man in der Auswahl erkennt, was was ist.
const MOTION = ['motion', 'occupancy', 'presence', 'moving', 'vibration'];
const OPENING = ['door', 'window', 'opening', 'garage_door'];
const MEDIA = { playing: 'spielt', paused: 'Pause', idle: 'bereit', on: 'an', off: 'aus', standby: 'aus', buffering: 'lädt' };
function fmtState(st) {
  if (!st || BAD.includes(st.state)) return 'nicht erreichbar';
  const a = st.attributes || {}; const dc = a.device_class; const unit = a.unit_of_measurement || '';
  const domain = st.entity_id.split('.')[0];
  if (domain === 'binary_sensor') {
    const on = st.state === 'on';
    if (MOTION.includes(dc)) return on ? 'Bewegung erkannt' : 'ruhig';
    if (OPENING.includes(dc)) return on ? 'offen' : 'zu';
    return on ? 'an' : 'aus';
  }
  if (domain === 'media_player') return MEDIA[st.state] || st.state;
  if (domain === 'weather') return (COND[st.state] || st.state) + (a.temperature != null ? ', ' + fmtNum(a.temperature, a.temperature_unit || '°C', 0) : '');
  const n = Number(st.state);
  if (dc === 'power' && isFinite(n)) return fmtW(unit === 'kW' ? n * 1000 : n);
  if (isFinite(n) && st.state !== '') return fmtNum(n, unit, Math.abs(n) < 10 ? 1 : 0);
  return st.state;
}
const hm = (d) => d.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
const COND = { sunny: 'Sonnig', 'clear-night': 'Klar', partlycloudy: 'Wolkig', cloudy: 'Bedeckt', fog: 'Nebel', rainy: 'Regen', pouring: 'Starkregen', snowy: 'Schnee', 'snowy-rainy': 'Schneeregen', lightning: 'Gewitter', 'lightning-rainy': 'Gewitter', windy: 'Windig', 'windy-variant': 'Windig', hail: 'Hagel', exceptional: 'Unwetter' };

// Grobe Sonnenstrom-Schätzung aus der Tagesvorhersage (ersetzt keine echte PV-Prognose).
function sunKwh(f, date, kwp) {
  const peakH = [1.6, 2.2, 3.2, 4.2, 5, 5.4, 5.4, 4.8, 3.8, 2.8, 1.8, 1.4][date.getMonth()];
  let cc = f.cloud_coverage;
  if (cc == null) cc = { sunny: 10, 'clear-night': 10, partlycloudy: 50, cloudy: 90, fog: 95 }[f.condition] ?? 85;
  if (/rain|pour|snow|lightning|hail/.test(f.condition || '')) cc = Math.max(cc, 92);
  const full = kwp * peakH * 0.85;
  const k = full * (1 - 0.8 * cc / 100);
  return { k, good: k >= full * 0.55 };
}

const STATUS = {
  ok: { cls: 'ok', pill: 'Werner: Alles in Ordnung', title: 'Alles in Ordnung' },
  asking: { cls: 'warn', pill: 'Werner fragt nach', title: 'Werner fragt nach' },
  informed: { cls: 'err', pill: 'Hilfe ist unterwegs', title: 'Vertrauensperson informiert' },
  help: { cls: 'err', pill: 'Hilfe ist unterwegs', title: 'Hilfe angefordert' },
  paused: { cls: 'grey', pill: 'Werner pausiert', title: 'Werner pausiert' }
};
const WAYS = [['ha_app', 'HA-App'], ['signal', 'Signal'], ['e_mail', 'E-Mail']];
const WAY_LABEL = { ha_app: 'HA-App', signal: 'Signal', e_mail: 'E-Mail', off: 'Nicht melden' };
const MODES = {
  minpv: ['Sonne nutzen, Plan einhalten', 'Lädt mit Sonnenstrom und nur so viel Netzstrom, dass Ihr Plan sicher klappt. Empfohlen.'],
  pv: ['Nur mit Sonne', 'Lädt ausschließlich mit Sonnenstrom. Kostet nichts, dauert lange.'],
  now: ['Sofort laden', 'Lädt gleich mit voller Leistung, auch mit Netzstrom.'],
  off: ['Pause', 'Das Auto wird nicht geladen.']
};

class WernerMeinZuhause extends HTMLElement {
  constructor() {
    super();
    this._ui = { tab: 'start', sub: 'wer', sheet: null, day: 0, adding: null };
    // Direktlink aus „Code auf anderem Gerät zeigen“: …/werner?signal=1
    try {
      if (new URLSearchParams(window.location.search).get('signal') === '1') { this._ui.tab = 'einstellen'; this._ui.sub = 'wer'; this._sgAuto = true; }
    } catch (e) { /* ohne Adresse (z. B. als Karte) egal */ }
    this._tests = {};
    this._sig = '';
    this._log = null;
  }

  /* ---------- Home Assistant ---------- */
  // Als Karte einstellbar:
  //   type: custom:werner-mein-zuhause
  //   screen: werner        # Start-Bildschirm: start, werner, energie, auto, einstellen
  //   resident: person.erika # nur für Helfer: diesen Bewohner zeigen
  //   hide_tabs: true        # Reiterleiste ausblenden (z. B. für ein Tablet an der Wand)
  setConfig(config) {
    this._config = config || {};
    if (['start', 'werner', 'energie', 'auto', 'einstellen'].includes(this._config.screen)) this._ui.tab = this._config.screen;
  }
  getCardSize() { return 12; }
  getGridOptions() { return { columns: 'full' }; }
  static getStubConfig() { return {}; }
  set panel(p) { this._panel = p; this.setAttribute('panel', ''); }
  set narrow(n) { this._narrow = n; }
  set hass(h) {
    this._h = h;
    if (!this.shadowRoot) {
      this.attachShadow({ mode: 'open' });
      this.shadowRoot.addEventListener('click', (ev) => this._click(ev));
      this.shadowRoot.addEventListener('change', (ev) => this._change(ev));
    }
    const hhSig = this._residents().map((x) => x.entity_id + x.attributes.consent).join('|');
    if (hhSig !== this._hhSig) { this._hhSig = hhSig; this._loadHousehold(); }
    const r = this._current();
    if (r) {
      this._subscribeForecast(r);
      if (!this._logT || Date.now() - this._logT > 60000 || this._logFor !== r.entity_id || this._logStatus !== r.state) this._loadLog(r);
    }
    this._render(false);
  }
  disconnectedCallback() { this._unsubForecast(); this._sgStopPoll(); }

  /* ---------- Bewohner und Entitäten ---------- */
  _residents() {
    const out = [];
    for (const [id, e] of Object.entries(this._h.entities || {})) {
      if (e.platform === 'werner' && e.translation_key === 'status' && this._h.states[id]) out.push(this._h.states[id]);
    }
    return out.sort((a, b) => String(a.attributes.resident || '').localeCompare(String(b.attributes.resident || '')));
  }
  _mine() {
    const uid = this._h.user && this._h.user.id;
    return this._residents().find((r) => { const p = this._h.states[r.attributes.person]; return p && p.attributes.user_id === uid; }) || null;
  }
  _current() {
    // Jeder sieht nur sich selbst. Ein Helfer (Administrator) kann umschalten.
    const mine = this._mine();
    if (!(this._h.user && this._h.user.is_admin)) return mine;
    const rs = this._residents();
    if (!this._who && this._config && this._config.resident) { const f = rs.find((r) => r.attributes.person === this._config.resident); if (f) return f; }
    if (this._who) { const f = rs.find((r) => r.entity_id === this._who); if (f) return f; }
    return mine || rs[0] || null;
  }
  async _loadHousehold() {
    try { this._hh = await this._h.callWS({ type: 'werner/household' }); } catch (err) { this._hh = { error: String(err.message || err) }; }
    this._render(true);
  }
  async _ws(msg) {
    this._busy = true; this._err = null; this._render(true);
    try { const res = await this._h.callWS(msg); this._busy = false; await this._loadHousehold(); return res || {}; }
    catch (err) { this._busy = false; this._err = err.message || String(err); this._render(true); return null; }
  }
  _id(key) { return (this._r && this._r.attributes.entities || {})[key]; }
  _st(key) { const id = this._id(key); const s = id && this._h.states[id]; return s ? s.state : undefined; }
  _num(key) { const v = parseFloat(this._st(key)); return isNaN(v) ? null : v; }
  _on(key) { return this._st(key) === 'on'; }
  _ent(id) { return id ? this._h.states[id] : undefined; }
  _entNum(id) { const s = this._ent(id); const v = s ? parseFloat(s.state) : NaN; return isNaN(v) ? null : v; }
  _energy() { return (this._r && this._r.attributes.energy) || {}; }
  _person(n) {
    const g = (k) => { const v = this._st(`person_${n}_${k}`); return BAD.includes(v) ? '' : String(v).trim(); };
    return { n, name: g('name'), way: this._st(`person_${n}_way`) || 'off', contact: g('contact'), phone: g('phone'), mail: g('e_mail') };
  }
  _people() { return [1, 2, 3].map((n) => this._person(n)); }
  _first() { const p = this._people().find((x) => x.name && x.way !== 'off'); return p ? p.name : null; }
  _hasCar() { const e = this._energy(); return !!(e.vehicle_soc || e.charge_mode); }

  _call(domain, service, data) { return this._h.callService(domain, service, data); }
  _press(key) { const id = this._id(key); if (id) this._call('button', 'press', { entity_id: id }); }

  /* ---------- Wetter ---------- */
  _weatherId() {
    const e = this._energy();
    if (e.weather && this._h.states[e.weather]) return e.weather;
    return Object.keys(this._h.states).find((id) => id.startsWith('weather.'));
  }
  _subscribeForecast() {
    const wid = this._weatherId();
    if (!wid || this._fcFor === wid) return;
    this._unsubForecast();
    this._fcFor = wid;
    this._fcUnsub = this._h.connection.subscribeMessage((m) => { this._fc = m.forecast; this._render(true); },
      { type: 'weather/subscribe_forecast', forecast_type: 'daily', entity_id: wid });
    this._fcUnsub.catch(() => { this._fcUnsub = null; });
  }
  _unsubForecast() { if (this._fcUnsub) { this._fcUnsub.then((u) => u && u()).catch(() => {}); this._fcUnsub = null; } this._fcFor = null; }
  _days() {
    const kwp = Number(this._energy().pv_kwp) || 0;
    const names = ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'];
    return (this._fc || []).slice(0, 5).map((f, i) => {
      const d = new Date(f.datetime);
      const sk = kwp ? sunKwh(f, d, kwp) : { k: null, good: /sunny|clear/.test(f.condition || '') };
      return { i, name: i === 0 ? 'Heute' : i === 1 ? 'Morgen' : names[d.getDay()], long: i === 0 ? 'Heute' : i === 1 ? 'Morgen' : d.toLocaleDateString('de-DE', { weekday: 'long' }),
        weather: COND[f.condition] || f.condition || '', kwh: sk.k, good: sk.good, t: f.temperature };
    });
  }
  _best(days) { const c = days.slice(0, 4); if (!c.length) return null; return c.reduce((a, b) => ((b.kwh ?? (b.good ? 1 : 0)) > (a.kwh ?? (a.good ? 1 : 0)) ? b : a)); }
  _tip(d, best) {
    const k = d.kwh != null ? ' Etwa ' + fmtNum(d.kwh, 'kWh', 1) + ' Sonnenstrom.' : '';
    if (d.good) return { cls: 'ok', title: d.long + ' ist ein Sonnentag', text: 'Zwischen 11 und 14 Uhr lohnt sich Waschen, Spülen und Auto laden.' + k };
    if (best && best.i !== d.i && best.good) return { cls: '', title: d.long + ': lohnt sich wenig', text: 'Wenig Sonne.' + k + ' Besser ' + (best.i === 1 ? 'morgen' : 'am ' + best.long) + ' mittags waschen und laden.' };
    return { cls: '', title: d.long + ': wenig Sonne', text: 'In den nächsten Tagen wird es nicht besser – waschen Sie, wann es Ihnen passt.' + k };
  }

  /* ---------- Protokoll ---------- */
  async _loadLog(r) {
    this._logT = Date.now(); this._logFor = r.entity_id; this._logStatus = r.state;
    try {
      const start = new Date(Date.now() - 24 * 3600 * 1000);
      const res = await this._h.callApi('GET', `logbook/${start.toISOString()}?entity=${encodeURIComponent(r.entity_id)}`);
      const prefix = (r.attributes.resident || '') + ': ';
      this._log = (res || []).filter((e) => e.message && !e.state).map((e) => {
        let text = String(e.message); if (text.startsWith(prefix)) text = text.slice(prefix.length);
        return { t: hm(new Date(e.when)), text };
      });
    } catch (err) { this._log = []; }
    this._render(true);
  }

  /* ---------- Darstellung ---------- */
  _render(force) {
    if (!this.shadowRoot) return;
    const active = this.shadowRoot.activeElement;
    if (!force && active && (active.tagName === 'INPUT' || active.tagName === 'SELECT')) return;
    const r = this._current();
    this._r = r;
    const ids = r ? Object.values(r.attributes.entities || {}) : [];
    const en = r ? Object.values(this._energy()).filter((v) => typeof v === 'string' && v.includes('.')) : [];
    // In der Geräte-Auswahl die Werte von gerade eben mitlaufen lassen (alle 10 Sekunden).
    const tick = this._ui.tab === 'einstellen' && this._ui.sub === 'sensoren' ? Math.floor(Date.now() / 10000) : '';
    const sig = (r ? r.state + JSON.stringify(r.attributes) : '') + ids.concat(en).map((i) => this._h.states[i] && this._h.states[i].state).join('|')
      + (r && this._h.states[r.attributes.person] ? this._h.states[r.attributes.person].state : '')
      + JSON.stringify(this._ui) + JSON.stringify(this._tests) + JSON.stringify(this._hh || null) + JSON.stringify(this._src || null) + JSON.stringify(this._en || null) + JSON.stringify(this._sg || null) + JSON.stringify(this._mail || null) + (this._busy ? 'B' : '') + (this._err || '') + (this._log ? this._log.length : -1) + (this._fc ? this._fc.length : 0) + (this._who || '') + tick;
    if (!force && sig === this._sig) return;
    this._sig = sig;

    let body;
    let tabs = [];
    if (!r) {
      body = this._onboarding();
    } else if (r.attributes.consent === false) {
      body = this._consentScreen();
    } else {
      tabs = [['einstellen', 'Einstellen']].concat(this._hasCar() ? [['auto', 'Auto']] : []).concat([['energie', 'Energie'], ['werner', 'Werner'], ['start', 'Start']]);
      if (!tabs.find((t) => t[0] === this._ui.tab)) this._ui.tab = 'start';
      const fn = { start: this._start, werner: this._werner, energie: this._energie, auto: this._auto, einstellen: this._einstellen }[this._ui.tab];
      body = fn.call(this);
    }
    const top = this._topBar();
    const nav = tabs.length && !(this._config && this._config.hide_tabs) ? `<nav aria-label="Reiter"><div class="wrapnav" style="grid-template-columns:repeat(${tabs.length},minmax(0,1fr))">${tabs.map((t) => `<button type="button" data-tab="${t[0]}" class="${this._ui.tab === t[0] ? 'on' : ''}" ${this._ui.tab === t[0] ? 'aria-current="page"' : ''}>${svg(t[0])}<span>${t[1]}</span></button>`).join('')}</div></nav>` : '';
    let sheet = '';
    if (this._ui.sheet === 'remove_me') sheet = this._sheetRemoveMe();
    else if (r && r.attributes.consent !== false) {
      if (r.state === 'asking' && this._ui.sheet !== 'hilfe' && this._ui.checkClosed !== r.last_changed) sheet = this._sheetCheck();
      else if (this._ui.sheet === 'hilfe') sheet = this._sheetHilfe();
      else if (this._ui.sheet === 'info') sheet = this._sheetInfo();
      else if (this._ui.sheet === 'data') sheet = this._sheetData();
      else if (this._ui.sheet === 'energy') sheet = this._sheetEnergy();
      else if (this._ui.sheet && this._ui.sheet.startsWith('consent_')) sheet = this._sheetConsent(this._ui.sheet);
    }
    const scroll = this.shadowRoot.querySelector('main');
    const pos = scroll ? scroll.scrollTop : 0;
    this.shadowRoot.innerHTML = `<style>${CSS}</style><div class="app"><main><div class="inner">${top}${body}</div></main>${nav}${sheet}</div>`;
    const m = this.shadowRoot.querySelector('main'); if (m && this._keepScroll) m.scrollTop = pos;
    this._keepScroll = true;
  }

  _topBar() {
    const rs = this._h ? this._residents() : [];
    const menu = this.hasAttribute('panel') && this._narrow ? `<button type="button" class="menu" data-act="menu" aria-label="Seitenleiste öffnen">${svg('menu', 22)}</button>` : '';
    const who = this._h.user && this._h.user.is_admin && rs.length > 1
      ? rs.map((r) => `<button type="button" class="who ${this._r && this._r.entity_id === r.entity_id ? 'on' : ''}" data-who="${esc(r.entity_id)}">${esc(r.attributes.resident)}</button>`).join('') : '';
    return menu || who ? `<div class="top">${menu}${who ? `<span class="small">Ansicht für:</span>${who}` : ''}</div>` : '';
  }

  _wv() {
    const r = this._r; const s = STATUS[r.state] || STATUS.ok; const first = this._first();
    const wait = this._num('wait_minutes') || 10;
    let text = '';
    if (r.state === 'ok') {
      const la = this._ent(this._id('last_activity'));
      let seit = '';
      if (la && !BAD.includes(la.state)) { const d = new Date(la.state); seit = ' Zuletzt bemerkt: ' + hm(d) + ' Uhr' + (d.toDateString() === new Date().toDateString() ? '' : ', ' + d.toLocaleDateString('de-DE', { day: 'numeric', month: 'numeric' })) + '.'; }
      text = 'Ihr Tag verläuft wie gewohnt.' + seit;
    } else if (r.state === 'asking') text = (r.attributes.reason || '') + ' Bitte bestätigen Sie kurz, dass alles in Ordnung ist. Ohne Antwort informiert Werner in ' + Math.round(wait) + ' Minuten ' + (first || 'Ihre Vertrauensperson') + '.';
    else if (r.state === 'informed') text = first ? 'Werner hat ' + first + ' benachrichtigt. Antwortet niemand, geht es in Ihrer Reihenfolge weiter.' : 'Sie haben niemanden eingetragen. Im Notfall rufen Sie bitte 112 an.';
    else if (r.state === 'help') text = first ? 'Werner informiert ' + first + ' und dann die nächsten Personen.' : 'Sie haben niemanden eingetragen. Rufen Sie bitte 112 an.';
    else text = 'Zum Beispiel wegen Besuch oder Urlaub. Werner meldet nichts, bis Sie ihn wieder einschalten.';
    return Object.assign({}, s, { text });
  }

  /* ---------- Start ---------- */
  /* ---------- Einrichtung: was noch fehlt ---------- */
  _setup() {
    const r = this._r; const people = this._people().filter((p) => p.name && p.way !== 'off');
    const items = [
      { ok: !!r.attributes.notify, sub: 'bewohner', done: 'Ihr Handy ist verbunden', todo: 'Ihr Handy wählen – dort fragt Werner zuerst nach' },
      { ok: people.length > 0, sub: 'wer', done: 'Vertrauensperson eingetragen', todo: 'Eine Vertrauensperson eintragen' },
      { ok: (r.attributes.sources || []).length > 0, sub: 'sensoren', done: 'Werner weiß, woran er Aktivität erkennt', todo: 'Wählen, woran Werner merkt, dass Sie aktiv sind' }
    ];
    if (people.some((p) => p.way === 'signal')) {
      if (!this._sg && !this._sgQuietT) { this._sgQuietT = Date.now(); this._h.callWS({ type: 'werner/signal/status' }).then((st) => { if (!this._sg) { this._sg = st; this._render(true); } }).catch(() => {}); }
      items.push({ ok: !!(this._sg && this._sg.connected), sub: 'wer', done: 'Signal ist verbunden', todo: 'Signal mit Werner verbinden' });
    }
    if (people.some((p) => p.way === 'e_mail')) {
      if (!this._mail && !this._mailQuietT) { this._mailQuietT = Date.now(); this._loadMail(); }
      items.push({ ok: !!(this._mail && this._mail.configured), sub: 'wer', done: 'E-Mail-Versand ist eingerichtet', todo: 'E-Mail-Versand einrichten (macht ein Helfer)' });
    }
    return { items, open: items.filter((i) => !i.ok).length };
  }
  _setupCard(compact) {
    const st = this._setup();
    if (!st.open) return '';
    if (compact) return `<section class="box warn" aria-label="Einrichtung"><div class="t-m">Noch ${st.open === 1 ? 'ein Schritt' : st.open + ' Schritte'}, dann passt Werner richtig auf</div><button type="button" class="btn" data-goto="${st.items.find((i) => !i.ok).sub}">Jetzt einrichten</button></section>`;
    return `<section class="card" aria-label="Einrichtung"><div class="t-m">So weit ist Werner eingerichtet</div>${st.items.map((i) => i.ok
      ? `<div class="row" style="gap:10px"><span aria-hidden="true" style="color:${C.green};font-size:22px;font-weight:700;width:28px">✓</span><span class="txt">${esc(i.done)}</span></div>`
      : `<button type="button" class="edit" style="display:flex;gap:10px;align-items:center;text-align:left" data-goto="${i.sub}"><span aria-hidden="true" style="font-size:22px;width:28px">○</span><span>${esc(i.todo)} ›</span></button>`).join('')}</section>`;
  }

  _start() {
    const now = new Date(); const h = now.getHours();
    const gruss = h < 11 ? 'Guten Morgen' : h < 18 ? 'Guten Tag' : 'Guten Abend';
    const w = this._wv();
    const days = this._days(); const best = this._best(days);
    let emp = '';
    if (best) {
      const t = best.good ? (best.i === 0 ? 'Heute mittags waschen' : 'Waschen lieber ' + (best.i === 1 ? 'morgen' : 'am ' + best.long) + ' ab 11 Uhr') : 'Diese Woche wenig Sonne';
      emp = `<section class="box ${best.good ? 'ok' : 'grey'}" aria-label="Empfehlung"><div class="t-xl" style="font-size:21px">${esc(t)}</div><div class="txt" style="font-size:17px">${esc(this._tip(best, best).text)}</div></section>`;
    }
    const e = this._energy(); const tiles = [];
    if (e.pv_power) tiles.push(`<button type="button" class="tile" data-tab="energie"><span class="l">Sonne liefert</span><span class="v">${fmtW(this._entNum(e.pv_power))}</span><span class="s">gerade</span></button>`);
    if (e.battery_soc) { const v = this._entNum(e.battery_soc); tiles.push(`<button type="button" class="tile" data-tab="energie"><span class="l">Batterie</span><span class="v">${fmtNum(v, '%')}</span><span class="bar"><span style="width:${v == null ? 0 : Math.max(0, Math.min(100, v))}%"></span></span></button>`); }
    if (e.grid_power) { const v = this._entNum(e.grid_power); tiles.push(`<button type="button" class="tile" data-tab="energie"><span class="l">${v != null && v < 0 ? 'Ins Netz' : 'Aus dem Netz'}</span><span class="v">${fmtW(v == null ? NaN : Math.abs(v))}</span><span class="s">am Zähler</span></button>`); }
    if (this._hasCar()) { const v = e.vehicle_soc ? this._entNum(e.vehicle_soc) : null; tiles.push(`<button type="button" class="tile" data-tab="auto"><span class="l">${esc(e.vehicle_name || 'Auto')}</span><span class="v">${v == null ? 'Laden' : fmtNum(v, '%')}</span><span class="s" style="color:${C.blue};font-weight:700">Ändern ›</span></button>`); }
    return `<header style="display:flex;flex-direction:column;gap:10px"><div class="date">${esc(now.toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long' }))}</div>
<h1 class="big">${gruss}, ${esc(this._r.attributes.resident)}</h1><button type="button" class="pill ${w.cls === 'err' ? 'red' : w.cls}" data-tab="werner">${esc(w.pill)}</button></header>${emp}
${this._setupCard(true)}${tiles.length ? `<div class="grid2">${tiles.join('')}</div>` : ''}`;
  }

  /* ---------- Werner ---------- */
  _sensorNote() {
    const parts = ['Ihr Handy'];
    if ((this._r.attributes.sources || []).length) parts.unshift('den Stromverbrauch und Geräte im Haus');
    const cam = this._on('consent_camera'); const mic = this._on('consent_microphone');
    return 'Werner achtet auf ' + parts.join(' und ') + '. ' + (cam || mic ? 'Kamera und Mikrofon nur mit Ihrer Zustimmung – Werner speichert keine Bilder und keine Töne.' : 'Keine Kamera, kein Mikrofon.');
  }
  _werner() {
    const w = this._wv(); const r = this._r; const paused = this._on('paused');
    const log = (this._log || []).slice(0, 10);
    const alarm = ['informed', 'help', 'asking'].includes(r.state);
    return `<h1>Werner passt auf</h1>
<section class="box ${w.cls}" aria-label="Status"><div class="t-xl">${esc(w.title)}</div><div class="txt">${esc(w.text)}</div></section>
${alarm ? `<button type="button" class="btn green" data-act="ok">Alles gut – Entwarnung</button>` : ''}
<section class="card" aria-label="Heute bemerkt"><div class="t-m">Heute bemerkt</div>
${this._log === null ? '<div class="muted">Wird geladen …</div>' : log.length ? log.map((e) => `<div class="log"><b>${esc(e.t)}</b><span>${esc(e.text)}</span></div>`).join('') : '<div class="muted">In den letzten 24 Stunden nichts Besonderes.</div>'}
<div class="small">Nur Sie sehen Ihr Protokoll.</div></section>
<div class="small">${esc(this._sensorNote())}</div>
<div style="display:flex;flex-direction:column;gap:10px">
<button type="button" class="btn ${paused ? 'blue' : ''}" data-act="pause">${paused ? 'Werner wieder einschalten' : 'Werner pausieren (Besuch, Urlaub)'}</button>
<button type="button" class="btn red" data-act="hilfe">Ich brauche Hilfe</button></div>`;
  }

  /* ---------- Energie ---------- */
  _energie() {
    const e = this._energy(); const days = this._days(); const best = this._best(days);
    const sel = days[this._ui.day] || days[0]; const tip = sel ? this._tip(sel, best) : null;
    const minis = [];
    if (e.grid_power) minis.push(`<div class="mini"><span class="small">Gerade aus dem Netz</span><span class="v">${fmtW(this._entNum(e.grid_power))}</span></div>`);
    if (e.grid_energy) minis.push(`<div class="mini"><span class="small">Zählerstand</span><span class="v">${fmtNum(this._entNum(e.grid_energy), 'kWh')}</span></div>`);
    if (e.pv_power) minis.push(`<div class="mini"><span class="small">Sonne gerade</span><span class="v">${fmtW(this._entNum(e.pv_power))}</span></div>`);
    if (e.battery_soc) minis.push(`<div class="mini"><span class="small">Batterie</span><span class="v">${fmtNum(this._entNum(e.battery_soc), '%')}</span></div>`);
    const kwp = Number(e.pv_kwp) || 0;
    const bestTime = best ? (best.good ? (best.i === 0 ? 'heute' : best.i === 1 ? 'morgen' : best.long) + ' 11–14 Uhr' : 'diese Woche egal') : '–';
    const devices = [['Waschmaschine', 'ca. 1 kWh je Wäsche'], ['Spülmaschine', 'ca. 1 kWh']];
    if (this._hasCar()) devices.unshift([e.vehicle_name || 'Auto', 'lädt nach Ihrem Lademodus', true]);
    return `<h1>Energie heute</h1>${kwp ? `<div class="muted">Solaranlage mit ${fmtNum(kwp, 'kWp', 1)}.</div>` : ''}
${minis.length ? `<div class="grid2">${minis.join('')}</div>` : `<div class="box grey"><div class="txt">Hier können Sie Stromzähler, Solaranlage, Batterie und Auto anzeigen lassen.</div></div>`}
<section aria-label="Die nächsten Tage" style="display:flex;flex-direction:column;gap:10px"><div class="t-l">Die nächsten Tage</div>
${days.length ? `<div class="days">${days.map((d) => `<button type="button" class="day ${d.good ? 'good' : ''} ${sel && d.i === sel.i ? 'sel' : ''}" data-day="${d.i}" aria-pressed="${sel && d.i === sel.i}"><span style="font-size:16px;font-weight:700">${esc(d.name)}</span><span style="font-size:14px">${esc(d.weather)}</span><span style="font-size:20px;font-weight:700">${d.kwh != null ? fmtNum(d.kwh, 'kWh', 1) : (d.t != null ? fmtNum(d.t, '°C') : '')}</span>${d.kwh != null ? '<span style="font-size:13px">Sonnenstrom</span>' : ''}</button>`).join('')}</div>` : '<div class="muted">Keine Wettervorhersage gefunden.</div>'}
${tip ? `<div class="box ${tip.cls || 'grey'}" style="border-radius:16px;padding:14px 16px"><div class="t-m">${esc(tip.title)}</div><div class="txt">${esc(tip.text)}</div></div>` : ''}</section>
<section aria-label="Meine Geräte" style="display:flex;flex-direction:column;gap:10px"><div class="t-l">Meine Geräte</div>
${devices.map((g) => `<div class="card" style="padding:14px;gap:6px"><div class="between" style="align-items:baseline"><span class="t-m">${esc(g[0])}</span><span class="small">${esc(g[1])}</span></div><div class="txt"><b>Beste Zeit:</b> ${esc(bestTime)}</div><span class="badge ${g[2] ? 'info' : 'grey'}">${g[2] ? 'Steuert evcc automatisch' : 'Tipp – Sie schalten selbst ein'}</span></div>`).join('')}
</section><div class="small">Sonnenstrom ist eine grobe Schätzung aus der Wettervorhersage.</div>
<button type="button" class="btn" style="min-height:52px;color:${C.blue}" data-act="energy">Was hier angezeigt wird – ändern</button>`;
  }

  /* ---------- Auto ---------- */
  _auto() {
    const e = this._energy(); const name = e.vehicle_name || 'Auto';
    const soc = e.vehicle_soc ? this._entNum(e.vehicle_soc) : null;
    const modeEnt = e.charge_mode ? this._ent(e.charge_mode) : null;
    const opts = modeEnt ? (modeEnt.attributes.options || []) : [];
    const order = ['minpv', 'pv', 'now', 'off'];
    const sorted = opts.slice().sort((a, b) => (order.indexOf(a) + 1 || 9) - (order.indexOf(b) + 1 || 9));
    return `<h1>${esc(name)} laden</h1>
${e.vehicle_soc ? `<div class="card"><div style="display:flex;flex-direction:column;gap:2px"><span class="small">Akku</span><span style="font-size:30px;font-weight:700">${fmtNum(soc, '%')}</span></div>
<span class="bar" style="height:12px"><span style="width:${soc == null ? 0 : Math.max(0, Math.min(100, soc))}%;background:${C.blue}"></span></span></div>` : ''}
${modeEnt ? `<div class="muted">So lädt die Wallbox:</div><div role="radiogroup" aria-label="Lademodus" style="display:flex;flex-direction:column;gap:10px">
${sorted.map((o) => { const m = MODES[o] || [o, '']; const on = modeEnt.state === o; return `<button type="button" role="radio" aria-checked="${on}" class="mode ${on ? 'on' : ''}" data-mode="${esc(o)}"><span class="t-l">${esc(m[0])}</span>${m[1] ? `<span style="font-size:15px;line-height:1.35">${esc(m[1])}</span>` : ''}</button>`; }).join('')}</div>
<div class="small">evcc plant das Laden mit der Sonnen-Vorhersage. Fehlt Sonne, lädt evcc rechtzeitig mit Netzstrom nach.</div>` : ''}`;
  }

  /* ---------- Einstellen ---------- */
  _einstellen() {
    const sub = this._ui.sub; const multi = this._residents().length > 1;
    const tabs = [['wer', 'Wer & wie'], ['wann', 'Wann'], ['sensoren', 'Sensoren'], ['bewohner', 'Bewohner']].map((t) => `<button type="button" role="tab" aria-selected="${sub === t[0]}" class="${sub === t[0] ? 'on' : ''}" data-sub="${t[0]}">${t[1]}</button>`).join('');
    if (sub === 'sensoren' && (!this._src || this._srcFor !== this._r.attributes.entry_id)) this._loadSources();
    const body = sub === 'wann' ? this._wann() : sub === 'sensoren' ? this._sensoren() : sub === 'bewohner' ? this._bewohner() : this._wer();
    return `<h1>Werner einstellen</h1><div class="muted">${multi ? 'Das sind Ihre Einstellungen, ' + esc(this._r.attributes.resident) + '. Nur Sie sehen und ändern sie.' : 'Sie bestimmen, wer wie und wann informiert wird.'}</div>
<button type="button" class="btn" style="min-height:52px;color:${C.blue}" data-act="info">So funktioniert Werner</button>
${this._setupCard(false)}<div class="sub" role="tablist" aria-label="Bereiche">${tabs}</div>${body}`;
  }

  /* Beispiel-Nachricht an eine Vertrauensperson – derselbe Aufbau wie in bewohner.py (_message). */
  _beispiel(p, active) {
    const r = this._r; const name = (r && r.attributes.resident) || 'Ihr Name';
    const until = Math.round(Number(this._num('morning_until')) || 10);
    const wait = Math.round(Number(this._num('wait_minutes')) || 10);
    const nxt = active[1] ? active[1].name : '';
    const lines = [
      'Werner: ' + name + ' meldet sich nicht', '',
      'Was ist los?',
      'Es ist schon ' + until + ':15 Uhr und Werner hat bei ' + name + ' heute noch keine Aktivität bemerkt. Werner hat ' + name + ' deshalb auf dem Handy gefragt, ob alles in Ordnung ist. ' + wait + ' Minuten lang kam keine Antwort.', '',
      'Warum bekommen Sie diese Nachricht?',
      name + ' hat Sie bei Werner als Vertrauensperson eingetragen' + (active.length > 1 ? ' – Sie sind Nr. 1 von ' + active.length + '.' : '.'), '',
      'Bitte rufen Sie ' + name + ' an oder schauen Sie vorbei.', '',
      (p.way === 'e_mail' ? 'Ein Klick genügt:' : p.way === 'signal' ? 'Bitte antworten Sie hier mit einer Zahl:' : 'Antwort mit den Knöpfen:'),
      '1 = Ich kümmere mich. Werner benachrichtigt dann niemanden sonst.',
      '2 = Fehlalarm, alles in Ordnung. Werner beendet den Alarm.',
      '3 = Ich kann gerade nicht. ' + (nxt ? 'Werner fragt dann ' + nxt + '.' : 'Werner rät ' + name + ' dann, selbst 112 anzurufen.'), '',
      'Im Notfall: 112.'
    ];
    return `<details class="card" style="padding:14px"><summary style="font-size:17px;font-weight:700;cursor:pointer;min-height:44px;display:flex;align-items:center">So sieht eine Nachricht an ${esc(p.name)} aus</summary>
<div class="small" style="margin:6px 0 8px">Beispiel: Sie haben sich morgens nicht gerührt und auf Werners Frage nicht geantwortet.</div>
<div style="white-space:pre-wrap;font-size:16px;line-height:1.45;background:#F6F3EC;border-radius:12px;padding:12px">${esc(lines.join('\n'))}</div></details>`;
  }

  _wer() {
    const people = this._people();
    const filled = people.filter((p) => p.name || this._ui.adding === p.n);
    const notify = Object.keys((this._h.services || {}).notify || {}).filter((s) => s.startsWith('mobile_app_')).sort();
    const cards = filled.map((p, i) => {
      const editingName = !p.name;
      const active = WAYS.filter((w) => p.way === w[0]).map((w) => w[1]);
      const summary = p.way === 'off' ? 'Wird nicht benachrichtigt' : active.join(' · ');
      const t = this._tests[p.n];
      let fields = '';
      if (editingName) fields += `<label class="f">Name der Person<input type="text" data-text="person_${p.n}_name" placeholder="z. B. Sabine (Tochter)" autocomplete="off"></label>`;
      if (p.way === 'ha_app') fields += `<label class="f">Handy mit der Home-Assistant-App<select data-text="person_${p.n}_contact"><option value="">– bitte wählen –</option>${notify.map((s) => `<option value="${esc(s)}" ${p.contact === s ? 'selected' : ''}>${esc(s.replace('mobile_app_', '').replace(/_/g, ' '))}</option>`).join('')}${p.contact && !notify.includes(p.contact) ? `<option value="${esc(p.contact)}" selected>${esc(p.contact)} (nicht gefunden)</option>` : ''}</select></label>`;
      if (p.way === 'signal') fields += `<label class="f">Handynummer für Signal<input type="tel" data-text="person_${p.n}_phone" value="${esc(p.phone)}" placeholder="+49 170 0000000"></label><div class="small">Bei einem Alarm schreibt Werner dieser Person eine Signal-Nachricht: was los ist und was sie tun kann. Sie antwortet mit einer Zahl – <b>1</b> ich kümmere mich, <b>2</b> Fehlalarm, <b>3</b> ich kann gerade nicht.</div>`;
      if (p.way === 'e_mail') fields += `<label class="f">E-Mail-Adresse<input type="email" data-text="person_${p.n}_e_mail" value="${esc(p.mail)}" placeholder="name@example.org"></label><div class="small">Bei einem Alarm schreibt Werner dieser Person eine E-Mail: was los ist und was sie tun kann. Sie antwortet mit einem Klick – ich kümmere mich, Fehlalarm oder ich kann gerade nicht. Sie braucht dafür nichts zu installieren.</div>`;
      return `<div class="card" style="padding:14px"><div class="row"><span class="nr">${i + 1}</span><span style="display:flex;flex-direction:column;gap:2px;min-width:0"><span style="font-size:19px;font-weight:700">${esc(p.name || 'Neue Person')}</span><span class="small">${esc(summary || 'Noch kein Weg gewählt')}</span></span></div>
<div class="small">So erreicht Werner diese Person:</div>
<div class="chips">${WAYS.map((w) => `<button type="button" class="ch ${p.way === w[0] ? 'on' : ''}" aria-pressed="${p.way === w[0]}" data-way="${p.n}|${w[0]}">${p.way === w[0] ? '✓ ' : ''}${w[1]}</button>`).join('')}<button type="button" class="ch ${p.way === 'off' ? 'on' : ''}" aria-pressed="${p.way === 'off'}" data-way="${p.n}|off">Nicht melden</button></div>
${fields}
${p.name ? `<button type="button" class="btn" style="min-height:52px;font-size:16px" data-test="${p.n}" ${t === 'busy' ? 'disabled' : ''}>${t === 'busy' ? 'Test läuft …' : 'Test-Nachricht senden'}</button>` : ''}
${t && t !== 'busy' ? `<div class="box ${t.ok ? 'ok' : 'err'}" style="padding:10px 12px"><div class="txt">${esc(t.text)}</div></div>` : ''}
<div style="display:flex;gap:8px;justify-content:flex-end"><button type="button" class="link" data-remove="${p.n}">Entfernen</button>
<button type="button" class="icon-btn" aria-label="Weiter nach oben" data-move="${p.n}|-1" ${i === 0 ? 'disabled' : ''}>↑</button>
<button type="button" class="icon-btn" aria-label="Weiter nach unten" data-move="${p.n}|1" ${i === filled.length - 1 ? 'disabled' : ''}>↓</button></div></div>`;
    }).join('');
    const free = people.find((p) => !p.name && this._ui.adding !== p.n);
    const sig = (people.some((p) => p.name && p.way === 'signal') || this._sgAuto || (this._sg && (this._sg.image || this._ui.sgOther))) ? this._signalCard() : '';
    const mailCard = people.some((p) => p.name && p.way === 'e_mail') ? this._mailCard() : '';
    return `${sig}${mailCard}<div class="txt">Zuerst fragt Werner <b>immer Sie selbst</b> – auf Ihrem Handy. Antworten Sie nicht, informiert er nacheinander:</div>
${cards}
${filled.some((p) => p.name && p.way !== 'off') ? this._beispiel(filled.find((p) => p.name && p.way !== 'off'), filled.filter((p) => p.name && p.way !== 'off')) : ''}
${!filled.length ? `<div class="box warn"><div class="txt">Niemand eingetragen: Werner fragt nur Sie selbst und informiert sonst niemanden.</div></div>` : ''}
${free && this._ui.adding == null ? `<button type="button" class="btn dashed" data-act="add">+ Person hinzufügen</button>` : ''}
<div class="small">Die Personen brauchen keine zusätzliche App. Sie bekommen nur die Meldung und die Uhrzeit – keine Bilder, keine Töne, nicht Ihren Tagesablauf.</div>
<div class="small">Warum nicht WhatsApp oder Threema? Werner nutzt nur Wege, die nichts kosten. Bei WhatsApp und Threema kostet jede automatische Nachricht Geld.</div>`;
  }

  _wann() {
    const rules = [
      { sw: 'rule_morning', num: 'morning_until', title: 'Morgens nichts los', text: 'Werner fragt nach, wenn bis zu dieser Uhrzeit noch nichts von Ihnen zu bemerken ist.', fmt: (v) => 'bis ' + v + ':00 Uhr' },
      { sw: 'rule_quiet', num: 'quiet_hours', title: 'Tagsüber lange still', text: 'Werner fragt nach, wenn Sie zu Hause sind und so lange nichts von Ihnen kommt.', fmt: (v) => v + ' Stunden' },
      { sw: 'rule_night', title: 'Nachts ungewöhnlich aktiv', text: 'Werner fragt nach, wenn zwischen 0 und 5 Uhr ungewöhnlich viel passiert.', fmt: () => 'sofort' },
      { num: 'wait_minutes', title: 'Wartezeit auf Ihre Antwort', text: 'So lange wartet Werner auf Ihr „Alles gut“, bevor er die erste Person informiert.', fmt: (v) => v + ' Minuten' }
    ];
    return rules.map((d) => {
      const on = d.sw ? this._on(d.sw) : true; const v = d.num ? this._num(d.num) : null;
      return `<div class="card" style="padding:14px 16px"><div class="between"><span class="t-m">${esc(d.title)}</span>${d.sw ? `<button type="button" class="sw ${on ? 'on' : ''}" role="switch" aria-checked="${on}" aria-label="${esc(d.title)}" data-toggle="${d.sw}"><span></span></button>` : ''}</div>
<div class="txt">${esc(d.text)}</div>${d.num ? `<div class="row" style="gap:10px"><button type="button" class="pm" aria-label="Weniger" data-step="${d.num}|-1" ${on ? '' : 'disabled'}>–</button><span class="val">${on ? esc(d.fmt(v == null ? '–' : Math.round(v))) : 'aus'}</span><button type="button" class="pm" aria-label="Mehr" data-step="${d.num}|1" ${on ? '' : 'disabled'}>+</button></div>` : `<div class="val">${on ? d.fmt() : 'aus'}</div>`}</div>`;
    }).join('') + `<div class="small">Ist Ihr Handy unterwegs oder Werner pausiert, gelten diese Regeln nicht.${(this._r.attributes.sources || []).length ? '' : ' Die Regeln arbeiten erst, wenn Sie unter „Sensoren“ mindestens ein Gerät gewählt haben.'}</div>`;
  }

  _sensoren() {
    const r = this._r;
    const p = this._h.states[r.attributes.person];
    const home = p ? p.state === 'home' : false;
    const card = (title, text, badge, ok, toggle) => `<div class="card" style="padding:14px 16px;gap:6px"><div class="between"><span class="t-m">${esc(title)}</span>${toggle || ''}</div><div style="font-size:15px;line-height:1.4;color:#3E4541">${esc(text)}</div><span class="badge ${ok === true ? 'ok' : ok === false ? 'warn' : 'grey'}">${esc(badge)}</span></div>`;
    let html = `<div class="txt">Woran Werner Ihren Tag erkennt.</div>`;
    html += card('Ihr Handy: zu Hause oder unterwegs', 'Sind Sie unterwegs, schweigt Werner.', p ? (home ? 'Gerade: zu Hause' : 'Gerade: unterwegs') : 'Nicht verbunden', p ? true : false);
    html += this._sourcesBlock();
    for (const [key, title, text] of [['consent_camera', 'Kamera', 'Erkennt nur, wer unterwegs ist: Sie, Besuch oder ein Tier. Werner speichert keine Bilder.'], ['consent_microphone', 'Mikrofon', 'Erkennt nur Geräusche wie einen Sturz oder einen Hilferuf. Werner speichert keine Töne.']]) {
      const on = this._on(key);
      html += card(title, text, on ? 'An – mit Ihrer Zustimmung' : 'Aus – nur mit Ihrer Zustimmung', on ? true : null,
        `<button type="button" class="sw ${on ? 'on' : ''}" role="switch" aria-checked="${on}" aria-label="${title}" data-consent="${key}"><span></span></button>`);
    }
    html += `<div class="card" style="padding:14px 16px;gap:8px"><span class="t-m">Ihre Daten gehören Ihnen</span><div style="font-size:15px;line-height:1.4;color:#3E4541">Alles bleibt in Ihrem Haus. Sie sehen jederzeit, was Werner über Sie weiß.</div><button type="button" class="btn" style="min-height:52px;color:${C.blue}" data-act="data">Ansehen</button></div>`;
    return html + `<div class="small">${esc(this._sensorNote())}</div>`;
  }

  /* ---------- Bewohner (Selbstbestimmung) ---------- */
  _phoneSelect(field, current, label, auto) {
    const phones = (this._hh && this._hh.phones) || [];
    return `<label class="f">${label || 'Mein Handy (dort fragt Werner nach)'}<select data-f="${field}">${auto ? '<option value="__auto" selected>Automatisch: das Handy der Person</option>' : ''}<option value="">– kein Handy –</option>${phones.map((s) => `<option value="${esc(s)}" ${current === s ? 'selected' : ''}>${esc(s.replace('mobile_app_', '').replace(/_/g, ' '))}</option>`).join('')}</select></label>`;
  }
  async _loadSources() {
    const id = this._r.attributes.entry_id; this._srcFor = id; this._src = this._src || null;
    try { this._src = await this._h.callWS({ type: 'werner/sources', entry_id: id }); } catch (err) { this._src = { error: err.message || String(err) }; }
    this._render(true);
  }
  async _saveSources(chosen, baseload) {
    const msg = { type: 'werner/resident/sources', entry_id: this._r.attributes.entry_id, sources: chosen };
    if (baseload != null) msg.baseload_w = baseload;
    try { await this._h.callWS(msg); this._err = null; } catch (err) { this._err = err.message || String(err); }
    await this._loadSources();
  }
  _sourcesBlock() {
    const s = this._src;
    if (!s) return '<div class="muted">Geräte werden gesucht …</div>';
    if (s.error) return `<div class="box err"><div class="txt">${esc(s.error)}</div></div>`;
    const groups = [['strom', 'Stromverbrauch', 'Wasserkocher, Herd oder Fernseher zeigen Ihren Tagesrhythmus.'], ['bewegung', 'Bewegung und Türen', 'Funksensoren ohne Kamera, zum Beispiel im Flur oder Bad.'], ['geraete', 'Fernseher und Musik', 'Wenn Sie ein- oder ausschalten.'], ['andere', 'Weitere', 'Vom Helfer eingetragen.']];
    const chosen = new Set(s.chosen);
    let html = `<section class="card" aria-label="Woran Werner Aktivität erkennt"><div class="t-m">Woran Werner merkt, dass Sie aktiv sind</div><div class="small">Sie bestimmen selbst, worauf Werner achtet. Werner merkt sich nur, <b>dass</b> sich etwas tut – nicht was.</div>`;
    let any = false;
    for (const [g, title, text] of groups) {
      const items = s.candidates.filter((c) => c.group === g);
      if (!items.length) continue; any = true;
      html += `<div style="border-top:1px solid #EFEBE2;padding-top:10px;display:flex;flex-direction:column;gap:8px"><div><div style="font-size:17px;font-weight:700">${title}</div><div class="small">${text}</div></div>`;
      html += items.map((c) => { const on = chosen.has(c.entity_id); const val = fmtState(this._h.states[c.entity_id]); const sub = [c.area, 'gerade: ' + val].filter(Boolean).join(' · '); return `<div class="between"><span style="display:flex;flex-direction:column;gap:2px;min-width:0"><span style="font-size:16px">${esc(c.name)}</span><span class="small">${esc(sub)}</span></span><button type="button" class="sw ${on ? 'on' : ''}" role="switch" aria-checked="${on}" aria-label="${esc(c.name)}" data-src="${esc(c.entity_id)}"><span></span></button></div>`; }).join('');
      html += '</div>';
    }
    if (!any) html += `<div class="box warn"><div class="txt">Werner hat keine passenden Geräte gefunden. Ein Helfer kann einen Stromzähler oder Bewegungsmelder anschließen – auswählen können Sie ihn dann hier selbst.</div></div>`;
    if (s.candidates.some((c) => c.group === 'strom' && chosen.has(c.entity_id))) {
      const b = Math.round(Number(s.baseload_w) || 0);
      html += `<div style="border-top:1px solid #EFEBE2;padding-top:10px;display:flex;flex-direction:column;gap:8px"><div style="font-size:17px;font-weight:700">Grundlast</div><div class="small">Bis zu diesem Verbrauch gilt es als still – Kühlschrank und Standby laufen ja immer.</div><div class="row" style="gap:10px"><button type="button" class="pm" aria-label="Weniger" data-base="-50">–</button><span class="val">${b} W</span><button type="button" class="pm" aria-label="Mehr" data-base="50">+</button></div></div>`;
    }
    if (!chosen.size) html += `<div class="box warn" style="padding:12px 14px"><div class="txt">Noch nichts gewählt. Dann kann Werner nicht merken, ob es ungewöhnlich still ist.</div></div>`;
    return html + this._errBox() + '</section>';
  }
  _errBox() { return this._err ? `<div class="box err" style="padding:12px 14px"><div class="txt">${esc(this._err)}</div></div>` : ''; }
  _household(withAdd) {
    const hh = this._hh;
    if (!hh) return '<div class="muted">Wird geladen …</div>';
    if (hh.error) return `<div class="box err"><div class="txt">Der Haushalt konnte nicht geladen werden. Ist Werner in der neuesten Version installiert?</div></div>`;
    const others = hh.residents.filter((x) => !x.mine);
    let html = `<section class="card" aria-label="Haushalt"><div class="t-m">Wer im Haushalt Werner nutzt</div>`;
    html += hh.residents.length ? hh.residents.map((x) => `<div class="between" style="border-top:1px solid #EFEBE2;padding-top:10px"><span style="display:flex;flex-direction:column;gap:2px"><span style="font-size:17px;font-weight:700">${esc(x.name)}${x.mine ? ' (Sie)' : ''}</span><span class="small">${x.consent ? 'Werner passt auf' : 'Wartet auf Zustimmung von ' + esc(x.name)}</span></span>${!x.mine && x.may_remove ? `<button type="button" class="link" data-remove-res="${esc(x.entry_id)}">${x.consent ? 'Entfernen' : 'Zurücknehmen'}</button>` : ''}</div>`).join('') : '<div class="muted">Noch niemand.</div>';
    html += `<div class="small">Jeder sieht nur seine eigenen Einstellungen und sein eigenes Protokoll.${others.length ? ' Von den anderen sehen Sie nur den Namen.' : ''}</div></section>`;
    if (!withAdd) return html;
    const free = hh.persons.filter((p) => !p.taken && (p.has_login || hh.is_admin));
    if (this._ui.addRes) {
      html += `<section class="card" aria-label="Bewohner hinzufügen"><div class="t-m">Bewohner hinzufügen</div>
<label class="f">Wer?<select data-f="add_person">${free.map((p) => `<option value="${esc(p.entity_id)}">${esc(p.name)}${p.me ? ' (Sie selbst)' : ''}</option>`).join('')}</select></label>
<label class="f">So soll Werner die Person ansprechen<input type="text" data-f="add_name" maxlength="40" placeholder="z. B. Erika"></label>
<div class="box info" style="padding:12px 14px"><div class="txt">Die Person muss <b>selbst zustimmen</b> – mit ihrer eigenen Anmeldung. Erst dann passt Werner auf sie auf. Sie bekommt einen Hinweis aufs Handy, wenn eines eingetragen ist.</div></div>
${this._phoneSelect('add_notify', '', 'Handy der Person (dort fragt Werner nach)', true)}${this._errBox()}
<button type="button" class="btn blue" data-act="add-res" ${this._busy ? 'disabled' : ''}>Eintragen</button><button type="button" class="btn" data-act="add-res-cancel">Abbrechen</button></section>`;
    } else if (free.length) {
      html += `<button type="button" class="btn dashed" data-act="add-res-open">+ Bewohner hinzufügen</button>`;
    } else {
      html += `<div class="small">Weitere Bewohner brauchen eine eigene Anmeldung in Home Assistant. Die richtet ein Helfer ein.</div>`;
    }
    return html;
  }
  _onboarding() {
    const hh = this._hh; const me = hh && hh.persons ? hh.persons.find((p) => p.me) : null;
    const taken = me && me.taken;
    const name = ((this._h.user && this._h.user.name) || '').split(' ')[0];
    let mine;
    if (!hh) mine = '<div class="muted">Wird geladen …</div>';
    else if (!me) mine = `<div class="box warn"><div class="t-m">Ihre Anmeldung gehört noch zu keiner Person</div><div class="txt">Das richtet Ihr Helfer unter Einstellungen › Personen ein. Danach können Sie Werner hier selbst einschalten.</div></div>`;
    else if (taken) mine = `<div class="box warn"><div class="txt">Für Sie ist Werner schon eingetragen.</div></div>`;
    else mine = `<section class="card" aria-label="Werner für mich einschalten"><div class="t-l">Werner für mich einschalten</div>
<ul style="margin:0;padding-left:22px;font-size:17px;line-height:1.45"><li>Werner passt auf, ob bei Ihnen alles in Ordnung ist.</li><li>Ist es ungewöhnlich still, fragt Werner <b>zuerst Sie</b>.</li><li>Wen Werner danach informiert, bestimmen Sie selbst.</li><li>Sie können Werner jederzeit pausieren oder wieder beenden.</li></ul>
<label class="f">So soll Werner Sie ansprechen<input type="text" data-f="my_name" maxlength="40" value="${esc(name)}"></label>
${this._phoneSelect('my_notify', me.phone || '')}${me.phone ? '<div class="small">Werner hat Ihr Handy schon gefunden.</div>' : ''}${this._errBox()}
<button type="button" class="btn green" data-act="add-me" ${this._busy ? 'disabled' : ''}>Werner einschalten</button></section>`;
    return `<h1>Willkommen bei Werner</h1><div class="muted">Sie entscheiden selbst, ob und wie Werner auf Sie aufpasst.</div>${mine}${hh && !hh.error ? this._household(true) : ''}`;
  }
  _consentScreen() {
    const r = this._r; const x = this._hh && this._hh.residents ? this._hh.residents.find((y) => y.entry_id === r.attributes.entry_id) : null;
    const who = x && x.created_by ? x.created_by : 'Jemand';
    return `<h1>Möchten Sie Werner?</h1>
<section class="box info"><div class="t-l">${esc(who)} hat Werner für Sie eingetragen</div><div class="txt">Werner passt erst auf Sie auf, wenn Sie zustimmen. Sie entscheiden das selbst.</div></section>
<section class="card"><ul style="margin:0;padding-left:22px;font-size:17px;line-height:1.45"><li>Werner merkt, ob sich bei Ihnen etwas tut. Keine Kamera, kein Mikrofon – außer Sie schalten es selbst ein.</li><li>Ist es ungewöhnlich still, fragt Werner <b>zuerst Sie</b>.</li><li>Wen Werner danach informiert, bestimmen nur Sie.</li><li>Ihre Einstellungen und Ihr Protokoll sieht niemand außer Ihnen.</li><li>Sie können Werner jederzeit pausieren oder beenden.</li></ul></section>
${this._errBox()}
<button type="button" class="btn green" style="min-height:64px;font-size:20px" data-act="consent-yes" ${this._busy ? 'disabled' : ''}>Ja, Werner soll auf mich aufpassen</button>
<button type="button" class="btn" style="min-height:60px" data-act="consent-no" ${this._busy ? 'disabled' : ''}>Nein, danke</button>
<div class="small">Bei „Nein, danke“ wird der Eintrag gelöscht.</div>`;
  }
  _bewohner() {
    const hh = this._hh; const x = hh && hh.residents ? hh.residents.find((y) => y.entry_id === this._r.attributes.entry_id) : null;
    const own = x && (x.mine || (hh && hh.is_admin));
    let html = '';
    if (own) {
      html += `<section class="card" aria-label="Über mich"><div class="t-m">${x.mine ? 'Über mich' : esc(x.name)}</div>
<label class="f">So spricht Werner ${x.mine ? 'Sie' : 'die Person'} an<input type="text" data-f="res_name" maxlength="40" value="${esc(x.name)}"></label>
${this._phoneSelect('res_notify', x.notify || '')}${this._errBox()}
<button type="button" class="btn blue" data-act="save-res" ${this._busy ? 'disabled' : ''}>Speichern</button></section>`;
    }
    html += this._household(true);
    if (x && x.may_remove) html += `<button type="button" class="btn redline" data-act="remove-me">${x.mine ? 'Werner für mich beenden' : 'Werner für ' + esc(x.name) + ' beenden'}</button>`;
    return html;
  }
  _sheetRemoveMe() {
    const id = this._ui.removeId; const x = this._hh && this._hh.residents ? this._hh.residents.find((y) => y.entry_id === id) : null;
    if (!x) return '';
    return this._sheet('Werner beenden', `<div style="font-size:26px;font-weight:700;line-height:1.2">${x.mine ? 'Werner für Sie beenden?' : 'Werner für ' + esc(x.name) + ' beenden?'}</div>
<div style="font-size:17px;line-height:1.45">Werner passt dann nicht mehr auf. ${x.mine ? 'Ihre' : 'Die'} Einstellungen und Vertrauenspersonen werden gelöscht. Sie können Werner später wieder einschalten.</div>${this._errBox()}
<button type="button" class="btn red" data-act="remove-yes" ${this._busy ? 'disabled' : ''}>Ja, beenden</button><button type="button" class="btn" data-act="close">Nein, doch nicht</button>`, 'alertdialog');
  }
  _val(field) { const el = this.shadowRoot.querySelector(`[data-f="${field}"]`); return el ? el.value.trim() : ''; }

  /* ---------- Fenster ---------- */
  _sheet(label, inner, role = 'dialog') { return `<div class="sheet-bg" data-act="close"><div class="sheet" role="${role}" aria-label="${esc(label)}">${inner}</div></div>`; }
  _sheetCheck() {
    const r = this._r; const wait = Math.round(this._num('wait_minutes') || 10); const first = this._first();
    return this._sheet('Werner fragt nach', `<div style="font-size:16px;color:${C.muted};font-weight:700">Werner fragt nach</div>
<div style="font-size:27px;font-weight:700;line-height:1.2">Hallo ${esc(r.attributes.resident)}, ist alles in Ordnung?</div>
<div style="font-size:17px;line-height:1.45">${esc(r.attributes.reason || '')}</div>
<div class="small">${first ? 'Ohne Antwort informiert Werner in ' + wait + ' Minuten ' + esc(first) + '.' : 'Sie haben niemanden eingetragen. Werner fragt nur Sie.'}</div>
<button type="button" class="btn redline" style="min-height:64px;font-size:21px" data-act="hilfe-ja">Bitte Hilfe holen</button>
<button type="button" class="btn green" style="min-height:80px;font-size:24px" data-act="ok">Ja, alles gut</button>`, 'alertdialog');
  }
  _sheetHilfe() {
    const first = this._first();
    return this._sheet('Soll Werner Hilfe holen?', `<div style="font-size:16px;color:${C.muted};font-weight:700">Werner</div>
<div style="font-size:27px;font-weight:700;line-height:1.2">Soll Werner Hilfe holen?</div>
<div style="font-size:17px;line-height:1.45">${first ? 'Werner informiert sofort ' + esc(first) + ' und dann die nächsten Personen.' : 'Sie haben niemanden eingetragen. Rufen Sie bitte 112 an.'}</div>
<button type="button" class="btn red" style="min-height:64px;font-size:21px" data-act="hilfe-ja">Ja, bitte Hilfe holen</button>
<button type="button" class="btn" style="min-height:64px" data-act="close">Nein, doch nicht</button>`, 'alertdialog');
  }
  _sheetInfo() {
    const wait = Math.round(this._num('wait_minutes') || 10); const first = this._first();
    const li = (t) => `<li>${t}</li>`;
    return this._sheet('So funktioniert Werner', `<div style="font-size:26px;font-weight:700;line-height:1.2">So funktioniert Werner</div><ul>
${li('Werner passt auf, ob bei Ihnen <b>alles in Ordnung</b> ist.')}
${li('Werner merkt, wenn sich im Haus etwas tut – zum Beispiel am <b>Stromverbrauch</b>.')}
${li('Werner merkt auch, ob Ihr <b>Handy zu Hause</b> ist. Sind Sie unterwegs, ist Werner still.')}
${li('Ist es <b>ungewöhnlich lange still</b>? Oder passiert <b>nachts</b> etwas Ungewöhnliches? Dann fragt Werner <b>zuerst Sie</b>: „Ist alles in Ordnung?“')}
${li('Tippen Sie dann auf <b>„Alles gut“</b>. Damit ist alles erledigt. Niemand wird gestört.')}
${li('Antworten Sie nicht innerhalb von <b>' + wait + ' Minuten</b>? Dann schreibt Werner Ihrer Vertrauensperson' + (first ? ' – zuerst <b>' + esc(first) + '</b>' : '') + '.')}
${li('Brauchen Sie Hilfe? Tippen Sie auf <b>„Ich brauche Hilfe“</b>. Dann sagt Werner sofort Bescheid.')}
${li('Besuch oder Urlaub? Tippen Sie auf <b>„Werner pausieren“</b>. Dann meldet Werner nichts.')}
${li('Ihre Vertrauenspersonen sehen <b>nur die Meldung</b> – nicht Ihren Tag.')}
${li('Sie bestimmen alles selbst: <b>wer</b>, <b>wie</b> und <b>wann</b>. Das stellen Sie unter „Einstellen“ ein.')}
</ul><div class="box err" style="padding:12px 14px"><div class="t-m">Im Notfall rufen Sie bitte 112 an.</div></div>
<button type="button" class="btn blue" data-act="close">Verstanden</button>`);
  }
  _sheetConsent(key) {
    const k = key.replace('consent_', ''); const cam = k === 'camera';
    const pts = cam
      ? ['Werner erkennt nur, wer unterwegs ist: Sie, Besuch oder ein Tier.', 'Es werden keine Bilder gespeichert. Alles bleibt in Ihrem Haus.', 'Ihre Vertrauenspersonen sehen nie Bilder – nur die Meldung.', 'Besuch wird nicht erkannt, nur als „Besuch“ gezählt. Sagen Sie Ihrem Besuch, dass es die Kamera gibt.', 'Das gilt nur für Sie. Andere Bewohner entscheiden selbst.', 'Sie können die Kamera hier jederzeit wieder ausschalten.']
      : ['Werner hört nur auf bestimmte Geräusche, zum Beispiel einen Sturz oder einen Hilferuf.', 'Es werden keine Töne aufgenommen oder gespeichert. Alles bleibt in Ihrem Haus.', 'Gespräche versteht Werner nicht und gibt nichts weiter.', 'Das gilt nur für Sie. Andere Bewohner entscheiden selbst.', 'Sie können das Mikrofon hier jederzeit wieder ausschalten.'];
    return this._sheet('Ihre Zustimmung', `<div style="font-size:16px;color:${C.muted};font-weight:700">Ihre Zustimmung</div>
<div style="font-size:26px;font-weight:700;line-height:1.2">${cam ? 'Kamera einschalten?' : 'Mikrofon einschalten?'}</div><ul>${pts.map((t) => `<li>${esc(t)}</li>`).join('')}</ul>
<div class="small">Werner nutzt ${cam ? 'die Kamera' : 'das Mikrofon'} erst, wenn Ihr Helfer ${cam ? 'eine Kamera mit Personenerkennung' : 'eine Geräuscherkennung'} angebunden hat.</div>
<button type="button" class="btn" style="min-height:60px;font-size:18px" data-act="close">Nein, lieber nicht</button>
<button type="button" class="btn green" style="min-height:64px;font-size:20px" data-consent-yes="${key}">Ja, einschalten</button>`);
  }
  async _loadEnergy() {
    this._en = null; this._render(true);
    try { this._en = await this._h.callWS({ type: 'werner/energy', entry_id: this._r.attributes.entry_id }); } catch (err) { this._en = { error: err.message || String(err) }; }
    this._render(true);
  }
  _sheetEnergy() {
    const e = this._en;
    let inner = `<div style="font-size:26px;font-weight:700;line-height:1.2">Was die Energie-Anzeige zeigt</div><div class="small">Sie wählen selbst. Hinter jedem Gerät steht der Wert von gerade eben – so erkennen Sie das richtige. „– nicht zeigen –“ blendet ein Feld aus.</div>`;
    if (!e) inner += '<div class="muted">Wird geladen …</div>';
    else if (e.error) inner += `<div class="box err"><div class="txt">${esc(e.error)}</div></div>`;
    else {
      const optLabel = (o) => [o.name, o.area, fmtState(this._h.states[o.entity_id])].filter(Boolean).join(' · ');
      const sel = (key, label) => { const opts = e.candidates[key] || []; const cur = e.current[key] || ''; const now = cur ? fmtState(this._h.states[cur]) : ''; return `<label class="f">${label}<select data-f="en_${key}"><option value="">– nicht zeigen –</option>${opts.map((o) => `<option value="${esc(o.entity_id)}" ${cur === o.entity_id ? 'selected' : ''}>${esc(optLabel(o))}</option>`).join('')}${cur && !opts.some((o) => o.entity_id === cur) ? `<option value="${esc(cur)}" selected>${esc(cur)}</option>` : ''}</select>${cur ? `<span class="small" style="font-weight:400">Gerade: ${esc(now)}</span>` : ''}</label>`; };
      inner += sel('weather', 'Wettervorhersage') + sel('grid_power', 'Strom aus dem Netz (gerade)') + sel('grid_energy', 'Zählerstand') + sel('pv_power', 'Sonnenstrom (gerade)')
        + `<label class="f">Größe der Solaranlage in kWp (für die Sonnen-Schätzung)<input type="number" inputmode="decimal" step="0.1" min="0" data-f="en_pv_kwp" value="${esc(e.current.pv_kwp || '')}" placeholder="z. B. 1,5"></label>`
        + sel('battery_soc', 'Batterie (Ladestand)')
        + `<label class="f">Name des Autos<input type="text" maxlength="40" data-f="en_vehicle_name" value="${esc(e.current.vehicle_name || '')}" placeholder="z. B. Mein Auto"></label>`
        + sel('vehicle_soc', 'Auto-Akku (Ladestand)') + sel('charge_mode', 'Lademodus der Wallbox');
    }
    inner += `${this._errBox()}<button type="button" class="btn blue" data-act="energy-save" ${!e || e.error || this._busy ? 'disabled' : ''}>Speichern</button><button type="button" class="btn" data-act="close">Abbrechen</button>`;
    return this._sheet('Energie-Anzeige', inner);
  }
  async _saveEnergy() {
    const keys = ['weather', 'grid_power', 'grid_energy', 'pv_power', 'battery_soc', 'vehicle_soc', 'charge_mode', 'vehicle_name'];
    const values = {}; keys.forEach((k) => { values[k] = this._val('en_' + k); });
    const kwp = parseFloat(this._val('en_pv_kwp').replace(',', '.')); values.pv_kwp = isNaN(kwp) ? 0 : kwp;
    this._busy = true; this._render(true);
    try { await this._h.callWS({ type: 'werner/resident/energy', entry_id: this._r.attributes.entry_id, values }); this._err = null; this._ui.sheet = null; this._fcFor = null; }
    catch (err) { this._err = err.message || String(err); }
    this._busy = false; this._render(true);
  }
  async _loadSignal(qr) {
    this._sg = Object.assign({}, this._sg || {}, { busy: true, err: null }); this._render(true);
    try {
      const st = await this._h.callWS({ type: 'werner/signal/status' });
      let image = (this._sg && this._sg.image) || null;
      if (qr && st.available && !st.connected) { image = (await this._h.callWS({ type: 'werner/signal/qr' })).image; this._ui.sgOther = false; }
      this._sg = Object.assign({}, st, { image: st.connected ? null : image, busy: false, checked: !qr && !!(this._sg && this._sg.image), t: Date.now() });
      if (st.connected) { this._ui.sgOther = false; this._sgAuto = false; }
    } catch (err) { this._sg = Object.assign({}, this._sg, { busy: false, err: err.message || String(err) }); }
    if (this._sg.image || this._ui.sgOther) this._sgStartPoll(); else this._sgStopPoll();
    this._render(true);
  }
  // Während ein Code gezeigt wird (hier oder auf dem anderen Gerät), schaut Werner selbst nach, ob es geklappt hat.
  _sgStartPoll() {
    if (this._sgTimer) return;
    this._sgUntil = Date.now() + 10 * 60 * 1000;
    this._sgTimer = setInterval(async () => {
      if (Date.now() > this._sgUntil || !this.isConnected) { this._sgStopPoll(); return; }
      try {
        const st = await this._h.callWS({ type: 'werner/signal/status' });
        if (st.connected) { this._sg = Object.assign({}, st, { image: null, busy: false }); this._ui.sgOther = false; this._sgAuto = false; this._sgStopPoll(); this._render(true); }
      } catch (e) { /* nächster Versuch */ }
    }, 4000);
  }
  _sgStopPoll() { if (this._sgTimer) { clearInterval(this._sgTimer); this._sgTimer = null; } }
  _isPhone() {
    try { return window.matchMedia('(pointer: coarse)').matches && Math.min(window.screen.width, window.screen.height) < 600; } catch (e) { return false; }
  }
  _sgLink() { return window.location.origin + '/werner?signal=1'; }
  _signalCard() {
    const s = this._sg;
    if (!s) { this._sg = { busy: true }; setTimeout(() => this._loadSignal(!!this._sgAuto && !this._isPhone())); return '<div class="muted">Signal wird geprüft …</div>'; }
    if (s.busy && !s.image) return `<div class="card" style="align-items:center;text-align:center"><div class="t-m">Einen Moment …</div><div class="txt">Werner fragt die Signal-App. Ein neuer Code kann bis zu 30 Sekunden dauern.</div></div>`;
    if (s.err) return `<div class="box err"><div class="txt">${esc(s.err)}</div><button type="button" class="btn" data-act="sg-check">Noch einmal versuchen</button></div>`;
    if (!s.available) return `<div class="box warn"><div class="t-m">Signal ist noch nicht eingerichtet</div><div class="txt">Dafür fehlt die App „Signal Messenger“ in Home Assistant. Die installiert einmal ein Helfer – verbinden können Sie Signal dann hier selbst.</div></div>`;
    if (s.connected) return `<div class="box ok"><div class="t-m">Signal ist verbunden</div><div class="txt">Werner schreibt Ihren Vertrauenspersonen über Ihr Signal. Wie so eine Nachricht aussieht, sehen Sie unten bei den Personen.</div></div>`;
    const phone = this._isPhone();
    const why = `<div class="txt">Werner schreibt dann <b>mit Ihrem Signal</b> an Ihre Vertrauenspersonen. Sie sehen Ihren Namen als Absender.</div>`;
    if (this._ui.sgOther) {
      const share = navigator.share ? `<button type="button" class="btn" data-act="sg-share">Link schicken …</button>` : '';
      return `<div class="card" style="gap:12px"><div class="t-m">Code auf einem zweiten Gerät zeigen</div>
<div class="txt">Mit dem Handy, auf dem Signal läuft, scannen Sie den Code. Der Code muss deshalb auf einem <b>anderen Bildschirm</b> stehen: Computer, Tablet oder das Handy eines Angehörigen.</div>
<ol style="margin:0;padding-left:22px;font-size:16px;line-height:1.5"><li>Öffnen Sie auf dem anderen Gerät diesen Link und melden Sie sich an:</li></ol>
<div style="font-size:17px;font-weight:700;word-break:break-all;background:${C.blueBg};color:${C.blueInk};border-radius:12px;padding:12px 14px">${esc(this._sgLink())}</div>
<div class="grid2" style="gap:8px"><button type="button" class="btn" data-act="sg-copy">${this._ui.sgCopied ? '✓ Kopiert' : 'Link kopieren'}</button>${share || '<span></span>'}</div>
<ol start="2" style="margin:0;padding-left:22px;font-size:16px;line-height:1.5"><li>Dort erscheint der Code. Oder Sie tippen dort auf Einstellen › Wer &amp; wie › Signal verbinden.</li><li>Auf diesem Handy in Signal: Ihr Bild › <b>Einstellungen</b> › <b>Verknüpfte Geräte</b> › <b>Gerät verknüpfen</b>. Dann den Code scannen.</li></ol>
<div class="box info" style="padding:12px 14px"><div class="txt">Werner merkt von selbst, wenn es geklappt hat. Diese Seite zeigt dann „Signal ist verbunden“.</div></div>
<button type="button" class="btn" data-act="sg-qr">Code doch hier zeigen</button></div>`;
    }
    if (!s.image) {
      const here = `<button type="button" class="btn ${phone ? '' : 'blue'}" data-act="sg-qr">Code hier zeigen</button>`;
      const other = `<button type="button" class="btn ${phone ? 'blue' : ''}" data-act="sg-other">Code auf anderem Gerät zeigen</button>`;
      return `<div class="box warn" style="gap:10px"><div class="t-m">Signal ist noch nicht verbunden</div><div class="txt">Damit Werner über Signal schreiben kann, verbinden Sie einmal Ihr Signal mit Werner. Dafür scannen Sie mit Ihrem Handy einen Code.</div>${why}
${phone ? '<div class="txt">Sie sind gerade am Handy. Den Code können Sie damit nicht selbst scannen – zeigen Sie ihn auf einem zweiten Gerät.</div>' + other + here : here + other}</div>`;
    }
    return `<div class="card" style="gap:12px"><div class="t-m">Signal mit Werner verbinden</div>
<div class="txt">Scannen Sie diesen Code mit dem Handy, auf dem Ihr Signal läuft:</div>
<ol style="margin:0;padding-left:22px;font-size:16px;line-height:1.5"><li>Öffnen Sie auf dem Handy die App <b>Signal</b>.</li><li>Tippen Sie auf Ihr Bild, dann auf <b>Einstellungen</b>.</li><li>Tippen Sie auf <b>Verknüpfte Geräte</b> und dann auf <b>Gerät verknüpfen</b>.</li><li>Halten Sie das Handy über diesen Code.</li></ol>
<img src="${esc(s.image)}" alt="QR-Code zum Verbinden" style="width:240px;height:240px;align-self:center;image-rendering:pixelated;border:1px solid ${C.line};border-radius:12px">
<div class="small">Der Code gilt nur wenige Minuten. Werner merkt von selbst, wenn es geklappt hat.</div>
${phone ? '<div class="box warn" style="padding:12px 14px"><div class="txt">Ist das hier das Handy mit Signal? Dann geht es nicht – zeigen Sie den Code auf einem zweiten Gerät.</div><button type="button" class="btn" data-act="sg-other">Code auf anderem Gerät zeigen</button></div>' : ''}
${s.checked && !s.connected ? '<div class="box warn" style="padding:12px 14px"><div class="txt">Noch nicht verbunden. Haben Sie auf dem Handy „Gerät verknüpfen“ bestätigt? Warten Sie kurz und prüfen Sie noch einmal.</div></div>' : ''}
<div class="grid2" style="gap:8px"><button type="button" class="btn" data-act="sg-qr" ${s.busy ? 'disabled' : ''}>Neuer Code</button><button type="button" class="btn green" data-act="sg-check" ${s.busy ? 'disabled' : ''}>${s.busy ? 'Wird geprüft …' : 'Ich habe gescannt'}</button></div></div>`;
  }
  /* ---------- E-Mail-Versand (für den ganzen Haushalt, richtet ein Helfer ein) ---------- */
  async _loadMail() {
    try { this._mail = await this._h.callWS({ type: 'werner/mail/status' }); } catch (err) { this._mail = { error: err.message || String(err) }; }
    this._render(true);
  }
  _mailCard() {
    const m = this._mail;
    if (!m) { this._mail = { loading: true }; setTimeout(() => this._loadMail()); return '<div class="muted">E-Mail wird geprüft …</div>'; }
    if (m.loading) return '<div class="muted">E-Mail wird geprüft …</div>';
    if (m.error) return `<div class="box err"><div class="txt">${esc(m.error)}</div></div>`;
    if (!m.may_edit) {
      return m.configured
        ? `<div class="box ok"><div class="t-m">E-Mail ist eingerichtet</div><div class="txt">Werner schreibt Ihren Vertrauenspersonen auch per E-Mail.</div></div>`
        : `<div class="box warn"><div class="t-m">E-Mail ist noch nicht eingerichtet</div><div class="txt">Dafür braucht Werner ein eigenes E-Mail-Postfach. Das richtet einmal ein Helfer ein. Bis dahin überspringt Werner Personen mit E-Mail.</div></div>`;
    }
    if (m.configured && !this._ui.mailEdit) {
      return `<div class="box ok" style="gap:10px"><div class="t-m">E-Mail ist eingerichtet</div><div class="txt">Werner sendet von ${esc(m.user)}.</div>${this._mailTestBlock()}<button type="button" class="btn" data-act="mail-edit">Postfach ändern</button></div>`;
    }
    const presets = [['GMX', 'mail.gmx.net', 587, 'starttls'], ['WEB.DE', 'smtp.web.de', 587, 'starttls'], ['Gmail', 'smtp.gmail.com', 587, 'starttls'], ['T-Online', 'securesmtp.t-online.de', 465, 'ssl'], ['Outlook', 'smtp-mail.outlook.com', 587, 'starttls']];
    const f = this._ui.mailForm || { server: m.server, port: m.port || 587, security: m.security || 'starttls' };
    return `<section class="card" aria-label="E-Mail-Versand"><div class="t-m">E-Mail-Versand einrichten</div>
<div class="txt">Werner braucht ein <b>eigenes Postfach</b>, z. B. bei GMX oder WEB.DE. Nehmen Sie nicht Ihr privates Postfach. Das gilt für den ganzen Haushalt.</div>
<div class="chips">${presets.map((x) => `<button type="button" class="ch ${f.server === x[1] ? 'on' : ''}" data-mail-preset="${x[1]}|${x[2]}|${x[3]}">${f.server === x[1] ? '✓ ' : ''}${x[0]}</button>`).join('')}</div>
<label class="f">Postausgangs-Server (SMTP)<input type="text" data-f="mail_server" value="${esc(f.server || '')}" placeholder="mail.gmx.net" autocomplete="off"></label>
<div class="grid2" style="gap:8px"><label class="f">Port<input type="number" data-f="mail_port" value="${esc(f.port || 587)}"></label>
<label class="f">Verschlüsselung<select data-f="mail_security"><option value="starttls" ${f.security !== 'ssl' ? 'selected' : ''}>STARTTLS</option><option value="ssl" ${f.security === 'ssl' ? 'selected' : ''}>SSL/TLS</option></select></label></div>
<label class="f">E-Mail-Adresse des Postfachs<input type="email" data-f="mail_user" value="${esc(m.user || '')}" placeholder="werner@example.org" autocomplete="off"></label>
<label class="f">Passwort<input type="password" data-f="mail_password" value="" placeholder="${m.has_password ? 'unverändert lassen' : ''}" autocomplete="new-password"></label>
<label class="f">Absendername<input type="text" data-f="mail_sender" value="${esc(m.sender_name || 'Werner')}" maxlength="60"></label>
<div class="small">Bei GMX und WEB.DE in den Postfach-Einstellungen „POP3/IMAP/SMTP“ erlauben. Bei Gmail ein App-Passwort verwenden. Das Passwort sieht in „Mein Zuhause“ niemand.</div>
${this._errBox()}<button type="button" class="btn blue" data-act="mail-save" ${this._busy ? 'disabled' : ''}>Speichern</button>${m.configured ? '<button type="button" class="btn" data-act="mail-cancel">Abbrechen</button>' : ''}</section>`;
  }
  _mailTestBlock() {
    const to = (this._people().find((p) => p.way === 'e_mail' && p.mail.includes('@')) || {}).mail || '';
    const t = this._ui.mailTest;
    return `<div class="row" style="gap:8px;align-items:flex-end"><label class="f" style="flex-grow:1">Test-E-Mail an<input type="email" data-f="mail_to" value="${esc(to)}"></label><button type="button" class="btn" data-act="mail-test" ${t === 'busy' ? 'disabled' : ''}>${t === 'busy' ? '…' : 'Senden'}</button></div>${t && t !== 'busy' ? `<div class="box ${t.ok ? 'ok' : 'err'}" style="padding:10px 12px"><div class="txt">${esc(t.text)}</div></div>` : ''}`;
  }
  async _saveMail() {
    const pw = (this.shadowRoot.querySelector('[data-f="mail_password"]') || {}).value || '';
    const msg = { type: 'werner/mail/set', server: this._val('mail_server'), port: Number(this._val('mail_port')) || 587, security: this._val('mail_security') || 'starttls', user: this._val('mail_user'), password: pw, sender_name: this._val('mail_sender') || 'Werner' };
    if (!msg.server || !msg.user.includes('@')) { this._err = 'Bitte Server und E-Mail-Adresse des Postfachs eintragen.'; this._render(true); return; }
    if (!pw && !(this._mail && this._mail.has_password)) { this._err = 'Bitte das Passwort eintragen.'; this._render(true); return; }
    this._busy = true; this._err = null; this._render(true);
    try { this._mail = Object.assign(await this._h.callWS(msg), { may_edit: true }); this._ui.mailEdit = false; this._ui.mailForm = null; }
    catch (err) { this._err = err.message || String(err); }
    this._busy = false; this._render(true);
  }
  async _testMail() {
    const to = this._val('mail_to'); if (!to.includes('@')) { this._ui.mailTest = { ok: false, text: 'Bitte eine E-Mail-Adresse eintragen.' }; this._render(true); return; }
    this._ui.mailTest = 'busy'; this._render(true);
    try { this._ui.mailTest = await this._h.callWS({ type: 'werner/mail/test', to }); } catch (err) { this._ui.mailTest = { ok: false, text: err.message || String(err) }; }
    this._render(true);
  }
  _sheetData() {
    const people = this._people().filter((p) => p.name);
    const rules = [['rule_morning', 'Morgens nichts los'], ['rule_quiet', 'Tagsüber lange still'], ['rule_night', 'Nachts ungewöhnlich aktiv']].filter((x) => this._on(x[0])).map((x) => x[1]);
    const cm = [this._on('consent_camera') ? 'Kamera' : null, this._on('consent_microphone') ? 'Mikrofon' : null].filter(Boolean);
    const items = [
      ['Ihr Protokoll', this._log ? this._log.length + ' Einträge aus den letzten 24 Stunden' : '–'],
      ['Ihre Vertrauenspersonen', people.length ? people.map((p) => p.name).join(', ') : 'niemand eingetragen'],
      ['Ihre Regeln', rules.length ? rules.join(', ') : 'alle aus'],
      ['Kamera und Mikrofon', cm.length ? 'An: ' + cm.join(' und ') + ' – nur Erkennung, keine Aufnahmen' : 'Aus']
    ];
    return this._sheet('Was Werner über Sie weiß', `<div style="font-size:26px;font-weight:700;line-height:1.2">Was Werner über Sie weiß</div>
${items.map((x) => `<div style="display:flex;flex-direction:column;gap:2px;border-top:1px solid #EFEBE2;padding-top:10px"><span class="small">${esc(x[0])}</span><span style="font-size:17px;font-weight:700;line-height:1.35">${esc(x[1])}</span></div>`).join('')}
<div class="box ok" style="padding:12px 14px"><div class="txt">Alles bleibt in Ihrem Haus. Ihre Vertrauenspersonen sehen nur Meldungen.</div></div>
<div class="small">Das Löschen des Protokolls kommt in einer der nächsten Versionen.</div>
<button type="button" class="btn blue" data-act="close">Schließen</button>`);
  }

  /* ---------- Bedienung ---------- */
  _setText(key, value) { const id = this._id(key); if (id) return this._call('text', 'set_value', { entity_id: id, value: value == null ? '' : String(value) }); return Promise.resolve(); }
  _setWay(n, way) { const id = this._id(`person_${n}_way`); if (id) return this._call('select', 'select_option', { entity_id: id, option: way }); return Promise.resolve(); }
  async _swap(a, b) {
    const pa = this._person(a); const pb = this._person(b);
    await Promise.all([
      this._setText(`person_${a}_name`, pb.name), this._setText(`person_${a}_contact`, pb.contact), this._setText(`person_${a}_phone`, pb.phone), this._setText(`person_${a}_e_mail`, pb.mail), this._setWay(a, pb.way),
      this._setText(`person_${b}_name`, pa.name), this._setText(`person_${b}_contact`, pa.contact), this._setText(`person_${b}_phone`, pa.phone), this._setText(`person_${b}_e_mail`, pa.mail), this._setWay(b, pa.way)
    ]);
  }
  async _remove(n) {
    await Promise.all([this._setText(`person_${n}_name`, ''), this._setText(`person_${n}_contact`, ''), this._setText(`person_${n}_phone`, ''), this._setText(`person_${n}_e_mail`, ''), this._setWay(n, 'off')]);
    // Lücken schließen: spätere Personen rücken nach.
    for (let i = n; i < 3; i++) { if (this._person(i + 1).name) await this._swap(i, i + 1); }
    delete this._tests[n];
  }
  async _test(n) {
    this._tests[n] = 'busy'; this._render(true);
    try {
      const res = await this._h.callWS({ type: 'call_service', domain: 'werner', service: 'test_person', service_data: { config_entry_id: this._r.attributes.entry_id, person: n }, return_response: true });
      this._tests[n] = (res && res.response) || { ok: false, text: 'Keine Antwort.' };
    } catch (err) { this._tests[n] = { ok: false, text: 'Fehler: ' + (err.message || err) }; }
    this._render(true);
  }

  _change(ev) {
    const el = ev.target;
    if (el.dataset.text) {
      const key = el.dataset.text; const value = el.value.trim();
      this._setText(key, value).then(() => {
        const m = key.match(/^person_(\d)_name$/);
        if (m && value && this._ui.adding === Number(m[1])) {
          this._ui.adding = null;
          if (this._person(Number(m[1])).way === 'off') this._setWay(Number(m[1]), 'ha_app');
        }
      });
      if (el.tagName === 'SELECT') this._render(true);
    }
  }

  _click(ev) {
    const el = ev.target.closest('button,[data-act]');
    if (!el) return;
    const d = el.dataset;
    if (d.act === 'close' && el.classList.contains('sheet-bg') && ev.target.closest('.sheet')) return;
    if (d.tab) { this._ui.tab = d.tab; this._ui.sheet = null; this._keepScroll = false; this._render(true); return; }
    if (d.who) { this._who = d.who; this._log = null; this._logT = 0; this._tests = {}; this._ui.adding = null; this._render(true); this.hass = this._h; return; }
    if (d.sub) { this._ui.sub = d.sub; this._render(true); return; }
    if (d.mailPreset) { const [server, port, security] = d.mailPreset.split('|'); this._ui.mailForm = { server, port: Number(port), security }; this._render(true); return; }
    if (d.goto) { this._ui.tab = 'einstellen'; this._ui.sub = d.goto; this._ui.sheet = null; this._render(true); return; }
    if (d.day) { this._ui.day = Number(d.day); this._render(true); return; }
    if (d.way) { const [n, w] = d.way.split('|'); this._setWay(Number(n), w); return; }
    if (d.test) { this._test(Number(d.test)); return; }
    if (d.move) { const [n, dir] = d.move.split('|').map(Number); this._swap(n, n + dir); return; }
    if (d.remove) { this._remove(Number(d.remove)); return; }
    if (d.toggle) { const id = this._id(d.toggle); if (id) this._call('switch', this._on(d.toggle) ? 'turn_off' : 'turn_on', { entity_id: id }); return; }
    if (d.consent) {
      if (this._on(d.consent)) this._call('switch', 'turn_off', { entity_id: this._id(d.consent) });
      else { this._ui.sheet = d.consent; this._render(true); }
      return;
    }
    if (d.consentYes) { this._call('switch', 'turn_on', { entity_id: this._id(d.consentYes) }); this._ui.sheet = null; this._render(true); return; }
    if (d.step) {
      const [key, dir] = d.step.split('|'); const id = this._id(key); const s = this._ent(id);
      if (!s) return;
      const step = Number(s.attributes.step) || 1; const v = (Number(s.state) || 0) + Number(dir) * step;
      const min = Number(s.attributes.min); const max = Number(s.attributes.max);
      this._call('number', 'set_value', { entity_id: id, value: Math.min(max, Math.max(min, v)) });
      return;
    }
    if (d.src && this._src && !this._src.error) {
      const set = new Set(this._src.chosen); if (set.has(d.src)) set.delete(d.src); else set.add(d.src);
      this._src = Object.assign({}, this._src, { chosen: [...set] }); this._render(true);
      this._saveSources([...set]); return;
    }
    if (d.base && this._src) {
      const v = Math.min(5000, Math.max(0, Math.round(Number(this._src.baseload_w) || 0) + Number(d.base)));
      this._src = Object.assign({}, this._src, { baseload_w: v }); this._render(true);
      clearTimeout(this._baseTO); this._baseTO = setTimeout(() => this._saveSources(this._src.chosen, this._src.baseload_w), 800); return;
    }
    if (d.removeRes) { this._ui.removeId = d.removeRes; this._ui.sheet = 'remove_me'; this._err = null; this._render(true); return; }
    if (d.mode) { this._call('select', 'select_option', { entity_id: this._energy().charge_mode, option: d.mode }); return; }
    switch (d.act) {
      case 'menu': this.dispatchEvent(new Event('hass-toggle-menu', { bubbles: true, composed: true })); break;
      case 'ok': this._press('all_good'); this._ui.sheet = null; this._render(true); break;
      case 'pause': { const id = this._id('paused'); if (id) this._call('switch', this._on('paused') ? 'turn_off' : 'turn_on', { entity_id: id }); break; }
      case 'hilfe': this._ui.sheet = 'hilfe'; this._render(true); break;
      case 'hilfe-ja': this._press('help'); this._ui.sheet = null; this._ui.tab = 'werner'; this._render(true); break;
      case 'info': this._ui.sheet = 'info'; this._render(true); break;
      case 'data': this._ui.sheet = 'data'; this._render(true); break;
      case 'energy': this._ui.sheet = 'energy'; this._err = null; this._loadEnergy(); break;
      case 'energy-save': this._saveEnergy(); break;
      case 'sg-qr': this._loadSignal(true); break;
      case 'sg-check': this._loadSignal(false); break;
      case 'mail-edit': this._ui.mailEdit = true; this._err = null; this._render(true); break;
      case 'mail-cancel': this._ui.mailEdit = false; this._ui.mailForm = null; this._err = null; this._render(true); break;
      case 'mail-save': this._saveMail(); break;
      case 'mail-test': this._testMail(); break;
      case 'sg-other': this._ui.sgOther = true; this._ui.sgCopied = false; if (this._sg) this._sg = Object.assign({}, this._sg, { image: null }); this._sgStartPoll(); this._render(true); break;
      case 'sg-copy': {
        const done = () => { this._ui.sgCopied = true; this._render(true); };
        if (navigator.clipboard) navigator.clipboard.writeText(this._sgLink()).then(done).catch(() => {}); break;
      }
      case 'sg-share': navigator.share({ title: 'Werner: Signal verbinden', text: 'Bitte auf einem zweiten Gerät öffnen und den Code mit meinem Handy scannen:', url: this._sgLink() }).catch(() => {}); break;
      case 'add': { const free = this._people().find((p) => !p.name); if (free) { this._ui.adding = free.n; this._render(true); const inp = this.shadowRoot.querySelector(`input[data-text="person_${free.n}_name"]`); if (inp) inp.focus(); } break; }
      case 'add-me': {
        const hh = this._hh; const me = hh && hh.persons.find((p) => p.me);
        if (!me) break;
        const name = this._val('my_name'); if (!name) { this._err = 'Bitte einen Namen eintragen.'; this._render(true); break; }
        this._ws({ type: 'werner/resident/add', person: me.entity_id, name, notify: this._val('my_notify') });
        break;
      }
      case 'add-res-open': this._ui.addRes = true; this._err = null; this._render(true); break;
      case 'add-res-cancel': this._ui.addRes = false; this._err = null; this._render(true); break;
      case 'add-res': {
        const person = this._val('add_person'); const name = this._val('add_name');
        if (!person || !name) { this._err = 'Bitte Person und Namen angeben.'; this._render(true); break; }
        const notify = this._val('add_notify'); const msg = { type: 'werner/resident/add', person, name }; if (notify !== '__auto') msg.notify = notify;
        this._ws(msg).then((res) => { if (res) { this._ui.addRes = false; this._render(true); } });
        break;
      }
      case 'save-res': {
        const name = this._val('res_name'); if (!name) { this._err = 'Bitte einen Namen eintragen.'; this._render(true); break; }
        this._ws({ type: 'werner/resident/update', entry_id: this._r.attributes.entry_id, name, notify: this._val('res_notify') });
        break;
      }
      case 'remove-me': this._ui.removeId = this._r.attributes.entry_id; this._ui.sheet = 'remove_me'; this._err = null; this._render(true); break;
      case 'remove-yes': this._ws({ type: 'werner/resident/remove', entry_id: this._ui.removeId }).then((res) => { if (res) { this._ui.sheet = null; this._ui.tab = 'start'; this._who = null; this._render(true); } }); break;
      case 'consent-yes': this._ws({ type: 'werner/resident/consent', entry_id: this._r.attributes.entry_id, accept: true }); break;
      case 'consent-no': this._ws({ type: 'werner/resident/consent', entry_id: this._r.attributes.entry_id, accept: false }); break;
      case 'close':
        if (this._r && this._r.state === 'asking' && !this._ui.sheet) this._ui.checkClosed = this._r.last_changed;
        this._ui.sheet = null; this._render(true); break;
      default: break;
    }
  }
}

if (!customElements.get('werner-mein-zuhause')) customElements.define('werner-mein-zuhause', WernerMeinZuhause);
window.customCards = window.customCards || [];
if (!window.customCards.find((c) => c.type === 'werner-mein-zuhause')) {
  window.customCards.push({ type: 'werner-mein-zuhause', name: 'Werner – Mein Zuhause', description: 'Einfache Bildschirme für Senioren: Start, Werner, Energie, Auto, Einstellen.' });
}
console.info('%c Werner – Mein Zuhause ' + WERNER_UI_VERSION, 'color:#1F4E79;font-weight:bold');
