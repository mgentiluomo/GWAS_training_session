(() => {
  'use strict';
  const pages = [...document.querySelectorAll('[data-page]')];
  const nav = [...document.querySelectorAll('.nav-link')];
  const rail = document.querySelector('.rail');
  const main = document.querySelector('main');
  function navigate() {
    const hash = location.hash.slice(1) || 'home';
    if (hash === 'main-content') { main.focus({preventScroll: true}); return; }
    const target = document.getElementById(hash);
    const page = target?.closest('[data-page]') || document.querySelector('[data-page="home"]');
    pages.forEach(p => { p.hidden = p !== page; });
    nav.forEach(link => {
      if (link.hash === '#' + page.id) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    document.title = page.dataset.title + ' · GWAS Practical Tutorial';
    rail.classList.remove('open');
    document.querySelector('.menu-button').setAttribute('aria-expanded', 'false');
    if (target && target !== page) target.scrollIntoView({block: 'start'});
    else window.scrollTo({top: 0, behavior: 'instant'});
    main.focus({preventScroll: true});
  }
  window.addEventListener('hashchange', navigate);
  navigate();
  rail.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    rail.classList.remove('open');
    document.querySelector('.menu-button').setAttribute('aria-expanded', 'false');
  }));
  document.querySelector('.menu-button').addEventListener('click', e => {
    const open = rail.classList.toggle('open');
    e.currentTarget.setAttribute('aria-expanded', String(open));
    if (open) rail.querySelector('a').focus();
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      const wasOpen = rail.classList.contains('open');
      rail.classList.remove('open');
      document.querySelector('.menu-button').setAttribute('aria-expanded', 'false');
      if (wasOpen) document.querySelector('.menu-button').focus();
    }
  });
  document.addEventListener('click', e => {
    if (rail.classList.contains('open') && !rail.contains(e.target) && !e.target.closest('.menu-button')) {
      rail.classList.remove('open');
      document.querySelector('.menu-button').setAttribute('aria-expanded', 'false');
    }
  });
  function toast(message) {
    const el = document.getElementById('toast');
    el.textContent = message;
    el.hidden = false;
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => { el.hidden = true; }, 3000);
  }
  document.querySelectorAll('.copy-button').forEach(button => {
    button.addEventListener('click', async () => {
      const code = button.parentElement.querySelector('code');
      try {
        await navigator.clipboard.writeText(code.textContent);
        toast('Code copied. Paste it into the indicated RStudio chunk or console.');
      } catch {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(code);
        selection.removeAllRanges();
        selection.addRange(range);
        toast('Code selected. Use your system’s Copy command.');
      }
    });
  });
  document.querySelectorAll('[data-os]').forEach(button => {
    button.addEventListener('click', () => {
      document.querySelectorAll('[data-os]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
      document.querySelectorAll('[data-os-panel]').forEach(p => { p.hidden = p.dataset.osPanel !== button.dataset.os; });
    });
  });
  document.querySelectorAll('[data-os-panel]').forEach(panel => {
    panel.hidden = panel.dataset.osPanel !== 'windows';
  });
  const slider = document.getElementById('missingness-threshold');
  if (slider) {
    const data = JSON.parse(document.getElementById('sample-missingness-data').textContent);
    function update() {
      const threshold = Number(slider.value) / 100;
      const removed = data.filter(v => v > threshold).length;
      document.getElementById('threshold-label').textContent = Number(slider.value).toFixed(0) + '%';
      slider.setAttribute('aria-valuetext', Number(slider.value).toFixed(0) + ' percent missing');
      document.getElementById('retained-count').textContent = String(data.length - removed);
      document.getElementById('excluded-count').textContent = String(removed);
    }
    slider.addEventListener('input', update);
    update();
  }
  document.querySelectorAll('[data-quiz]').forEach(form => {
    form.querySelector('button').addEventListener('click', e => {
      e.preventDefault();
      const choice = form.querySelector('input:checked');
      const feedback = form.querySelector('.feedback');
      if (!choice) { feedback.textContent = 'Choose one answer, then check it.'; return; }
      const correct = choice.value === form.dataset.correct;
      feedback.textContent = (correct ? 'Yes. ' : 'Try the reasoning again. ') + form.dataset.explanation;
      feedback.className = 'feedback ' + (correct ? 'check' : 'warning');
    });
  });
  const checklist = [...document.querySelectorAll('[data-progress]')];
  const progressKey = 'gwas-tutorial-qc-progress-v1';
  let storageAvailable = true;
  try {
    const stored = JSON.parse(localStorage.getItem(progressKey) || '{}');
    checklist.forEach(box => { box.checked = stored[box.dataset.progress] === true; });
  } catch { storageAvailable = false; }
  function progress() {
    const done = checklist.filter(b => b.checked).length;
    document.getElementById('progress-text').textContent = done + ' of ' + checklist.length + ' checks completed';
    document.querySelector('.progress-bar').style.width = (100 * done / checklist.length) + '%';
    if (storageAvailable) {
      try { localStorage.setItem(progressKey, JSON.stringify(Object.fromEntries(checklist.map(b => [b.dataset.progress, b.checked])))); }
      catch { storageAvailable = false; }
    }
    document.getElementById('progress-note').textContent = storageAvailable
      ? 'Checklist ticks stay in this browser. No student account or submission.'
      : 'Checklist ticks last for this visit; browser storage is unavailable.';
  }
  checklist.forEach(box => box.addEventListener('change', progress));
  document.getElementById('reset-progress').addEventListener('click', () => {
    checklist.forEach(box => { box.checked = false; });
    progress();
    toast('Checklist reset.');
  });
  progress();
})();
