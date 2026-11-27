from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    """دسته‌بندی موضوعی کتاب‌ها."""

    name = models.CharField(max_length=120, unique=True, verbose_name='نام دسته‌بندی')
    slug = models.SlugField(max_length=140, unique=True, allow_unicode=True, verbose_name='نامک (Slug)')

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    """اطلاعات کامل هر کتاب در کتابینو."""

    title = models.CharField(max_length=200, verbose_name='عنوان کتاب')
    author = models.CharField(max_length=150, verbose_name='نویسنده')
    description = models.TextField(verbose_name='معرفی و توضیحات')
    cover = models.ImageField(upload_to='covers/', blank=True, null=True, verbose_name='تصویر جلد')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name='دسته‌بندی',
    )
    publication_year = models.PositiveIntegerField(verbose_name='سال انتشار')
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=4.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name='امتیاز',
    )
    is_book_of_week = models.BooleanField(default=False, verbose_name='کتاب پیشنهادی هفته')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')

    class Meta:
        verbose_name = 'کتاب'
        verbose_name_plural = 'کتاب‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.author}'

    def get_absolute_url(self):
        return reverse('books:book_detail', kwargs={'pk': self.pk})


class Favorite(models.Model):
    """کتاب‌های موردعلاقه کاربران."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='کاربر',
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='کتاب',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ افزودن')

    class Meta:
        verbose_name = 'علاقه‌مندی'
        verbose_name_plural = 'علاقه‌مندی‌ها'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'book'],
                name='unique_user_book_favorite',
            )
        ]

    def __str__(self):
        return f'{self.user.username} -> {self.book.title}'


class Review(models.Model):
    """نظرات و پاسخ‌های کاربران برای کتاب‌ها."""

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='کتاب',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='book_reviews',
        verbose_name='کاربر',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='در پاسخ به',
    )
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='امتیاز',
    )
    comment = models.TextField(verbose_name='متن نظر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')

    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات کاربران'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'
