import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authApi } from '../services/api';
import type { User } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signUp: (email: string, password: string, firstName: string, lastName: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if we have a stored token and load user profile
    const token = localStorage.getItem('access_token');
    if (token) {
      authApi
        .getProfile()
        .then((profile) => {
          setUser({
            id: profile.id,
            email: profile.email,
            first_name: profile.first_name,
            last_name: profile.last_name,
            created_at: profile.created_at,
          });
        })
        .catch(() => {
          // Token invalid or expired, try refresh
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            authApi
              .refresh(refreshToken)
              .then(() => authApi.getProfile())
              .then((profile) => {
                setUser({
                  id: profile.id,
                  email: profile.email,
                  first_name: profile.first_name,
                  last_name: profile.last_name,
                  created_at: profile.created_at,
                });
              })
              .catch(() => {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
              });
          } else {
            localStorage.removeItem('access_token');
          }
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const signUp = async (email: string, password: string, firstName: string, lastName: string) => {
    await authApi.signup(email, password, firstName, lastName);
  };

  const signIn = async (email: string, password: string) => {
    const data = await authApi.login(email, password);
    setUser({
      id: data.user.id,
      email: data.user.email,
      first_name: data.user.first_name,
      last_name: data.user.last_name,
      created_at: data.user.created_at ?? new Date().toISOString(),
    });
  };

  const signOut = async () => {
    try {
      await authApi.logout();
    } catch {
      // Ignore errors on logout
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, signUp, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
