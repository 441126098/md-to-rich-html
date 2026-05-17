(function () {
  // -- Theme toggle ---------------------------------------------------
  const root = document.documentElement;
  const btn = document.querySelector('.theme-toggle');
  const STORAGE_KEY = 'mdrh-theme';

  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) root.dataset.theme = saved;

  if (btn) {
    btn.addEventListener('click', function () {
      const current = root.dataset.theme;
      let next;
      if (current === 'light') next = 'dark';
      else if (current === 'dark') next = 'auto';
      else next = 'light';
      root.dataset.theme = next;
      localStorage.setItem(STORAGE_KEY, next);
    });
  }

  // -- Task checkbox persistence -------------------------------------
  // Each rendered HTML doc gets its own task state, keyed by a hash of
  // the document title so reloads remember progress.

  const titleEl = document.querySelector('.doc-title');
  const docKey = 'mdrh-tasks::' + (titleEl ? titleEl.textContent.trim() : 'doc');
  const stored = (function () {
    try { return JSON.parse(localStorage.getItem(docKey) || '{}'); }
    catch (e) { return {}; }
  })();

  const checkboxes = document.querySelectorAll('.task-list-item-checkbox');
  checkboxes.forEach(function (cb, i) {
    cb.disabled = false;
    if (stored[i] !== undefined) cb.checked = stored[i];

    cb.addEventListener('change', function () {
      stored[i] = cb.checked;
      localStorage.setItem(docKey, JSON.stringify(stored));
      updateProgress();
    });
  });

  function updateProgress() {
    const bar = document.querySelector('.tasks-progress-bar');
    const label = document.querySelector('.tasks-progress-label');
    if (!bar || !label) return;
    const total = checkboxes.length;
    if (!total) return;
    const done = Array.prototype.filter.call(checkboxes, function (c) { return c.checked; }).length;
    const pct = Math.round(100 * done / total);
    bar.style.width = pct + '%';
    const pctSpan = label.querySelector('.tasks-progress-pct');
    label.firstChild.nodeValue = ''; // wipe
    label.innerHTML = '<strong>' + done + '</strong> / ' + total + ' tasks ' +
                      '<span class="tasks-progress-pct">· ' + pct + '%</span>';
    const progEl = document.querySelector('.tasks-progress');
    if (progEl) progEl.setAttribute('aria-valuenow', pct);
  }
})();
