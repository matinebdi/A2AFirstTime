import axios from 'axios';
import type { Package, Destination, Booking, AuthResponse, User, TripAdvisorLocation, TripAdvisorPhoto, TripAdvisorReview } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors - try refresh token before redirecting
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          return api(originalRequest);
        } catch {
          // Refresh failed
        }
      }
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const authApi = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const { data } = await api.post('/api/auth/login', { email, password });
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  },

  signup: async (
    email: string,
    password: string,
    firstName: string,
    lastName: string
  ): Promise<{ user_id: string }> => {
    const { data } = await api.post('/api/auth/signup', {
      email,
      password,
      first_name: firstName,
      last_name: lastName,
    });
    return data;
  },

  logout: async (): Promise<void> => {
    await api.post('/api/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  refresh: async (refreshToken: string): Promise<AuthResponse> => {
    const { data } = await api.post('/api/auth/refresh', {
      refresh_token: refreshToken,
    });
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  },

  getProfile: async (): Promise<User> => {
    const { data } = await api.get('/api/auth/me');
    return data;
  },
};

// Destinations
export const destinationsApi = {
  list: async (params?: { country?: string; tags?: string; limit?: number }) => {
    const { data } = await api.get('/api/destinations', { params });
    return data.destinations as Destination[];
  },

  get: async (id: string): Promise<Destination & { packages: Package[] }> => {
    const { data } = await api.get(`/api/destinations/${id}`);
    return data;
  },
};

// Packages
export const packagesApi = {
  list: async (params?: {
    destination?: string;
    min_price?: number;
    max_price?: number;
    min_duration?: number;
    max_duration?: number;
    limit?: number;
    offset?: number;
  }) => {
    const { data } = await api.get('/api/packages', { params });
    return data as { packages: Package[]; total: number };
  },

  featured: async (limit = 6): Promise<Package[]> => {
    const { data } = await api.get('/api/packages/featured', { params: { limit } });
    return data.packages;
  },

  get: async (id: string): Promise<Package> => {
    const { data } = await api.get(`/api/packages/${id}`);
    return data;
  },

  checkAvailability: async (
    id: string,
    startDate: string,
    numPersons: number
  ) => {
    const { data } = await api.get(`/api/packages/${id}/availability`, {
      params: { start_date: startDate, num_persons: numPersons },
    });
    return data;
  },
};

// Bookings
export const bookingsApi = {
  list: async (status?: string): Promise<Booking[]> => {
    const { data } = await api.get('/api/bookings', { params: { status } });
    return data.bookings;
  },

  get: async (id: string): Promise<Booking> => {
    const { data } = await api.get(`/api/bookings/${id}`);
    return data;
  },

  create: async (booking: {
    package_id: string;
    start_date: string;
    num_persons: number;
    special_requests?: string;
  }): Promise<{ booking: Booking }> => {
    const { data } = await api.post('/api/bookings', booking);
    return data;
  },

  cancel: async (id: string): Promise<{ booking: Booking }> => {
    const { data } = await api.delete(`/api/bookings/${id}`);
    return data;
  },
};

// Favorites
export const favoritesApi = {
  list: async () => {
    const { data } = await api.get('/api/favorites');
    return data.favorites as Array<{ packages: Package }>;
  },

  add: async (packageId: string) => {
    const { data } = await api.post(`/api/favorites/${packageId}`);
    return data;
  },

  remove: async (packageId: string) => {
    const { data } = await api.delete(`/api/favorites/${packageId}`);
    return data;
  },

  check: async (packageId: string): Promise<{ is_favorite: boolean }> => {
    const { data } = await api.get(`/api/favorites/check/${packageId}`);
    return data;
  },
};

// Conversations
export const conversationsApi = {
  create: async (): Promise<{ conversation_id: string }> => {
    const { data } = await api.post('/api/conversations/new');
    return data;
  },

  get: async (id: string) => {
    const { data } = await api.get(`/api/conversations/${id}`);
    return data;
  },

  sendMessage: async (
    id: string,
    message: string,
    context?: Record<string, unknown>
  ) => {
    const { data } = await api.post(`/api/conversations/${id}/message`, {
      message,
      context,
    });
    return data;
  },

  clear: async (id: string) => {
    const { data } = await api.delete(`/api/conversations/${id}`);
    return data;
  },
};

// TripAdvisor (via backend API)
export const tripadvisorApi = {
  getLocations: async (country?: string): Promise<TripAdvisorLocation[]> => {
    const { data } = await api.get('/api/tripadvisor/locations', {
      params: country ? { country } : {},
    });
    return data.locations;
  },

  getLocation: async (locationId: string): Promise<TripAdvisorLocation | null> => {
    const { data } = await api.get(`/api/tripadvisor/locations/${locationId}`);
    return data;
  },

  getPhotos: async (locationId: string): Promise<TripAdvisorPhoto[]> => {
    const { data } = await api.get(`/api/tripadvisor/locations/${locationId}/photos`);
    return data.photos;
  },

  getReviews: async (locationId: string): Promise<TripAdvisorReview[]> => {
    const { data } = await api.get(`/api/tripadvisor/locations/${locationId}/reviews`);
    return data.reviews;
  },

  getCountries: async (): Promise<string[]> => {
    const { data } = await api.get('/api/tripadvisor/countries');
    return data.countries;
  },

  getLocationDetails: async (locationId: string) => {
    const [location, photos, reviews] = await Promise.all([
      tripadvisorApi.getLocation(locationId),
      tripadvisorApi.getPhotos(locationId),
      tripadvisorApi.getReviews(locationId),
    ]);
    return { location, photos, reviews };
  },

  getPhotoUrl: (photo: TripAdvisorPhoto): string => {
    return photo.url_medium || photo.url_large || photo.url_original;
  },
};

export default api;
