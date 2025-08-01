# In your app's models.py (e.g., webscrapper/models.py)

from django.db import models
from django.contrib.auth.models import User # Import Django's built-in User model
import uuid # Import uuid for generating unique IDs

class Bot(models.Model):
    """
    Represents a web scraping bot owned by a specific user.
    Each bot will have its own vector database collection.
    """
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE, # If the user is deleted, their bots are also deleted
        related_name='bots' # Allows you to access bots from a User object (e.g., user.bots.all())
    )
    name = models.CharField(max_length=100) # Name of the bot (no longer unique globally, but unique per user is good practice)
    description = models.TextField(blank=True, null=True) # Optional description
    
    # New field: Stores the unique name for this bot's vector database collection
    # We use a UUID to ensure global uniqueness for collection names.
    collection_name = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    
    created_at = models.DateTimeField(auto_now_add=True) # Automatically sets creation timestamp
    updated_at = models.DateTimeField(auto_now=True) # Automatically updates on each save

    class Meta:
        # Ensure that a user cannot have two bots with the same name
        unique_together = ('owner', 'name')
        ordering = ['-created_at'] # Order bots by creation date, newest first

    def __str__(self):
        return f"{self.name} (Owner: {self.owner.username})"

