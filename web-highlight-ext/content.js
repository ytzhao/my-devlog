(() => {
  'use strict';

  const SERVER = 'http://localhost:3721';
  let toolbar = null;
  let selectedText = '';
  let mouseX = 0, mouseY = 0;
  let hideTimer = null;
  let pendingScreenshot = null;
  const TB_WIDTH = 220;
  const HL_CLASS = 'dl-highlight';
  const STORAGE_KEY = (url) => 'hl_' + btoa(unescape(encodeURIComponent(url))).replace(/[^a-zA-Z0-9]/g, '').slice(0, 40);

  /* ── Toolbar UI ── */
  function removeToolbar() {
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
    if (toolbar) { toolbar.remove(); toolbar = null; }
  }

  function posAtMouse(el, h) {
    const sx = window.scrollX || 0, sy = window.scrollY || 0;
    const vw = window.innerWidth, vh = window.innerHeight;
    let left = mouseX + sx;
    if (left + TB_WIDTH > sx + vw - 6) left = sx + vw - TB_WIDTH - 6;
    if (left < sx + 6) left = sx + 6;

    let top = mouseY + sy + 14;
    if (top + h > sy + vh - 6) top = mouseY + sy - h - 10;
    el.style.top = top + 'px';
    el.style.left = left + 'px';
  }

  function showToolbar() {
    removeToolbar();
    selectedText = window.getSelection().toString().trim();
    if (!selectedText) return;

    toolbar = document.createElement('div');
    toolbar.id = 'dl-toolbar';
    toolbar.innerHTML = `
      <button id="dl-hl" title="Highlight & Save">🖍️</button>
      <button id="dl-note" title="Add note">📝</button>
      <button id="dl-screenshot" title="Area screenshot & Save">📷</button>
      <button id="dl-copy" title="Copy text">📋</button>
    `;
    posAtMouse(toolbar, 40);
    document.body.appendChild(toolbar);

    toolbar.querySelector('#dl-hl').onclick = (e) => { e.stopPropagation(); doHighlightSave(); };
    toolbar.querySelector('#dl-note').onclick = (e) => { e.stopPropagation(); showNoteInput(); };
    toolbar.querySelector('#dl-screenshot').onclick = (e) => { e.stopPropagation(); startAreaScreenshot(); };
    toolbar.querySelector('#dl-copy').onclick = (e) => { e.stopPropagation(); doCopy(); };
  }

  function showNoteInput() {
    removeToolbar();
    toolbar = document.createElement('div');
    toolbar.id = 'dl-toolbar';
    toolbar.className = 'dl-note-mode';
    toolbar.innerHTML = `
      <input type="text" id="dl-tag" value="web" />
      <input type="text" id="dl-note-in" placeholder="Note…" autofocus />
      <button id="dl-ok" title="Save">✓</button>
      <button id="dl-x" title="Cancel" class="dl-ghost">✕</button>
    `;
    posAtMouse(toolbar, 42);
    document.body.appendChild(toolbar);

    const noteIn = toolbar.querySelector('#dl-note-in');
    noteIn.focus();

    toolbar.querySelector('#dl-ok').onclick = (e) => {
      e.stopPropagation();
      const note = noteIn.value.trim();
      const tag = toolbar.querySelector('#dl-tag').value.trim() || 'web';
      doSave(note, tag);
    };
    toolbar.querySelector('#dl-x').onclick = (e) => { e.stopPropagation(); removeToolbar(); };
  }

  /* ── Area Screenshot ── */
  function startAreaScreenshot() {
    removeToolbar();
    showToast('📷 Capturing…', 'info');

    chrome.runtime.sendMessage({ action: 'captureFullPage' }, (res) => {
      if (chrome.runtime.lastError || !res || res.status !== 'ok') {
        showToast('❌ Screenshot failed: ' + (res?.message || chrome.runtime.lastError?.message || 'unknown'), 'error');
        return;
      }
      enterCropMode(res.dataUrl);
    });
  }

  function enterCropMode(fullPageDataUrl) {
    const overlay = document.createElement('div');
    overlay.id = 'dl-screenshot-overlay';
    overlay.innerHTML = `
      <div class="dl-screenshot-hint">拖动鼠标框选截图区域，按 ESC 取消</div>
      <div class="dl-screenshot-selection"></div>
    `;
    document.body.appendChild(overlay);

    let startX, startY, isDragging = false;
    const sel = overlay.querySelector('.dl-screenshot-selection');

    const onMouseDown = (e) => {
      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;
      sel.style.left = startX + 'px';
      sel.style.top = startY + 'px';
      sel.style.width = '0px';
      sel.style.height = '0px';
      sel.style.display = 'block';
    };

    const onMouseMove = (e) => {
      if (!isDragging) return;
      const x = Math.min(startX, e.clientX);
      const y = Math.min(startY, e.clientY);
      const w = Math.abs(e.clientX - startX);
      const h = Math.abs(e.clientY - startY);
      sel.style.left = x + 'px';
      sel.style.top = y + 'px';
      sel.style.width = w + 'px';
      sel.style.height = h + 'px';
    };

    const onMouseUp = (e) => {
      if (!isDragging) return;
      isDragging = false;
      const w = Math.abs(e.clientX - startX);
      const h = Math.abs(e.clientY - startY);

      if (w < 10 || h < 10) {
        showToast('Selection too small, cancelled', 'info');
        cleanup();
        return;
      }

      const x = Math.min(startX, e.clientX);
      const y = Math.min(startY, e.clientY);
      cleanup();
      cropAndSave(fullPageDataUrl, x, y, w, h);
    };

    const cleanup = () => {
      overlay.removeEventListener('mousedown', onMouseDown);
      overlay.removeEventListener('mousemove', onMouseMove);
      overlay.removeEventListener('mouseup', onMouseUp);
      document.removeEventListener('keydown', onKeyDown);
      overlay.remove();
    };

    const onKeyDown = (e) => {
      if (e.key === 'Escape') {
        cleanup();
        showToast('Screenshot cancelled', 'info');
      }
    };

    overlay.addEventListener('mousedown', onMouseDown);
    overlay.addEventListener('mousemove', onMouseMove);
    overlay.addEventListener('mouseup', onMouseUp);
    document.addEventListener('keydown', onKeyDown);
  }

  function cropAndSave(dataUrl, x, y, w, h) {
    const img = new Image();
    img.onload = () => {
      const dpr = window.devicePixelRatio || 1;
      const canvas = document.createElement('canvas');
      const sx = Math.round(x * dpr);
      const sy = Math.round(y * dpr);
      const sw = Math.round(w * dpr);
      const sh = Math.round(h * dpr);
      canvas.width = sw;
      canvas.height = sh;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, sx, sy, sw, sh, 0, 0, sw, sh);
      pendingScreenshot = canvas.toDataURL('image/png');

      // Debug: check if crop rect is valid
      console.log('[DevLog] === Screenshot Debug ===');
      console.log('[DevLog] DPR:', dpr);
      console.log('[DevLog] Viewport CSS:', window.innerWidth, 'x', window.innerHeight);
      console.log('[DevLog] Capture img size:', img.width, 'x', img.height);
      console.log('[DevLog] Expected img size:', Math.round(window.innerWidth * dpr), 'x', Math.round(window.innerHeight * dpr));
      console.log('[DevLog] Crop CSS coords:', x, y, w, h);
      console.log('[DevLog] Crop physical:', sx, sy, sw, sh);
      console.log('[DevLog] Bounds check:', sx >= 0 && sy >= 0 && sx + sw <= img.width && sy + sh <= img.height);
      console.log('[DevLog] Screenshot data URL length:', pendingScreenshot.length);

      // Auto-save: screenshot button now means "capture + save"
      if (selectedText) {
        console.log('[DevLog] Auto-saving with screenshot. Text:', selectedText.slice(0, 40));
        doSave('', 'web');
      } else {
        showToast('📷 Screenshot ready — re-select text to save', 'ok');
      }
    };
    img.onerror = () => showToast('❌ Failed to process screenshot', 'error');
    img.src = dataUrl;
  }

  /* ── Save ── */
  async function doSave(note, tag) {
    showToast('⏳ Saving…', 'info');

    const payload = {
      text: selectedText,
      note: note || '',
      tag: tag || 'web',
      url: location.href,
      title: document.title,
      screenshot: pendingScreenshot,
    };

    console.log('[DevLog] doSave called. Text length:', selectedText.length, 'Screenshot:', pendingScreenshot ? pendingScreenshot.length : 0);

    try {
      const res = await fetch(`${SERVER}/highlight`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`Server ${res.status}: ${txt}`);
      }

      const data = await res.json();
      console.log('[DevLog] Server response:', data);

      if (data.status !== 'ok') {
        showToast('❌ ' + (data.message || 'Server error'), 'error');
        return;
      }

      await persistHighlight(selectedText);
      findAndHighlight(selectedText);

      const hadScreenshot = !!pendingScreenshot;
      pendingScreenshot = null;

      if (hadScreenshot) {
        showToast('✅ Saved with screenshot', 'ok');
      } else {
        showToast('✅ Saved to DevLog', 'ok');
      }
      hideTimer = setTimeout(removeToolbar, 900);
    } catch (err) {
      if (err.message.includes('fetch') || err.message.includes('Failed')) {
        showToast('❌ Server offline — run start-server.bat', 'error');
      } else {
        showToast('❌ ' + err.message, 'error');
      }
      console.error('[DevLog] Save failed:', err);
    }
  }

  function doHighlightSave() {
    doSave('', 'web');
  }

  function doCopy() {
    navigator.clipboard.writeText(selectedText).then(() => {
      showToast('📋 Copied to clipboard', 'ok');
      hideTimer = setTimeout(removeToolbar, 600);
    });
  }

  function showToast(msg, type) {
    const existing = document.getElementById('dl-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'dl-toast';
    toast.textContent = msg;

    const color = type === 'ok' ? '#a6e3a1' : type === 'error' ? '#f38ba8' : '#89b4fa';
    toast.style.cssText = `
      position: fixed;
      bottom: 28px;
      right: 28px;
      z-index: 2147483647;
      background: #1e1e2e;
      color: ${color};
      padding: 12px 18px;
      border-radius: 10px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 14px;
      font-weight: 500;
      border: 1px solid #313244;
      box-shadow: 0 8px 32px rgba(0,0,0,0.45);
      pointer-events: none;
      animation: dl-slide-up 0.18s ease-out;
      max-width: 320px;
      line-height: 1.4;
    `;
    document.body.appendChild(toast);

    setTimeout(() => {
      if (toast.parentNode) toast.remove();
    }, type === 'error' ? 4000 : 2200);
  }

  /* ── Highlight engine ── */
  function findAndHighlight(text) {
    if (!text) return false;
    if (document.querySelector(`span[data-dl-text="${CSS.escape(text)}"]`)) return true;

    const found = window.find(text, false, false, true, false, true, false);
    if (!found) {
      console.log('[DevLog] window.find returned false for:', text.slice(0, 60));
      return false;
    }

    const sel = window.getSelection();
    if (!sel.rangeCount) {
      console.log('[DevLog] window.find succeeded but no range');
      return false;
    }

    const range = sel.getRangeAt(0);
    const span = document.createElement('span');
    span.className = HL_CLASS;
    span.dataset.dlText = text;
    span.title = 'Double-click or click ✕ to remove';

    try {
      range.surroundContents(span);
      attachRemoveHandler(span);
      sel.removeAllRanges();
      return true;
    } catch (e) {
      try {
        const frag = range.extractContents();
        span.appendChild(frag);
        range.insertNode(span);
        attachRemoveHandler(span);
        sel.removeAllRanges();
        return true;
      } catch (e2) {
        console.log('[DevLog] Both surroundContents & insertNode failed:', e2.message);
        sel.removeAllRanges();
        return false;
      }
    }
  }

  function attachRemoveHandler(span) {
    // 双击删除（保留向后兼容）
    span.addEventListener('dblclick', async (e) => {
      e.stopPropagation();
      e.preventDefault();
      hideRemoveBtn(); // 如果悬停按钮正显示，一并清理
      await removeHighlight(span);
    });

    // 悬停显示删除按钮
    let removeBtn = null;

    span.addEventListener('mouseenter', () => {
      if (removeBtn) {
        if (removeBtn._hideTimer) clearTimeout(removeBtn._hideTimer);
        return;
      }

      const rects = span.getClientRects();
      if (!rects.length) return;

      const firstLine = rects[0];
      removeBtn = document.createElement('button');
      removeBtn.className = 'dl-hl-remove-btn';
      removeBtn.textContent = '✕';
      removeBtn.title = 'Remove highlight';
      removeBtn.style.cssText = `
        position: fixed;
        left: ${Math.min(firstLine.right + 4, window.innerWidth - 26)}px;
        top: ${Math.max(firstLine.top - 10, 4)}px;
        width: 20px;
        height: 20px;
        padding: 0;
        margin: 0;
        background: #ef4444;
        color: #fff;
        border: none;
        border-radius: 50%;
        font-size: 11px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        line-height: 20px;
        text-align: center;
        cursor: pointer;
        z-index: 2147483640;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
        opacity: 0;
        transition: opacity 0.15s ease;
        pointer-events: auto;
        user-select: none;
      `;
      document.body.appendChild(removeBtn);
      requestAnimationFrame(() => { if (removeBtn) removeBtn.style.opacity = '1'; });

      removeBtn._hideTimer = null;

      removeBtn.addEventListener('mouseenter', () => {
        if (removeBtn && removeBtn._hideTimer) clearTimeout(removeBtn._hideTimer);
      });

      removeBtn.addEventListener('mouseleave', () => {
        if (!removeBtn) return;
        removeBtn._hideTimer = setTimeout(() => {
          if (removeBtn) hideRemoveBtn();
        }, 100);
      });

      removeBtn.addEventListener('click', async (ev) => {
        ev.stopPropagation();
        ev.preventDefault();
        const btn = removeBtn;
        removeBtn = null;
        if (btn && btn.parentNode) {
          btn.style.opacity = '0';
          setTimeout(() => btn.remove(), 150);
        }
        await removeHighlight(span);
      });
    });

    const hideRemoveBtn = () => {
      if (!removeBtn) return;
      removeBtn.style.opacity = '0';
      setTimeout(() => {
        if (removeBtn && removeBtn.parentNode) removeBtn.remove();
        removeBtn = null;
      }, 150);
    };

    span.addEventListener('mouseleave', () => {
      if (!removeBtn) return;
      removeBtn._hideTimer = setTimeout(() => {
        if (removeBtn) hideRemoveBtn();
      }, 250);
    });
  }

  async function removeHighlight(span) {
    const text = span.dataset.dlText;
    if (!text) return;

    await removePersistedHighlight(text);

    // Unwrap: move children before span to preserve nested structure
    const parent = span.parentNode;
    if (parent) {
      while (span.firstChild) {
        parent.insertBefore(span.firstChild, span);
      }
      parent.removeChild(span);
      parent.normalize();
    }

    showToast('🗑️ Highlight removed', 'info');
  }

  /* ── Persistence ── */
  async function persistHighlight(text) {
    const key = STORAGE_KEY(location.href);
    const data = await chrome.storage.local.get(key);
    const list = data[key] || [];
    if (!list.some(h => h.text === text)) {
      list.push({ text, timestamp: Date.now() });
      await chrome.storage.local.set({ [key]: list });
      console.log('[DevLog] Persisted highlight. Key:', key, 'Count:', list.length);
    }
  }

  async function removePersistedHighlight(text) {
    const key = STORAGE_KEY(location.href);
    const data = await chrome.storage.local.get(key);
    const list = (data[key] || []).filter(h => h.text !== text);
    await chrome.storage.local.set({ [key]: list });
    console.log('[DevLog] Removed highlight. Key:', key, 'Count:', list.length);
  }

  async function restoreHighlights() {
    const key = STORAGE_KEY(location.href);
    const data = await chrome.storage.local.get(key);
    const list = data[key] || [];
    console.log('[DevLog] Restoring', list.length, 'highlights for key:', key);
    let success = 0;
    for (const h of list) {
      if (findAndHighlight(h.text)) success++;
      else console.log('[DevLog] Failed to highlight:', h.text.slice(0, 80));
    }
    console.log('[DevLog] Restored', success, '/', list.length);
  }

  /* ── Event wiring ── */
  document.addEventListener('mouseup', (e) => {
    if (e.target.closest && e.target.closest('#dl-toolbar')) return;
    if (e.target.closest && e.target.closest('#dl-screenshot-overlay')) return;
    mouseX = e.clientX;
    mouseY = e.clientY;
    const text = window.getSelection().toString().trim();
    if (!text) { removeToolbar(); return; }
    setTimeout(() => showToolbar(), 60);
  });

  window.addEventListener('scroll', removeToolbar, { passive: true });
  window.addEventListener('resize', removeToolbar);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') removeToolbar(); });

  /* ── Restore on load (with retry for dynamic content) ── */
  function initRestore() {
    restoreHighlights();
    setTimeout(restoreHighlights, 2000);
    setTimeout(restoreHighlights, 5000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRestore);
  } else {
    initRestore();
  }

  console.log('DevLog Highlighter v10 — highlight removal with hover button');
})();
