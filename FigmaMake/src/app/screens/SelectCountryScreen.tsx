import { useState, useMemo, useRef, useEffect } from 'react';
import { motion } from 'motion/react';
import { Input } from '@/app/components/Input';
import { ListItem } from '@/app/components/ListItem';
import { useNavigate } from 'react-router';
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

export function SelectCountryScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const { locations, loading, error, reload } = useLocations();
  const { reducedMotion } = useSettings();
  const hasAnimated = useRef(false);

  // Mark as animated after first render to prevent re-animations
  useEffect(() => {
    if (!loading && !error) {
      hasAnimated.current = true;
    }
  }, [loading, error]);

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
      <div className="min-h-screen px-5 max-w-[360px] mx-auto" style={{ backgroundColor: 'var(--app-bg)', paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
        <motion.div
          initial={reducedMotion ? false : { opacity: 0, y: -10 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
          className="mb-6"
        >
          <h1
            className="text-[24px] leading-[28px] mb-2"
            style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
          >
            Where are you local to?
          </h1>
          <p className="text-[14px] leading-[20px]" style={{ color: 'var(--app-text-secondary)' }}>
            Select your country to start sharing local knowledge
          </p>
        </motion.div>
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen px-5 max-w-[360px] mx-auto" style={{ backgroundColor: 'var(--app-bg)', paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
        <motion.div
          initial={reducedMotion ? false : { opacity: 0, y: -10 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
          className="mb-6"
        >
          <h1
            className="text-[24px] leading-[28px] mb-2"
            style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
          >
            Where are you local to?
          </h1>
          <p className="text-[14px] leading-[20px]" style={{ color: 'var(--app-text-secondary)' }}>
            Select your country to start sharing local knowledge
          </p>
        </motion.div>
        <ErrorMessage message={error} onRetry={reload} />
      </div>
    );
  }

  return (
    <div className="min-h-screen px-5 max-w-[360px] mx-auto" style={{ backgroundColor: 'var(--app-bg)', paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
      <motion.div
        initial={reducedMotion ? false : { opacity: 0, y: -10 }}
        animate={reducedMotion ? false : { opacity: 1, y: 0 }}
        className="mb-6"
      >
        <h1
          className="text-[24px] leading-[28px] mb-2"
          style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
        >
          Where are you local to?
        </h1>
        <p className="text-[14px] leading-[20px]" style={{ color: 'var(--app-text-secondary)' }}>
          Select your country to start sharing local knowledge
        </p>
      </motion.div>

      <div className="mb-6">
        <Input
          type="search"
          placeholder="Search countries..."
          value={searchQuery}
          onChange={setSearchQuery}
        />
      </div>

      <div className="flex flex-col gap-3 mb-6">
        {filteredCountries.map((country) => (
          <div key={country.name}>
            <ListItem
              flag={country.flag}
              title={country.name}
              onClick={() => navigate('/onboarding/city', { state: { country: country.name } })}
            />
          </div>
        ))}
      </div>

      <motion.button
        onClick={() => navigate('/home')}
        initial={reducedMotion ? false : { opacity: 0 }}
        animate={reducedMotion ? false : { opacity: 1 }}
        transition={reducedMotion ? { duration: 0 } : { delay: 0.3 }}
        className="text-[15px] w-full py-3"
        style={{ color: 'var(--app-text-accent)' }}
        whileTap={reducedMotion ? {} : { scale: 0.98 }}
      >
        Skip for now
      </motion.button>
    </div>
  );
}