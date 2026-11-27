from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactMessageForm


def contact_view(request):
    """صفحه تماس با ما و ذخیره پیام در دیتابیس."""
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'پیام شما با موفقیت ارسال و ثبت شد. همکاران ما به‌زودی پاسخ خواهند داد.')
            return redirect('contact:contact')
        messages.error(request, 'لطفاً تمام فیلدهای فرم تماس را به‌درستی تکمیل کنید.')
    else:
        form = ContactMessageForm()

    return render(request, 'contact/contact.html', {'form': form})
