# 🎬 CineMitr Dashboard - Production Ready

A professional, modular Streamlit dashboard for content management with comprehensive API integration, security features, and production deployment capabilities.

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## 🚀 Features

### 🏗️ **Enterprise Architecture**
- **Modular Design**: Clean separation of concerns with dedicated modules
- **Production Ready**: Comprehensive error handling, logging, and security
- **API Integration**: Complete REST API integration layer with retry mechanisms
- **Environment Management**: Full environment variable configuration support
- **Docker Support**: Multi-stage Docker builds with security best practices

### 📊 **Dashboard Capabilities**
- **Interactive Analytics**: Real-time charts and metrics visualization
- **Multi-Page Navigation**: Dashboard, Movies, Content Items, Upload Pipeline, Analytics, Settings
- **Content Management**: CRUD operations for movies and content items
- **File Upload System**: Secure file handling with validation
- **Export/Import**: Data export and import functionality

### 🔒 **Security & Production Features**
- **Input Validation**: Comprehensive data sanitization and validation
- **Error Handling**: Graceful error handling with custom exceptions
- **Logging System**: Structured logging with rotation and multiple handlers
- **Rate Limiting**: Built-in rate limiting configuration
- **CSRF Protection**: Cross-Site Request Forgery protection
- **Authentication Ready**: JWT and API key authentication support

### 🎨 **UI/UX Excellence**
- **Responsive Design**: Mobile-friendly layout with custom CSS
- **Interactive Charts**: Plotly-based visualizations with hover details
- **Real-time Updates**: Cached data with configurable refresh intervals
- **Custom Theming**: Configurable color schemes and branding

## 📁 Project Structure

```
cinemitr-dashboard/
├── 📄 cinemitr_dashboard.py      # Main application entry point
├── ⚙️ config.py                  # Configuration management
├── 🔌 api_service.py             # API integration layer
├── 🛣️ api_endpoints.py           # API endpoint definitions
├── 🎨 components.py              # UI components and rendering
├── 🧪 tests/                     # Comprehensive test suite
│   ├── test_api_service.py
│   ├── test_config.py
│   └── test_validators.py
├── 🔧 utils/                     # Utility modules
│   ├── logger.py                 # Logging configuration
│   ├── exceptions.py             # Custom exceptions
│   └── validators.py             # Data validation utilities
├── 🐳 Dockerfile                 # Multi-stage Docker build
├── 🐳 docker-compose.yml         # Complete deployment stack
├── 📋 requirements.txt           # Python dependencies
├── 🔒 .env.example              # Environment template
└── 📚 README.md                  # This comprehensive guide
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional, for containerized deployment)
- Redis (optional, for caching)

### 1. Local Development Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd cinemitr-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
streamlit run cinemitr_dashboard.py

python -m streamlit run cinemitr_dashboard.py
```

### 2. Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build Docker image manually
docker build -t cinemitr-dashboard .
docker run -p 8501:8501 cinemitr-dashboard
```

### 3. Production Deployment

```bash
# Set production environment variables
export ENVIRONMENT=production
export SECRET_KEY=your-secure-secret-key
export API_BASE_URL=https://your-api.com/v1

# Run with production settings
docker-compose -f docker-compose.yml up -d
```

## 🔧 Configuration

### Environment Variables

The application uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

```bash
# Application Configuration
APP_NAME="CineMitr Dashboard"
APP_VERSION="1.0.0"
ENVIRONMENT=development  # development, staging, production
DEBUG=false
LOG_LEVEL=INFO

# API Configuration
API_BASE_URL=http://localhost:8000/api/v1
API_KEY=your_api_key_here
API_TIMEOUT=30

# Security Configuration
SECRET_KEY=your-secret-key-for-sessions
CSRF_ENABLED=true
SESSION_TIMEOUT_MINUTES=60

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_FILE_UPLOAD=true
ENABLE_EXPORT=true
ENABLE_IMPORT=true

# Cache Configuration
CACHE_TYPE=redis
REDIS_URL=redis://localhost:6379/0

# File Upload Configuration
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_EXTENSIONS=mp4,avi,mov,mkv,jpg,jpeg,png,pdf
```

### Configuration Classes

The application uses structured configuration with validation:

```python
from config import DashboardConfig

# Load configuration
config = DashboardConfig()

# Access nested configurations
api_config = config.api
security_config = config.security
upload_config = config.file_upload
```

## 🔌 API Integration

### Setting Up API Connections

1. **Configure Base URL**
   ```python
   # In .env file
   API_BASE_URL=https://your-api-domain.com/api/v1
   API_KEY=your-secret-api-key
   ```

2. **Implement API Calls**
   ```python
   # In api_service.py, replace mock data:
   def get_dashboard_metrics(self) -> DashboardMetrics:
       response = self.session.get(f"{self.config.api.base_url}/metrics")
       response.raise_for_status()
       return DashboardMetrics(**response.json())
   ```

3. **Add Authentication**
   ```python
   # API service automatically includes authentication headers
   headers = self.config.api.get_headers()
   # Includes API key, content type, and user agent
   ```

### Available API Methods

All buttons and interactions are connected to API service methods:

```python
# Dashboard data
api_service.get_dashboard_metrics()
api_service.get_status_distribution()
api_service.get_priority_distribution()
api_service.get_recent_activity()

# Content management
api_service.add_content(content_data)
api_service.update_content_status(id, status)
api_service.delete_content(id)

# File operations
api_service.import_data(file_data, file_type)
api_service.refresh_data()
```

### API Endpoint Configuration

All endpoints are configured in `api_endpoints.py`:

```python
class APIEndpoints:
    BASE_URL = "http://localhost:8000/api/v1"
    
    # Dashboard endpoints
    METRICS = "/dashboard/metrics"
    STATUS_DISTRIBUTION = "/dashboard/status-distribution"
    
    # Content management
    CONTENT_LIST = "/content"
    CONTENT_CREATE = "/content"
    CONTENT_UPDATE = "/content/{id}"
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api_service.py

# Run with verbose output
pytest -v
```

### Test Structure

- **Unit Tests**: Individual component testing
- **Integration Tests**: API service integration
- **Configuration Tests**: Environment and config validation
- **Validation Tests**: Data validation and sanitization

### Example Test

```python
def test_dashboard_metrics_retrieval(api_service):
    """Test successful dashboard metrics retrieval"""
    metrics = api_service.get_dashboard_metrics()
    
    assert isinstance(metrics, DashboardMetrics)
    assert metrics.total_movies >= 0
    assert metrics.upload_rate >= 0.0
```

## 🔒 Security Features

### Input Validation

```python
from utils.validators import ContentValidator

# Validate content data
try:
    ContentValidator.validate_content_item(content_data)
except ValidationException as e:
    logger.error(f"Validation error: {e.message}")
```

### Error Handling

```python
from utils.exceptions import APIException, ValidationException

try:
    result = api_service.get_data()
except APIException as e:
    st.error(f"API Error: {e.message}")
except ValidationException as e:
    st.warning(f"Invalid data: {e.message}")
```

### Logging

```python
from utils.logger import logger

# Structured logging
logger.info("User action", extra={"user_id": "123", "action": "create_content"})
logger.error("API error", extra={"endpoint": "/api/content", "status": 500})
```

## 🎨 Customization

### Adding New Pages

1. **Create page function**
   ```python
   def render_custom_page():
       st.header("🎯 Custom Page")
       # Add your custom functionality
   ```

2. **Add to navigation**
   ```python
   # In config.py
   MENU_ITEMS.append({
       "icon": "🎯", 
       "label": "Custom Page", 
       "key": "custom_page"
   })
   ```

3. **Add routing**
   ```python
   # In cinemitr_dashboard.py main()
   elif selected_page == "custom_page":
       render_custom_page()
   ```

### Custom Components

```python
# In components.py
class CustomComponent:
    def __init__(self, config, api_service):
        self.config = config
        self.api_service = api_service
    
    def render_custom_chart(self, data):
        # Custom chart implementation
        pass
```

### Styling

```python
# Custom CSS in components.py
def render_custom_css(self):
    st.markdown("""
    <style>
        .custom-metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)
```

## 🚀 Deployment Options

### Local Development
```bash
streamlit run cinemitr_dashboard.py
```

### Docker Development
```bash
docker-compose up --build
```

### Production Docker
```bash
# Build production image
docker build --target production -t cinemitr-dashboard:prod .

# Run with production settings
docker run -d \
  --name cinemitr-prod \
  -p 8501:8501 \
  -e ENVIRONMENT=production \
  -e SECRET_KEY=your-secret-key \
  cinemitr-dashboard:prod
```

### Cloud Deployment

#### AWS ECS/Fargate
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t cinemitr-dashboard .
docker tag cinemitr-dashboard:latest <account>.dkr.ecr.us-east-1.amazonaws.com/cinemitr-dashboard:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/cinemitr-dashboard:latest
```

#### Google Cloud Run
```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT-ID/cinemitr-dashboard
gcloud run deploy --image gcr.io/PROJECT-ID/cinemitr-dashboard --platform managed
```

## 📊 Monitoring & Logging

### Log Files
- **Application logs**: `logs/cinemitr_dashboard.log`
- **Error logs**: `logs/cinemitr_dashboard_errors.log`
- **Rotation**: 10MB files, 5 backup files

### Health Checks
- **Docker**: Built-in health check endpoint
- **Kubernetes**: Liveness and readiness probes ready
- **Monitoring**: Structured logs compatible with ELK stack

### Performance Monitoring
```python
# Built-in performance logging
logger.log_performance("database_query", duration=0.5)
logger.log_api_call("GET", "/api/metrics", status_code=200, duration=1.2)
```

## 🛠️ Development Workflow

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy .

# Linting
flake8 .
```

### Pre-commit Setup
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run on all files
pre-commit run --all-files
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Add tests** for new functionality
4. **Run test suite**: `pytest`
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Submit Pull Request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- **API Documentation**: See `api_endpoints.py` for all available endpoints
- **Configuration Guide**: Check `.env.example` for all configuration options
- **Code Examples**: Browse `tests/` directory for usage examples

### Troubleshooting

#### Common Issues

1. **Port 8501 already in use**
   ```bash
   # Kill existing Streamlit process
   pkill -f streamlit
   # Or use different port
   streamlit run cinemitr_dashboard.py --server.port 8502
   ```

2. **API connection failures**
   ```bash
   # Check API_BASE_URL in .env
   # Verify API service is running
   # Check network connectivity
   ```

3. **Docker build failures**
   ```bash
   # Clear Docker cache
   docker system prune -a
   # Rebuild with no cache
   docker-compose build --no-cache
   ```

### Getting Help

- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact maintainers for urgent issues

## 🎯 Roadmap

- [ ] **Authentication UI**: Login/logout interface
- [ ] **Advanced Analytics**: More chart types and metrics
- [ ] **Real-time Updates**: WebSocket integration
- [ ] **Mobile App**: React Native companion
- [ ] **API Documentation**: OpenAPI/Swagger integration
- [ ] **Database Integration**: Direct database connectivity
- [ ] **Notification System**: Email and in-app notifications

---

**Made with ❤️ for content management professionals**

*CineMitr Dashboard - Transforming content management into a seamless experience*