(() => {
  const menuButton = document.querySelector('.menu-button');
  const nav = document.querySelector('.global-nav');
  const closeMenu = () => {
    if (!menuButton || !nav) return;
    nav.classList.remove('open');
    menuButton.setAttribute('aria-expanded', 'false');
  };

  if (menuButton && nav) {
    menuButton.addEventListener('click', () => {
      const isOpen = nav.classList.toggle('open');
      menuButton.setAttribute('aria-expanded', String(isOpen));
    });
    nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeMenu();
    });
  }

  const mobileBar = document.querySelector('.mobile-line-bar');
  const heroLineButton = document.querySelector('.hero-actions .button-line');
  if (mobileBar && heroLineButton && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(([entry]) => {
      mobileBar.classList.toggle('is-hidden', entry.isIntersecting);
    }, { threshold: 0.35 });
    observer.observe(heroLineButton);
  }

  const filterButtons = document.querySelectorAll('[data-work-filter]');
  const workCards = document.querySelectorAll('[data-work-category]');

  filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const filter = button.dataset.workFilter;
      filterButtons.forEach((item) => {
        const active = item === button;
        item.classList.toggle('is-active', active);
        item.setAttribute('aria-pressed', String(active));
      });
      workCards.forEach((card) => {
        const categories = (card.dataset.workCategory || '').split(' ');
        card.classList.toggle('is-hidden', filter !== 'all' && !categories.includes(filter));
      });
    });
  });
})();
