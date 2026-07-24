# AutoInsure Connect

**Enterprise Insurance Management Platform**

AutoInsure Connect is a complete cloud-based Insurance Management Platform (Insurance ERP / Insurance Operating System) that hosts the complete digital operations of multiple insurance companies inside one secure multi-tenant SaaS platform.

---

## Architecture

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui, React Query |
| **Backend** | Python 3.12, Django 5.1, Django REST Framework 3.15 |
| **Database** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **Task Queue** | Celery 5.4 + Redis |
| **Object Storage** | AWS S3 compatible |
| **Reverse Proxy** | Nginx |
| **Containerization** | Docker + Docker Compose |
| **CI/CD** | GitHub Actions |
| **API Docs** | Swagger / ReDoc (drf-spectacular) |

### Architecture Principles

- Clean Architecture
- Domain-Driven Design (DDD)
- SOLID Principles
- Repository Pattern
- Service Layer
- Event-Driven Design
- Feature-First Organization
- Multi-Tenant Isolation

---

## Modules

### Business Domain Apps

| App | Description |
|-----|-------------|
| **customers** | Customer management, profiles, vehicles, documents |
| **products** | Insurance product catalog, variants, pricing rules |
| **policies** | Policy lifecycle (draft, active, expired, cancelled), endorsements, renewals |
| **quotes** | Quote engine, versioning, conversion to policy |
| **claims** | Claims management, assessments, investigations, payments |
| **payments** | Payment processing, invoices, receipts |
| **commissions** | Commission structures, calculations, payments |
| **agents** | Agent management, performance tracking |
| **brokers** | Broker management, credit limits, settlements |
| **dealers** | Dealer management, vehicle insurance |
| **branches** | Branch office management |
| **underwriting** | Underwriting rules, decisions, referral queue |

### Platform Apps

| App | Description |
|-----|-------------|
| **authentication** | JWT auth, MFA, sessions, password reset |
| **users** | User management, RBAC (18 roles) |
| **tenants** | Multi-tenant management, invitations |
| **notifications** | Email/SMS/push/in-app notifications, templates |
| **documents** | Document management, versioning |
| **reports** | Report generation, scheduling |
| **audit** | Audit logging, data change tracking |
| **integrations** | Third-party integration management |
| **ai_features** | AI models, predictions, fraud detection |
| **workflows** | Workflow automation, templates, steps |
| **core** | Shared models, permissions, exceptions, pagination |

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+

### Quick Start (Docker)

```bash
# Clone the repository
git clone https://github.com/nairobytes/autoinsure-connect.git
cd autoinsure-connect

# Copy environment file
cp .env.example .env

# Start all services
docker compose up -d

# Run migrations
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1/
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

### Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements/development.txt
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev
```

---

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout
- `POST /api/v1/auth/token/refresh/` - Refresh token
- `GET /api/v1/auth/me/` - Current user
- `POST /api/v1/auth/change-password/` - Change password
- `POST /api/v1/auth/password-reset/` - Request password reset
- `POST /api/v1/auth/mfa/enable/` - Enable MFA
- `POST /api/v1/auth/mfa/verify/` - Verify MFA

### Business Resources (CRUD + Filters)
- `GET/POST /api/v1/customers/` - List/Create customers
- `GET/POST /api/v1/policies/` - List/Create policies
- `GET/POST /api/v1/claims/` - List/Create claims
- `GET/POST /api/v1/quotes/` - List/Create quotes
- `GET/POST /api/v1/payments/` - List/Create payments
- `GET/POST /api/v1/products/` - List/Create products
- `GET/POST /api/v1/agents/` - List/Create agents
- `GET/POST /api/v1/brokers/` - List/Create brokers
- `GET/POST /api/v1/dealers/` - List/Create dealers
- `GET/POST /api/v1/branches/` - List/Create branches
- `GET/POST /api/v1/commissions/` - List/Create commissions
- `GET/POST /api/v1/underwriting/` - Underwriting decisions
- `GET/POST /api/v1/notifications/` - Notifications
- `GET/POST /api/v1/audit/` - Audit logs
- `GET/POST /api/v1/reports/` - Reports

All endpoints support:
- **Pagination**: `?page=1&page_size=20`
- **Search**: `?search=query`
- **Filtering**: `?status=active&role=agent`
- **Sorting**: `?ordering=-created_at`

---

## User Roles

| Role | Description |
|------|-------------|
| Platform Administrator | Full system access |
| Company Administrator | Tenant-level admin |
| Branch Manager | Branch operations |
| Underwriter | Risk assessment |
| Claims Officer | Claims processing |
| Finance Officer | Financial operations |
| Agent | Sales agent |
| Broker | Insurance broker |
| Dealer | Vehicle dealer |
| Customer | End customer |
| Surveyor | Damage assessment |
| Vehicle Inspector | Vehicle inspections |
| Repair Garage | Repair management |
| Call Centre | Support operations |
| Support Team | Customer support |
| Compliance Officer | Regulatory compliance |
| Executive Management | Analytics & reporting |
| Auditor | Audit trail review |

---

## Database

### Key Features
- UUID primary keys
- Multi-tenant isolation via `tenant` foreign key
- Soft deletes with restore capability
- Audit trail on all data changes
- Optimistic locking where appropriate
- Comprehensive indexing for query performance
- Database constraints for data integrity

### Entity Relationship

```
Tenant
├── User (18 roles)
├── Branch
├── Customer
│   ├── CustomerVehicle
│   ├── CustomerDocument
│   └── CustomerContact
├── Product
│   ├── ProductCategory
│   ├── ProductVariant
│   ├── ProductPricing
│   └── ProductDocument
├── Policy
│   ├── PolicyEndorsement
│   ├── PolicyRenewal
│   ├── PolicyCancellation
│   └── PolicyDocument
├── Quote
│   ├── QuoteItem
│   └── QuoteVersion
├── Claim
│   ├── ClaimActivity
│   ├── ClaimDocument
│   ├── ClaimAssessment
│   ├── ClaimPayment
│   └── ClaimInvestigation
├── Payment
│   ├── Invoice
│   └── Receipt
├── Commission
│   ├── CommissionStructure
│   └── CommissionPayment
├── Agent
├── Broker
├── Dealer
├── Notification
├── Document
├── AuditLog
├── Integration
├── Workflow
└── AI Model
```

---

## Security

- JWT authentication with refresh token rotation
- Multi-factor authentication (TOTP)
- Role-based access control (18 roles)
- Tenant data isolation
- Rate limiting (100/hr anonymous, 1000/hr authenticated)
- OWASP Top 10 protections
- SQL injection protection (Django ORM)
- XSS protection
- CSRF protection
- Input validation (Zod + DRF serializers)
- Audit logging on all mutations
- Secrets management via environment variables
- HTTPS enforcement in production
- Content Security Policy headers

---

## Deployment

### Production

```bash
# Set production environment
export DJANGO_SETTINGS_MODULE=config.settings.production
export DJANGO_DEBUG=false

# Docker Compose production
docker compose -f docker-compose.yml up -d
```

### Environment Variables

See `.env.example` for all required environment variables.

---

## License

MIT License - Copyright (c) 2026 Nairobytes Tech
