// Smooth scroll for "Get Started" button
function scrollToSection(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.scrollIntoView({ behavior: "smooth", block: "start" });
}

// Helper to highlight nav link based on scroll position
function setupActiveNav() {
  const sections = ["home", "about", "analysis"]
    .map((id) => document.getElementById(id))
    .filter(Boolean);

  const links = Array.from(document.querySelectorAll(".nav-links a"));

  function updateActive() {
    let best = null;
    let bestOffset = Infinity;

    sections.forEach((section) => {
      const rect = section.getBoundingClientRect();
      const offset = Math.abs(rect.top - 80); // account for navbar height
      if (offset < bestOffset) {
        bestOffset = offset;
        best = section;
      }
    });

    if (!best) return;
    const id = best.id;
    links.forEach((link) => {
      const href = link.getAttribute("href") || "";
      if (href === `#${id}`) {
        link.classList.add("is-active");
      } else {
        link.classList.remove("is-active");
      }
    });
  }

  updateActive();
  window.addEventListener("scroll", updateActive);
}

// Update footer year
document.addEventListener("DOMContentLoaded", () => {
  const yearSpan = document.getElementById("year");
  if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear().toString();
  }

  setupActiveNav();

  // Click handlers for analysis cards.
  // TODO: Replace the URLs below with your real routes
  // (for example, your Streamlit app URL or other pages).
  const urlMap = {
    mental: "mental.html",
    diabetes: "diabetes.html",
    bp: "bp.html",
    overall: "overall.html",
  };

  document.querySelectorAll(".card[data-target]").forEach((card) => {
    card.addEventListener("click", () => {
      const target = card.getAttribute("data-target");
      if (!target) return;
      const url = urlMap[target];
      if (!url) return;
      window.location.href = url;
    });
  });
});
