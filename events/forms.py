from django import forms
from django.core.exceptions import ValidationError
from .models import Event, Category

class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'title_ru', 'description', 'description_ru', 
                 'date_time', 'location', 'address', 'price', 'event_type', 'is_published']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'description_ru': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        title_ru = cleaned_data.get('title_ru')
        
        if title and len(title) < 5:
            raise ValidationError({'title': 'Title is too short. Minimum 5 characters required.'})
        
        if title_ru and len(title_ru) < 5:
            raise ValidationError({'title_ru': 'Название слишком короткое. Минимум 5 символов.'})
        
        return cleaned_data

# Remove or update the old EventForm since we have EventCreateForm
class EventForm(forms.Form):
    title = forms.CharField(label='Event Title', max_length=255)
    title_ru = forms.CharField(label='Название мероприятия', max_length=255)
    description = forms.CharField(label='Description', widget=forms.Textarea)
    description_ru = forms.CharField(label='Описание', widget=forms.Textarea)
    date_time = forms.DateTimeField(label='Event Date')
    location = forms.CharField(label='Location', max_length=255)
    price = forms.DecimalField(label='Price')
    event_type = forms.ChoiceField(choices=Event.EVENT_TYPES)
    is_published = forms.BooleanField(required=False, initial=True)

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise ValidationError('Event title must be at least 5 characters long.')
        return title

    def clean_title_ru(self):
        title_ru = self.cleaned_data['title_ru']
        if len(title_ru) < 5:
            raise ValidationError('Название мероприятия должно содержать не менее 5 символов.') 
        return title_ru

# Add the Ticket Purchase Form
class TicketPurchaseForm(forms.Form):
    TICKET_TYPES = [
        ('standard', 'Standard Ticket / Стандартный билет'),
        ('vip', 'VIP Ticket / VIP билет'),
        ('premium', 'Premium Ticket / Премиум билет'),
    ]
    
    full_name = forms.CharField(
        max_length=100,
        label='Full Name / Полное Имя',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your full name / Введите ваше полное имя',
            'class': 'form-control'
        })
    )
    email = forms.EmailField(
        label='Email / Электронная почта',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email / Введите вашу электронную почту',
            'class': 'form-control'
        })
    )
    phone = forms.CharField(
        max_length=20,
        label='Phone Number / Номер телефона',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your phone number / Введите ваш номер телефона',
            'class': 'form-control'
        })
    )
    ticket_type = forms.ChoiceField(
        choices=TICKET_TYPES,
        label='Ticket Type / Тип билета',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        label='Quantity / Количество',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # Basic phone validation - you can enhance this
        if len(phone) < 5:
            raise ValidationError('Please enter a valid phone number / Пожалуйста, введите корректный номер телефона')
        return phone
    
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise ValidationError('Quantity must be at least 1 / Количество должно быть не менее 1')
        if quantity > 10:
            raise ValidationError('Maximum 10 tickets per order / Максимум 10 билетов за один заказ')
        return quantity