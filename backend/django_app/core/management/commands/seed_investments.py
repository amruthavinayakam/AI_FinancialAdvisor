from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import InvestmentAccount, Investment
from datetime import date


HOLDINGS = [
    ("VTI", "Vanguard Total Stock Market ETF", "ETF", 100, 200, 250, date(2024, 1, 1)),
    ("VXUS", "Vanguard Total International Stock ETF", "ETF", 80, 55, 60, date(2024, 2, 1)),
    ("BND", "Vanguard Total Bond Market ETF", "ETF", 120, 75, 72, date(2023, 11, 1)),
    ("AAPL", "Apple Inc.", "stock", 20, 150, 190, date(2023, 6, 15)),
]


class Command(BaseCommand):
    help = "Seed an investment account and several holdings for a user (default user_123)"

    def add_arguments(self, parser):
        parser.add_argument("--username", default="user_123")
        parser.add_argument("--account_name", default="My 401k")

    def handle(self, *args, **opts):
        username = opts["username"]
        account_name = opts["account_name"]

        user = User.objects.get(username=username)

        account, _ = InvestmentAccount.objects.get_or_create(
            user=user,
            account_name=account_name,
            defaults={
                "account_type": "401k",
                "current_value": 0,
                "initial_investment": 0,
                "is_active": True,
            },
        )

        created = 0
        for symbol, name, asset_type, qty, buy, current, pdate in HOLDINGS:
            inv, was_created = Investment.objects.get_or_create(
                account=account,
                symbol=symbol,
                defaults={
                    "name": name,
                    "asset_type": asset_type,
                    "quantity": qty,
                    "purchase_price": buy,
                    "current_price": current,
                    "purchase_date": pdate,
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
            else:
                inv.name = name
                inv.asset_type = asset_type
                inv.quantity = qty
                inv.purchase_price = buy
                inv.current_price = current
                inv.purchase_date = pdate
                inv.is_active = True
                inv.save()

        # Update account current_value
        total_value = sum([h[3] * h[5] for h in HOLDINGS])
        account.current_value = total_value
        if account.initial_investment == 0:
            account.initial_investment = sum([h[3] * h[4] for h in HOLDINGS])
        account.save(update_fields=["current_value", "initial_investment"])

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} holdings into '{account_name}' for {username}."))


