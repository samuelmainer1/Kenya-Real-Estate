// Hero Carousel JavaScript
document.addEventListener('DOMContentLoaded', function() {
  const slides = document.querySelectorAll('.hero-slide');
  const indicators = document.querySelectorAll('.hero-indicator');
  let currentSlide = 0;
  const slideInterval = 5000; // 5 seconds

  function showSlide(index) {
    // Remove active class from all slides and indicators
    slides.forEach(slide => slide.classList.remove('active'));
    indicators.forEach(indicator => indicator.classList.remove('active'));
    
    // Add active class to current slide and indicator
    slides[index].classList.add('active');
    indicators[index].classList.add('active');
    
    currentSlide = index;
  }

  function nextSlide() {
    const next = (currentSlide + 1) % slides.length;
    showSlide(next);
  }

  // Auto-advance slides
  setInterval(nextSlide, slideInterval);

  // Manual navigation with indicators
  indicators.forEach((indicator, index) => {
    indicator.addEventListener('click', () => {
      showSlide(index);
    });
  });

  // Pause on hover
  const heroSection = document.querySelector('.premium-hero');
  let autoSlide = setInterval(nextSlide, slideInterval);

  heroSection.addEventListener('mouseenter', () => {
    clearInterval(autoSlide);
  });

  heroSection.addEventListener('mouseleave', () => {
    autoSlide = setInterval(nextSlide, slideInterval);
  });
});