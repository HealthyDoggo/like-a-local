export interface Tip {
  id: string;
  category: string;
  title?: string;
  text: string;
  supportingText?: string;
  keywords?: string[];
}

export const tipsByCategory: Record<string, Tip[]> = {
  'Food & Dining': [
    { 
      id: 'dining-1',
      category: 'Food & Dining',
      title: 'Service is included',
      text: "Service is already included in your bill — tipping isn't necessary and staff are paid well!",
      keywords: ['Service', 'tipping']
    },
    { 
      id: 'dining-2',
      category: 'Food & Dining',
      title: 'Meal gratitude phrases',
      text: "Say 'itadakimasu' before eating and 'gochisousama' after finishing to show gratitude.",
      supportingText: "These phrases express respect for the food and those who prepared it.",
      keywords: ['itadakimasu', 'gochisousama', 'gratitude']
    },
    { 
      id: 'dining-3',
      category: 'Food & Dining',
      title: 'Chopstick placement',
      text: "Keep chopsticks flat on your plate when not using them — placing them upright in rice is reserved for memorial ceremonies.",
      keywords: ['chopsticks', 'memorial ceremonies']
    },
    { 
      id: 'dining-4',
      category: 'Food & Dining',
      title: 'Noodle enjoyment',
      text: "Slurping noodles is completely normal and shows you're enjoying your meal!",
      keywords: ['Slurping', 'enjoying']
    },
  ],
  'Getting Around': [
    { 
      id: 'transport-1',
      category: 'Getting Around',
      title: 'Peaceful commute',
      text: "Keep your phone on silent mode on public transport to maintain a peaceful atmosphere.",
      keywords: ['silent mode', 'peaceful']
    },
    { 
      id: 'transport-2',
      category: 'Getting Around',
      title: 'Orderly boarding',
      text: "Queue in an orderly line and wait for people to exit before boarding — locals appreciate it!",
      keywords: ['Queue', 'orderly']
    },
    { 
      id: 'transport-3',
      category: 'Getting Around',
      title: 'Priority seating',
      text: "Priority seating is reserved for elderly, pregnant, or passengers with disabilities — please help keep these seats available.",
      keywords: ['Priority seating']
    },
  ],
  'Social Interactions': [
    { 
      id: 'greetings-1',
      category: 'Social Interactions',
      title: 'Respectful greeting',
      text: "A slight bow of 15 degrees is the standard greeting for casual situations — it shows respect.",
      keywords: ['bow', 'respect']
    },
    { 
      id: 'greetings-2',
      category: 'Social Interactions',
      title: 'Personal space',
      text: "Personal space is valued — handshakes, hugs, or kisses aren't common greetings here.",
      keywords: ['Personal space']
    },
  ],
  'Everyday Etiquette': [
    { 
      id: 'etiquette-1',
      category: 'Everyday Etiquette',
      title: 'Indoor shoes',
      text: "Remove your shoes when entering homes, traditional restaurants, and temples — slippers are often provided.",
      keywords: ['shoes', 'slippers']
    },
    { 
      id: 'etiquette-2',
      category: 'Everyday Etiquette',
      title: 'Gift giving',
      text: "When giving or receiving gifts, use both hands as a sign of respect and gratitude.",
      keywords: ['gifts', 'both hands']
    },
  ],
  'Public Spaces': [
    { 
      id: 'public-1',
      category: 'Public Spaces',
      title: 'Keep parks clean',
      text: "Keep parks clean — locals appreciate it! Trash bins are rare, so many people take their trash home.",
      keywords: ['parks', 'trash']
    },
    { 
      id: 'public-2',
      category: 'Public Spaces',
      title: 'Quiet public areas',
      text: "Keep conversations at a moderate volume in public spaces — loud talking can be considered disruptive.",
      keywords: ['volume', 'public spaces']
    },
  ],
  'Cultural Customs': [
    { 
      id: 'cultural-1',
      category: 'Cultural Customs',
      title: 'Business card exchange',
      text: "When receiving a business card, accept it with both hands and take a moment to read it before putting it away.",
      keywords: ['business card', 'both hands']
    },
  ],
  'Things Locals Appreciate': [
    { 
      id: 'appreciate-1',
      category: 'Things Locals Appreciate',
      title: 'Learning basic phrases',
      text: "Learning a few basic Japanese phrases goes a long way — locals really appreciate the effort!",
      keywords: ['Japanese phrases', 'appreciate']
    },
  ],
  'Common Misunderstandings': [
    { 
      id: 'misunderstanding-1',
      category: 'Common Misunderstandings',
      title: 'Service quality',
      text: "Excellent service is the standard everywhere — it's not dependent on tipping and is simply part of the culture.",
      keywords: ['service', 'culture']
    },
  ],
  'Helpful Local Tips': [
    { 
      id: 'helpful-1',
      category: 'Helpful Local Tips',
      title: '24/7 convenience stores',
      text: "Convenience stores (konbini) are everywhere and open 24/7 — they have everything from hot meals to ATMs!",
      keywords: ['konbini', '24/7']
    },
  ],
};
