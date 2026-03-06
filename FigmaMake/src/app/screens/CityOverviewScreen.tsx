import { motion } from 'motion/react';
import { useLocation, useNavigate } from 'react-router';
import { CategoryCard } from '@/app/components/CategoryCard';
import { BottomNav } from '@/app/components/BottomNav';
import { useCategories } from '@/hooks/useCategories';
import { useSettings } from '@/hooks/useSettings';
import { ErrorMessage } from '@/app/components/ErrorMessage';
import { ArrowLeft, Lightbulb } from 'lucide-react';
import { Button } from '@/app/components/Button';

export function CityOverviewScreen() {
  const location = useLocation();
  const navigate = useNavigate();
  const city = location.state?.city || 'Tokyo';
  const country = location.state?.country || 'Japan';
  const { reducedMotion } = useSettings();

  // Fetch categories and counts from backend
  const { categories, loading, error } = useCategories(city, country);

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: 'var(--app-bg)' }}>
      <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
        <motion.div
          initial={reducedMotion ? false : { opacity: 0, y: -10 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
          className="flex items-center gap-3 mb-6"
        >
          <button
            onClick={() => navigate(-1)}
            className="p-2 -ml-2"
            style={{ color: 'var(--app-text-accent)' }}
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <h1
            className="text-[24px] leading-[28px]"
            style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
          >
            {city}
          </h1>
        </motion.div>

        <div className="mb-4">
          <h2 className="text-[18px] leading-[24px] mb-4" style={{ color: 'var(--app-text-primary)', fontWeight: 500 }}>
            Categories
          </h2>
        </div>

        {loading ? (
          <div className="text-center py-8" style={{ color: 'var(--app-text-secondary)' }}>
            Loading categories...
          </div>
        ) : error || categories.length === 0 ? (
          <div>
            {error && (
              <div className="mb-6">
                <ErrorMessage message={error} />
              </div>
            )}
            <div className="mb-6">
              <p className="text-center text-[14px] mb-4" style={{ color: 'var(--app-text-secondary)' }}>
                {error ? 'Unable to load categories. View general tips instead:' : 'No categories available yet. View general tips:'}
              </p>
            </div>
            <div className="grid grid-cols-1 gap-2">
              <CategoryCard
                icon={Lightbulb}
                title="All Tips"
                tipCount={0}
                iconColor="teal"
                onClick={() => navigate('/tips', { state: { city, country, categoryId: undefined, category: 'All Tips' } })}
              />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-2">
            {categories.map((category) => {
              try {
                return (
                  <CategoryCard
                    key={category.id}
                    icon={category.icon}
                    title={category.title}
                    tipCount={category.tipCount}
                    iconColor={category.color}
                    onClick={() => navigate('/tips', { state: { city, country, categoryId: category.id, category: category.title } })}
                  />
                );
              } catch (err) {
                console.error(`Error rendering category ${category.id}:`, err);
                return null;
              }
            })}
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}