import { Outlet } from 'react-router-dom';
import { Header } from './common/Header';
import { Footer } from './common/Footer';
import { ChatWidget } from './chat/ChatWidget';

export const Layout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow">
        <Outlet />
      </main>
      <Footer />
      <ChatWidget />
    </div>
  );
};

export default Layout;
