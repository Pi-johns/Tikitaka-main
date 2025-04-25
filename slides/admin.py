from django.contrib import admin
from .models import Slide

@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ('heading', 'is_active', 'display_order')
    list_filter = ('is_active',)
    search_fields = ('heading', 'subheading')
    ordering = ('display_order',)
