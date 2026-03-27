from django.contrib import admin
from .models import SupportTicket, TicketComment

class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 1

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'employee', 'status', 'priority', 'category', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('subject', 'description', 'employee__first_name', 'employee__last_name')
    inlines = [TicketCommentInline]
    readonly_fields = ('created_at', 'updated_at')
