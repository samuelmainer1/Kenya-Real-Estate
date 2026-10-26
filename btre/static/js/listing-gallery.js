(function () {
  'use strict';

  function createModalController(modalEl) {
    if (typeof $ !== 'undefined' && $.fn.modal) {
      return {
        show: function () { $(modalEl).modal('show'); },
        hide: function () { $(modalEl).modal('hide'); }
      };
    }
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
      if (typeof bootstrap.Modal.getOrCreateInstance === 'function') {
        var bs5 = bootstrap.Modal.getOrCreateInstance(modalEl);
        return { show: function () { bs5.show(); }, hide: function () { bs5.hide(); } };
      }
      var bs4 = new bootstrap.Modal(modalEl);
      return { show: function () { bs4.show(); }, hide: function () { bs4.hide(); } };
    }
    return null;
  }

  function collectImages() {
    var urls = [];
    var seen = {};

    document.querySelectorAll('.listing-thumbnail img').forEach(function (img) {
      if (img.src && !seen[img.src]) {
        seen[img.src] = true;
        urls.push(img.src);
      }
    });

    var mainImage = document.getElementById('mainImage');
    if (mainImage && mainImage.src && !seen[mainImage.src]) {
      urls.unshift(mainImage.src);
    }

    if (!urls.length) {
      var root = document.getElementById('listingGalleryData');
      if (root) {
        try {
          urls = JSON.parse(root.dataset.images || '[]');
        } catch (e) { /* ignore */ }
      }
    }

    return urls;
  }

  function initListingGallery() {
    var modalEl = document.getElementById('propertyGalleryModal');
    var root = document.getElementById('listingGalleryData');
    if (!modalEl) return;

    var images = collectImages();
    if (!images.length) return;

    var modal = createModalController(modalEl);
    if (!modal) return;

    var title = (root && root.dataset.title) ? root.dataset.title : 'Property photos';
    var currentIndex = 0;

    var imageEl = document.getElementById('propertyGalleryImage');
    var counterEl = document.getElementById('propertyGalleryCounter');
    var titleEl = document.getElementById('propertyGalleryTitle');
    var prevBtn = document.getElementById('propertyGalleryPrev');
    var nextBtn = document.getElementById('propertyGalleryNext');
    var closeBtn = document.getElementById('propertyGalleryClose');
    var mainImage = document.getElementById('mainImage');

    function render(index) {
      currentIndex = (index + images.length) % images.length;
      if (imageEl) {
        imageEl.src = images[currentIndex];
        imageEl.alt = title + ' – photo ' + (currentIndex + 1);
      }
      if (counterEl) {
        counterEl.textContent = (currentIndex + 1) + ' / ' + images.length;
      }
      if (titleEl) titleEl.textContent = title;

      document.querySelectorAll('.listing-thumbnail').forEach(function (thumb) {
        var img = thumb.querySelector('img');
        thumb.classList.toggle('active-thumb', img && img.src === images[currentIndex]);
      });
    }

    function openGallery(index) {
      var start = typeof index === 'number' ? index : 0;
      if (start < 0 || start >= images.length) start = 0;
      render(start);
      modal.show();
    }

    function setMainImage(src) {
      if (mainImage) mainImage.src = src;
      document.querySelectorAll('.listing-thumbnail').forEach(function (thumb) {
        var img = thumb.querySelector('img');
        thumb.classList.toggle('active-thumb', img && img.src === src);
      });
    }

    window.openPropertyGallery = openGallery;

    if (prevBtn) {
      prevBtn.addEventListener('click', function (e) {
        e.preventDefault();
        render(currentIndex - 1);
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', function (e) {
        e.preventDefault();
        render(currentIndex + 1);
      });
    }
    if (closeBtn) {
      closeBtn.addEventListener('click', function (e) {
        e.preventDefault();
        modal.hide();
      });
    }

    document.addEventListener('keydown', function (e) {
      if (!modalEl.classList.contains('show')) return;
      if (e.key === 'ArrowLeft') render(currentIndex - 1);
      if (e.key === 'ArrowRight') render(currentIndex + 1);
      if (e.key === 'Escape') modal.hide();
    });

    document.querySelectorAll('[data-gallery-open]').forEach(function (el) {
      function openFromEl() {
        var idx = 0;
        if (mainImage) {
          idx = images.indexOf(mainImage.src);
          if (idx < 0) idx = 0;
        }
        openGallery(idx);
      }
      el.addEventListener('click', function (e) {
        e.preventDefault();
        openFromEl();
      });
      el.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openFromEl();
        }
      });
    });

    document.querySelectorAll('.listing-thumbnail').forEach(function (thumb) {
      thumb.addEventListener('click', function (e) {
        e.preventDefault();
        var img = thumb.querySelector('img');
        if (!img) return;
        setMainImage(img.src);
        var idx = images.indexOf(img.src);
        openGallery(idx >= 0 ? idx : 0);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initListingGallery);
  } else {
    initListingGallery();
  }
})();
