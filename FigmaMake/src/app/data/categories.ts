import { Utensils, Train, MessageCircle, TreePine, Users, Sparkles, Heart, AlertCircle, Lightbulb, LucideIcon } from 'lucide-react';

export interface Category {
  id: string;
  icon: LucideIcon;
  title: string;
  tipCount: number;
  color: 'teal' | 'yellow';
}

export const categories: Category[] = [
  { id: 'everyday-etiquette', icon: Sparkles, title: 'Everyday Etiquette', tipCount: 15, color: 'teal' },
  { id: 'food-dining', icon: Utensils, title: 'Food & Dining', tipCount: 12, color: 'yellow' },
  { id: 'getting-around', icon: Train, title: 'Getting Around', tipCount: 8, color: 'teal' },
  { id: 'public-spaces', icon: TreePine, title: 'Public Spaces', tipCount: 10, color: 'yellow' },
  { id: 'social-interactions', icon: Users, title: 'Social Interactions', tipCount: 6, color: 'teal' },
  { id: 'cultural-customs', icon: MessageCircle, title: 'Cultural Customs', tipCount: 9, color: 'yellow' },
  { id: 'locals-appreciate', icon: Heart, title: 'Things Locals Appreciate', tipCount: 11, color: 'teal' },
  { id: 'misunderstandings', icon: AlertCircle, title: 'Common Misunderstandings', tipCount: 7, color: 'yellow' },
  { id: 'helpful-tips', icon: Lightbulb, title: 'Helpful Local Tips', tipCount: 13, color: 'teal' },
];
