import { motion } from 'framer-motion';
import type { ReactNode, MouseEventHandler } from 'react';

interface AnimatedButtonProps {
  children: ReactNode;
  className?: string;
  onClick?: MouseEventHandler<HTMLButtonElement>;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
}

export const AnimatedButton: React.FC<AnimatedButtonProps> = ({
  children,
  className,
  onClick,
  disabled,
  type = 'button',
}) => {
  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={className}
      whileHover={disabled ? {} : {
        scale: 1.05,
        boxShadow: '0 0 20px rgba(59, 130, 246, 0.5)',
      }}
      whileTap={disabled ? {} : { scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
    >
      {children}
    </motion.button>
  );
};

interface AnimatedLinkButtonProps {
  children: ReactNode;
  className?: string;
  to: string;
}

export const AnimatedLinkButton: React.FC<AnimatedLinkButtonProps> = ({
  children,
  className,
  to,
}) => {
  return (
    <motion.a
      href={to}
      className={className}
      whileHover={{
        scale: 1.05,
        boxShadow: '0 0 20px rgba(59, 130, 246, 0.5)',
      }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
    >
      {children}
    </motion.a>
  );
};
