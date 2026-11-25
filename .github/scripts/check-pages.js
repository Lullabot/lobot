#!/usr/bin/env node
// Checks the GitHub Pages site (docs/): skills.html has a card for every skill
// and agent in engine/, and none for one that no longer exists; every page
// links the shared stylesheet and script and has the same nav.
// No dependencies. Run from the repository root: node .github/scripts/check-pages.js
'use strict';
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..', '..');
const docs = path.join(root, 'docs');
const read = (f) => fs.readFileSync(path.join(docs, f), 'utf8');
const pages = fs.readdirSync(docs).filter((f) => f.endsWith('.html'));
const catalog = 'skills.html';
const problems = [];

const skills = fs.readdirSync(path.join(root, 'engine', 'skills'), { withFileTypes: true })
  .filter((d) => d.isDirectory() && fs.existsSync(path.join(root, 'engine', 'skills', d.name, 'SKILL.md')))
  .map((d) => d.name);
const agents = fs.readdirSync(path.join(root, 'engine', 'agents'))
  .filter((f) => f.endsWith('.md'))
  .map((f) => f.slice(0, -3));

const cards = (html, attr) => [...html.matchAll(new RegExp(`data-${attr}="([^"]+)"`, 'g'))].map((m) => m[1]);

if (!pages.includes(catalog)) {
  problems.push(`docs/${catalog} is missing; it holds the skill and agent cards`);
} else {
  const page = read(catalog);
  for (const [kind, expected] of [['skill', skills], ['agent', agents]]) {
    const found = cards(page, kind);
    for (const name of expected) {
      if (!found.includes(name)) problems.push(`missing ${kind}: ${name} (add a card to docs/${catalog} with data-${kind}="${name}")`);
    }
    for (const name of found) {
      if (!expected.includes(name)) problems.push(`stale ${kind}: ${name} is on docs/${catalog} but not in engine/`);
    }
    const dupes = found.filter((n, i) => found.indexOf(n) !== i);
    for (const name of new Set(dupes)) problems.push(`duplicate ${kind} card: ${name}`);
  }
}

const navOf = (html) => ((html.match(/<nav class="top"[\s\S]*?<\/nav>/) || [''])[0])
  .replace(/\s*aria-current="page"/g, '').replace(/\s+/g, ' ');
const nav = pages.includes('index.html') ? navOf(read('index.html')) : '';
for (const f of pages) {
  const html = read(f);
  if (f !== catalog && /data-(skill|agent)="/.test(html)) problems.push(`docs/${f}: skill and agent cards belong only on docs/${catalog}`);
  if (!html.includes('href="assets/site.css"')) problems.push(`docs/${f}: doesn't link assets/site.css`);
  if (!html.includes('src="assets/site.js"')) problems.push(`docs/${f}: doesn't load assets/site.js`);
  if (navOf(html) !== nav) problems.push(`docs/${f}: nav differs from docs/index.html`);
  for (const m of html.matchAll(/(?:href|src)="([a-z0-9/_.-]+\.(?:html|css|js|svg|png|webp|jpg))(?:#[^"]*)?"/gi)) {
    if (!fs.existsSync(path.join(docs, m[1]))) problems.push(`docs/${f}: broken link to ${m[1]}`);
  }
}

if (problems.length) {
  console.error('The Pages site (docs/) is out of date:\n- ' + problems.join('\n- '));
  process.exit(1);
}
console.log(`pages: ok (${pages.length} pages, ${skills.length} skills, ${agents.length} agents)`);
