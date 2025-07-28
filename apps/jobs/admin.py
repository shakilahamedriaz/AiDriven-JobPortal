from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'posted_by', 'is_featured', 'posted_at')
    list_filter = ('is_featured', 'posted_at', 'location')
    search_fields = ('title', 'company_name', 'description')
    list_editable = ('is_featured',)
    actions = ['make_featured', 'remove_featured']
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} jobs marked as featured.')
    make_featured.short_description = "Mark selected jobs as featured"
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} jobs removed from featured.')
    remove_featured.short_description = "Remove featured status from selected jobs"
