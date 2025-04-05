// Show/hide scroll button based on page position
window.onscroll = function() {
  scrollFunction();
};

function scrollFunction() {
  const scrollBtn = document.getElementById("scrollBtn");
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    scrollBtn.style.display = "block";
  } else {
    scrollBtn.style.display = "none";
  }
}

// Toggle mobile menu
function myFunction() {
  const x = document.getElementById("navDemo");
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
  } else {
    x.className = x.className.replace(" w3-show", "");
  }
}

// Document ready function with modern approach
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('currentYear').textContent = new Date().getFullYear();
  // Smooth scrolling for internal links
  document.querySelectorAll('a[href*="#"]').forEach(anchor => {
    if (!anchor.getAttribute('href').startsWith('#') || anchor.getAttribute('href') === '#0') return;

    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href').substring(1);
      const targetElement = document.getElementById(targetId);

      if (targetElement) {
        e.preventDefault();
        window.scrollTo({
          top: targetElement.offsetTop,
          behavior: 'smooth'
        });
      }
    });
  });

  // Track outbound links
  document.querySelectorAll('a.track').forEach(link => {
    link.addEventListener('click', function(e) {
      const currentLink = this.href;
      ga('send', 'event', {
        eventCategory: 'Outbound Link',
        eventAction: 'click',
        eventLabel: currentLink,
        transport: 'beacon'
      });
    });
  });

  // Show loading indicator when forms are submitted
  const createForm = document.getElementById("create");
  if (createForm) {
    createForm.addEventListener('submit', function() {
      document.getElementById('loading').style.display = "block";
      document.getElementById("scrollBtn").click();
    });
  }

  const submitLoadForm = document.getElementById("submitLoad");
  if (submitLoadForm) {
    submitLoadForm.addEventListener('submit', function() {
      document.getElementById('loading').style.display = "block";
      document.getElementById("scrollBtn").click();
    });

    submitLoadForm.addEventListener('click', function() {
      document.getElementById('loading').style.display = "block";
      document.getElementById("scrollBtn").click();
    });
  }
});

// Initialize modal functionality when window loads
window.addEventListener('load', function() {
  // Modal elements
  const modal = document.getElementById('myModal');
  const categories = document.getElementById('id01');
  const btn = document.getElementById("myBtn");
  const span = document.querySelector(".close");
  const toogleBtn = document.getElementById('toogle');

  // Open modal when button is clicked
  if (btn) {
    btn.addEventListener('click', function() {
      modal.style.display = "block";
    });
  }

  // Close modal when X is clicked
  if (span) {
    span.addEventListener('click', function() {
      modal.style.display = "none";
    });
  }

  // Close modals when clicking outside
  window.addEventListener('click', function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
    if (event.target == categories) {
      categories.style.display = "none";
    }

    // Close mobile navigation when clicking outside
    const navDemo = document.getElementById("navDemo");
    if (navDemo && navDemo.className.indexOf("w3-show") !== -1) {
      navDemo.className = navDemo.className.replace(" w3-show", "");
    }
  });

  // Prevent navigation menu from closing when toggle button is clicked
  if (toogleBtn) {
    toogleBtn.addEventListener('click', function(event) {
      event.stopPropagation();
    });
  }
});