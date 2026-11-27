from django.shortcuts import render


def csrf_failure(request, reason=''):
    """صفحه خطای اختصاصی برای درخواست‌های با توکن CSRF نامعتبر یا منقضی‌شده."""
    return render(request, 'errors/403_csrf.html', {'reason': reason}, status=403)


def custom_403(request, exception=None):
    """صفحه اختصاصی خطای ۴۰۳ (عدم دسترسی)."""
    return render(request, '403.html', status=403)


def custom_404(request, exception=None):
    """صفحه اختصاصی خطای ۴۰۴ (صفحه یافت نشد)."""
    return render(request, '404.html', status=404)


def custom_500(request):
    """صفحه اختصاصی خطای ۵۰۰ (خطای سرور)."""
    return render(request, '500.html', status=500)
