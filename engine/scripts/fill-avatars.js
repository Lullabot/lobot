#!/usr/bin/env node
// Fill the avatar placeholders in a page copied from a Lobot template.
// Usage: node .ai/general/scripts/fill-avatars.js tmp/<page>.html
// Replaces {{LOBOT_AVATAR}}, {{LUCY_AVATAR}}, and {{PEPPER_AVATAR}} with data URIs
// read from Lobot's own files, so the image travels inside the hosted page (hosted
// pages can't load local files). A missing image becomes "" and the page hides it.
// Edits the file in place. No dependencies.
'use strict';
const fs = require('fs');
const path = require('path');

const general = path.join(__dirname, '..');
const images = {
  '{{LOBOT_AVATAR}}': path.join(general, 'avatar.webp'),
  '{{LUCY_AVATAR}}': path.join(general, 'agents', 'lucy', 'avatar.webp'),
  '{{PEPPER_AVATAR}}': path.join(general, 'agents', 'pepper', 'avatar.webp'),
};

const file = process.argv[2];
if (!file || !fs.existsSync(file)) {
  console.error('usage: node fill-avatars.js <page.html>');
  process.exit(1);
}
let html = fs.readFileSync(file, 'utf8');
const filled = [];
for (const [key, img] of Object.entries(images)) {
  if (!html.includes(key)) continue;
  const uri = fs.existsSync(img) ? 'data:image/webp;base64,' + fs.readFileSync(img).toString('base64') : '';
  html = html.split(key).join(uri);
  filled.push(key.slice(2, -2).toLowerCase() + (uri ? '' : ' (missing, hidden)'));
}
fs.writeFileSync(file, html);
console.log('avatars: ' + (filled.length ? filled.join(', ') : 'none in this page'));
