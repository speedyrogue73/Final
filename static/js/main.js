document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss alerts after 5 seconds
  document.querySelectorAll('.alert-dismissible').forEach((alertEl) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
      bsAlert.close();
    }, 5000);
  });

  // AJAX favorite toggle on book cards
  document.querySelectorAll('.js-favorite-form').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const button = form.querySelector('.book-fav-btn');
      const icon = button.querySelector('i');
      const formData = new FormData(form);

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
          },
          body: formData,
        });

        if (!response.ok) {
          form.submit();
          return;
        }

        const data = await response.json();
        button.classList.toggle('is-favorite', data.is_favorite);
        icon.className = data.is_favorite ? 'bi bi-heart-fill' : 'bi bi-heart';
        button.setAttribute(
          'title',
          data.is_favorite ? 'حذف از علاقه‌مندی‌ها' : 'افزودن به علاقه‌مندی‌ها'
        );
      } catch (err) {
        form.submit();
      }
    });
  });
});
