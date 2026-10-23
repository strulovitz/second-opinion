// Small browser-test transport using installed Chrome and Node's native WebSocket.
import { spawn } from 'node:child_process';
import { mkdtemp, rm } from 'node:fs/promises';
import { createServer } from 'node:net';

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
export async function browser() {
  const port = await new Promise(resolve => { const s = createServer(); s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => resolve(p)); }); });
  const profile = await mkdtemp('/tmp/opencode/second-opinion-browser-');
  const chrome = spawn('/usr/bin/google-chrome', ['--headless=new', `--remote-debugging-port=${port}`, '--remote-debugging-address=127.0.0.1', `--user-data-dir=${profile}`, '--no-first-run', '--no-default-browser-check', '--enable-unsafe-swiftshader', 'about:blank'], { stdio: 'ignore' });
  let socket;
  const pending = new Map(), events = [], errors = [];
  try {
    let targets;
    for (let i = 0; i < 100; i++) {
      try { targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); break; } catch { await delay(100); }
    }
    if (!targets) throw new Error('Isolated Chrome did not start');
    socket = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
    await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
    let id = 0;
    socket.onmessage = event => {
      const message = JSON.parse(event.data);
      if (message.id) { const task = pending.get(message.id); if (task) { pending.delete(message.id); clearTimeout(task.timeout); message.error ? task.reject(new Error(JSON.stringify(message.error))) : task.resolve(message.result); } }
      else { events.push(message); if (message.method === 'Runtime.exceptionThrown') errors.push(message.params.exceptionDetails); }
    };
    const send = (method, params = {}) => new Promise((resolve, reject) => {
      const n = ++id, timeout = setTimeout(() => { pending.delete(n); reject(new Error(`CDP timeout: ${method}`)); }, 15000);
      pending.set(n, { resolve, reject, timeout }); socket.send(JSON.stringify({ id: n, method, params }));
    });
    await send('Runtime.enable'); await send('Page.enable'); await send('Network.enable');
    return { send, events, errors,
      async evaluate(expression) {
        const result = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
        if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
        return result.result.value;
      },
      async close() { socket.close(); chrome.kill('SIGTERM'); await new Promise(resolve => chrome.once('exit', resolve)); await rm(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 }); }
    };
  } catch (error) { socket?.close(); chrome.kill('SIGTERM'); throw error; }
}

export async function until(check, label, timeout = 15000) {
  const end = Date.now() + timeout;
  while (Date.now() < end) { const result = await check(); if (result) return result; await delay(100); }
  throw new Error(`Timed out: ${label}`);
}
