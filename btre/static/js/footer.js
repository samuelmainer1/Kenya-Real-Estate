// Footer Enhancement JavaScript
document.addEventListener('DOMContentLoaded', function() {
  
  // Newsletter form handling
  const newsletterForm = document.querySelector('.newsletter-form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const email = this.querySelector('.newsletter-input').value;
      
      // Show success message
      const btn = this.querySelector('.newsletter-btn');
      const originalText = btn.innerHTML;
      btn.innerHTML = '<i class="fas fa-check"></i> Subscribed!';
      btn.style.background = '#28b894';
      
      // Reset after 3 seconds
      setTimeout(() => {
        btn.innerHTML = originalText;
        btn.style.background = '';
        this.querySelector('.newsletter-input').value = '';
      }, 3000);
    });
  }

  // Smooth scroll for footer links
  const footerLinks = document.querySelectorAll('.footer-links-list a[href^="#"]');
  footerLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href').substring(1);
      const targetElement = document.getElementById(targetId);
      
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // Animate footer elements on scroll
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);

  // Observe footer sections
  const footerSections = document.querySelectorAll('.footer-links-section, .footer-brand-section, .footer-social-section');
  footerSections.forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(20px)';
    section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(section);
  });

  // Social media link hover effects
  const socialLinks = document.querySelectorAll('.footer-social-link');
  socialLinks.forEach(link => {
    link.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-3px) scale(1.1)';
    });
    
    link.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0) scale(1)';
    });
  });

  // Contact info hover effects
  const contactItems = document.querySelectorAll('.footer-contact-item');
  contactItems.forEach(item => {
    item.addEventListener('mouseenter', function() {
      this.style.transform = 'translateX(5px)';
      this.style.opacity = '1';
    });
    
    item.addEventListener('mouseleave', function() {
      this.style.transform = 'translateX(0)';
      this.style.opacity = '0.9';
    });
  });

  // Footer links hover effects
  const footerLinkItems = document.querySelectorAll('.footer-links-list a');
  footerLinkItems.forEach(link => {
    link.addEventListener('mouseenter', function() {
      const icon = this.querySelector('i');
      if (icon) {
        icon.style.transform = 'scale(1.2) rotate(5deg)';
        icon.style.color = '#4dd4b0';
      }
    });
    
    link.addEventListener('mouseleave', function() {
      const icon = this.querySelector('i');
      if (icon) {
        icon.style.transform = 'scale(1) rotate(0deg)';
        icon.style.color = '#30caa0';
      }
    });
  });

  // Add current year to copyright
  const copyrightElement = document.querySelector('.footer-copyright');
  if (copyrightElement) {
    const currentYear = new Date().getFullYear();
    copyrightElement.innerHTML = copyrightElement.innerHTML.replace('{{ now|date:\'Y\' }}', currentYear);
  }

  // Newsletter input focus effects
  const newsletterInput = document.querySelector('.newsletter-input');
  if (newsletterInput) {
    newsletterInput.addEventListener('focus', function() {
      this.parentElement.style.transform = 'scale(1.02)';
    });
    
    newsletterInput.addEventListener('blur', function() {
      this.parentElement.style.transform = 'scale(1)';
    });
  }

  // Footer bottom links hover effects
  const bottomLinks = document.querySelectorAll('.footer-bottom-links a');
  bottomLinks.forEach(link => {
    link.addEventListener('mouseenter', function() {
      this.style.color = '#4dd4b0';
      this.style.textDecoration = 'underline';
    });
    
    link.addEventListener('mouseleave', function() {
      this.style.color = '';
      this.style.textDecoration = 'none';
    });
  });

  // Add loading animation for footer
  const footer = document.querySelector('.vincent-footer');
  if (footer) {
    footer.style.opacity = '0';
    footer.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
      footer.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
      footer.style.opacity = '1';
      footer.style.transform = 'translateY(0)';
    }, 100);
  }

  // Enhanced accessibility
  const allFooterLinks = document.querySelectorAll('.vincent-footer a');
  allFooterLinks.forEach(link => {
    // Add keyboard navigation support
    link.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.click();
      }
    });
    
    // Add focus indicators
    link.addEventListener('focus', function() {
      this.style.outline = '2px solid #30caa0';
      this.style.outlineOffset = '2px';
    });
    
    link.addEventListener('blur', function() {
      this.style.outline = 'none';
    });
  });

  // Newsletter form validation
  const emailInput = document.querySelector('.newsletter-input');
  if (emailInput) {
    emailInput.addEventListener('input', function() {
      const email = this.value;
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      
      if (email && !emailRegex.test(email)) {
        this.style.borderColor = '#e74c3c';
        this.style.boxShadow = '0 0 0 2px rgba(231, 76, 60, 0.2)';
      } else {
        this.style.borderColor = '';
        this.style.boxShadow = '';
      }
    });
  }

  console.log('Footer enhancement loaded successfully!');
}); 