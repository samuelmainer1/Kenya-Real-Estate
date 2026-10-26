// Cookie Consent Management
class CookieConsent {
  constructor() {
    this.cookieName = 'kenya-realestate-platform_cookie_consent';
    this.cookieExpiry = 365; // days
    this.init();
  }

  init() {
    // Check if user has already made a choice
    if (!this.getCookie(this.cookieName)) {
      this.showBanner();
    } else {
      this.loadUserPreferences();
    }

    this.bindEvents();
  }

  showBanner() {
    const banner = document.getElementById('cookie-consent-banner');
    if (banner) {
      banner.style.display = 'block';
    }
  }

  hideBanner() {
    const banner = document.getElementById('cookie-consent-banner');
    if (banner) {
      banner.style.display = 'none';
    }
  }

  bindEvents() {
    // Accept All button
    const acceptAllBtn = document.getElementById('cookie-accept-all');
    if (acceptAllBtn) {
      acceptAllBtn.addEventListener('click', () => {
        this.acceptAll();
      });
    }

    // Necessary Only button
    const necessaryBtn = document.getElementById('cookie-accept-necessary');
    if (necessaryBtn) {
      necessaryBtn.addEventListener('click', () => {
        this.acceptNecessaryOnly();
      });
    }

    // Settings button
    const settingsBtn = document.getElementById('cookie-settings');
    if (settingsBtn) {
      settingsBtn.addEventListener('click', () => {
        this.showSettings();
      });
    }

    // Modal close button
    const closeBtn = document.getElementById('cookie-modal-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        this.hideSettings();
      });
    }

    // Save settings button
    const saveBtn = document.getElementById('cookie-save-settings');
    if (saveBtn) {
      saveBtn.addEventListener('click', () => {
        this.saveCustomSettings();
      });
    }

    // Close modal when clicking outside
    const modal = document.getElementById('cookie-settings-modal');
    if (modal) {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          this.hideSettings();
        }
      });
    }
  }

  acceptAll() {
    const preferences = {
      necessary: true,
      analytics: true,
      marketing: true,
      timestamp: Date.now()
    };
    
    this.setCookie(this.cookieName, JSON.stringify(preferences), this.cookieExpiry);
    this.hideBanner();
    this.loadAnalytics();
    this.loadMarketing();
    this.showNotification('All cookies accepted');
  }

  acceptNecessaryOnly() {
    const preferences = {
      necessary: true,
      analytics: false,
      marketing: false,
      timestamp: Date.now()
    };
    
    this.setCookie(this.cookieName, JSON.stringify(preferences), this.cookieExpiry);
    this.hideBanner();
    this.showNotification('Only necessary cookies accepted');
  }

  showSettings() {
    const modal = document.getElementById('cookie-settings-modal');
    if (modal) {
      // Load current preferences
      const preferences = this.getUserPreferences();
      document.getElementById('analytics-cookies').checked = preferences.analytics;
      document.getElementById('marketing-cookies').checked = preferences.marketing;
      
      modal.style.display = 'flex';
    }
  }

  hideSettings() {
    const modal = document.getElementById('cookie-settings-modal');
    if (modal) {
      modal.style.display = 'none';
    }
  }

  saveCustomSettings() {
    const preferences = {
      necessary: true,
      analytics: document.getElementById('analytics-cookies').checked,
      marketing: document.getElementById('marketing-cookies').checked,
      timestamp: Date.now()
    };
    
    this.setCookie(this.cookieName, JSON.stringify(preferences), this.cookieExpiry);
    this.hideBanner();
    this.hideSettings();
    
    // Load/unload scripts based on preferences
    if (preferences.analytics) {
      this.loadAnalytics();
    }
    if (preferences.marketing) {
      this.loadMarketing();
    }
    
    this.showNotification('Cookie preferences saved');
  }

  loadUserPreferences() {
    const preferences = this.getUserPreferences();
    
    if (preferences.analytics) {
      this.loadAnalytics();
    }
    if (preferences.marketing) {
      this.loadMarketing();
    }
  }

  getUserPreferences() {
    const cookie = this.getCookie(this.cookieName);
    if (cookie) {
      try {
        return JSON.parse(cookie);
      } catch (e) {
        return { necessary: true, analytics: false, marketing: false };
      }
    }
    return { necessary: true, analytics: false, marketing: false };
  }

  loadAnalytics() {
    // Load Google Analytics if not already loaded
    if (typeof gtag === 'undefined' && window.GA_MEASUREMENT_ID) {
      const script = document.createElement('script');
      script.async = true;
      script.src = `https://www.googletagmanager.com/gtag/js?id=${window.GA_MEASUREMENT_ID}`;
      document.head.appendChild(script);

      script.onload = () => {
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', window.GA_MEASUREMENT_ID);
      };
    }
  }

  loadMarketing() {
    // Load Facebook Pixel if not already loaded
    if (typeof fbq === 'undefined' && window.FB_PIXEL_ID) {
      !function(f,b,e,v,n,t,s)
      {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
      n.callMethod.apply(n,arguments):n.queue.push(arguments)};
      if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
      n.queue=[];t=b.createElement(e);t.async=!0;
      t.src=v;s=b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t,s)}(window, document,'script',
      'https://connect.facebook.net/en_US/fbevents.js');
      fbq('init', window.FB_PIXEL_ID);
      fbq('track', 'PageView');
    }
  }

  setCookie(name, value, days) {
    const expires = new Date();
    expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
  }

  getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  }

  showNotification(message) {
    // Create a simple notification
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #30caa0;
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      z-index: 10001;
      animation: slideInRight 0.3s ease-out;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.remove();
    }, 3000);
  }
}

// Initialize cookie consent when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new CookieConsent();
});

// Add CSS for notification animation
const style = document.createElement('style');
style.textContent = `
  @keyframes slideInRight {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
`;
document.head.appendChild(style);