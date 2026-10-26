'use strict';
/**
 * Control Centre sidebar behaviour.
 *
 * Django's stock `nav_sidebar.js` hides the sidebar until JS adds `.shifted`,
 * so a JS error or a slow script would leave the owner with no navigation.
 * This controller replaces that: `admin-control.css` shows the panel by default
 * and this file only *collapses* it, remembering the choice per browser.
 *
 * Responsibilities:
 *  - desktop: remember open/collapsed state (`html.kc-nav-collapsed`)
 *  - desktop: remember which sections are expanded (`kc.navGroup.<title>`)
 *  - mobile: off-canvas drawer with scrim, Escape and link-click to close
 *  - search: filter menu items by label
 */
(function () {
  const STORAGE_COLLAPSED = 'kc.navCollapsed';
  const STORAGE_GROUP = 'kc.navGroup.';
  const MOBILE = window.matchMedia('(max-width: 767px)');

  const html = document.documentElement;
  const body = document.body;
  const sidebar = document.getElementById('kc-sidebar');
  const toggle = document.getElementById('kc-nav-toggle');
  const filter = document.getElementById('kc-nav-filter');
  const emptyMessage = document.getElementById('kc-nav-empty');
  const scrollArea = document.getElementById('kc-sidebar-scroll');

  const groups = () => Array.from(document.querySelectorAll('.kc-nav-group[data-kc-group]'));

  function readStore(key) {
    try {
      return localStorage.getItem(key);
    } catch (e) {
      return null; // private mode / storage disabled
    }
  }

  function writeStore(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (e) {
      /* storage unavailable - the toggle still works for this page */
    }
  }

  /* ---------- Restore state ---------- */

  function restoreCollapsed() {
    html.classList.toggle('kc-nav-collapsed', readStore(STORAGE_COLLAPSED) === 'true');
    updateToggleLabel();
  }

  function restoreGroups() {
    groups().forEach((group) => {
      const key = group.getAttribute('data-kc-group');
      const stored = readStore(STORAGE_GROUP + key);
      if (stored === 'open') {
        group.open = true;
      } else if (stored === 'closed') {
        group.open = false;
      }
      // No stored value: keep the server's choice (the current section opens).
      group.addEventListener('toggle', () => {
        writeStore(STORAGE_GROUP + key, group.open ? 'open' : 'closed');
      });
    });
  }

  /* ---------- Toggle ---------- */

  function navIsCollapsed() {
    return html.classList.contains('kc-nav-collapsed');
  }

  function updateToggleLabel() {
    if (!toggle) return;
    const drawerOpen = body.classList.contains('kc-nav-open');
    toggle.setAttribute('aria-expanded', String(MOBILE.matches ? drawerOpen : !navIsCollapsed()));
  }

  function closeDrawer() {
    body.classList.remove('kc-nav-open');
    updateToggleLabel();
  }

  function openDrawer() {
    body.classList.add('kc-nav-open');
    updateToggleLabel();
    if (filter) filter.focus({ preventScroll: true });
  }

  if (toggle) {
    toggle.addEventListener('click', () => {
      if (MOBILE.matches) {
        if (body.classList.contains('kc-nav-open')) {
          closeDrawer();
        } else {
          openDrawer();
        }
        return;
      }
      const collapsed = !navIsCollapsed();
      html.classList.toggle('kc-nav-collapsed', collapsed);
      writeStore(STORAGE_COLLAPSED, String(collapsed));
      updateToggleLabel();
    });
  }

  /* Scrim: click anywhere outside the drawer to close it. */
  const scrim = document.createElement('button');
  scrim.type = 'button';
  scrim.className = 'kc-nav-scrim';
  scrim.setAttribute('aria-label', 'Close navigation');
  scrim.addEventListener('click', closeDrawer);
  body.appendChild(scrim);

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && body.classList.contains('kc-nav-open')) {
      closeDrawer();
    }
  });

  if (sidebar) {
    // Following a link on mobile should close the drawer behind you.
    sidebar.addEventListener('click', (event) => {
      if (event.target.closest('a') && MOBILE.matches) {
        closeDrawer();
      }
    });
  }

  MOBILE.addEventListener('change', () => {
    closeDrawer();
    updateToggleLabel();
  });

  /* ---------- Menu filter ---------- */

  function applyFilter(rawValue) {
    const value = (rawValue || '').trim().toLowerCase();
    let anyVisible = false;

    groups().forEach((group) => {
      const rows = Array.from(group.querySelectorAll('.kc-nav-link-row'));
      let groupHasMatch = false;

      rows.forEach((row) => {
        const link = row.querySelector('.kc-nav-link');
        const label = (link && link.getAttribute('data-kc-label')) || '';
        const match = !value || label.indexOf(value) !== -1;
        row.hidden = !match;
        if (match) groupHasMatch = true;
      });

      // Sub-labels ("Public pages", "Policies…") only make sense while the
      // links beneath them are still visible.
      group.querySelectorAll('.kc-nav-sublabel').forEach((subLabel) => {
        let next = subLabel.nextElementSibling;
        let hasVisibleLink = false;
        while (next && next.classList.contains('kc-nav-links')) {
          if (next.querySelector('.kc-nav-link-row:not([hidden])')) hasVisibleLink = true;
          next = next.nextElementSibling;
        }
        subLabel.hidden = Boolean(value) && !hasVisibleLink;
      });

      group.hidden = !groupHasMatch;
      if (groupHasMatch) anyVisible = true;

      if (value) {
        group.open = groupHasMatch; // reveal matches without extra clicks
      }
    });

    if (emptyMessage) emptyMessage.hidden = anyVisible;
  }

  if (filter) {
    filter.addEventListener('input', (event) => applyFilter(event.target.value));
    filter.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        event.target.value = '';
        applyFilter('');
      }
    });
  }

  /* ---------- Boot ---------- */

  restoreCollapsed();
  restoreGroups();
  updateToggleLabel();

  // Keep the active item in view on long menus (deep change forms would
  // otherwise open scrolled to the top of the list).
  const current = sidebar && sidebar.querySelector('.kc-nav-link-current');
  if (current && scrollArea) {
    const offset = current.getBoundingClientRect().top - scrollArea.getBoundingClientRect().top;
    if (offset > scrollArea.clientHeight - 40) {
      scrollArea.scrollTop += offset - scrollArea.clientHeight / 2;
    }
  }
})();
