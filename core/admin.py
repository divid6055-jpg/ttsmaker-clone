from django.contrib import admin
from .models import TTSConversion

@admin.register(TTSConversion)
class TTSConversionAdmin(admin.ModelAdmin):
    list_display = ['id', 'language', 'voice_id', 'file_format', 'file_size', 'created_at']
    list_filter = ['language', 'file_format', 'created_at']
    search_fields = ['text', 'voice_id']
    readonly_fields = ['id', 'created_at', 'file_size']
