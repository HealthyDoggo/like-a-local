import { ReactNode } from 'react';

interface SafeAreaViewProps {
  children: ReactNode;
  className?: string;
  top?: boolean;
  bottom?: boolean;
}

export function SafeAreaView({
  children,
  className = '',
  top = true,
  bottom = false,
}: SafeAreaViewProps) {
  const style: React.CSSProperties = {};

  if (top) {
    style.paddingTop = 'max(env(safe-area-inset-top), 0.5rem)';
  }

  if (bottom) {
    style.paddingBottom = 'max(env(safe-area-inset-bottom), 0.5rem)';
  }

  return (
    <div className={className} style={style}>
      {children}
    </div>
  );
}
