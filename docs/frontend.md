# Frontend - VacanceAI

React 18 application with TypeScript, Vite, Tailwind CSS, and Framer Motion.

---

## Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | Home | Landing page with Ken Burns hero carousel + popular packages |
| `/search` | Search | Search with filters (price, duration, tags, pagination, URL state) |
| `/packages/:id` | PackageDetail | Package details + booking form |
| `/hotels` | Hotels | TripAdvisor hotels (3-column grid, 3D tilt) |
| `/hotels/:locationId` | HotelDetail | Hotel details + photo gallery + progressive review reveal |
| `/favorites` | Favorites | Saved packages (user's favorites) |
| `/bookings` | Bookings | User's bookings (AG Grid with sort/filter/pagination) |
| `/profile` | Profile | User profile + avatar upload |
| `/login` | Login | Sign in |
| `/signup` | SignUp | Registration |

---

## Main Components

### Layout (`components/Layout.tsx`)
Common structure for all pages:
- `AnimatedBackground`: full-screen Ken Burns background (5 images, crossfade, fixed)
- `Header`: navigation bar with glass effect (`bg-white/80 backdrop-blur-md`)
- `AnimatePresence mode="wait"`: animated page transitions
- `Footer`: footer (`bg-gray-900/95 backdrop-blur-sm`)

### ChatWidget (`components/chat/ChatWidget.tsx`)
Floating chat widget in the bottom-right corner:
- Real-time WebSocket communication
- Reads `PageContext` and sends it with every message
- Handles `ui_actions` returned by the agent (navigation, card display)
- Automatic navigation after booking (`/bookings`) and favorite (`/favorites`)

### PackageCard (`components/packages/PackageCard.tsx`)
Vacation package display card:
- 3D tilt effect with `react-parallax-tilt` (tiltMax 8, glare 0.15, scale 1.02)
- Displays image, name, destination, price, duration, rating

### Animations (`components/animations/`)

| Component | Description |
|-----------|-------------|
| `FadeIn` | Scroll reveal wrapper (direction, delay, duration) with `whileInView` |
| `StaggerContainer` + `StaggerItem` | Staggered animations for lists/grids |
| `PageTransition` | Page entry animation wrapper (opacity + y) |
| `HeroCarousel` | Ken Burns carousel (4 Unsplash images, crossfade, zoom/pan) |
| `AnimatedButton` + `AnimatedLinkButton` | Hover scale+glow, tap scale, spring transition |
| `AnimatedBackground` | Full-screen Ken Burns background (5 images, white/80 overlay + backdrop-blur) |

### Search (`components/search/`)

| Component | Description |
|-----------|-------------|
| `DualRangeSlider` | Dual slider for price and duration |
| `TagFilter` | Tag selection filter |
| `ActiveFilters` | Active filter badges |
| `Pagination` | Results page navigation |

---

## Contexts

### AuthContext (`contexts/AuthContext.tsx`)
JWT authentication management:
- Tokens stored in `localStorage`
- Exposes: `user`, `login()`, `logout()`, `signup()`, `refreshToken()`

### PageContext (`contexts/PageContext.tsx`)
Page context for the AI agent:
- `PageContextProvider`: wraps the application
- `usePageContext()`: reads the current context
- `useSetPageContext()`: updates the context (called in each page)
- Data: current page, route, displayed data

---

## Services

### API Client (`services/api.ts`)
REST client for the backend:
- `authApi`: signup, login, logout, refresh, me, updateProfile, uploadAvatar
- `packagesApi`: list, featured, getById, checkAvailability
- `bookingsApi`: list, create, update, delete
- `favoritesApi`: list, add, remove, check
- `reviewsApi`: getByPackage, create
- `destinationsApi`: list, getById, getPackages
- `conversationsApi`: create, get, sendMessage, delete
- `tripadvisorApi`: getLocations, getLocationsWithDetails, getCountries, getById, getPhotos, getReviews

### Hooks

- `useChat` (`hooks/useChat.ts`): WebSocket hook for chat (connection, send, receive, reconnect)

---

## File Structure

```
frontend/src/
├── components/
│   ├── Layout.tsx
│   ├── animations/
│   │   ├── index.ts
│   │   ├── FadeIn.tsx
│   │   ├── StaggerContainer.tsx
│   │   ├── PageTransition.tsx
│   │   ├── HeroCarousel.tsx
│   │   ├── HeroVideo.tsx
│   │   ├── AnimatedButton.tsx
│   │   └── AnimatedBackground.tsx
│   ├── common/
│   │   ├── Header.tsx
│   │   └── Footer.tsx
│   ├── chat/
│   │   ├── ChatWidget.tsx
│   │   └── ChatErrorBoundary.tsx
│   ├── search/
│   │   ├── DualRangeSlider.tsx
│   │   ├── TagFilter.tsx
│   │   ├── ActiveFilters.tsx
│   │   └── Pagination.tsx
│   └── packages/
│       └── PackageCard.tsx
├── pages/
│   ├── Home.tsx
│   ├── Search.tsx
│   ├── Favorites.tsx
│   ├── PackageDetail.tsx
│   ├── Hotels.tsx
│   ├── HotelDetail.tsx
│   ├── Bookings.tsx
│   ├── Profile.tsx
│   ├── Login.tsx
│   └── SignUp.tsx
├── contexts/
│   ├── AuthContext.tsx
│   └── PageContext.tsx
├── hooks/
│   └── useChat.ts
├── services/
│   ├── api.ts
│   └── tripadvisor.ts
├── utils/
│   ├── uuid.ts
│   └── telemetry.ts
├── types/index.ts
├── App.tsx
└── main.tsx
```

---

## Technical Notes

- **Glass effect**: all cards and panels use `bg-white/90 backdrop-blur-sm`
- **TypeScript**: `ease: 'easeOut' as const` required for Framer Motion variant types
- **React gotcha**: `{num && <JSX>}` renders "0" when num=0, use `{num > 0 && <JSX>}` instead
- **Photos**: `getPhotoUrl` prioritizes `url_large` over `url_medium` for quality
- **Hotels**: single API call (`getLocationsWithDetails`) instead of N+1 queries
