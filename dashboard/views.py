from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from books.models import Favorite
from .forms import ProfileUpdateForm


@login_required
def profile_view(request):
    """پنل کاربری: نمایش و ویرایش پروفایل و مدیریت کتاب‌های موردعلاقه."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات پروفایل شما با موفقیت به‌روزرسانی شد.')
            return redirect('dashboard:profile')
        messages.error(request, 'لطفاً خطاهای فرم پروفایل را بررسی کنید.')
    else:
        form = ProfileUpdateForm(instance=request.user)

    favorites = Favorite.objects.filter(user=request.user).select_related('book', 'book__category')
    context = {
        'form': form,
        'favorites': favorites,
    }
    return render(request, 'dashboard/profile.html', context)


@login_required
@require_POST
def remove_favorite_view(request, pk):
    """حذف کتاب از علاقه‌مندی‌های کاربر جاری."""
    favorite = get_object_or_404(Favorite, pk=pk, user=request.user)
    book_title = favorite.book.title
    favorite.delete()
    messages.success(request, f'کتاب «{book_title}» از لیست علاقه‌مندی‌های شما حذف شد.')
    return redirect('dashboard:profile')
