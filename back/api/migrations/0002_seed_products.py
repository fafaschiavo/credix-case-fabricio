from django.db import migrations

def seed_products(apps, schema_editor):
    Product = apps.get_model("api", "Product")

    # ✅ Create initial products
    Product.objects.create(sku="oweuriek", name="Product A", price=100)
    Product.objects.create(sku="eepheeje", name="Product B", price=150)

class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),  # ✅ Replace with the latest migration file
    ]

    operations = [
        migrations.RunPython(seed_products),  # ✅ Runs function to insert data
    ]
