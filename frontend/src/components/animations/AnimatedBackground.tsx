import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const BG_IMAGES = [
  'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1920&q=80',
  'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1920&q=80',
  'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1920&q=80',
  'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1920&q=80',
  'https://images.unsplash.com/photo-1506929562872-bb421503ef21?w=1920&q=80',
];

const INTERVAL = 8000;
const KEN_BURNS_DURATION = 10;

const kenBurnsVariants = [
  { scale: [1, 1.1], x: ['0%', '1%'], y: ['0%', '1%'] },
  { scale: [1.08, 1], x: ['1%', '-1%'], y: ['1%', '-1%'] },
  { scale: [1, 1.08], x: ['-1%', '1%'], y: ['-1%', '1%'] },
  { scale: [1.06, 1], x: ['1%', '-1%'], y: ['1%', '0%'] },
  { scale: [1, 1.1], x: ['0%', '-1%'], y: ['0%', '1%'] },
];

export const AnimatedBackground: React.FC = () => {
  const [current, setCurrent] = useState(0);

  const next = useCallback(() => {
    setCurrent((prev) => (prev + 1) % BG_IMAGES.length);
  }, []);

  useEffect(() => {
    const timer = setInterval(next, INTERVAL);
    return () => clearInterval(timer);
  }, [next]);

  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      <AnimatePresence mode="popLayout">
        <motion.div
          key={current}
          className="absolute inset-0"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1.5, ease: 'easeInOut' }}
        >
          <motion.img
            src={BG_IMAGES[current]}
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
      {/* Overlay for readability */}
      <div className="absolute inset-0 bg-white/80 backdrop-blur-sm" />
    </div>
  );
};
