from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """فرم ثبت‌نام کاربر جدید با نام و نام خانوادگی و ایمیل یکتا."""

    full_name = forms.CharField(
        max_length=150,
        label='نام و نام خانوادگی',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً: سارا محمدی'}),
    )
    email = forms.EmailField(
        label='ایمیل',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com', 'dir': 'ltr'}),
    )

    class Meta:
        model = User
        fields = ('full_name', 'username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'نام کاربری'
        self.fields['username'].help_text = 'حداکثر ۱۵۰ کاراکتر شامل حروف انگلیسی، اعداد و @/./+/-/_'
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'username', 'dir': 'ltr'})

        self.fields['password1'].label = 'رمز عبور'
        self.fields['password1'].help_text = 'حداقل ۸ کاراکتر و ترکیبی از حروف و اعداد باشد.'
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '••••••••'})

        self.fields['password2'].label = 'تکرار رمز عبور'
        self.fields['password2'].help_text = 'برای اطمینان، رمز عبور را دوباره وارد کنید.'
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '••••••••'})

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('این ایمیل قبلاً در سیستم ثبت شده است.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data['full_name'].strip()
        parts = full_name.split(None, 1)
        user.first_name = parts[0] if parts else ''
        user.last_name = parts[1] if len(parts) > 1 else ''
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """فرم ورود کاربران با قابلیت مرا به خاطر بسپار."""

    remember_me = forms.BooleanField(
        required=False,
        label='مرا به خاطر بسپار',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    error_messages = {
        'invalid_login': 'نام کاربری یا رمز عبور اشتباه است. لطفاً دوباره تلاش کنید.',
        'inactive': 'این حساب کاربری غیرفعال شده است.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'نام کاربری'
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'نام کاربری', 'dir': 'ltr'})
        self.fields['password'].label = 'رمز عبور'
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': '••••••••'})
