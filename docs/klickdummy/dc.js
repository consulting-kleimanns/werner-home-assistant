/* Kleine Laufzeit für den Werner-Klickdummy: {{wert}}, <sc-if>, <sc-for>, onClick. MIT-Lizenz, Jochen Kleimann */
(function () {
  class DCLogic {
    constructor(props) { this.props = props || {}; this.state = {}; }
    setState(patch) { Object.assign(this.state, typeof patch === 'function' ? patch(this.state) : patch); render(); }
  }
  let comp, tpl, root;
  const RE = /\{\{\s*([^}]*?)\s*\}\}/g;
  function get(path, scope) {
    if (path === 'true') return true; if (path === 'false') return false;
    if (path !== '' && !isNaN(path)) return Number(path);
    let v = scope;
    for (const k of path.split('.')) { if (v == null) return undefined; v = v[k]; }
    return v;
  }
  function single(str) { const m = /^\s*\{\{\s*([^}]*?)\s*\}\}\s*$/.exec(str); return m ? m[1] : null; }
  function text(str, scope) { return str.replace(RE, (_, p) => { const v = get(p, scope); return v == null ? '' : String(v); }); }
  function build(node, scope, out) {
    if (node.nodeType === 3) { out.appendChild(document.createTextNode(text(node.nodeValue, scope))); return; }
    if (node.nodeType !== 1) return;
    const tag = node.localName;
    if (tag === 'sc-if') {
      if (get(single(node.getAttribute('value')) || '', scope)) node.childNodes.forEach((c) => build(c, scope, out));
      return;
    }
    if (tag === 'sc-for') {
      const list = get(single(node.getAttribute('list')) || '', scope) || [];
      const as = node.getAttribute('as') || 'item';
      list.forEach((item, i) => { const s = Object.create(scope); s[as] = item; s[as + 'Index'] = i; node.childNodes.forEach((c) => build(c, s, out)); });
      return;
    }
    const el = node.namespaceURI === 'http://www.w3.org/2000/svg' ? document.createElementNS(node.namespaceURI, tag) : document.createElement(tag);
    for (const a of node.attributes) {
      if (a.name.startsWith('hint-')) continue;
      const p = single(a.value);
      if (a.name.startsWith('on')) { const fn = p ? get(p, scope) : null; if (typeof fn === 'function') el.addEventListener(a.name.slice(2), (e) => fn(e)); continue; }
      if (p !== null) { const v = get(p, scope); if (v === false || v == null) { if (a.name.startsWith('aria-')) el.setAttribute(a.name, 'false'); continue; } el.setAttribute(a.name, v === true ? (a.name.startsWith('aria-') ? 'true' : '') : String(v)); }
      else el.setAttribute(a.name, text(a.value, scope));
    }
    const kids = node.content ? node.content.childNodes : node.childNodes;
    kids.forEach((c) => build(c, scope, el));
    out.appendChild(el);
  }
  function render() {
    const scrolls = [...root.querySelectorAll('*')].filter((e) => e.scrollTop > 0).map((e) => [path(e), e.scrollTop]);
    const frag = document.createDocumentFragment();
    const vals = comp.renderVals();
    tpl.content.childNodes.forEach((c) => build(c, vals, frag));
    root.replaceChildren(frag);
    for (const [p, t] of scrolls) { const e = byPath(p); if (e) e.scrollTop = t; }
  }
  function path(e) { const p = []; while (e && e !== root) { p.unshift([...e.parentNode.children].indexOf(e)); e = e.parentNode; } return p; }
  function byPath(p) { let e = root; for (const i of p) { e = e && e.children[i]; } return e; }
  document.addEventListener('DOMContentLoaded', () => {
    const x = document.querySelector('x-dc');
    const src = x.innerHTML; x.remove();
    tpl = document.createElement('template'); tpl.innerHTML = src;
    const helmet = tpl.content.querySelector('helmet');
    if (helmet) { [...helmet.childNodes].forEach((n) => document.head.appendChild(n)); helmet.remove(); }
    const sc = document.querySelector('script[data-dc-script]');
    const props = JSON.parse(sc.getAttribute('data-props') || '{}');
    if (new URLSearchParams(location.search).get('werner') === '1') props.startWerner = true;
    const Component = new Function('DCLogic', sc.textContent + '\n;return Component;')(DCLogic);
    root = document.createElement('div'); root.id = 'dc-root'; document.body.appendChild(root);
    comp = new Component(props); render();
  });
})();
