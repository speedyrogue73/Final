from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """فرم ثبت نظر و امتیاز برای کتاب."""

    RATING_CHOICES = [
        (5, '۵ ستاره — عالی'),
        (4, '۴ ستاره — بسیار خوب'),
        (3, '۳ ستاره — خوب'),
        (2, '۲ ستاره — متوسط'),
        (1, '۱ ستاره — ضعیف'),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        label='امتیاز شما',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Review
        fields = ('rating', 'comment')
        labels = {
            'comment': 'دیدگاه شما',
        }
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'نظر و تجربه خود از مطالعه این کتاب را بنویسید...',
                }
            ),
        }


class ReplyForm(forms.ModelForm):
    """فرم ثبت پاسخ به یک نظر."""

    class Meta:
        model = Review
        fields = ('comment',)
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-sm',
                    'rows': 2,
                    'placeholder': 'پاسخ خود را بنویسید...',
                }
            ),
        }
