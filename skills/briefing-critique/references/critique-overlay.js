// Critique highlight overlay — add this to scripts/delayed.js
// Activated only when ?critique-section or ?critique-target query params are present.
// Zero production impact — the code exits immediately if no params are found.
//
// Supports three targeting modes:
//   ?critique-section=N        — highlights the Nth <main> .section (1-indexed)
//   ?critique-target=header    — highlights the <header> element
//   ?critique-target=footer    — highlights the <footer> element
//   ?critique-label=TEXT       — optional label shown as a tag on the highlighted element

(() => {
  const params = new URLSearchParams(window.location.search);
  const sectionIdx = params.get('critique-section');
  const critiqueTarget = params.get('critique-target');
  if (!sectionIdx && !critiqueTarget) return;

  let target;
  if (critiqueTarget === 'header') {
    target = document.querySelector('header');
  } else if (critiqueTarget === 'footer') {
    target = document.querySelector('footer');
  } else if (sectionIdx) {
    const sections = document.querySelectorAll('main > .section');
    target = sections[parseInt(sectionIdx, 10) - 1];
  }
  if (!target) return;

  const label = params.get('critique-label') || '';
  target.style.outline = '3px solid #c0392b';
  target.style.outlineOffset = '-3px';
  target.style.background = 'rgba(192,57,43,0.06)';
  target.style.position = 'relative';
  if (label) {
    const tag = document.createElement('div');
    tag.textContent = label;
    Object.assign(tag.style, {
      position: 'absolute', top: '0', right: '0', background: '#c0392b', color: '#fff',
      fontSize: '12px', fontFamily: 'system-ui, sans-serif', fontWeight: '600',
      padding: '4px 10px', borderRadius: '0 0 0 6px', zIndex: '9999',
    });
    target.appendChild(tag);
  }
  target.scrollIntoView({ behavior: 'smooth', block: 'center' });
})();
