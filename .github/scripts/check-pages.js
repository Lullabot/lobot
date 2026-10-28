#!/usr/bin/env node
// Checks that the GitHub Pages site (docs/index.html) has a card for every
// skill and agent in engine/, and none for one that no longer exists.
// No dependencies. Run from the repository root: node .github/scripts/check-pages.js
'use strict';
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..', '..');
const page = fs.readFileSync(path.join(root, 'docs', 'index.html'), 'utf8');

const skills = fs.readdirSync(path.join(root, 'engine', 'skills'), { withFileTypes: true })
  .filter((d) => d.isDirectory() && fs.existsSync(path.join(root, 'engine', 'skills', d.name, 'SKILL.md')))
  .map((d) => d.name);
const agents = fs.readdirSync(path.join(root, 'engine', 'agents'))
  .filter((f) => f.endsWith('.md'))
  .map((f) => f.slice(0, -3));

const onPage = (attr) => [...page.matchAll(new RegExp(`data-${attr}="([^"]+)"`, 'g'))].map((m) => m[1]);
const problems = [];

for (const [kind, expected] of [['skill', skills], ['agent', agents]]) {
  const found = onPage(kind);
  for (const name of expected) {
    if (!found.includes(name)) problems.push(`missing ${kind}: ${name} (add a card with data-${kind}="${name}")`);
  }
  for (const name of found) {
    if (!expected.includes(name)) problems.push(`stale ${kind}: ${name} is on the page but not in engine/`);
  }
  const dupes = found.filter((n, i) => found.indexOf(n) !== i);
  for (const name of new Set(dupes)) problems.push(`duplicate ${kind} card: ${name}`);
}

if (problems.length) {
  console.error('docs/index.html is out of date:\n- ' + problems.join('\n- '));
  process.exit(1);
}
console.log(`pages: ok (${skills.length} skills, ${agents.length} agents)`);
