from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ReplyForm, ReviewForm
from .models import Book, Category, Favorite, Review


def _get_user_favorite_ids(user):
    if user.is_authenticated:
        return set(Favorite.objects.filter(user=user).values_list('book_id', flat=True))
    return set()


def home(request):
    """صفحه اصلی کتابینو."""
    popular_books = Book.objects.select_related('category').order_by('-rating', '-created_at')[:4]
    latest_books = Book.objects.select_related('category').order_by('-created_at')[:4]
    categories = Category.objects.annotate(book_count=Count('books')).order_by('-book_count', 'name')
    book_of_week = (
        Book.objects.select_related('category').filter(is_book_of_week=True).first()
        or Book.objects.select_related('category').order_by('-rating').first()
    )
    context = {
        'popular_books': popular_books,
        'latest_books': latest_books,
        'categories': categories,
        'book_of_week': book_of_week,
        'user_favorite_ids': _get_user_favorite_ids(request.user),
    }
    return render(request, 'books/home.html', context)


def book_list(request):
    """صفحه همه کتاب‌ها با قابلیت جست‌وجو، فیلتر دسته‌بندی و مرتب‌سازی."""
    books_qs = Book.objects.select_related('category').all()
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    sort_by = request.GET.get('sort', 'newest').strip()

    if query:
        books_qs = books_qs.filter(Q(title__icontains=query) | Q(author__icontains=query))

    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        books_qs = books_qs.filter(category=active_category)

    sort_map = {
        'newest': ('-created_at',),
        'rating': ('-rating', '-created_at'),
        'year': ('-publication_year', '-rating'),
        'title': ('title',),
    }
    books_qs = books_qs.order_by(*sort_map.get(sort_by, ('-created_at',)))

    paginator = Paginator(books_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.annotate(book_count=Count('books')).order_by('name')
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'active_category': active_category,
        'sort_by': sort_by,
        'total_results': paginator.count,
        'user_favorite_ids': _get_user_favorite_ids(request.user),
    }
    return render(request, 'books/book_list.html', context)


def book_detail(request, pk):
    """صفحه جزئیات کتاب، بخش نظرات و پاسخ‌های کاربران و نمایش کتاب‌های مشابه."""
    book = get_object_or_404(Book.objects.select_related('category'), pk=pk)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'برای ثبت نظر یا پاسخ ابتدا وارد حساب کاربری خود شوید.')
            return redirect('accounts:login')

        parent_id = request.POST.get('parent_id')
        if parent_id:
            parent_review = get_object_or_404(Review, pk=parent_id, book=book)
            reply_form = ReplyForm(request.POST)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.book = book
                reply.user = request.user
                reply.parent = parent_review
                reply.rating = None
                reply.save()
                messages.success(request, 'پاسخ شما با موفقیت ثبت شد.')
                return redirect(f'{book.get_absolute_url()}#review-{parent_review.pk}')
            messages.error(request, 'لطفاً متن پاسخ را وارد کنید.')
            review_form = ReviewForm()
        else:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.book = book
                review.user = request.user
                review.save()
                messages.success(request, 'دیدگاه شما با موفقیت ثبت شد.')
                return redirect(f'{book.get_absolute_url()}#reviews')
            messages.error(request, 'لطفاً متن نظر و امتیاز را به‌درستی وارد کنید.')
    else:
        review_form = ReviewForm()

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, book=book).exists()

    reviews = (
        book.reviews.filter(parent__isnull=True)
        .select_related('user')
        .prefetch_related('replies__user')
    )
    related_books = (
        Book.objects.select_related('category')
        .filter(category=book.category)
        .exclude(pk=book.pk)
        .order_by('-rating')[:4]
    )
    context = {
        'book': book,
        'is_favorite': is_favorite,
        'reviews': reviews,
        'review_form': review_form,
        'reply_form': ReplyForm(),
        'related_books': related_books,
        'user_favorite_ids': _get_user_favorite_ids(request.user),
    }
    return render(request, 'books/book_detail.html', context)


@login_required
@require_POST
def delete_review(request, pk):
    """حذف نظر توسط نویسنده همان نظر."""
    review = get_object_or_404(Review, pk=pk, user=request.user)
    book_url = review.book.get_absolute_url()
    review.delete()
    messages.info(request, 'دیدگاه شما حذف شد.')
    return redirect(f'{book_url}#reviews')


@login_required
@require_POST
def toggle_favorite(request, pk):
    """افزودن یا حذف کتاب از لیست علاقه‌مندی‌های کاربر."""
    book = get_object_or_404(Book, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, book=book)

    if created:
        is_favorite = True
        msg = f'کتاب «{book.title}» به علاقه‌مندی‌های شما اضافه شد.'
        messages.success(request, msg)
    else:
        favorite.delete()
        is_favorite = False
        msg = f'کتاب «{book.title}» از علاقه‌مندی‌های شما حذف شد.'
        messages.info(request, msg)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_favorite': is_favorite, 'message': msg})

    next_url = request.POST.get('next') or book.get_absolute_url()
    return redirect(next_url)


def about(request):
    """صفحه درباره ما."""
    context = {
        'books_count': Book.objects.count(),
        'categories_count': Category.objects.count(),
        'users_count': User.objects.count(),
    }
    return render(request, 'books/about.html', context)
