import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useLocation } from 'react-router-dom';

export interface PageContextData {
  page: string;
  route: string;
  data?: Record<string, any>;
}

interface PageContextType {
  pageContext: PageContextData;
  setPageContext: (data: Omit<PageContextData, 'route'>) => void;
}

const PageContext = createContext<PageContextType | undefined>(undefined);

export const PageContextProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const location = useLocation();
  const [contextData, setContextData] = useState<PageContextData>({
    page: 'home',
    route: location.pathname + location.search,
  });

  // Keep route in sync with navigation
  useEffect(() => {
    setContextData((prev) => ({
      ...prev,
      route: location.pathname + location.search,
    }));
  }, [location.pathname, location.search]);

  const setPageContext = (data: Omit<PageContextData, 'route'>) => {
    setContextData({
      ...data,
      route: location.pathname + location.search,
    });
  };

  return (
    <PageContext.Provider value={{ pageContext: contextData, setPageContext }}>
      {children}
    </PageContext.Provider>
  );
};

export const usePageContext = (): PageContextData => {
  const context = useContext(PageContext);
  if (context === undefined) {
    throw new Error('usePageContext must be used within a PageContextProvider');
  }
  return context.pageContext;
};

export const useSetPageContext = () => {
  const context = useContext(PageContext);
  if (context === undefined) {
    throw new Error('useSetPageContext must be used within a PageContextProvider');
  }
  return context.setPageContext;
};
