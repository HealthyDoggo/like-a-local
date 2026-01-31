import { useState, useMemo } from 'react';
import { motion } from 'motion/react';
import { Input } from '@/app/components/Input';
import { ListItem } from '@/app/components/ListItem';
import { useNavigate } from 'react-router';
import { BottomNav } from '@/app/components/BottomNav';
import { useLocations } from '@/hooks/useLocations';
import { LoadingSpinner } from '@/app/components/LoadingSpinner';
import { ErrorMessage } from '@/app/components/ErrorMessage';
import { useSettings } from '@/hooks/useSettings';

// Flag emoji mapping for common countries
const countryFlags: Record<string, string> = {
  'United States': '🇺🇸',
  'United Kingdom': '🇬🇧',
  'France': '🇫🇷',
  'Germany': '🇩🇪',
  'Japan': '🇯🇵',
  'Australia': '🇦🇺',
  'Canada': '🇨🇦',
  'Spain': '🇪🇸',
  'Italy': '🇮🇹',
  'China': '🇨🇳',
  'India': '🇮🇳',
  'Brazil': '🇧🇷',
  'Mexico': '🇲🇽',
  'Netherlands': '🇳🇱',
  'Switzerland': '🇨🇭',
  'South Korea': '🇰🇷',
  'Thailand': '🇹🇭',
  'Singapore': '🇸🇬',
  'Ireland': '🇮🇪',
  'Portugal': '🇵🇹',
};

const getCountryFlag = (country: string): string => {
  return countryFlags[country] || '🌍';
};

export function VisitCountryScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const { locations, loading, error, reload } = useLocations();
  const { reducedMotion } = useSettings();

  // Extract unique countries from locations
  const countries = useMemo(() => {
    const uniqueCountries = Array.from(
      new Set(locations.map(loc => loc.country))
    ).sort();

    return uniqueCountries.map(country => ({
      name: country,
      flag: getCountryFlag(country),
    }));
  }, [locations]);

  const filteredCountries = countries.filter(country =>
    country.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen pb-20 max-w-[360px] mx-auto" style={{ backgroundColor: 'var(--app-bg)' }}>
        <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
          <motion.h1
            initial={reducedMotion ? false : { opacity: 0, y: -10 }}
            animate={reducedMotion ? false : { opacity: 1, y: 0 }}
            className="text-[24px] leading-[28px] mb-6"
            style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
          >
            Select country you're visiting
          </motion.h1>
          <LoadingSpinner />
        </div>
        <BottomNav />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen pb-20 max-w-[360px] mx-auto" style={{ backgroundColor: 'var(--app-bg)' }}>
        <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
          <motion.h1
            initial={reducedMotion ? false : { opacity: 0, y: -10 }}
            animate={reducedMotion ? false : { opacity: 1, y: 0 }}
            className="text-[24px] leading-[28px] mb-6"
            style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
          >
            Select country you're visiting
          </motion.h1>
          <ErrorMessage message={error} onRetry={reload} />
        </div>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-20 max-w-[360px] mx-auto" style={{ backgroundColor: 'var(--app-bg)' }}>
      <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
        <motion.h1
          initial={reducedMotion ? false : { opacity: 0, y: -10 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
          className="text-[24px] leading-[28px] mb-6"
          style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
        >
          Select country you're visiting
        </motion.h1>

        <div className="mb-6">
          <Input
            type="search"
            placeholder="Search countries..."
            value={searchQuery}
            onChange={setSearchQuery}
          />
        </div>

        <div className="flex flex-col gap-3">
          {filteredCountries.map((country) => (
            <div key={country.name}>
              <ListItem
                flag={country.flag}
                title={country.name}
                onClick={() => navigate('/visit/city', { state: { country: country.name } })}
              />
            </div>
          ))}
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
