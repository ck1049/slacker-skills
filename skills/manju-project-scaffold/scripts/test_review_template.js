// Offline behavior checks, not a substitute for a real-browser playback test.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

async function main() {
  const template = fs.readFileSync(path.join(__dirname, '../assets/episode-review.html'), 'utf8');
  const script = template.split('<script>')[1].split('</script>')[0];
  const events = {};
  const auto = { checked: true, addEventListener: (name, fn) => { events['auto:' + name] = fn; } };
  const refresh = { addEventListener: (name, fn) => { events['refresh:' + name] = fn; } };
  const details = { open: false };
  const field = { value: 'D:\\示例 项目\\图片', focus: () => { field.focused = true; }, select: () => { field.selected = true; }, closest: () => details };
  const feedback = { textContent: '' };
  const copy = { dataset: { copy: 'folder-path' }, addEventListener: (name, fn) => { events['copy:' + name] = fn; } };
  const media = { paused: true, ended: false };
  let timer;
  let reloads = 0;
  let focused = false;
  let saved = '';
  const document = {
    hidden: false,
    getElementById: id => ({ 'auto-refresh': auto, refresh, 'folder-path': field, feedback })[id],
    querySelectorAll: selector => selector === 'audio,video' ? [media] : [copy],
    querySelector: () => focused ? field : null,
  };
  vm.runInNewContext(script, {
    document, navigator: {},
    location: { pathname: '/测试.html', reload: () => { reloads += 1; } },
    window: { scrollY: 240, scrollTo: () => {}, addEventListener: () => {} },
    sessionStorage: { getItem: () => null, setItem: (_, value) => { saved = value; } },
    setInterval: fn => { timer = fn; },
  });
  timer();
  assert.equal(reloads, 1);
  assert.equal(JSON.parse(saved).scroll, 240);
  media.paused = false;
  timer();
  assert.equal(reloads, 1, 'playing media must suppress automatic reload');
  media.paused = true;
  document.hidden = true;
  timer();
  assert.equal(reloads, 1, 'hidden page must not reload');
  document.hidden = false;
  auto.checked = false;
  timer();
  assert.equal(reloads, 1, 'user can disable automatic reload');
  auto.checked = true;
  focused = true;
  timer();
  assert.equal(reloads, 1, 'copying a path must not be interrupted');
  await events['copy:click']();
  assert.ok(details.open && field.selected && field.focused, 'clipboard restriction must expose selectable path');
  assert.match(feedback.textContent, /Ctrl\+C/);
  events['refresh:click']();
  assert.equal(reloads, 2);
  console.log('Template offline checks passed: refresh, media/visibility/opt-out guards, scroll and clipboard fallback.');
}
main().catch(error => { console.error(error); process.exitCode = 1; });
