from django.contrib import admin
from .models import Book, Category, Favorite, Review

admin.site.site_header = 'پنل مدیریت Bookeat'
admin.site.site_title = 'مدیریت Bookeat'
admin.site.index_title = 'به بخش مدیریت وب‌سایت Bookeat خوش آمدید'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'book_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='تعداد کتاب‌ها')
    def book_count(self, obj):
        return obj.books.count()


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'publication_year', 'rating', 'is_book_of_week', 'created_at')
    list_filter = ('category', 'is_book_of_week', 'publication_year')
    search_fields = ('title', 'author', 'description')
    list_editable = ('rating', 'is_book_of_week')
    ordering = ('-created_at',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'book__title')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'parent', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('book__title', 'user__username', 'comment')
