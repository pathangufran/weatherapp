# 🌦️ Weather Tracker Backend

A production-ready Weather Tracking Backend built using **Django REST Framework**, **PostgreSQL**, **Redis**, **Celery**, and **Docker**. The application allows users to monitor weather conditions, configure custom weather alerts, receive notifications, and analyze weather trends through an analytics dashboard.

---

# 🚀 Features

## Authentication

- JWT Authentication
- User Registration & Login
- Refresh Token Support
- Secure Password Management

---

## City Management

- Add Multiple Cities
- Track Favourite Cities
- CRUD Operations
- Optimized Database Queries

---

## Weather

- Current Weather
- Latest Weather
- Weather History
- Weather Forecast
- Automatic Weather Synchronization
- Redis Caching

---

## Weather Alerts

- Create Alert
- Update Alert
- Delete Alert
- Enable / Disable Alert
- Temperature Alerts
- Humidity Alerts
- Pressure Alerts
- Wind Speed Alerts

---

## Notification System

- Alert Notifications
- Mark Notification as Read
- Mark All as Read
- Notification History
- Celery Background Processing

---

## Dashboard & Analytics

- Dashboard Summary
- Weather Analytics
- Weather Trends
- City Analytics
- Alert Analytics
- Notification Analytics
- Recent Activity Feed

---

## Background Jobs

- Celery Worker
- Celery Beat
- Periodic Weather Sync
- Alert Evaluation
- Notification Generation

---

## Production Ready Features

- Docker
- Gunicorn
- Nginx
- PostgreSQL
- Redis
- Health Check APIs
- Environment-based Settings
- Rate Limiting
- OpenAPI Documentation
- Swagger UI
- ReDoc
- Structured Logging

---

# 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.13 |
| Framework | Django 5.x |
| API | Django REST Framework |
| Authentication | Simple JWT |
| Database | PostgreSQL |
| Cache | Redis |
| Task Queue | Celery |
| Scheduler | Celery Beat |
| Containerization | Docker |
| Web Server | Gunicorn |
| Reverse Proxy | Nginx |
| Documentation | drf-spectacular |
| CI | GitHub Actions |

---

# 📁 Project Structure

```text
weather-tracker/

├── accounts/
├── alerts/
├── cities/
├── dashboard/
├── weatherapp/
├── common/
│   ├── cache/
│   ├── health/
│   ├── middleware/
│   ├── throttling.py
│   └── responses.py
│
├── weather/
│   ├── settings/
│   ├── urls.py
│   ├── celery.py
│   ├── wsgi.py
│   └── asgi.py
│
├── docker/
│   ├── development/
│   └── production/
│
├── nginx/
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

---

# 🏗️ Architecture

```
                        Client
                           │
                           ▼
                     Nginx Reverse Proxy
                           │
                           ▼
                        Gunicorn
                           │
                           ▼
                   Django REST Framework
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
      PostgreSQL        Redis        Celery
                                           │
                                           ▼
                                     Celery Beat
```

```
                                    +----------------------+
                                    |      Client App      |
                                    | Web / Mobile / Postman|
                                    +----------+-----------+
                                               |
                                               |
                                         HTTP / HTTPS
                                               |
                                               v
                                    +----------------------+
                                    |        Nginx         |
                                    | Reverse Proxy        |
                                    | Static Files         |
                                    | SSL Termination      |
                                    +----------+-----------+
                                               |
                                               |
                                               v
                                    +----------------------+
                                    |      Gunicorn        |
                                    | WSGI Application     |
                                    +----------+-----------+
                                               |
                                               |
                                               v
                 +------------------------------------------------------+
                 |                Django REST Framework                  |
                 +------------------------------------------------------+
                  |           |             |            |              |
                  |           |             |            |              |
                  v           v             v            v              v
            +----------+ +----------+ +-----------+ +-----------+ +-----------+
            | Accounts | | Weather  | | Alerts    | | Dashboard | | Analytics |
            +----------+ +----------+ +-----------+ +-----------+ +-----------+
                  |            |            |             |
                  |            |            |             |
                  +------------+------------+-------------+
                               |
                               |
                    +----------+-----------+
                    |      PostgreSQL      |
                    | Users, Cities,       |
                    | Weather History      |
                    | Alerts, Analytics    |
                    +----------------------+

                               ^
                               |
                    +----------+-----------+
                    |         Redis        |
                    | Cache                |
                    | Celery Broker        |
                    +----------+-----------+
                               ^
                               |
                    +----------+-----------+
                    |      Celery Worker   |
                    +----------+-----------+
                               ^
                               |
                    +----------+-----------+
                    |      Celery Beat     |
                    | Periodic Scheduler   |
                    +----------------------+

```

---

# ⚡ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/weather-tracker.git

cd weather-tracker
```

---

## Install Dependencies

```bash
uv sync
```

---

## Configure Environment

Create

```
.env
```

Example

```env
SECRET_KEY=your_secret_key

DEBUG=True

POSTGRES_DB=POSTGRES_DB

POSTGRES_USER=POSTGRES_USER

POSTGRES_PASSWORD=POSTGRES_PASSWORD

POSTGRES_HOST=POSTGRES_HOST

POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/0
```

---

## Apply Migrations

```bash
python manage.py migrate
```

---

## Create Superuser

```bash
python manage.py createsuperuser
```

---

## Run Development Server

```bash
python manage.py runserver
```

---

# 🐳 Docker

Development

```bash
docker compose up --build
```

Production

```bash
docker compose -f docker-compose.prod.yml up --build
```

---

# 📚 API Documentation

Swagger

```
/api/docs/
```

ReDoc

```
/api/redoc/
```

OpenAPI Schema

```
/api/schema/
```

---

# ❤️ Health Check

Basic

```
GET /health/
```

Detailed

```
GET /health/detailed/
```

---

# 🚦 Rate Limiting

| API | Rate Limit |
|------|------------|
| Login | 5/min |
| Register | 3/min |
| Refresh Token | 20/min |
| Weather APIs | 100/min |
| Dashboard APIs | 60/min |
| Alert APIs | 30/min |

---

# 🔄 Background Tasks

- Weather Synchronization
- Alert Evaluation
- Notification Generation
- Scheduled Jobs using Celery Beat

---

# 🔐 Security

- JWT Authentication
- Secure Cookies
- HTTPS Ready
- HSTS
- CSRF Protection
- XSS Protection
- Clickjacking Protection
- Non-root Docker Container
- Reverse Proxy using Nginx

---

# 📈 Performance Optimizations

- Redis Caching
- Optimized ORM Queries
- select_related()
- prefetch_related()
- annotate()
- aggregate()
- Database Indexing
- Background Processing
- Docker Layer Caching

---

# 🧪 Testing

```bash
python manage.py test
```
---

# 🎯 Future Improvements

GitHub Actions automatically performs:

- Install Dependencies
- Ruff Linting
- Format Checking
- Django System Check
- Unit Tests
- Docker Build Verification

- AWS EC2 Deployment
- Amazon RDS
- ElastiCache Redis
- S3 Media Storage
- Prometheus Metrics
- Grafana Monitoring
- Kubernetes Deployment
- WebSocket Notifications

---

# 👨‍💻 Author

**Gufran Pathan**

Backend Developer | Python | Django | Django REST Framework | PostgreSQL | Redis | Docker | AWS
