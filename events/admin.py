from django.contrib import admin
from .models import Event, Category, Author, EventRegistration, Review, TicketType, Ticket, Order, OrderItem

class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'date_time', 'is_published', 'price']
    list_filter = ['event_type', 'is_published', 'date_time']
    search_fields = ['title', 'title_ru', 'description']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_ru']
    search_fields = ['name', 'name_ru']

class AuthorAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'created_at']
    search_fields = ['user__username']

class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'registration_date', 'payment_status']
    list_filter = ['payment_status', 'registration_date']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'rating', 'created_at', 'is_approved']
    list_filter = ['rating', 'is_approved', 'created_at']

class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ['event', 'name', 'price', 'quantity_available', 'quantity_sold', 'available_tickets']
    list_filter = ['event']
    search_fields = ['name', 'event__title']

class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'ticket_type', 'user', 'status', 'purchase_date']
    list_filter = ['status', 'purchase_date']
    search_fields = ['ticket_number', 'user__username', 'ticket_type__name']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'event', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'event__title']
    inlines = [OrderItemInline]

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'ticket_type', 'quantity', 'price']
    list_filter = ['ticket_type']

# Register all your models
admin.site.register(Event, EventAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(EventRegistration, EventRegistrationAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(TicketType, TicketTypeAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)