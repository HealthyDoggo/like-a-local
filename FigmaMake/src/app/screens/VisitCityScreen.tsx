import { useState, useMemo } from 'react';
import { motion } from 'motion/react';
import { Input } from '@/app/components/Input';
import { ListItem } from '@/app/components/ListItem';
import { useNavigate, useLocation } from 'react-router';
import { ArrowLeft } from 'lucide-react';
import { BottomNav } from '@/app/components/BottomNav';
import { useLocations } from '@/hooks/useLocations';
import { LoadingSpinner } from '@/app/components/LoadingSpinner';
import { ErrorMessage } from '@/app/components/ErrorMessage';
import { useSettings } from '@/hooks/useSettings';

export function VisitCityScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const country = location.state?.country || 'Japan';
  const { locations, loading, error, reload } = useLocations();
  const { reducedMotion } = useSettings();

  // Filter cities by selected country
  const cities = useMemo(() => {
    return locations
      .filter(loc => loc.country === country)
      .map(loc => loc.name)
      .sort();
  }, [locations, country]);

  const filteredCities = cities.filter(city =>
    city.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const header = (
    <motion.div
      initial={reducedMotion ? false : { opacity: 0, y: -10 }}
      animate={reducedMotion ? false : { opacity: 1, y: 0 }}
      className="flex items-center mb-6"
    >
      <button
        onClick={() => navigate(-1)}
        className="p-2 -ml-2"
        style={{ color: 'var(--app-text-accent)' }}
      >
        <ArrowLeft className="w-6 h-6" />
      </button>
      <h1
        className="text-[24px] leading-[28px] ml-2"
        style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
      >
        Select city you're visiting
      </h1>
    </motion.div>
  );

  if (loading) {
    return (
      <div className="min-h-screen pb-20" style={{ backgroundColor: 'var(--app-bg)' }}>
        <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
          {header}
          <LoadingSpinner />
        </div>
        <BottomNav />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen pb-20" style={{ backgroundColor: 'var(--app-bg)' }}>
        <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
          {header}
          <ErrorMessage message={error} onRetry={reload} />
        </div>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: 'var(--app-bg)' }}>
      <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
        {header}

        <div className="mb-6">
          <Input
            type="search"
            placeholder="Search cities..."
            value={searchQuery}
            onChange={setSearchQuery}
          />
        </div>

        <div className="flex flex-col gap-3">
          {filteredCities.map((city) => (
            <div key={city}>
              <ListItem
                title={city}
                onClick={() => navigate('/city-overview', { state: { city, country } })}
              />
            </div>
          ))}
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
