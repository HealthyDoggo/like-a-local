import { useState, useMemo } from 'react';
import { motion } from 'motion/react';
import { Input } from '@/app/components/Input';
import { ListItem } from '@/app/components/ListItem';
import { useNavigate, useLocation } from 'react-router';
import { useCountriesAndCities } from '@/hooks/useCountriesAndCities';
import { LoadingSpinner } from '@/app/components/LoadingSpinner';
import { ErrorMessage } from '@/app/components/ErrorMessage';
import { useSettings } from '@/hooks/useSettings';

export function SelectCityScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const country = location.state?.country || 'United States';
  const { data, loading, error, reload } = useCountriesAndCities();
  const { reducedMotion } = useSettings();

  // Filter cities by selected country
  const cities = useMemo(() => {
    if (!data) return [];

    const selectedCountry = data.countries.find(c => c.name === country);
    if (!selectedCountry) return [];

    return selectedCountry.cities
      .map(city => ({
        name: city.name,
        latitude: city.latitude,
        longitude: city.longitude,
      }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [data, country]);

  const filteredCities = cities.filter(city =>
    city.name.toLowerCase().includes(searchQuery.toLowerCase())
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
            Which city?
          </h1>
          <p className="text-[14px] leading-[20px]" style={{ color: 'var(--app-text-secondary)' }}>
            We'll show you tips specific to this location
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
            Which city?
          </h1>
          <p className="text-[14px] leading-[20px]" style={{ color: 'var(--app-text-secondary)' }}>
            We'll show you tips specific to this location
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
          Which city?
        </h1>
        <p className="text-[14px] leading-[20px]" style={{ color: 'var(--app-text-secondary)' }}>
          We'll show you tips specific to this location
        </p>
      </motion.div>

      <div className="mb-6">
        <Input
          type="search"
          placeholder="Search cities..."
          value={searchQuery}
          onChange={setSearchQuery}
        />
      </div>

      <div className="flex flex-col gap-3 mb-6">
        {filteredCities.length === 0 ? (
          <p className="text-center text-[14px] py-8" style={{ color: 'var(--app-text-secondary)' }}>
            {searchQuery ? `No cities found matching "${searchQuery}"` : 'No cities available'}
          </p>
        ) : (
          filteredCities.map((city) => (
            <div key={city.name}>
              <ListItem
                title={city.name}
                onClick={() => navigate('/onboarding/tips', { state: { country, city: city.name } })}
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