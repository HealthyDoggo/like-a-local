/**
 * Apply saved settings to the document on initial load
 * This should be called as early as possible to avoid flash of unstyled content
 */
export function applySettings() {
  // Apply dark mode
  const darkMode = localStorage.getItem('darkMode') === 'true';
  if (darkMode) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }

  // Apply reading mode
  const readingMode = localStorage.getItem('readingMode') === 'true';
  if (readingMode) {
    document.documentElement.classList.add('reading-mode');
  } else {
    document.documentElement.classList.remove('reading-mode');
  }

  // Apply reduced motion
  const reducedMotion = localStorage.getItem('reducedMotion') === 'true';
  if (reducedMotion) {
    document.documentElement.classList.add('reduced-motion');
  } else {
    document.documentElement.classList.remove('reduced-motion');
  }
}
