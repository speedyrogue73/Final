from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from books.models import Book, Category, Favorite, Review
from contact.models import ContactMessage


class KetabinoTests(TestCase):
    def setUp(self):
        self.cat1 = Category.objects.create(name='ادبیات ایران', slug='iranian-lit')
        self.cat2 = Category.objects.create(name='فلسفه', slug='philosophy')
        self.book1 = Book.objects.create(
            title='سووشون',
            author='سیمین دانشور',
            description='رمان کلاسیک ایرانی',
            category=self.cat1,
            publication_year=1348,
            rating=4.8,
            is_book_of_week=True,
        )
        self.book2 = Book.objects.create(
            title='دنیای سوفی',
            author='یوستین گردر',
            description='آشنایی با تاریخ فلسفه',
            category=self.cat2,
            publication_year=1991,
            rating=4.6,
        )
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='StrongPassword123',
            first_name='علی',
            last_name='رضایی',
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='StrongPassword123',
        )

    def test_public_pages_status_codes(self):
        urls = [
            reverse('books:home'),
            reverse('books:book_list'),
            reverse('books:book_detail', args=[self.book1.pk]),
            reverse('books:about'),
            reverse('contact:contact'),
            reverse('accounts:login'),
            reverse('accounts:register'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f'Failed on {url}')

    def test_book_search_and_category_filter(self):
        res_search = self.client.get(reverse('books:book_list'), {'q': 'دانشور'})
        self.assertContains(res_search, 'سووشون')
        self.assertNotContains(res_search, 'دنیای سوفی')

        res_cat = self.client.get(reverse('books:book_list'), {'category': 'philosophy'})
        self.assertContains(res_cat, 'دنیای سوفی')
        self.assertNotContains(res_cat, 'سووشون')

    def test_favorite_uniqueness_and_toggle(self):
        Favorite.objects.create(user=self.user, book=self.book1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Favorite.objects.create(user=self.user, book=self.book1)

        self.client.login(username='tester', password='StrongPassword123')
        # Toggle off
        res = self.client.post(reverse('books:toggle_favorite', args=[self.book1.pk]))
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Favorite.objects.filter(user=self.user, book=self.book1).exists())

        # Toggle on
        self.client.post(reverse('books:toggle_favorite', args=[self.book1.pk]))
        self.assertTrue(Favorite.objects.filter(user=self.user, book=self.book1).exists())

    def test_dashboard_requires_login_and_isolates_favorites(self):
        res_anon = self.client.get(reverse('dashboard:profile'))
        self.assertEqual(res_anon.status_code, 302)

        other_fav = Favorite.objects.create(user=self.other_user, book=self.book2)
        self.client.login(username='tester', password='StrongPassword123')
        res_auth = self.client.get(reverse('dashboard:profile'))
        self.assertEqual(res_auth.status_code, 200)

        # User cannot delete another user's favorite
        res_del = self.client.post(reverse('dashboard:remove_favorite', args=[other_fav.pk]))
        self.assertEqual(res_del.status_code, 404)
        self.assertTrue(Favorite.objects.filter(pk=other_fav.pk).exists())

    def test_contact_form_saves_message(self):
        response = self.client.post(
            reverse('contact:contact'),
            {
                'name': 'مریم کریمی',
                'email': 'maryam@example.com',
                'subject': 'پیشنهاد کتاب',
                'message': 'لطفاً کتاب‌های بیشتری در حوزه شعر اضافه کنید.',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(ContactMessage.objects.first().name, 'مریم کریمی')

    def test_book_review_create_and_delete(self):
        self.client.login(username='tester', password='StrongPassword123')
        res = self.client.post(
            reverse('books:book_detail', args=[self.book1.pk]),
            {'rating': 5, 'comment': 'کتاب فوق‌العاده‌ای بود!'},
        )
        self.assertEqual(res.status_code, 302)
        review = Review.objects.get(book=self.book1, user=self.user)
        self.assertEqual(review.comment, 'کتاب فوق‌العاده‌ای بود!')

        # Reply to review
        self.client.login(username='other', password='StrongPassword123')
        res_reply = self.client.post(
            reverse('books:book_detail', args=[self.book1.pk]),
            {'parent_id': review.pk, 'comment': 'من هم کاملاً موافقم!'},
        )
        self.assertEqual(res_reply.status_code, 302)
        self.assertEqual(review.replies.count(), 1)
        self.assertEqual(review.replies.first().comment, 'من هم کاملاً موافقم!')

        # Other user cannot delete tester's review
        self.client.login(username='other', password='StrongPassword123')
        res_forbidden = self.client.post(reverse('books:delete_review', args=[review.pk]))
        self.assertEqual(res_forbidden.status_code, 404)
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())

        # Author can delete own review
        self.client.login(username='tester', password='StrongPassword123')
        res_ok = self.client.post(reverse('books:delete_review', args=[review.pk]))
        self.assertEqual(res_ok.status_code, 302)
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())
