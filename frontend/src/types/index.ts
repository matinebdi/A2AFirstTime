// VacanceAI Types

export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  avatar_url?: string;
  preferences?: UserPreferences;
  created_at: string;
}

export interface UserPreferences {
  budget?: string;
  destinations_preferred?: string[];
}

export interface Destination {
  id: string;
  name: string;
  country: string;
  city?: string;
  description?: string;
  image_url?: string;
  tags: string[];
  average_rating: number;
  created_at: string;
}

export interface Package {
  id: string;
  destination_id: string;
  name: string;
  description?: string;
  duration_days: number;
  price_per_person: number;
  max_persons: number;
  included?: PackageIncludes;
  not_included?: string[];
  highlights?: string[];
  image_url?: string;
  available_from: string;
  available_to: string;
  is_active: boolean;
  images: string[];
  hotel_category?: number;
  created_at: string;
  // Joined data
  destinations?: Destination;
  reviews?: Review[];
}

export interface PackageIncludes {
  transport: string;
  hotel: string;
  meals: string;
  activities: string[];
  transfers: string;
}

export interface Booking {
  id: string;
  user_id: string;
  package_id: string;
  status: BookingStatus;
  start_date: string;
  end_date: string;
  num_persons: number;
  total_price: number;
  payment_status: PaymentStatus;
  special_requests?: string;
  created_at: string;
  // Joined data
  packages?: Package;
}

export type BookingStatus = 'pending' | 'confirmed' | 'cancelled' | 'completed';
export type PaymentStatus = 'unpaid' | 'paid' | 'refunded';

export interface Review {
  id: string;
  user_id: string;
  package_id: string;
  booking_id: string;
  rating: number;
  comment?: string;
  created_at: string;
  // Joined data
  users?: Pick<User, 'first_name' | 'last_name' | 'avatar_url'>;
}

export interface Favorite {
  id: string;
  user_id: string;
  package_id: string;
  created_at: string;
  // Joined data
  packages?: Package;
}

export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  ui_actions?: UIAction[];
}

export interface UIAction {
  action: string;
  [key: string]: unknown;
}

export interface Conversation {
  id: string;
  user_id?: string;
  messages: ChatMessage[];
  context?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

// API Response types
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user: User;
}

// TripAdvisor Types
export interface TripAdvisorLocation {
  id: string;
  location_id: string;
  name: string;
  address_obj: {
    street1?: string;
    street2?: string;
    city?: string;
    state?: string;
    country?: string;
    postalcode?: string;
    address_string?: string;
  };
  search_country: string;
  category: string;
  created_at: string;
}

export interface TripAdvisorPhoto {
  id: string;
  location_id: string;
  photo_id: string;
  url_original: string;
  url_large: string;
  url_medium: string;
  url_small: string;
  caption?: string;
  uploaded_to_storage: boolean;
  storage_path?: string;
  created_at: string;
}

export interface TripAdvisorReview {
  id: string;
  location_id: string;
  review_id: string;
  rating: number;
  title: string;
  text: string;
  published_date: string;
  user_name: string;
  created_at: string;
}
