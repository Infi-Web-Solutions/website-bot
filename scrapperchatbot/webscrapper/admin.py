# In your app's admin.py (e.g., webscrapper/admin.py)

from django.contrib import admin
from .models import Bot # Import your Bot model

# Register your models here.

# Option 1: Simple registration
admin.site.register(Bot)

# Option 2: More advanced registration with customization (recommended for better admin experience)
# class BotAdmin(admin.ModelAdmin):
#     list_display = ('name', 'owner', 'created_at', 'updated_at') # Fields to display in the list view
#     list_filter = ('owner', 'created_at') # Fields to filter by
#     search_fields = ('name', 'description', 'owner__username') # Fields to search by
#     raw_id_fields = ('owner',) # Use a raw ID input for owner, useful for many users
#     date_hierarchy = 'created_at' # Add a date drill-down navigation

# admin.site.register(Bot, BotAdmin)

