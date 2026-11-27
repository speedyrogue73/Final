from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegisterForm


def register_view(request):
    """ثبت‌نام کاربر جدید."""
    if request.user.is_authenticated:
        return redirect('dashboard:profile')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'ثبت‌نام شما با موفقیت انجام شد! اکنون می‌توانید وارد حساب کاربری خود شوید.')
            return redirect('accounts:login')
        messages.error(request, 'لطفاً خطاهای فرم ثبت‌نام را بررسی و برطرف کنید.')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """ورود کاربر به حساب کاربری."""
    if request.user.is_authenticated:
        return redirect('dashboard:profile')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if form.cleaned_data.get('remember_me'):
                request.session.set_expiry(60 * 60 * 24 * 14)  # 14 days
            else:
                request.session.set_expiry(0)

            display_name = user.get_full_name() or user.username
            messages.success(request, f'{display_name} عزیز، خوش آمدید!')
            next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard:profile'
            return redirect(next_url)
        messages.error(request, 'نام کاربری یا رمز عبور نادرست است.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': request.GET.get('next', '')})


@require_POST
def logout_view(request):
    """خروج از حساب کاربری."""
    logout(request)
    messages.info(request, 'با موفقیت از حساب کاربری خود خارج شدید.')
    return redirect('books:home')
