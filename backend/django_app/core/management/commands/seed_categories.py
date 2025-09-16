from django.core.management.base import BaseCommand
from core.models import ExpenseCategory


DEFAULT_CATEGORIES = [
    ("Food & Dining", "#E74C3C", "restaurant"),
    ("Groceries", "#27AE60", "shopping_cart"),
    ("Transportation", "#3498DB", "directions_car"),
    ("Fuel", "#E67E22", "local_gas_station"),
    ("Public Transit", "#16A085", "directions_transit"),
    ("Rideshare", "#9B59B6", "local_taxi"),
    ("Shopping", "#8E44AD", "local_mall"),
    ("Bills & Utilities", "#2980B9", "receipt_long"),
    ("Rent/Mortgage", "#2C3E50", "home"),
    ("Internet", "#1ABC9C", "wifi"),
    ("Mobile Phone", "#2ECC71", "smartphone"),
    ("Entertainment", "#F39C12", "movie"),
    ("Subscriptions", "#D35400", "autorenew"),
    ("Healthcare", "#C0392B", "local_hospital"),
    ("Pharmacy", "#E74C3C", "local_pharmacy"),
    ("Insurance", "#7F8C8D", "shield"),
    ("Education", "#34495E", "school"),
    ("Travel", "#F1C40F", "flight_takeoff"),
    ("Hotels", "#95A5A6", "hotel"),
    ("Gifts & Donations", "#E84393", "card_giftcard"),
    ("Personal Care", "#A569BD", "spa"),
    ("Fitness", "#27AE60", "fitness_center"),
    ("Household", "#7DCEA0", "cleaning_services"),
    ("Childcare", "#F5B041", "child_care"),
    ("Pets", "#AF7AC5", "pets"),
    ("Taxes & Fees", "#5D6D7E", "attach_money"),
    ("Business Expense", "#566573", "work"),
    ("Miscellaneous", "#BDC3C7", "category"),
]


class Command(BaseCommand):
    help = "Seed default expense categories"

    def handle(self, *args, **options):
        created = 0
        for name, color, icon in DEFAULT_CATEGORIES:
            obj, was_created = ExpenseCategory.objects.get_or_create(
                name=name,
                defaults={
                    "description": f"Default category: {name}",
                    "color": color,
                    "icon": icon,
                    "is_active": True,
                },
            )
            if not was_created:
                obj.color = color
                obj.icon = icon
                obj.is_active = True
                obj.save(update_fields=["color", "icon", "is_active"]) 
            else:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Seed complete. Created {created} categories."))


