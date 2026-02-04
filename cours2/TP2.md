# TP Flask avancé — API + SQL (IA générative autorisée)

> **IA générative utilisable** (ChatGPT, Copilot, etc.).  

> 📌 **Rendu final : dépôt GitHub** (lien fourni le jour du rendu).

---

## Partie 1 — Modèle métier (fonctionnalités à implémenter)

Vous développez une API REST pour une université qui prête du matériel (caméras, micros, PC…) et permet la réservation de ressources. Le système doit être **multi-organisation** (multi-tenant), avec **règles métier strictes**, **audit**, et **gestion des conflits**.

### 1.1 Entités obligatoires (minimum)

#### Organisation & utilisateurs
- **Organization**
  - `id`, `name`, `timezone`, `created_at`
- **User**
  - `id`, `org_id`, `email`, `password_hash`, `full_name`, `is_active`, `created_at`
- **Role**
  - `id`, `name` (au minimum : `student`, `staff`, `admin`)
- **UserRole**
  - `user_id`, `role_id`, `org_id`
  - **Remarque** : rôles attribués **par organisation**, pas globalement.

#### Inventaire
- **Resource**
  - `id`, `org_id`, `type`, `name`, `description`, `serial_number`
  - `status` (ex : AVAILABLE, MAINTENANCE, DISABLED)
  - `version` (pour optimistic locking)
  - `created_at`, `deleted_at` (soft delete)
- **Tag**
  - `id`, `org_id`, `name`
- **ResourceTag**
  - `resource_id`, `tag_id`
- **ResourceUnit**
  - `id`, `resource_id`, `barcode`, `condition`, `status`
  - Permet plusieurs exemplaires d’une ressource (ex : 5 micros identiques).

#### Réservation
- **Booking**
  - `id`, `org_id`, `requester_user_id`
  - `status` (ex : DRAFT, PENDING, APPROVED, REJECTED, CANCELLED)
  - `start_at`, `end_at`, `purpose`
  - `version` (optimistic locking)
  - `created_at`, `cancelled_at`
- **BookingItem**
  - `id`, `booking_id`, `resource_unit_id`, `quantity`
  - Option : imposer `quantity=1` si vous préférez la simplicité.

> **Règle centrale** : une `ResourceUnit` ne peut pas être engagée dans deux `Booking` qui se chevauchent, pour des statuts actifs (ex : PENDING/APPROVED).

#### Attente / arbitrage (complexité)
- **WaitlistEntry**
  - `id`, `booking_request_id` (ou `booking_id` si vous modélisez une demande comme un booking)
  - `priority_score`, `created_at`
  - Statuts possibles : WAITING, OFFERED, ACCEPTED, EXPIRED, CANCELLED

Quand une ressource n’est pas disponible :
- l’utilisateur crée une **demande**,
- le système l’ajoute à la **waitlist**,
- si une ressource se libère, une offre peut être faite à la meilleure demande.

#### Audit (traçabilité)
- **AuditEvent**
  - `id`, `org_id`, `actor_user_id`
  - `entity_type`, `entity_id`
  - `action` ∈ {CREATE, UPDATE, SOFT_DELETE, RESTORE, STATUS_CHANGE}
  - `before_json`, `after_json`, `at`

---

## Partie 2 — Règles métier (anti “copier-coller IA”)

### 2.1 Réservation sans double booking (course critique)
Deux utilisateurs peuvent envoyer `POST /bookings` au même moment.  
Vous devez garantir **au niveau transactionnel** qu’une `ResourceUnit` ne sera pas réservée deux fois sur une période qui se chevauche.

Attendu (choisir une stratégie et la justifier) :
- verrouillage SQL (`SELECT ... FOR UPDATE`) + transaction
- contrainte DB (ex : PostgreSQL exclusion constraint) + gestion d’erreur
- stratégie mixte (contrainte + retry contrôlé)

**À prouver** par tests (voir partie tests du TP) : en concurrence, une seule réservation doit passer.

### 2.2 Arbitrage + file d’attente
Si indisponible :
- création d’une demande + entrée en waitlist
- un `staff/admin` peut arbitrer : accepter, refuser, proposer alternative

Si une réservation est annulée :
- le système doit pouvoir proposer la ressource au premier de la waitlist
- statuts recommandés : `OFFERED` avec expiration (ex: TTL 10 minutes)

### 2.3 Calcul de priorité (SQL non trivial)
Le `priority_score` dépend de (au minimum) :
- ancienneté de la demande
- rôle (staff > student)
- pénalités (retards/amendes précédents)
- nombre de réservations actives (moins il y en a, plus le score monte)

**Exigence** : au moins un endpoint doit utiliser une requête DB **non triviale** :
- CTE / window function / agrégations / vue matérialisée (Postgres)
- ou équivalent documenté

### 2.4 Versioning & conflits (optimistic locking)
Sur au moins 2 ressources, imposer :
- `ETag` dans la réponse
- `If-Match` obligatoire dans `PATCH`
- si `version` ne correspond pas : `412 Precondition Failed` (ou `409`, mais cohérent partout)

Endpoints minimum :
- `PATCH /resources/{id}`
- `PATCH /bookings/{id}`

### 2.5 Idempotence
Sur 2 endpoints critiques :
- accepter `Idempotency-Key`
- même clé + même user + même org => **même réponse**, sans dupliquer l’action

Endpoints conseillés :
- `POST /bookings`
- `POST /fines/payments` (ou équivalent si vous implémentez amendes/retards)

### 2.6 Multi-tenant : isolation stricte
Toutes les tables métier doivent avoir `org_id` (ou une chaîne de relation sûre) et toutes les requêtes doivent filtrer correctement.
- header obligatoire : `X-Org-Id`
- aucun endpoint ne doit permettre d’accéder à des données d’une autre org

### 2.7 Soft delete + règles
- suppression logique (`deleted_at`)
- endpoints de restore
- règles : une ressource soft-delete ne peut plus être réservée (sauf restore)

### 2.8 Audit obligatoire
Chaque action CREATE/UPDATE/SOFT_DELETE/RESTORE/STATUS_CHANGE crée un `AuditEvent`.

---

## Partie 3 — API à implémenter (spécification minimale)

> **Toutes les routes** (sauf login/health) nécessitent :
> - `Authorization: Bearer <token>`
> - `X-Org-Id: <org_id>`

### 3.1 Auth
- `POST /auth/register`  
  - (au choix) réservé admin, ou bootstrap contrôlé
- `POST /auth/login` → JWT
- `POST /auth/refresh`
- Middleware :
  - vérifie token
  - vérifie `X-Org-Id`
  - applique RBAC

### 3.2 Resources / Inventory
- `GET /resources`  
  - pagination + tri + filtres : `type`, `status`, `tag`, `q`, `created_from/to`, `include_deleted`
- `POST /resources` (staff/admin)
- `GET /resources/{id}`
- `PATCH /resources/{id}` (optimistic locking via `If-Match`)
- `DELETE /resources/{id}` (soft delete)
- `POST /resources/{id}/restore`

### 3.3 Booking
- `POST /bookings` (Idempotency-Key obligatoire)
  - body : `start_at`, `end_at`, `items`, `purpose`
  - règle : empêcher chevauchement sur `ResourceUnit`
- `GET /bookings`  
  - filtres : `status`, `requester`, range dates, tri
- `GET /bookings/{id}`
- `PATCH /bookings/{id}` (optimistic locking)
- `POST /bookings/{id}/cancel`
- `POST /bookings/{id}/approve` (staff/admin)
- `POST /bookings/{id}/reject` (staff/admin)

### 3.4 Waitlist / Arbitration
- `POST /waitlist`  
  - crée une demande si indisponible
  - calcule et stocke `priority_score`
- `GET /waitlist` (staff/admin)
  - tri par score + pagination
- `POST /waitlist/{id}/offer` (staff/admin)
- `POST /waitlist/{id}/accept` (utilisateur)
- `POST /waitlist/{id}/expire` (admin ou job simulé)

### 3.5 Audit & Admin
- `GET /audit` (staff/admin)
  - filtres : `entity_type`, `entity_id`, `actor`, `date range`, `action`
- `GET /health` (public)

---

## Rendu (GitHub)

Le rendu final est **un dépôt GitHub** contenant :
- code source + README (installation, exécution, migrations)
- documentation API (Swagger/OpenAPI accessible)
- scripts de seed (optionnel mais recommandé)