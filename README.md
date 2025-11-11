# FastVal - Healthcare Claims Processing System

A production-ready healthcare claims processing system that ingests, validates, and manages X12 837 claim files with 835 remittance generation capabilities.

## 🏥 Features

- **X12 837 Parsing**: Support for institutional (837I) and professional (837P) claim formats
- **Data Validation**: Comprehensive validation using Pydantic models
- **PostgreSQL Storage**: Structured claim data storage with full audit trail
- **RESTful API**: FastAPI-based endpoints for claim management
- **React Dashboard**: Modern UI for claim review, filtering, and adjudication simulation
- **835 Remittance**: Generate remittance advice summaries
- **Cloud-Native**: Designed for Azure App Service/AKS deployment
- **CI/CD Ready**: GitHub Actions workflows included

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React     │────────▶│   FastAPI    │────────▶│ PostgreSQL  │
│  Dashboard  │         │   Backend    │         │  Database   │
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  X12 Parser  │
                        │ (837 → Data) │
                        └──────────────┘
```

## 📦 Tech Stack

### Backend
- **FastAPI**: High-performance async API framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and settings management
- **Alembic**: Database migrations
- **pytest**: Testing framework

### Frontend
- **React 18**: UI library
- **Material-UI (MUI)**: Component library
- **Axios**: HTTP client
- **React Router**: Navigation

### Infrastructure
- **Azure Container Apps/AKS**: Container orchestration
- **Azure Database for PostgreSQL**: Managed database
- **Terraform**: Infrastructure as Code
- **GitHub Actions**: CI/CD pipeline
- **Docker**: Containerization

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 14+

### Local Development

1. **Clone and setup**
```bash
cd /home/domjweb/workspace/Python/FastAPI/FastVal
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. **Initialize database**
```bash
alembic upgrade head
```

4. **Run backend**
```bash
uvicorn app.main:app --reload
```

5. **Run frontend** (in another terminal)
```bash
cd frontend
npm install
npm start
```

6. **Or use Docker Compose**
```bash
docker-compose up
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

```
POST   /api/v1/claims/upload           - Upload 837 claim file
GET    /api/v1/claims                  - List all claims
GET    /api/v1/claims/{id}             - Get claim details
PATCH  /api/v1/claims/{id}/status      - Update claim status
POST   /api/v1/claims/{id}/adjudicate  - Simulate adjudication
GET    /api/v1/remittance/{claim_id}   - Generate 835 remittance
GET    /api/v1/health                  - Health check
```

## 🗄️ Database Schema

### Claims Table
- claim_id, claim_type, patient_info, provider_info
- service_lines, diagnosis_codes, total_amount
- status, adjudication_result, created_at, updated_at

### Remittance Table
- remittance_id, claim_id, payment_amount
- adjustment_codes, check_number, payment_date

## 🧪 Testing

```bash
# Backend tests
pytest app/tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
```

## 🌐 Deployment

### Azure Deployment with Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### CI/CD Pipeline

Push to `main` branch triggers:
1. Run tests
2. Build Docker images
3. Push to Azure Container Registry
4. Deploy to Azure Container Apps/AKS


## 🔐 Security

- Environment variables for sensitive data
- CORS configuration for frontend
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy
- Azure Key Vault integration ready




