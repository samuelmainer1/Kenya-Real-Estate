// Set current year safely
const yearElement = document.querySelector('.year');
if (yearElement) {
  const date = new Date();
  yearElement.innerHTML = date.getFullYear();
}

// Hide messages after 3 seconds
setTimeout(function() {
  const messageElement = document.getElementById('message');
  if (messageElement) {
    $('#message').fadeOut('slow');
  }
}, 3000);

// Initialize tooltips if Bootstrap is available
document.addEventListener('DOMContentLoaded', function() {
  if (typeof bootstrap !== 'undefined') {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }
});
