import { Outlet, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { Header } from './common/Header';
import { Footer } from './common/Footer';
import { ChatWidget } from './chat/ChatWidget';
import { AnimatedBackground } from './animations';

export const Layout: React.FC = () => {
  const location = useLocation();

  return (
    <div className="min-h-screen flex flex-col">
      <AnimatedBackground />
      <Header />
      <main className="flex-grow">
        <AnimatePresence mode="wait">
          <Outlet key={location.pathname} />
        </AnimatePresence>
      </main>
      <Footer />
      <ChatWidget />
    </div>
  );
};

export default Layout;
