from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, default="General")  # ADDED DEFAULT HERE
    name_ru = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    rating = models.IntegerField(default=0)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.CharField(max_length=500, blank=True, null=True)  # CHANGED: ImageField → CharField
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} (Author)"

class Event(models.Model):
    EVENT_TYPES = [
        ('tech', '🚀 Technology'),
        ('music', '🎸 Music'),
        ('food', '🍷 Food & Drink'),
        ('art', '🎨 Art'),
        ('sports', '🏃 Sports'),
        ('dance', '💃 Dance'),
        ('business', '💼 Business'),
        ('education', '📚 Education'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    description_ru = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='events')
    categories = models.ManyToManyField(Category, related_name='events')
    
    # Event details
    date_time = models.DateTimeField()
    duration = models.DurationField(default=timezone.timedelta(hours=2))
    location = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='USD')
    
    # Capacity
    max_attendees = models.IntegerField(default=100)
    current_attendees = models.IntegerField(default=0)
    
    # Media
    featured_image = models.CharField(max_length=500, blank=True, null=True)  # CHANGED: ImageField → CharField
    
    # Status and timestamps
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_time']
        indexes = [
            models.Index(fields=['date_time', 'is_published']),
            models.Index(fields=['event_type', 'is_published']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.pk})
    
    def is_upcoming(self):
        return self.date_time > timezone.now()
    
    def available_spots(self):
        return self.max_attendees - self.current_attendees
    
    def is_sold_out(self):
        return self.current_attendees >= self.max_attendees

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    tickets_count = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    
    # Additional registration info
    special_requirements = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class Review(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-created_at']
    
    def __str__(self): 
        return f"Review by {self.user.username} for {self.event.title}"

# FIXED: TicketType class moved OUTSIDE of Review class
class TicketType(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=100)  # e.g., "General Admission", "VIP"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.IntegerField(default=100)
    quantity_sold = models.IntegerField(default=0)
    
    def available_tickets(self):
        return self.quantity_available - self.quantity_sold
    
    def __str__(self):
        return f"{self.name} - {self.event.title}"

class Ticket(models.Model):
    TICKET_STATUS = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled'),
    ]
    
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tickets')
    status = models.CharField(max_length=20, choices=TICKET_STATUS, default='available')
    purchase_date = models.DateTimeField(null=True, blank=True)
    ticket_number = models.CharField(max_length=20, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            # Generate unique ticket number
            import uuid
            self.ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.ticket_number} - {self.ticket_type.name}"

class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.ticket_type.name}"