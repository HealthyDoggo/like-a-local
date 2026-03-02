import { motion } from 'motion/react';
import { ReactNode } from 'react';

interface ButtonProps {
  children: ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
  className?: string;
  type?: 'button' | 'submit';
}

export function Button({ children, onClick, variant = 'primary', className = '', type = 'button' }: ButtonProps) {
  const baseStyles = 'px-6 py-4 rounded-xl transition-all duration-200';
  const variantStyles = variant === 'primary'
    ? 'text-white'
    : 'border-2';

  return (
    <motion.button
      type={type}
      onClick={onClick}
      className={`${baseStyles} ${variantStyles} ${className}`}
      style={variant === 'primary'
        ? { backgroundColor: 'var(--app-text-accent)' }
        : { backgroundColor: 'var(--app-surface)', color: 'var(--app-text-accent)', borderColor: 'var(--app-text-accent)' }}
      whileTap={{ scale: 0.95 }}
      whileHover={{ boxShadow: '0 4px 12px rgba(69, 123, 157, 0.3)' }}
    >
      {children}
    </motion.button>
  );
}
