import { useState } from 'react';
import { motion } from 'framer-motion';

const HERO_VIDEO = 'https://videos.pexels.com/video-files/1409899/1409899-uhd_2560_1440_25fps.mp4';
const FALLBACK_IMAGE = 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1920&q=80';

export const HeroVideo: React.FC = () => {
  const [videoLoaded, setVideoLoaded] = useState(false);

  return (
    <>
      {/* Fallback image while video loads */}
      {!videoLoaded && (
        <motion.div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url('${FALLBACK_IMAGE}')` }}
          initial={{ scale: 1 }}
          animate={{ scale: 1.1 }}
          transition={{ duration: 20, ease: 'linear', repeat: Infinity, repeatType: 'reverse' }}
        />
      )}

      {/* Video background */}
      <motion.video
        className="absolute inset-0 w-full h-full object-cover"
        src={HERO_VIDEO}
        autoPlay
        muted
        loop
        playsInline
        onCanPlay={() => setVideoLoaded(true)}
        initial={{ opacity: 0, scale: 1.05 }}
        animate={videoLoaded ? { opacity: 1, scale: 1 } : {}}
        transition={{ duration: 1.5, ease: 'easeOut' }}
      />

      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-900/75 via-blue-800/50 to-blue-900/75" />
      <div className="absolute inset-0 bg-gradient-to-t from-blue-900/40 to-transparent" />
    </>
  );
};
