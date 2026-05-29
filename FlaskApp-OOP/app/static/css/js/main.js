(function () {
  'use strict';

  const STORAGE_KEY = 'expensex-theme';

  function getCsrfEase() {
    return CSS.supports('transition-timing-function', 'cubic-bezier(0.16,1,0.3,1)')
      ? 'cubic-bezier(0.16, 1, 0.3, 1)'
      : 'ease-out';
  }

  function replaceFeather() {
    if (typeof feather !== 'undefined') {
      feather.replace({ 'stroke-width': 1.5 });
    }
  }

  function syncThemeIcons() {
    const isLight = document.body.classList.contains('light');
    const darkIcon = document.getElementById('theme-icon-dark');
    const lightIcon = document.getElementById('theme-icon-light');
    if (darkIcon) darkIcon.style.display = isLight ? 'none' : '';
    if (lightIcon) lightIcon.style.display = isLight ? '' : 'none';
  }

  function initTheme() {
    const saved = localStorage.getItem(STORAGE_KEY);
    const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
    const theme = saved || (prefersLight ? 'light' : 'dark');
    document.body.classList.toggle('light', theme === 'light');
    const btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.setAttribute(
        'aria-label',
        theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'
      );
    }
    syncThemeIcons();
  }

  function toggleTheme() {
    const isLight = document.body.classList.toggle('light');
    localStorage.setItem(STORAGE_KEY, isLight ? 'light' : 'dark');
    syncThemeIcons();
    replaceFeather();
  }

  function initFab() {
    const fabBtn = document.getElementById('fab-btn');
    const fabMenu = document.getElementById('fab-menu');
    if (!fabBtn || !fabMenu) return;

    fabBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      fabBtn.classList.toggle('open');
      fabMenu.classList.toggle('open');
      replaceFeather();
    });

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.fab-container')) {
        fabBtn.classList.remove('open');
        fabMenu.classList.remove('open');
      }
    });
  }

  function initSidebar() {
    const toggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (!toggle || !sidebar) return;
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      replaceFeather();
    });
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 900 && sidebar.classList.contains('open')) {
        if (!e.target.closest('.sidebar') && !e.target.closest('#sidebar-toggle')) {
          sidebar.classList.remove('open');
        }
      }
    });
  }

  function initAlerts() {
    document.querySelectorAll('.flash-stack .alert, .alert-dismissible').forEach((el) => {
      setTimeout(() => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(-8px)';
        setTimeout(() => el.remove(), 300);
      }, 5000);
    });
  }

  function initLiveSearch() {
    const userInput = document.getElementById('user-search');
    const userTable = document.getElementById('users-table');
    if (userInput && userTable) {
      userInput.addEventListener('input', () => {
        const q = userInput.value.toLowerCase().trim();
        userTable.querySelectorAll('tbody tr').forEach((row) => {
          const text = (row.getAttribute('data-search') || row.textContent).toLowerCase();
          row.style.display = text.includes(q) ? '' : 'none';
        });
      });
      return;
    }

    const globalInput = document.getElementById('global-search');
    if (!globalInput) return;
    globalInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && globalInput.value.trim()) {
        const q = globalInput.value.trim().toLowerCase();
        document.querySelectorAll('table tbody tr').forEach((row) => {
          const match = row.textContent.toLowerCase().includes(q);
          row.style.background = match ? 'var(--brand-glow-sm)' : '';
        });
      }
    });
  }

  function initConfirmModal() {
    const modal = document.getElementById('confirm-modal');
    if (!modal) return;

    const msgEl = document.getElementById('confirm-msg');
    const okBtn = document.getElementById('confirm-ok');
    const cancelBtn = document.getElementById('confirm-cancel');
    const cancelX = document.getElementById('confirm-cancel-x');
    let pendingForm = null;

    function closeModal() {
      modal.hidden = true;
      pendingForm = null;
    }

    function openModal(message, form) {
      pendingForm = form;
      if (msgEl) msgEl.textContent = message;
      modal.hidden = false;
      replaceFeather();
    }

    document.querySelectorAll('form[data-confirm]').forEach((form) => {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        openModal(form.getAttribute('data-confirm') || 'Are you sure?', form);
      });
    });

    document.querySelectorAll('form[onsubmit*="confirm"]').forEach((form) => {
      const attr = form.getAttribute('onsubmit') || '';
      const match = attr.match(/confirm\(['"](.+?)['"]\)/);
      if (!match) return;
      form.removeAttribute('onsubmit');
      form.setAttribute('data-confirm', match[1]);
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        openModal(match[1], form);
      });
    });

    if (okBtn) {
      okBtn.addEventListener('click', () => {
        if (pendingForm) pendingForm.submit();
        closeModal();
      });
    }
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
    if (cancelX) cancelX.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });
  }

  window.drawSparkline = function (svgEl, data, color) {
    if (!svgEl || !data || data.length < 2) return;
    svgEl.innerHTML = '';
    const w = 72;
    const h = 28;
    const pad = 2;
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    const pts = data.map((v, i) => {
      const x = pad + (i / (data.length - 1)) * (w - pad * 2);
      const y = h - pad - ((v - min) / range) * (h - pad * 2);
      return `${x},${y}`;
    });
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', `M${pts.join('L')}`);
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', color);
    path.setAttribute('stroke-width', '1.5');
    path.setAttribute('stroke-linecap', 'round');
    path.setAttribute('stroke-linejoin', 'round');
    const len = path.getTotalLength();
    path.style.strokeDasharray = len;
    path.style.strokeDashoffset = len;
    path.style.transition = `stroke-dashoffset 1s ${getCsrfEase()} 0.3s`;
    svgEl.appendChild(path);
    requestAnimationFrame(() => {
      path.style.strokeDashoffset = '0';
    });
  };

  window.animateHealthScore = function (score) {
    const arc = document.getElementById('health-fill');
    const txt = document.getElementById('health-score-text');
    if (!arc || !txt) return;
    const total = 157;
    const color =
      score >= 70 ? 'var(--income)' : score >= 40 ? 'var(--warning)' : 'var(--expense)';
    arc.setAttribute('stroke', color);
    let current = 0;
    const step = () => {
      current = Math.min(current + 2, score);
      txt.textContent = current;
      arc.setAttribute('stroke-dasharray', `${(current / 100) * total} ${total}`);
      if (current < score) requestAnimationFrame(step);
    };
    setTimeout(() => requestAnimationFrame(step), 400);
  };

  window.initDashboardSparklines = function (config) {
    if (!config) return;
    const colors = {
      income:
        getComputedStyle(document.documentElement).getPropertyValue('--income').trim() ||
        '#0BC990',
      expense:
        getComputedStyle(document.documentElement).getPropertyValue('--expense').trim() ||
        '#F5476A',
      balance:
        getComputedStyle(document.documentElement).getPropertyValue('--brand').trim() ||
        '#4F7EFF',
      streak:
        getComputedStyle(document.documentElement).getPropertyValue('--warning').trim() ||
        '#F5A623',
    };
    Object.keys(config).forEach((key) => {
      const el = document.querySelector(`.sparkline[data-key="${key}"]`);
      if (el) drawSparkline(el, config[key], colors[key] || colors.balance);
    });
    replaceFeather();
  };

  window.initHealthScore = function (score) {
    animateHealthScore(score);
    replaceFeather();
  };

  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initFab();
    initSidebar();
    initAlerts();
    initLiveSearch();
    initConfirmModal();
    replaceFeather();

    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
      themeBtn.addEventListener('click', toggleTheme);
    }
  });
})();