# AI Personal Finance Advisor

A comprehensive, AI-powered personal finance advisor that tracks expenses, suggests investment strategies, and forecasts financial health using cutting-edge AI technologies.

## 🚀 Features

### Core AI Capabilities
- **Multi-Model AI Integration**: Combines GPT-4 and Google Gemini for specialized financial analysis
- **LangGraph Workflows**: Orchestrates complex financial advice generation using LangGraph
- **Intelligent Expense Analysis**: AI-powered spending pattern recognition and budget optimization
- **Investment Strategy Generation**: Personalized portfolio recommendations based on risk tolerance and goals
- **Financial Forecasting**: Advanced cash flow and net worth projections with risk scenarios

### Financial Management
- **Expense Tracking**: Comprehensive expense categorization and analysis
- **Budget Management**: AI-driven budget recommendations and spending insights
- **Portfolio Analysis**: Real-time portfolio health assessment and rebalancing suggestions
- **Market Intelligence**: Integration with Alpha Vantage and Yahoo Finance APIs
- **Risk Assessment**: Multi-scenario risk analysis and mitigation strategies

### Technical Architecture
- **FastAPI Backend**: High-performance async API with comprehensive endpoints
- **PostgreSQL Database**: Robust data storage with async support
- **Firebase Integration**: Mobile app support and real-time updates
- **Modular Design**: Clean, maintainable codebase with clear separation of concerns

## 🏗️ Architecture

```
FinancialAdvisor_AIAgent/
├── ai_core/                          # AI Core Components
│   ├── config.py                     # Configuration management
│   ├── financial_advisor_graph.py    # Main LangGraph workflow
│   ├── financial_data.py            # Financial data collection
│   ├── expense_tracker.py           # Expense tracking and analysis
│   ├── investment_advisor.py        # Investment strategy generation
│   └── financial_forecaster.py      # Financial forecasting
├── backend/                          # Backend Services
│   ├── fastapi_app/                 # FastAPI Application
│   │   ├── main.py                  # Main API endpoints
│   │   └── requirements.txt         # Python dependencies
│   └── django_app/                  # Django Application (User Management)
├── infra/                           # Infrastructure & Deployment
└── requirements.txt                  # Global dependencies
```

## 🛠️ Technology Stack

### AI & Machine Learning
- **LangChain**: LLM orchestration and prompt management
- **LangGraph**: Complex workflow orchestration
- **OpenAI GPT-4**: Advanced financial analysis and advice
- **Google Gemini**: Specialized expense and pattern analysis

### Backend & Database
- **FastAPI**: High-performance async API framework
- **Django**: User management and business logic
- **PostgreSQL**: Primary database with async support
- **AsyncPG**: High-performance async database driver

### Financial APIs
- **Alpha Vantage**: Market data and fundamental analysis
- **Yahoo Finance**: Real-time stock data and historical prices
- **Firebase**: Mobile app backend and real-time updates

### Development & Deployment
- **Python 3.9+**: Modern Python with async support
- **Docker**: Containerization support
- **Uvicorn**: ASGI server for FastAPI

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- PostgreSQL database
- OpenAI API key
- Google Gemini API key
- Alpha Vantage API key (optional)
- Firebase project (optional)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/FinancialAdvisor_AIAgent.git
cd FinancialAdvisor_AIAgent
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy the configuration example and fill in your API keys:
```bash
cp backend/fastapi_app/config_example.py backend/fastapi_app/config.py
# Edit config.py with your actual API keys
```

### 5. Set Up Database
```sql
CREATE DATABASE financial_advisor_db;
CREATE USER your_db_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE financial_advisor_db TO your_db_user;
```

### 6. Run the Application
```bash
cd backend/fastapi_app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Endpoints

### Financial Advice
- `POST /api/v1/financial-advice` - Get comprehensive AI financial advice

### Expense Management
- `GET /api/v1/expenses` - Retrieve user expenses
- `POST /api/v1/expenses` - Add new expense
- `GET /api/v1/expenses/summary` - Get expense summary and analytics
- `GET /api/v1/expenses/patterns` - Analyze spending patterns
- `GET /api/v1/expenses/recommendations` - Get budget recommendations

### Portfolio & Investment
- `GET /api/v1/portfolio` - Comprehensive portfolio analysis
- `POST /api/v1/investment-strategy` - Personalized investment strategy
- `GET /api/v1/market-opportunities` - Current market opportunities

### Financial Forecasting
- `GET /api/v1/forecast` - Comprehensive financial forecast
- `GET /api/v1/financial-data` - User financial data

### System
- `GET /` - API information and endpoints
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the `backend/fastapi_app/` directory:

```env
# Database
POSTGRES_DB=financial_advisor_db
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# AI APIs
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Security
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
```

### AI Model Configuration
- **Temperature**: Controls response creativity (0.0-1.0)
- **Max Tokens**: Maximum response length
- **Model Selection**: Choose between GPT-4 and Gemini based on use case

## 🧠 AI Workflow

### 1. Financial Data Collection
- Portfolio data from financial APIs
- Expense data from user input
- Market data from Alpha Vantage and Yahoo Finance

### 2. AI Analysis Pipeline
- **Expense Analysis**: Gemini analyzes spending patterns
- **Investment Advice**: GPT-4 generates personalized investment strategies
- **Risk Assessment**: Multi-scenario risk modeling
- **Forecasting**: Cash flow and net worth projections

### 3. Recommendation Synthesis
- Combines insights from multiple AI models
- Prioritizes recommendations by impact
- Provides actionable next steps

## 📱 Mobile App Support

The system is designed to support mobile applications:

- **Firebase Integration**: Real-time updates and push notifications
- **RESTful API**: Standard HTTP endpoints for mobile consumption
- **Authentication**: JWT-based security for mobile apps
- **Real-time Data**: WebSocket support for live financial updates

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **API Rate Limiting**: Protection against abuse
- **Input Validation**: Comprehensive request validation
- **CORS Configuration**: Secure cross-origin resource sharing
- **Environment Variables**: Secure API key management

## 🚀 Deployment

### Docker Deployment
```bash
docker build -t financial-advisor .
docker run -p 8000:8000 financial-advisor
```

### Production Considerations
- Use production-grade PostgreSQL
- Implement proper logging and monitoring
- Set up SSL/TLS certificates
- Configure proper CORS origins
- Implement API rate limiting
- Set up backup and recovery procedures

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint for interactive API docs
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions in GitHub Discussions

## 🔮 Roadmap

### Phase 1 (Current)
- ✅ Core AI infrastructure
- ✅ Expense tracking and analysis
- ✅ Investment strategy generation
- ✅ Financial forecasting

### Phase 2 (Next)
- 🔄 Mobile app development
- 🔄 Advanced portfolio optimization
- 🔄 Tax planning integration
- 🔄 Retirement planning tools

### Phase 3 (Future)
- 📋 Estate planning
- 📋 Insurance analysis
- 📋 Cryptocurrency integration
- 📋 Social trading features

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Google for Gemini API
- LangChain team for the amazing framework
- FastAPI community for the excellent documentation
- All contributors and beta testers

---

**Built with ❤️ using cutting-edge AI technology**
