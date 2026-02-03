import { useState, useMemo, useRef, useEffect } from 'react';
import { motion } from 'motion/react';
import { Input } from '@/app/components/Input';
import { ListItem } from '@/app/components/ListItem';
import { useNavigate } from 'react-router';
import { useCountriesAndCities } from '@/hooks/useCountriesAndCities';
import { LoadingSpinner } from '@/app/components/LoadingSpinner';
import { ErrorMessage } from '@/app/components/ErrorMessage';
import { useSettings } from '@/hooks/useSettings';

// Generate flag image URL from country code
const getFlagUrl = (countryCode: string): string => {
  return `https://flagsapi.com/${countryCode.toUpperCase()}/flat/64.png`;
};

export function SelectCountryScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const { data, loading, error, reload } = useCountriesAndCities();
  const { reducedMotion } = useSettings();
  const hasAnimated = useRef(false);

  // Mark as animated after first render to prevent re-animations
  useEffect(() => {
    if (!loading && !error) {
      hasAnimated.current = true;
    }
  }, [loading, error]);

  // Map countries from API data
  const countries = useMemo(() => {
    if (!data) return [];

    return data.countries.map(country => ({
      name: country.name,
      code: country.code,
      flag: getFlagUrl(country.code),
      cityCount: country.cities.length,
    }));
  }, [data]);

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
        {filteredCountries.length === 0 ? (
          <p className="text-center text-[14px] py-8" style={{ color: 'var(--app-text-secondary)' }}>
            No countries found matching "{searchQuery}"
          </p>
        ) : (
          filteredCountries.map((country) => (
            <div key={country.code}>
              <ListItem
                flag={country.flag}
                title={country.name}
                subtitle={`${country.cityCount} ${country.cityCount === 1 ? 'city' : 'cities'}`}
                onClick={() => navigate('/onboarding/city', { state: { country: country.name } })}
              />
            </div>
          ))
        )}
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