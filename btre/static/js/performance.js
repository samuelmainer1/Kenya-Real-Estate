// Lazy Loading Implementation
document.addEventListener('DOMContentLoaded', function() {
  // Intersection Observer for lazy loading
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.add('loaded');
        observer.unobserve(img);
      }
    });
  }, {
    rootMargin: '50px 0px',
    threshold: 0.01
  });

  // Observe all lazy images
  document.querySelectorAll('.lazy-image').forEach(img => {
    imageObserver.observe(img);
  });

  // Preload critical images
  const criticalImages = document.querySelectorAll('[data-preload="true"]');
  criticalImages.forEach(img => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'image';
    link.href = img.dataset.src || img.src;
    document.head.appendChild(link);
  });
});

// Debounced scroll handler
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Optimized scroll events
const handleScroll = debounce(() => {
  // Your scroll logic here
}, 16); // ~60fps

window.addEventListener('scroll', handleScroll, { passive: true });
