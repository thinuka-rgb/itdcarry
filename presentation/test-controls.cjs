const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, 'OPEN-PRESENTATION.html'), 'utf8');
const spoken = fs.readFileSync(path.join(__dirname, 'PRESENTATION-SCRIPT.txt'), 'utf8').replace(/\r\n/g, '\n');
function element() {
  return {children: [], style: {}, attrs: {}, open: false, paused: true,
    classList: {add() {}, toggle() {}},
    setAttribute(k, v) { this.attrs[k] = v; },
    append(child) { this.children.push(child); },
    pause() { this.paused = true; },
    play() { this.paused = false; return Promise.resolve(); }, load() {},
    showModal() { this.open = true; }, close() { this.open = false; }};
}
const elements = Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(m => [m[1], element()]));
const listeners = {};
const timers = [];
const context = vm.createContext({document: {
  getElementById: id => { assert.ok(elements[id], `Missing element ${id}`); return elements[id]; },
  createElement: element, addEventListener: (name, fn) => listeners[name] = fn,
}, setInterval: fn => timers.push(fn), Date});
vm.runInContext(html.match(/<script>([\s\S]*)<\/script>/)[1], context);
const state = () => vm.runInContext('[index,index===3?demoStep:0].join(":")', context);
const click = id => elements[id].onclick();
const key = (key, repeat = false) => listeners.keydown({key, repeat, target: {tagName: 'BODY'}, preventDefault() {}});
click('begin');
assert.equal(state(), '0:0');
assert.equal(elements.prev.disabled, true);
click('next'); key('ArrowRight'); key('PageDown');
assert.equal(state(), '3:0');
assert.equal(elements.film.paused, true);
const firstFrame = elements.demoFrame.src;
key('ArrowRight');
assert.equal(state(), '3:1');
assert.notEqual(elements.demoFrame.src, firstFrame);
click('notes');
assert.match(elements.noteBody.textContent, /first setting finds the pattern/);
key('ArrowRight');
assert.equal(state(), '3:1', 'Notes must block slide keyboard shortcuts');
click('close'); key(' '); click('next');
assert.equal(state(), '3:3');
assert.equal(elements.demoSteps.children[3].attrs['aria-current'], 'true');
click('next');
assert.equal(state(), '4:0');
click('prev');
assert.equal(state(), '3:3', 'Returning from slide 5 restores the final demo step');
key('ArrowLeft');
assert.equal(state(), '3:2');
elements.demoSteps.children[0].onclick();
assert.equal(state(), '3:0');
elements.demoSteps.children[3].onclick();
key('r');
assert.equal(state(), '3:0');
click('next'); click('replay');
assert.equal(state(), '3:0');
key('ArrowRight', true); key('p'); timers.forEach(fn => fn());
assert.equal(state(), '3:0', 'A demo step must never advance on its own');
assert.equal(elements.film.paused, true);
click('prev');
assert.equal(state(), '2:0');
click('next');
assert.equal(state(), '3:0', 'Forward entry starts at demo step 1');
for (let i = 0; i < 5; i++) click('next');
assert.equal(state(), '5:0');
assert.equal(elements.next.disabled, true);
key('ArrowRight');
assert.equal(state(), '5:0');
const slides = vm.runInContext('slides', context);
for (const slide of slides) {
  assert.ok(spoken.includes(slide.title), 'Slide heading matches external script');
  assert.ok(spoken.includes(slide.script), 'Embedded and external scripts match');
}
assert.equal(slides[3].steps.length, 4);
for (const step of slides[3].steps) assert.ok(spoken.includes(step.script));
console.log('Presentation controls and script checks passed.');
