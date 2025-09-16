from django.contrib import admin
from .models import (
    ExpenseCategory,
    Expense,
    Budget,
    InvestmentAccount,
    Investment,
    FinancialGoal,
    FinancialData,
    AIRecommendation,
    UserProfile,
)


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "color", "icon", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "category", "date", "merchant", "payment_method", "is_recurring")
    list_filter = ("category", "payment_method", "is_recurring", "date")
    search_fields = ("user__username", "description", "merchant", "tags")
    date_hierarchy = "date"


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "monthly_limit", "alert_threshold", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("user__username", "category__name")


@admin.register(InvestmentAccount)
class InvestmentAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "account_name", "account_type", "current_value", "is_active")
    list_filter = ("account_type", "is_active")
    search_fields = ("user__username", "account_name")


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ("account", "symbol", "name", "asset_type", "quantity", "purchase_price", "current_price", "purchase_date", "is_active")
    list_filter = ("asset_type", "is_active")
    search_fields = ("symbol", "name", "account__account_name")
    date_hierarchy = "purchase_date"


@admin.register(FinancialGoal)
class FinancialGoalAdmin(admin.ModelAdmin):
    list_display = ("user", "goal_name", "goal_type", "target_amount", "current_amount", "priority", "is_achieved")
    list_filter = ("goal_type", "priority", "is_achieved")
    search_fields = ("user__username", "goal_name")


@admin.register(FinancialData)
class FinancialDataAdmin(admin.ModelAdmin):
    list_display = ("user", "data_type", "value", "date")
    list_filter = ("data_type",)
    search_fields = ("user__username",)
    date_hierarchy = "date"


@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "recommendation_type", "priority", "is_implemented", "is_dismissed")
    list_filter = ("recommendation_type", "priority", "is_implemented", "is_dismissed")
    search_fields = ("user__username", "title")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "monthly_income", "monthly_budget", "target_daily_spending", "savings_goal", "risk_tolerance", "investment_horizon", "age")
    list_filter = ("risk_tolerance", "investment_horizon")
    search_fields = ("user__username",)


