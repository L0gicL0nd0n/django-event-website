from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .forms import TicketPurchaseForm
from .models import Event

# Add these missing views that are referenced in your urls.py
def home(request):
    """Home page view"""
    # Get upcoming events
    upcoming_events = Event.objects.filter(is_published=True).order_by('date_time')[:6]
    
    context = {
        'upcoming_events': upcoming_events,
    }
    return render(request, 'events/home.html', context)

def past_events(request):
    """Past events page"""
    past_events = Event.objects.filter(is_published=True, date_time__lt=timezone.now()).order_by('-date_time')
    
    context = {
        'past_events': past_events,
    }
    return render(request, 'events/past_events.html', context)

def event_detail(request, event_id):
    """Event detail page view"""
    event = get_object_or_404(Event, id=event_id, is_published=True)
    
    context = {
        'event': event,
        'event_id': event_id,
    }
    return render(request, 'events/event_detail.html', context)

# Your existing ticket purchase views
def buy_tickets(request, event_id):
    # Get the event from database
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = TicketPurchaseForm(request.POST)
        if form.is_valid():
            # Process the ticket purchase
            ticket_data = form.cleaned_data
            
            # Calculate total price
            base_price = event.price
            ticket_multipliers = {
                'standard': 1.0,
                'vip': 1.5,
                'premium': 2.0
            }
            ticket_price = base_price * ticket_multipliers[ticket_data['ticket_type']]
            total_price = ticket_price * ticket_data['quantity']
            
            # Store purchase data in session
            request.session['last_purchase'] = {
                'event_id': event.id,
                'event_title': event.title,
                'event_title_ru': event.title_ru,
                'full_name': ticket_data['full_name'],
                'email': ticket_data['email'],
                'ticket_type': ticket_data['ticket_type'],
                'quantity': ticket_data['quantity'],
                'total_price': float(total_price)
            }
            
            messages.success(
                request, 
                f"Ticket purchase successful! / Покупка билета успешна! "
                f"You have purchased {ticket_data['quantity']} {ticket_data['ticket_type']} ticket(s) for {event.title}. "
                f"Total: ${total_price:.2f}"
            )
            return redirect('events:ticket_confirmation', event_id=event_id)
    else:
        form = TicketPurchaseForm()
    
    return render(request, 'events/buy_tickets.html', {
        'form': form,
        'event': event,
        'event_id': event_id
    })

def ticket_confirmation(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    purchase_data = request.session.get('last_purchase', {})
    
    return render(request, 'events/ticket_confirmation.html', {
        'event': event,
        'purchase_data': purchase_data
    })