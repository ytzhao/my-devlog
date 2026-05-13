const SERVER = 'http://localhost:3721';

async function checkServer() {
  const el = document.getElementById('status');
  try {
    const res = await fetch(`${SERVER}/highlight`, { method: 'OPTIONS' });
    if (res.ok) {
      el.className = 'status ok';
      el.textContent = '✅ Server online (localhost:3721)';
    } else {
      throw new Error('bad status');
    }
  } catch {
    el.className = 'status err';
    el.textContent = '❌ Server offline. Run: python tools/web_highlight_server.py';
  }
}

checkServer();
