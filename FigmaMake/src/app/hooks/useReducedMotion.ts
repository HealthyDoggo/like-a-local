import { useState, useEffect } from 'react';

export function useReducedMotion() {
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    // Check localStorage preference
    const prefersReducedMotion = localStorage.getItem('reducedMotion') === 'true';
    setReducedMotion(prefersReducedMotion);

    // Listen for changes
    const interval = setInterval(() => {
      const current = localStorage.getItem('reducedMotion') === 'true';
      setReducedMotion(current);
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return reducedMotion;
}
