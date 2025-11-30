from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.home, name='home'),
    path('past-events/', views.past_events, name='past_events'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    # Add these two lines for ticket purchasing
    path('event/<int:event_id>/buy-tickets/', views.buy_tickets, name='buy_tickets'),
    path('event/<int:event_id>/confirmation/', views.ticket_confirmation, name='ticket_confirmation'),
]