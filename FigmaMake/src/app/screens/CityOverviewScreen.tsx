import { motion } from 'motion/react';
import { useLocation, useNavigate } from 'react-router';
import { CategoryCard } from '@/app/components/CategoryCard';
import { BottomNav } from '@/app/components/BottomNav';
import { categories } from '@/app/data/categories';
import { usePromotedTips } from '@/hooks/useTips';
import { useSettings } from '@/hooks/useSettings';

export function CityOverviewScreen() {
  const location = useLocation();
  const navigate = useNavigate();
  const city = location.state?.city || 'Tokyo';
  const country = location.state?.country || 'Japan';
  const { reducedMotion } = useSettings();

  // Fetch tips to get total count
  const { tips } = usePromotedTips(city, country, 100);
  const totalTips = tips.length;

  return (
    <div className="min-h-screen pb-20 max-w-[360px] mx-auto" style={{ backgroundColor: 'var(--app-bg)' }}>
      <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
        <motion.h1
          initial={reducedMotion ? false : { opacity: 0, y: -10 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
          className="text-[24px] leading-[28px] mb-6"
          style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
        >
          {city}
        </motion.h1>

        <div className="mb-4">
          <h2 className="text-[18px] leading-[24px] mb-4" style={{ color: 'var(--app-text-primary)', fontWeight: 500 }}>
            Categories
          </h2>
        </div>

        <div className="overflow-x-auto -mx-5 px-5">
          <div className="flex gap-4 pb-4">
            {categories.map((category) => (
              <div key={category.id}>
                <CategoryCard
                  icon={category.icon}
                  title={category.title}
                  tipCount={totalTips}
                  iconColor={category.color}
                  onClick={() => navigate('/tips', { state: { city, country, category: category.title } })}
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}