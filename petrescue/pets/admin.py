from django.contrib import admin
from .models import Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'species', 'age', 'created_at')
    search_fields = ('name', 'owner__username', 'owner__email')
    list_filter = ('species',)
