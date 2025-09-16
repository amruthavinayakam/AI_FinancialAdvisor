# Database Setup Guide

This guide will help you set up the database connections for the Financial Advisor AI Agent.

## Prerequisites

1. **PostgreSQL** installed and running
2. **Python 3.8+** with virtual environment activated
3. **Required Python packages** installed

## Quick Setup

### 1. Install Dependencies

```bash
# Install FastAPI dependencies
pip install -r backend/fastapi_app/requirements.txt

# Install Django dependencies
pip install -r backend/django_app/requirements.txt

# Install additional database dependencies
pip install asyncpg psycopg2-binary
```

### 2. Configure Environment

Copy the example environment file and update with your database credentials:

```bash
cp env.example .env
```

Edit `.env` file with your PostgreSQL credentials:

```env
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=financial_advisor
```

### 3. Run Database Setup

```bash
python setup_database.py
```

This script will:
- Create the database if it doesn't exist
- Run Django migrations to create tables
- Set up initial data (expense categories, sample user)
- Initialize database connections

### 4. Start the Services

**FastAPI Server:**
```bash
cd backend/fastapi_app
python main.py
```

**Django Server:**
```bash
cd backend/django_app
python manage.py runserver
```

## Database Schema

### Core Tables

1. **User Profiles** (`core_userprofile`)
   - Extended user information for financial data
   - Monthly income, budget, savings goals
   - Risk tolerance and investment preferences

2. **Expense Categories** (`core_expensecategory`)
   - Predefined expense categories
   - Color coding and icons for UI

3. **Expenses** (`core_expense`)
   - Individual expense records
   - Amount, category, date, merchant
   - Recurring expense support

4. **Budgets** (`core_budget`)
   - Monthly budget limits per category
   - Alert thresholds for overspending

5. **Investment Accounts** (`core_investmentaccount`)
   - User investment accounts (401k, IRA, brokerage)
   - Account types and current values

6. **Investments** (`core_investment`)
   - Individual investment holdings
   - Stock symbols, quantities, prices
   - Gain/loss calculations

7. **Financial Goals** (`core_financialgoal`)
   - User financial objectives
   - Target amounts and dates
   - Progress tracking

8. **Financial Data** (`core_financialdata`)
   - Historical financial snapshots
   - Net worth, income, expenses over time

9. **AI Recommendations** (`core_airecommendation`)
   - AI-generated financial advice
   - Priority and impact ratings

## Database Connection Architecture

### FastAPI (asyncpg)
- **Connection Pool**: Managed by asyncpg
- **Async Operations**: All database operations are async
- **Connection Manager**: Centralized in `database_manager.py`

### Django (psycopg2)
- **ORM**: Django's built-in ORM
- **Migrations**: Automatic schema management
- **Admin Interface**: Built-in admin for data management

## API Endpoints

### Expense Management
- `GET /api/v1/expenses` - Get user expenses
- `POST /api/v1/expenses` - Add new expense
- `GET /api/v1/expenses/summary` - Get expense analytics
- `GET /api/v1/expenses/patterns` - Get spending patterns
- `GET /api/v1/expenses/recommendations` - Get budget recommendations

### Investment Management
- `GET /api/v1/portfolio` - Get portfolio analysis
- `POST /api/v1/investment-strategy` - Get investment strategy
- `GET /api/v1/market-opportunities` - Get market opportunities

### Financial Forecasting
- `GET /api/v1/forecast` - Get financial forecast
- `GET /api/v1/financial-data` - Get comprehensive financial data

## Testing the Setup

### 1. Test Database Connection
```bash
curl http://localhost:8001/health
```

### 2. Test Expense Tracking
```bash
# Get sample expenses
curl http://localhost:8001/api/v1/test/expenses

# Add a new expense
curl -X POST http://localhost:8001/api/v1/expenses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer demo_token" \
  -d '{
    "amount": 25.50,
    "category": "Food & Dining",
    "description": "Lunch at restaurant",
    "merchant": "Local Restaurant"
  }'
```

### 3. Test Financial Advice
```bash
curl -X POST http://localhost:8001/api/v1/quick-advice \
  -H "Content-Type: application/json" \
  -d '{"query": "How should I invest $1000?"}'
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check PostgreSQL is running
   - Verify credentials in `.env` file
   - Ensure database exists

2. **Migration Errors**
   - Run `python backend/django_app/manage.py migrate` manually
   - Check Django settings configuration

3. **Import Errors**
   - Ensure virtual environment is activated
   - Install all required packages
   - Check Python path configuration

### Logs and Debugging

- **FastAPI logs**: Check console output for database connection status
- **Django logs**: Run with `--verbosity=2` for detailed output
- **Database logs**: Check PostgreSQL logs for connection issues

## Production Considerations

1. **Connection Pooling**: Adjust pool sizes based on expected load
2. **Database Indexing**: Ensure proper indexes for query performance
3. **Backup Strategy**: Implement regular database backups
4. **Security**: Use environment variables for sensitive data
5. **Monitoring**: Set up database monitoring and alerting

## Next Steps

1. **Add Authentication**: Implement proper user authentication
2. **Data Validation**: Add comprehensive input validation
3. **Caching**: Implement Redis for frequently accessed data
4. **API Rate Limiting**: Add rate limiting for API endpoints
5. **Real-time Updates**: Add WebSocket support for real-time data
