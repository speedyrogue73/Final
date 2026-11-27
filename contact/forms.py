from django import forms
from .models import ContactMessage


class ContactMessageForm(forms.ModelForm):
    """فرم ارتباط با ما."""

    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'subject', 'message')
        labels = {
            'name': 'نام و نام خانوادگی',
            'email': 'ایمیل',
            'subject': 'موضوع',
            'message': 'متن پیام',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خود را وارد کنید'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com', 'dir': 'ltr'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'موضوع پیام شما'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'متن پیام خود را بنویسید...'}),
        }
