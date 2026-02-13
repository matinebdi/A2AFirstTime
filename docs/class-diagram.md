# Diagramme de Classes - Backend VacanceAI

![Diagramme de classes](sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-074224.png)

## Description

Ce diagramme represente les 11 modeles SQLAlchemy ORM du backend VacanceAI et leurs relations. Chaque classe correspond a une table Oracle 21c XE.

---

## Modeles principaux

### User
Modele central representant un utilisateur de la plateforme.
- Identifiant UUID genere par Oracle (`SYS_GUID()`)
- Mot de passe hashe avec bcrypt
- Relations : possede des reservations, favoris, avis et tokens de refresh

### Destination
Lieu de voyage (pays + ville) avec coordonnees GPS et tags de categorisation.
- 15 destinations pre-chargees (une par pays)
- Contient un rating moyen et un nombre total d'avis
- Methodes de serialisation : `to_dict()`, `to_summary_dict()` (sans timestamps), `to_minimal_dict()` (nom + pays + image)

### Package
Offre de vacances tout compris rattachee a une destination.
- Prix par personne, duree en jours, capacite max
- Listes JSON : inclus, non-inclus, points forts, galerie images
- Periode de disponibilite (`available_from` / `available_to`)
- 30 packages pre-charges (2 par destination : Explorer + Premium)
- Methodes : `to_dict_with_destination()` (avec destination imbriquee), `to_booking_dict()`, `to_favorite_dict()`

### Booking
Reservation d'un package par un utilisateur.
- Statut : `pending`, `confirmed`, `cancelled`
- Statut de paiement : `unpaid`, `paid`, `refunded`
- Calcul automatique du prix total (`price_per_person * num_persons`)
- Methode `to_dict_with_joins()` imbrique le package et sa destination

### Favorite
Association utilisateur-package (table pivot).
- Contrainte d'unicite `UNIQUE(user_id, package_id)` : un package ne peut etre en favori qu'une fois
- Methode `to_dict_with_joins()` imbrique le package et sa destination

### Review
Avis laisse par un utilisateur sur un package, optionnellement lie a une reservation.
- Note de 1 a 5 (champ `rating`)
- Commentaire stocke en CLOB Oracle
- Methode `to_dict_with_user()` imbrique les infos auteur (prenom, nom, avatar)

### Conversation
Historique de chat avec l'assistant IA.
- Identifiant fourni par le frontend (pas de `SYS_GUID()`)
- Messages et contexte stockes en JSON dans des CLOB Oracle
- Relation `SET NULL` vers User (conversation conservee meme si l'utilisateur est supprime)

---

## Modeles TripAdvisor

### TripAdvisorLocation
Hotel importe depuis l'API TripAdvisor.
- `location_id` : identifiant TripAdvisor (unique)
- Adresse stockee en JSON (`address_obj`)
- Rating, nombre d'avis, niveau de prix
- Methode `to_dict_with_details()` imbrique photos, avis et calcule le rating moyen

### TripAdvisorPhoto
Photo d'un hotel TripAdvisor.
- 4 tailles d'URL : original, large, medium, small
- Flag `uploaded_to_storage` pour migration eventuelle vers un stockage propre

### TripAdvisorReview
Avis TripAdvisor sur un hotel.
- Auteur (`username`), localisation, type de voyage
- Date de publication et date du sejour

---

## Relations

| Relation | Type | Cascade |
|----------|------|---------|
| User -> RefreshToken | 1:N | CASCADE (suppression en cascade) |
| User -> Booking | 1:N | CASCADE |
| User -> Favorite | 1:N | CASCADE |
| User -> Review | 1:N | CASCADE |
| User -> Conversation | 1:N | SET NULL |
| Destination -> Package | 1:N | CASCADE |
| Package -> Booking | 1:N | - |
| Package -> Favorite | 1:N | CASCADE |
| Package -> Review | 1:N | CASCADE |
| Booking -> Review | 1:N | - |
| TripAdvisorLocation -> TripAdvisorPhoto | 1:N | viewonly (jointure sur `location_id` string) |
| TripAdvisorLocation -> TripAdvisorReview | 1:N | viewonly (jointure sur `location_id` string) |

---

## Types personnalises Oracle

| Type SQLAlchemy | Stockage Oracle | Utilisation |
|---|---|---|
| `JSONEncodedCLOB` | CLOB | Tags, included, not_included, highlights, images, messages, context, address_obj |
| `OracleBoolean` | NUMBER(1) | is_active (Package), uploaded_to_storage (Photo) |
| `String(36)` + `SYS_GUID()` | VARCHAR2(36) | Tous les identifiants (sauf Conversation) |
| `TIMESTAMP(timezone=True)` | TIMESTAMP WITH TIME ZONE | created_at, updated_at, expires_at, published_date |

---

## Patterns cles

- **`joinedload()`** : chargement eager des relations pour eviter les requetes N+1
- **`to_dict()` et variantes** : serialisation des modeles vers dict/JSON pour l'API
- **`_f()` helper** : conversion `Decimal` -> `float` pour la serialisation JSON
- **`updated_at`** : gere par des triggers Oracle (pas par SQLAlchemy)
- **`sa_text()`** : alias de `sqlalchemy.text` pour eviter le conflit avec `TripAdvisorReview.text`
