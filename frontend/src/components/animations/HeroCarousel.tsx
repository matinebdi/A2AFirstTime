import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const HERO_IMAGES = [
  'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1920&q=80',
  'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1920&q=80',
  'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1920&q=80',
  'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1920&q=80',
];

const INTERVAL = 6000;
const KEN_BURNS_DURATION = 8;

const kenBurnsVariants = [
  { scale: [1, 1.15], x: ['0%', '2%'], y: ['0%', '1%'] },
  { scale: [1.1, 1], x: ['2%', '-1%'], y: ['1%', '-1%'] },
  { scale: [1, 1.12], x: ['-1%', '1%'], y: ['-1%', '2%'] },
  { scale: [1.08, 1], x: ['1%', '-2%'], y: ['2%', '0%'] },
];

export const HeroCarousel: React.FC = () => {
  const [current, setCurrent] = useState(0);

  const next = useCallback(() => {
    setCurrent((prev) => (prev + 1) % HERO_IMAGES.length);
  }, []);

  useEffect(() => {
    const timer = setInterval(next, INTERVAL);
    return () => clearInterval(timer);
  }, [next]);

  return (
    <>
      <AnimatePresence mode="popLayout">
        <motion.div
          key={current}
          className="absolute inset-0"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1.2, ease: 'easeInOut' }}
        >
          <motion.img
            src={HERO_IMAGES[current]}
            alt=""
            className="w-full h-full object-cover"
            animate={kenBurnsVariants[current % kenBurnsVariants.length]}
            transition={{
              duration: KEN_BURNS_DURATION,
              ease: 'linear',
              repeat: Infinity,
              repeatType: 'reverse',
            }}
          />
        </motion.div>
      </AnimatePresence>
      <div className="absolute inset-0 bg-gradient-to-r from-blue-900/70 via-blue-800/50 to-blue-900/70" />

      {/* Dots */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2 z-10">
        {HERO_IMAGES.map((_, i) => (
          <button
            key={i}
            onClick={() => setCurrent(i)}
            className={`w-2.5 h-2.5 rounded-full transition-all duration-300 ${
              i === current ? 'bg-white w-8' : 'bg-white/50 hover:bg-white/75'
            }`}
          />
        ))}
      </div>
    </>
  );
};
