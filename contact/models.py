from django.db import models


class ContactMessage(models.Model):
    """پیام‌های ارسال‌شده از فرم تماس با ما."""

    name = models.CharField(max_length=120, verbose_name='نام و نام خانوادگی')
    email = models.EmailField(verbose_name='ایمیل')
    subject = models.CharField(max_length=200, verbose_name='موضوع')
    message = models.TextField(verbose_name='متن پیام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')

    class Meta:
        verbose_name = 'پیام تماس'
        verbose_name_plural = 'پیام‌های تماس با ما'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.subject} ({self.name})'
