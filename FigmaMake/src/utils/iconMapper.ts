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
  Handshake,
  Bus,
  Landmark,
  CalendarCheck,
  AlertTriangle,
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
  'handshake': Handshake,
  'bus': Bus,
  'landmark': Landmark,
  'calendar-star': CalendarCheck,
  'alert-triangle': AlertTriangle,
};

export function getIconComponent(iconName?: string | null): LucideIcon {
  if (!iconName) {
    console.warn('No icon name provided, using default HelpCircle');
    return HelpCircle; // Default icon
  }

  const normalizedName = iconName.toLowerCase();
  const icon = iconMap[normalizedName];

  if (!icon) {
    console.warn(`Icon '${iconName}' not found in iconMap, using default HelpCircle. Available icons:`, Object.keys(iconMap));
    return HelpCircle;
  }

  return icon;
}

export function getColorVariant(color?: string | null): 'teal' | 'yellow' {
  if (!color) {
    return 'teal'; // Default color
  }

  const normalizedColor = color.toLowerCase();

  // Yellow-ish colors (warm colors)
  if (
    normalizedColor === 'yellow' ||
    normalizedColor === '#f4d35e' ||
    normalizedColor.includes('#f39c12') || // Orange
    normalizedColor.includes('#e67e22') || // Dark orange
    normalizedColor.includes('#ffc107') || // Amber
    normalizedColor.includes('#ff6b6b') || // Red-ish
    normalizedColor.includes('#e94b3c') || // Red
    normalizedColor.includes('#e91e63')    // Pink
  ) {
    return 'yellow';
  }

  // Default to teal for blues, purples, greens, etc.
  return 'teal';
}
