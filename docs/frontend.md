# Frontend - VacanceAI

Application React 18 avec TypeScript, Vite, Tailwind CSS et Framer Motion.

---

## Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | Home | Accueil avec hero carousel Ken Burns + packages populaires |
| `/search` | Search | Recherche avec filtres (prix, duree, tags, pagination, URL state) |
| `/packages/:id` | PackageDetail | Details d'un package + formulaire reservation |
| `/hotels` | Hotels | Hotels TripAdvisor (grille 3 colonnes, tilt 3D) |
| `/hotels/:locationId` | HotelDetail | Details hotel + galerie photos + avis progressifs |
| `/favorites` | Favorites | Mes favoris (packages sauvegardes) |
| `/bookings` | Bookings | Mes reservations (AG Grid avec tri/filtre/pagination) |
| `/profile` | Profile | Profil utilisateur + upload avatar |
| `/login` | Login | Connexion |
| `/signup` | SignUp | Inscription |

---

## Composants principaux

### Layout (`components/Layout.tsx`)
Structure commune a toutes les pages :
- `AnimatedBackground` : fond Ken Burns plein ecran (5 images, crossfade, fixed)
- `Header` : barre de navigation avec glass effect (`bg-white/80 backdrop-blur-md`)
- `AnimatePresence mode="wait"` : transitions de page animees
- `Footer` : pied de page (`bg-gray-900/95 backdrop-blur-sm`)

### ChatWidget (`components/chat/ChatWidget.tsx`)
Widget de chat flottant en bas a droite :
- Communication WebSocket temps reel
- Lit le `PageContext` et l'envoie avec chaque message
- Gere les `ui_actions` retournees par l'agent (navigation, affichage de cartes)
- Navigation automatique apres booking (`/bookings`) et favori (`/favorites`)

### PackageCard (`components/packages/PackageCard.tsx`)
Carte d'affichage d'un package vacances :
- Effet tilt 3D avec `react-parallax-tilt` (tiltMax 8, glare 0.15, scale 1.02)
- Affiche image, nom, destination, prix, duree, rating

### Animations (`components/animations/`)

| Composant | Description |
|-----------|-------------|
| `FadeIn` | Scroll reveal wrapper (direction, delay, duration) avec `whileInView` |
| `StaggerContainer` + `StaggerItem` | Animations echelonnees pour listes/grilles |
| `PageTransition` | Animation d'entree de page (opacity + y) |
| `HeroCarousel` | Carousel Ken Burns (4 images Unsplash, crossfade, zoom/pan) |
| `AnimatedButton` + `AnimatedLinkButton` | Hover scale+glow, tap scale, spring transition |
| `AnimatedBackground` | Fond Ken Burns plein ecran (5 images, overlay blanc/80 + backdrop-blur) |

### Recherche (`components/search/`)

| Composant | Description |
|-----------|-------------|
| `DualRangeSlider` | Slider double pour prix et duree |
| `TagFilter` | Selection de tags de filtrage |
| `ActiveFilters` | Badges des filtres actifs |
| `Pagination` | Navigation entre pages de resultats |

---

## Contexts

### AuthContext (`contexts/AuthContext.tsx`)
Gestion de l'authentification JWT :
- Tokens stockes dans `localStorage`
- Expose : `user`, `login()`, `logout()`, `signup()`, `refreshToken()`

### PageContext (`contexts/PageContext.tsx`)
Contexte de page pour l'agent IA :
- `PageContextProvider` : wraps l'application
- `usePageContext()` : lit le contexte courant
- `useSetPageContext()` : met a jour le contexte (appele dans chaque page)
- Donnees : page courante, route, donnees affichees

---

## Services

### API Client (`services/api.ts`)
Client REST pour le backend :
- `authApi` : signup, login, logout, refresh, me, updateProfile, uploadAvatar
- `packagesApi` : list, featured, getById, checkAvailability
- `bookingsApi` : list, create, update, delete
- `favoritesApi` : list, add, remove, check
- `reviewsApi` : getByPackage, create
- `destinationsApi` : list, getById, getPackages
- `conversationsApi` : create, get, sendMessage, delete
- `tripadvisorApi` : getLocations, getLocationsWithDetails, getCountries, getById, getPhotos, getReviews

### Hooks

- `useChat` (`hooks/useChat.ts`) : hook WebSocket pour le chat (connexion, envoi, reception, reconnexion)

---

## Structure des fichiers

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

## Notes techniques

- **Glass effect** : toutes les cartes et panels utilisent `bg-white/90 backdrop-blur-sm`
- **TypeScript** : `ease: 'easeOut' as const` necessaire pour les variants Framer Motion
- **React gotcha** : `{num && <JSX>}` affiche "0" quand num=0, utiliser `{num > 0 && <JSX>}` a la place
- **Photos** : `getPhotoUrl` priorise `url_large` sur `url_medium` pour la qualite
- **Hotels** : single API call (`getLocationsWithDetails`) au lieu de N+1 requetes
