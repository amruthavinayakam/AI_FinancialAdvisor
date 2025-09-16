from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

class UserProfile(models.Model):
    """Extended user profile for financial data"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='financial_profile')
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, default=3000)
    target_daily_spending = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    savings_goal = models.DecimalField(max_digits=12, decimal_places=2, default=500)
    risk_tolerance = models.CharField(
        max_length=20,
        choices=[
            ('conservative', 'Conservative'),
            ('moderate', 'Moderate'),
            ('aggressive', 'Aggressive')
        ],
        default='moderate'
    )
    investment_horizon = models.CharField(
        max_length=20,
        choices=[
            ('short_term', '1-3 years'),
            ('medium_term', '3-10 years'),
            ('long_term', '10+ years')
        ],
        default='long_term'
    )
    age = models.PositiveIntegerField(default=35)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Financial Profile"

class ExpenseCategory(models.Model):
    """Predefined expense categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3498db')  # Hex color
    icon = models.CharField(max_length=50, default='receipt')  # Icon name
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Expense Categories"

    def __str__(self):
        return self.name

class Expense(models.Model):
    """User expense records"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
    description = models.TextField(blank=True)
    merchant = models.CharField(max_length=200, blank=True)
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('credit_card', 'Credit Card'),
            ('debit_card', 'Debit Card'),
            ('cash', 'Cash'),
            ('bank_transfer', 'Bank Transfer'),
            ('digital_wallet', 'Digital Wallet'),
            ('other', 'Other')
        ],
        default='credit_card'
    )
    date = models.DateTimeField()
    tags = models.JSONField(default=list, blank=True)
    is_recurring = models.BooleanField(default=False)
    recurring_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly')
        ],
        blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['category']),
            models.Index(fields=['amount']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.category.name}"

class Budget(models.Model):
    """User budget settings"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, related_name='budgets')
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    alert_threshold = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=80.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )  # Percentage
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'category']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.category.name} - {self.monthly_limit}"

class InvestmentAccount(models.Model):
    """User investment accounts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investment_accounts')
    account_name = models.CharField(max_length=200)
    account_type = models.CharField(
        max_length=50,
        choices=[
            ('401k', '401(k)'),
            ('ira', 'IRA'),
            ('roth_ira', 'Roth IRA'),
            ('brokerage', 'Brokerage Account'),
            ('savings', 'Savings Account'),
            ('cd', 'Certificate of Deposit'),
            ('other', 'Other')
        ]
    )
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    initial_investment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.account_name}"

class Investment(models.Model):
    """Individual investment holdings"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(InvestmentAccount, on_delete=models.CASCADE, related_name='investments')
    symbol = models.CharField(max_length=20)  # Stock symbol
    name = models.CharField(max_length=200)
    asset_type = models.CharField(
        max_length=50,
        choices=[
            ('stock', 'Stock'),
            ('bond', 'Bond'),
            ('etf', 'ETF'),
            ('mutual_fund', 'Mutual Fund'),
            ('crypto', 'Cryptocurrency'),
            ('commodity', 'Commodity'),
            ('other', 'Other')
        ]
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=6, validators=[MinValueValidator(0)])
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    current_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    purchase_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_value(self):
        return self.quantity * self.current_price

    @property
    def total_cost(self):
        return self.quantity * self.purchase_price

    @property
    def gain_loss(self):
        return self.total_value - self.total_cost

    @property
    def gain_loss_percentage(self):
        if self.total_cost > 0:
            return (self.gain_loss / self.total_cost) * 100
        return 0

    class Meta:
        indexes = [
            models.Index(fields=['account', 'symbol']),
            models.Index(fields=['asset_type']),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.quantity} shares"

class FinancialGoal(models.Model):
    """User financial goals"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_goals')
    goal_name = models.CharField(max_length=200)
    goal_type = models.CharField(
        max_length=50,
        choices=[
            ('emergency_fund', 'Emergency Fund'),
            ('retirement', 'Retirement'),
            ('vacation', 'Vacation'),
            ('house', 'House Purchase'),
            ('education', 'Education'),
            ('debt_payoff', 'Debt Payoff'),
            ('investment', 'Investment Growth'),
            ('other', 'Other')
        ]
    )
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_date = models.DateField()
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        default='medium'
    )
    is_achieved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            return (self.current_amount / self.target_amount) * 100
        return 0

    @property
    def remaining_amount(self):
        return max(0, self.target_amount - self.current_amount)

    class Meta:
        ordering = ['-priority', 'target_date']
        indexes = [
            models.Index(fields=['user', 'is_achieved']),
            models.Index(fields=['goal_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.goal_name}"

class FinancialData(models.Model):
    """Historical financial data snapshots"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_data')
    data_type = models.CharField(
        max_length=50,
        choices=[
            ('net_worth', 'Net Worth'),
            ('monthly_income', 'Monthly Income'),
            ('monthly_expenses', 'Monthly Expenses'),
            ('savings_rate', 'Savings Rate'),
            ('debt_to_income', 'Debt to Income Ratio'),
            ('credit_score', 'Credit Score'),
            ('other', 'Other')
        ]
    )
    value = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'data_type', 'date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.data_type} - {self.value}"

class AIRecommendation(models.Model):
    """AI-generated recommendations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_recommendations')
    recommendation_type = models.CharField(
        max_length=50,
        choices=[
            ('budget', 'Budget Optimization'),
            ('investment', 'Investment Strategy'),
            ('savings', 'Savings Strategy'),
            ('debt', 'Debt Management'),
            ('expense', 'Expense Reduction'),
            ('general', 'General Financial Advice')
        ]
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent')
        ],
        default='medium'
    )
    estimated_impact = models.CharField(
        max_length=50,
        choices=[
            ('low', 'Low Impact'),
            ('medium', 'Medium Impact'),
            ('high', 'High Impact')
        ],
        default='medium'
    )
    estimated_savings = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_implemented = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_implemented', 'is_dismissed']),
            models.Index(fields=['recommendation_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"
