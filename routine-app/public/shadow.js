/**
 * Shadow Protocol — client logic
 *
 * Fixes vs the old inline version:
 *  - API is same-origin ('/api'), so it works when opened over Tailscale from
 *    any device. (The old 'http://localhost:3001' pointed at whatever device
 *    you opened the page on — your phone, not the Spark.)
 *  - No inline event handlers, so it works under a strict Content-Security-Policy.
 */
(function () {
  'use strict';

  const API_BASE = '/api';
  const API_TOKEN = 'local_tailnet_token';

  async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
      method,
      headers: { 
        'X-API-Token': `${API_TOKEN}`,
        'Content-Type': 'application/json' 
      }
    };
    if (body) options.body = JSON.stringify(body);
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, options);
      if (res.status === 401) { window.location.href = '/'; return null; }
      return await res.json();
    } catch (e) {
      console.error('API Error:', e);
      return null;
    }
  }

  // ── Teeter Totter ────────────────────────────────────────
  let tilt = 0;
  function adjustSeesaw(amount) {
    tilt = Math.max(-30, Math.min(30, tilt + amount));
    updateSeesawUI();
    apiCall('/shadow/balance', 'POST', { tilt_value: tilt });
  }
  function updateSeesawUI() {
    const board = document.getElementById('seesaw-board');
    const status = document.getElementById('seesaw-status');
    if (board) board.style.transform = `rotate(${tilt}deg)`;
    if (!status) return;
    if (tilt < -10) {
      status.textContent = '⚠️ Warning: Persona overload. Shadow weight accumulating.';
      status.style.color = '#ef4444';
    } else if (tilt > 10) {
      status.textContent = '⭐ Integration active. Tension is releasing.';
      status.style.color = '#5eead4';
    } else {
      status.textContent = 'Balance is neutral.';
      status.style.color = 'var(--aurora-teal)';
    }
  }

  // ── Journal ──────────────────────────────────────────────
  const prompts = [
    'What quality do I hate most in others right now? Do I possess it?',
    'What am I pretending not to need today?',
    "If I had no 'independent' image to maintain, what would I do differently?",
    'What would I scream right now if no one could hear?',
    "Where did I say 'I'm fine' today when I actually wasn't?"
  ];
  let promptIdx = 0;

  function rotatePrompt() {
    promptIdx = (promptIdx + 1) % prompts.length;
    const el = document.getElementById('journal-prompt');
    if (el) el.textContent = `"${prompts[promptIdx]}"`;
  }

  async function saveJournal() {
    const text = document.getElementById('shadow-journal').value;
    const msg = document.getElementById('journal-save-msg');
    if (msg) { msg.textContent = 'Syncing…'; msg.style.display = 'inline'; }
    await apiCall('/shadow/journal', 'POST', { prompt: prompts[promptIdx], entry_text: text });
    if (msg) { msg.textContent = 'Saved.'; setTimeout(() => { msg.style.display = 'none'; }, 2000); }
  }

  function clearJournal() {
    if (confirm('Clear current entry?')) {
      document.getElementById('shadow-journal').value = '';
    }
  }

  // ── 3-Chair Exercise ─────────────────────────────────────
  function switchChair(idx) {
    const tabs = document.querySelectorAll('.chair-tab');
    const contents = document.querySelectorAll('.chair-content');
    tabs.forEach(t => t.classList.remove('active'));
    contents.forEach(c => c.classList.remove('active'));
    if (tabs[idx]) tabs[idx].classList.add('active');
    if (contents[idx]) contents[idx].classList.add('active');
  }

  async function saveChairExercise() {
    const msg = document.getElementById('chair-save-msg');
    if (msg) { msg.textContent = 'Syncing…'; msg.style.display = 'inline'; }
    await apiCall('/shadow/chair', 'POST', {
      ego_text: document.getElementById('chair-0-text').value,
      shadow_text: document.getElementById('chair-1-text').value,
      self_text: document.getElementById('chair-2-text').value
    });
    if (msg) { msg.textContent = 'Saved.'; setTimeout(() => { msg.style.display = 'none'; }, 2000); }
  }

  // ── Wire up events (no inline handlers) ──────────────────
  function wire() {
    document.querySelectorAll('[data-action]').forEach(node => {
      const action = node.getAttribute('data-action');
      node.addEventListener('click', () => {
        switch (action) {
          case 'seesaw': adjustSeesaw(Number(node.getAttribute('data-amount')) || 0); break;
          case 'rotate-prompt': rotatePrompt(); break;
          case 'save-journal': saveJournal(); break;
          case 'clear-journal': clearJournal(); break;
          case 'chair': switchChair(Number(node.getAttribute('data-idx')) || 0); break;
          case 'save-chair': saveChairExercise(); break;
        }
      });
    });
  }

  // ── Boot: load saved state ───────────────────────────────
  async function boot() {
    wire();

    const bal = await apiCall('/shadow/balance');
    if (bal && typeof bal.tilt_value === 'number') { tilt = bal.tilt_value; updateSeesawUI(); }

    const journal = await apiCall('/shadow/journal');
    if (journal && journal.entry_text) {
      const ta = document.getElementById('shadow-journal');
      if (ta) ta.value = journal.entry_text;
      if (journal.prompt) {
        const idx = prompts.indexOf(String(journal.prompt).replace(/"/g, ''));
        if (idx !== -1) promptIdx = idx;
        const pe = document.getElementById('journal-prompt');
        if (pe) pe.textContent = `"${prompts[promptIdx]}"`;
      }
    }

    const chair = await apiCall('/shadow/chair');
    if (chair) {
      const map = { 'chair-0-text': chair.ego_text, 'chair-1-text': chair.shadow_text, 'chair-2-text': chair.self_text };
      for (const [id, val] of Object.entries(map)) {
        const el = document.getElementById(id);
        if (el && val) el.value = val;
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
