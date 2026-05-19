/* ─── Template field switching ───────────────────────────────── */
function showTemplate(type) {
  document.querySelectorAll(".tpl-fields").forEach(el => el.classList.add("hidden"));
  const target = document.getElementById("tpl-" + type);
  if (target) target.classList.remove("hidden");

  // Update selected state on template cards
  document.querySelectorAll(".template-card").forEach(c => c.classList.remove("selected"));
  const radio = document.querySelector(`input[name="template_type"][value="${type}"]`);
  if (radio) radio.closest(".template-card").classList.add("selected");
}

/* ─── Colour scheme toggling ─────────────────────────────────── */
function toggleCustomColor(scheme) {
  const customBox = document.getElementById("custom-colors");
  if (scheme === "custom") {
    customBox.classList.remove("hidden");
  } else {
    customBox.classList.add("hidden");
  }

  // Update selected state
  document.querySelectorAll(".color-swatch").forEach(c => c.classList.remove("selected"));
  const radio = document.querySelector(`input[name="color_scheme"][value="${scheme}"]`);
  if (radio) radio.closest(".color-swatch").classList.add("selected");
}

/* ─── Frame text visibility ──────────────────────────────────── */
function toggleFrameText(style) {
  const group = document.getElementById("frame-text-group");
  if (style !== "none" && style !== "simple") {
    group.classList.remove("hidden");
  } else {
    group.classList.add("hidden");
  }

  // Update selected state
  document.querySelectorAll(".frame-card").forEach(c => c.classList.remove("selected"));
  const radio = document.querySelector(`input[name="frame_style"][value="${style}"]`);
  if (radio) radio.closest(".frame-card").classList.add("selected");
}

/* ─── Generic card selection ─────────────────────────────────── */
function selectCard(radio) {
  const container = radio.closest(".ec-grid, .logo-grid");
  if (!container) return;
  container.querySelectorAll(".ec-card, .logo-card").forEach(c => c.classList.remove("selected"));
  radio.closest(".ec-card, .logo-card").classList.add("selected");
}

/* ─── Logo card selection ────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", function () {
  // Wire logo radio buttons
  document.querySelectorAll('input[name="logo"]').forEach(radio => {
    radio.addEventListener("change", function () {
      document.querySelectorAll(".logo-card").forEach(c => c.classList.remove("selected"));
      this.closest(".logo-card").classList.add("selected");
    });
  });

  // Wire error correction radio buttons
  document.querySelectorAll('input[name="error_correction"]').forEach(radio => {
    radio.addEventListener("change", function () {
      document.querySelectorAll(".ec-card").forEach(c => c.classList.remove("selected"));
      this.closest(".ec-card").classList.add("selected");
    });
  });

  // Show the default template on load (website)
  showTemplate("website");

  // Initialise frame text visibility
  const defaultFrame = document.querySelector('input[name="frame_style"]:checked');
  if (defaultFrame) toggleFrameText(defaultFrame.value);
});
