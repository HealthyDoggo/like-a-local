import {
  Utensils,
  Train,
  MessageCircle,
  TreePine,
  Users,
  Sparkles,
  Heart,
  AlertCircle,
  Lightbulb,
  HelpCircle,
  LucideIcon,
} from 'lucide-react';

const iconMap: Record<string, LucideIcon> = {
  'sparkles': Sparkles,
  'utensils': Utensils,
  'train': Train,
  'tree-pine': TreePine,
  'users': Users,
  'message-circle': MessageCircle,
  'heart': Heart,
  'alert-circle': AlertCircle,
  'lightbulb': Lightbulb,
};

export function getIconComponent(iconName?: string | null): LucideIcon {
  if (!iconName) {
    return HelpCircle; // Default icon
  }

  return iconMap[iconName.toLowerCase()] || HelpCircle;
}

export function getColorVariant(color?: string | null): 'teal' | 'yellow' {
  if (!color) {
    return 'teal'; // Default color
  }

  const normalizedColor = color.toLowerCase();
  if (normalizedColor === 'yellow' || normalizedColor === '#f4d35e') {
    return 'yellow';
  }

  return 'teal';
}
