import html
from io import BytesIO
from pathlib import Path

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from books.models import Book, Category, Favorite, Review


PALETTES = [
    ('#3B2618', '#D97736', '#FAF6F0'),
    ('#1F3A3D', '#E09F3E', '#F4F1DE'),
    ('#4A2545', '#D4A373', '#FEFAE0'),
    ('#2B3A67', '#E88D67', '#F7F4EA'),
    ('#3D405B', '#E07A5F', '#F4F1DE'),
    ('#582F0E', '#DDA15E', '#FEFAE0'),
    ('#283618', '#BC6C25', '#FEFAE0'),
    ('#6D2E46', '#E29578', '#FFF1E6'),
]


def _generate_pillow_cover(index: int, filename: str) -> ContentFile:
    """تولید تصویر جلد جایگزین در صورت در دسترس نبودن مرورگر."""
    bg_hex, accent_hex, light_hex = PALETTES[index % len(PALETTES)]
    width, height = 450, 600
    img = Image.new('RGB', (width, height), bg_hex)
    draw = ImageDraw.Draw(img)
    draw.rectangle([width - 28, 0, width, height], fill='#1E140D')
    draw.rectangle([28, 28, width - 52, height - 28], outline=accent_hex, width=3)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), name=filename)


def _render_bespoke_covers_with_playwright(books_list):
    """رندر جلد اختصاصی فارسی برای هر کتاب با عنوان، نویسنده و دسته‌بندی همان کتاب."""
    from playwright.sync_api import sync_playwright

    covers_dir = Path(settings.MEDIA_ROOT) / 'covers'
    covers_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = None
        for channel in ('chrome', 'msedge', None):
            try:
                browser = p.chromium.launch(channel=channel) if channel else p.chromium.launch()
                break
            except Exception:
                continue
        if browser is None:
            raise RuntimeError('No Chromium browser available')
        page = browser.new_page(viewport={'width': 450, 'height': 600}, device_scale_factor=1)

        for idx, item in enumerate(books_list):
            bg_hex, accent_hex, light_hex = PALETTES[idx % len(PALETTES)]
            title_esc = html.escape(item['title'])
            author_esc = html.escape(item['author'])
            cat_esc = html.escape(item['category_name'])
            year_esc = html.escape(str(item['publication_year']))
            symbol = item.get('symbol', '📖')

            html_content = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      width: 450px;
      height: 600px;
      background: linear-gradient(155deg, {bg_hex} 0%, #1B120C 100%);
      color: {light_hex};
      font-family: Tahoma, 'Segoe UI', sans-serif;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 34px 48px 34px 34px;
    }}
    .spine {{
      position: absolute;
      top: 0; right: 0; bottom: 0;
      width: 24px;
      background: linear-gradient(90deg, rgba(0,0,0,0.45), rgba(255,255,255,0.08));
      border-left: 3px solid {accent_hex};
    }}
    .frame {{
      position: absolute;
      inset: 18px 36px 18px 18px;
      border: 2px solid {accent_hex};
      border-radius: 10px;
      pointer-events: none;
    }}
    .frame-inner {{
      position: absolute;
      inset: 25px 43px 25px 25px;
      border: 1px solid rgba(255,255,255,0.22);
      border-radius: 6px;
      pointer-events: none;
    }}
    .top-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
      opacity: 0.9;
      z-index: 2;
      padding-top: 8px;
    }}
    .cat-badge {{
      background: {accent_hex};
      color: #1A110B;
      font-weight: 700;
      padding: 5px 14px;
      border-radius: 999px;
      font-size: 12px;
    }}
    .center-area {{
      text-align: center;
      z-index: 2;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 18px;
    }}
    .medallion {{
      width: 112px;
      height: 112px;
      border-radius: 50%;
      border: 3px solid {accent_hex};
      background: rgba(255,255,255,0.06);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 46px;
      box-shadow: 0 10px 26px rgba(0,0,0,0.35);
    }}
    .title {{
      font-size: 30px;
      font-weight: 800;
      line-height: 1.45;
      color: #FFFFFF;
      text-shadow: 0 3px 10px rgba(0,0,0,0.45);
      padding: 0 10px;
    }}
    .divider {{
      width: 86px;
      height: 3px;
      background: {accent_hex};
      border-radius: 4px;
    }}
    .author {{
      font-size: 19px;
      font-weight: 600;
      color: {accent_hex};
    }}
    .footer-bar {{
      text-align: center;
      font-size: 12px;
      letter-spacing: 0.5px;
      opacity: 0.78;
      z-index: 2;
      padding-bottom: 6px;
    }}
  </style>
</head>
<body>
  <div class="spine"></div>
  <div class="frame"></div>
  <div class="frame-inner"></div>
  <div class="top-bar">
    <span class="cat-badge">{cat_esc}</span>
    <span>سال {year_esc}</span>
  </div>
  <div class="center-area">
    <div class="medallion">{symbol}</div>
    <h1 class="title">{title_esc}</h1>
    <div class="divider"></div>
    <div class="author">{author_esc}</div>
  </div>
  <div class="footer-bar">نشر و معرفی اختصاصی • Bookeat</div>
</body>
</html>"""

            page.set_content(html_content)
            out_path = covers_dir / f'book_{idx + 1}.png'
            page.screenshot(path=str(out_path))
            item['cover_rel_path'] = f'covers/book_{idx + 1}.png'

        browser.close()


class Command(BaseCommand):
    help = 'ایجاد دسته‌بندی‌ها، ۱۶ کتاب نمونه با جلد اختصاصی هر کتاب، نظرات نمونه و کاربران آزمایشی'

    def handle(self, *args, **options):
        categories_data = [
            ('ادبیات ایران', 'iranian-literature'),
            ('ادبیات جهان', 'world-literature'),
            ('فلسفه و اندیشه', 'philosophy'),
            ('روانشناسی و توسعه فردی', 'psychology'),
            ('تاریخ و تمدن', 'history'),
            ('علمی و فناوری', 'science'),
        ]

        categories = {}
        for name, slug in categories_data:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            categories[slug] = cat

        books_data = [
            {
                'title': 'سووشون',
                'author': 'سیمین دانشور',
                'category': 'iranian-literature',
                'category_name': 'ادبیات ایران',
                'publication_year': 1348,
                'rating': 4.8,
                'is_book_of_week': True,
                'symbol': '🌾',
                'description': (
                    'سووشون نخستین رمان بلند به قلم یک زن ایرانی و یکی از ماندگارترین آثار ادبیات معاصر فارسی است. '
                    'داستان در شهر شیراز و در سال‌های پایانی جنگ جهانی دوم رخ می‌دهد و زندگی یوسف و زری را در کشاکش اشغال ایران، '
                    'آرمان‌خواهی، عشق و ایستادگی روایت می‌کند.'
                ),
            },
            {
                'title': 'بوف کور',
                'author': 'صادق هدایت',
                'category': 'iranian-literature',
                'category_name': 'ادبیات ایران',
                'publication_year': 1315,
                'rating': 4.6,
                'symbol': '🦉',
                'description': (
                    'شاهکار سوررئالیستی صادق هدایت که به عنوان مهم‌ترین رمان مدرن فارسی شناخته می‌شود. '
                    'راوی داستان در فضایی وهم‌آلود و شاعرانه، میان گذشته و حال و رویا و واقعیت، به جست‌وجوی معنای هستی و رنج انسانی می‌پردازد.'
                ),
            },
            {
                'title': 'کلیدر',
                'author': 'محمود دولت‌آبادی',
                'category': 'iranian-literature',
                'category_name': 'ادبیات ایران',
                'publication_year': 1357,
                'rating': 4.9,
                'symbol': '🐎',
                'description': (
                    'حماسه‌ای ده جلدی درباره زندگی و مبارزه خانواده کلمیشی در منطقه سبزوار خراسان. '
                    'گل‌محمد، شخصیت محوری رمان، نماد شرف، غیرت و ایستادگی در برابر ظلم اربابان و ساختارهای فاسد است.'
                ),
            },
            {
                'title': 'چشم‌هایش',
                'author': 'بزرگ علوی',
                'category': 'iranian-literature',
                'category_name': 'ادبیات ایران',
                'publication_year': 1331,
                'rating': 4.5,
                'symbol': '🎨',
                'description': (
                    'روایتی عاشقانه و سیاسی درباره نقاش مشهوری به نام استاد ماکان و تابلوی مرموز «چشم‌هایش». '
                    'ناظم مدرسه هنر پس از مرگ استاد، در پی کشف هویت زن ناشناس تابلو و رازهای نهفته در آن برمی‌آید.'
                ),
            },
            {
                'title': 'صد سال تنهایی',
                'author': 'گابریل گارسیا مارکز',
                'category': 'world-literature',
                'category_name': 'ادبیات جهان',
                'publication_year': 1967,
                'rating': 4.9,
                'symbol': '🦋',
                'description': (
                    'مهم‌ترین اثر رئالیسم جادویی در ادبیات جهان که داستان هفت نسل از خاندان بوئندیا را در شهر خیالی ماکوندو روایت می‌کند. '
                    'مارکز با نثری جادویی، تاریخ، عشق، جنگ و تنهایی انسان مدرن را در هم می‌آمیزد.'
                ),
            },
            {
                'title': 'شازده کوچولو',
                'author': 'آنتوان دو سنت اگزوپری',
                'category': 'world-literature',
                'category_name': 'ادبیات جهان',
                'publication_year': 1943,
                'rating': 4.9,
                'symbol': '🌹',
                'description': (
                    'داستانی لطیف و فلسفی درباره خلبانی که در صحرا سقوط می‌کند و با شاهزاده‌ای کوچک از سیارکی دوردست آشنا می‌شود. '
                    'این کتاب با زبانی ساده، عمیق‌ترین مفاهیم دوستی، عشق، مسئولیت‌پذیری و نگاه کودکانه به جهان را یادآوری می‌کند.'
                ),
            },
            {
                'title': '۱۹۸۴',
                'author': 'جورج اورول',
                'category': 'world-literature',
                'category_name': 'ادبیات جهان',
                'publication_year': 1949,
                'rating': 4.8,
                'symbol': '👁️',
                'description': (
                    'رمانی پادآرمان‌شهری و هشداردهنده درباره جامعه‌ای تمامیت‌خواه تحت نظارت دائمی «برادر بزرگ». '
                    'وینستون اسمیت در تلاش است در میان سانسور، تغییر تاریخ و کنترل افکار، حقیقت و آزادی فردی را حفظ کند.'
                ),
            },
            {
                'title': 'جنایت و مکافات',
                'author': 'فئودور داستایفسکی',
                'category': 'world-literature',
                'category_name': 'ادبیات جهان',
                'publication_year': 1866,
                'rating': 4.8,
                'symbol': '⚖️',
                'description': (
                    'کاوشی عمیق در روان انسان و کشمکش وجدان اخلاقی. راسکولنیکف، دانشجوی فقیر سن‌پترزبورگ، مرتکب قتلی می‌شود '
                    'اما پس از آن در گرداب عذاب وجدان، ترس و جست‌وجوی رستگاری گرفتار می‌آید.'
                ),
            },
            {
                'title': 'دنیای سوفی',
                'author': 'یوستین گردر',
                'category': 'philosophy',
                'category_name': 'فلسفه و اندیشه',
                'publication_year': 1991,
                'rating': 4.6,
                'symbol': '🦉',
                'description': (
                    'رمانی جذاب برای آشنایی با تاریخ فلسفه غرب؛ از فیلسوفان پیشاسقراطی تا اندیشمندان معاصر. '
                    'دختری نوجوان به نام سوفی با دریافت نامه‌های مرموز و پرسش‌هایی بنیادین، سفری شگفت‌انگیز در دنیای اندیشه آغاز می‌کند.'
                ),
            },
            {
                'title': 'تسلی‌بخشی‌های فلسفه',
                'author': 'آلن دو باتن',
                'category': 'philosophy',
                'category_name': 'فلسفه و اندیشه',
                'publication_year': 2000,
                'rating': 4.4,
                'symbol': '🏛️',
                'description': (
                    'آلن دو باتن نشان می‌دهد که چگونه اندیشه‌های شش فیلسوف بزرگ از جمله سقراط، اپیکور، سنکا، مونتنی، شوپنهاور و نیچه '
                    'می‌توانند در مواجهه با مشکلات روزمره مانند شکست، تنهایی و اضطراب به ما آرامش ببخشند.'
                ),
            },
            {
                'title': 'انسان در جست‌وجوی معنا',
                'author': 'ویکتور فرانکل',
                'category': 'psychology',
                'category_name': 'روانشناسی و توسعه فردی',
                'publication_year': 1946,
                'rating': 4.8,
                'symbol': '🕯️',
                'description': (
                    'خاطرات تکان‌دهنده ویکتور فرانکل از اردوگاه‌های کار اجباری و معرفی مکتب روان‌درمانی «معنادرمانی». '
                    'او نشان می‌دهد که حتی در سخت‌ترین شرایط، انسان می‌تواند با یافتن معنا، امید و هدف را زنده نگه دارد.'
                ),
            },
            {
                'title': 'عادت‌های اتمی',
                'author': 'جیمز کلیر',
                'category': 'psychology',
                'category_name': 'روانشناسی و توسعه فردی',
                'publication_year': 2018,
                'rating': 4.7,
                'symbol': '⚛️',
                'description': (
                    'راهنمای عملی و علمی برای ساخت عادت‌های خوب و ترک عادت‌های مخرب از طریق تغییرات کوچک اما پیوسته. '
                    'جیمز کلیر چهار قانون تغییر رفتار را با مثال‌های ملموس و کاربردی آموزش می‌دهد.'
                ),
            },
            {
                'title': 'اثر مرکب',
                'author': 'دارن هاردی',
                'category': 'psychology',
                'category_name': 'روانشناسی و توسعه فردی',
                'publication_year': 2010,
                'rating': 4.3,
                'symbol': '📈',
                'description': (
                    'کتابی درباره قدرت انتخاب‌های کوچک روزانه که در طول زمان به نتایج بزرگ و شگفت‌انگیز منتهی می‌شوند. '
                    'نویسنده به جای وعده‌های موفقیت سریع، بر استمرار، انضباط شخصی و پیگیری عادت‌ها تمرکز دارد.'
                ),
            },
            {
                'title': 'انسان خردمند',
                'author': 'یووال نوح هراری',
                'category': 'history',
                'category_name': 'تاریخ و تمدن',
                'publication_year': 2011,
                'rating': 4.7,
                'symbol': '🌍',
                'description': (
                    'مروری جامع و خواندنی بر تاریخ گونه انسان؛ از انقلاب شناختی و کشاورزی تا انقلاب علمی و عصر مدرن. '
                    'هراری بررسی می‌کند چگونه داستان‌ها، پول، امپراتوری‌ها و علم سرنوشت بشر را شکل داده‌اند.'
                ),
            },
            {
                'title': 'تاریخ تمدن ایران',
                'author': 'عبدالحسین زرین‌کوب',
                'category': 'history',
                'category_name': 'تاریخ و تمدن',
                'publication_year': 1378,
                'rating': 4.6,
                'symbol': '🏺',
                'description': (
                    'نگاهی ژرف و مستند به فراز و نشیب‌های تاریخ، فرهنگ و تمدن ایران از دوران باستان تا عصر جدید. '
                    'زرین‌کوب با نثری شیوا، پیوستگی فرهنگی ایران را در طول سده‌ها تحلیل می‌کند.'
                ),
            },
            {
                'title': 'تاریخچه زمان',
                'author': 'استیون هاوکینگ',
                'category': 'science',
                'category_name': 'علمی و فناوری',
                'publication_year': 1988,
                'rating': 4.6,
                'symbol': '🌌',
                'description': (
                    'یکی از پرفروش‌ترین کتاب‌های علم برای عموم که به زبان ساده مفاهیمی چون مهبانگ، سیاه‌چاله‌ها، نسبیت و ماهیت زمان را توضیح می‌دهد. '
                    'هاوکینگ خواننده را به قلب پرسش‌های بنیادین کیهان‌شناسی می‌برد.'
                ),
            },
        ]

        use_playwright = False
        try:
            _render_bespoke_covers_with_playwright(books_data)
            use_playwright = True
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f'Playwright در دسترس نبود ({exc})؛ استفاده از جلد جایگزین.'))

        official_urls = {
            'سووشون': 'https://covers.openlibrary.org/b/id/3973029-L.jpg',
            'بوف کور': 'https://upload.wikimedia.org/wikipedia/commons/6/60/Cover_of_The_Blind_Owl.png',
            'کلیدر': 'https://covers.openlibrary.org/b/id/999462-L.jpg',
            'چشم‌هایش': 'https://covers.openlibrary.org/b/id/12629553-L.jpg',
            'صد سال تنهایی': 'https://covers.openlibrary.org/b/id/12627383-L.jpg',
            'شازده کوچولو': 'https://covers.openlibrary.org/b/id/10708272-L.jpg',
            '۱۹۸۴': 'https://covers.openlibrary.org/b/id/9267242-L.jpg',
            'جنایت و مکافات': 'https://covers.openlibrary.org/b/id/9411873-L.jpg',
            'دنیای سوفی': 'https://covers.openlibrary.org/b/id/223463-L.jpg',
            'تسلی‌بخشی‌های فلسفه': 'https://covers.openlibrary.org/b/id/10124965-L.jpg',
            'انسان در جست‌وجوی معنا': 'https://covers.openlibrary.org/b/id/8516506-L.jpg',
            'عادت‌های اتمی': 'https://covers.openlibrary.org/b/id/12539702-L.jpg',
            'اثر مرکب': 'https://covers.openlibrary.org/b/id/7115046-L.jpg',
            'انسان خردمند': 'https://covers.openlibrary.org/b/id/8634250-L.jpg',
            'تاریخ تمدن ایران': 'https://img.taaghche.com/frontCover/217805.jpg',
            'تاریخچه زمان': 'https://covers.openlibrary.org/b/id/10432365-L.jpg',
        }

        covers_dir = Path(settings.MEDIA_ROOT) / 'covers'
        covers_dir.mkdir(parents=True, exist_ok=True)

        created_count = 0
        for idx, item in enumerate(books_data):
            book, created = Book.objects.get_or_create(
                title=item['title'],
                author=item['author'],
                defaults={
                    'category': categories[item['category']],
                    'publication_year': item['publication_year'],
                    'rating': item['rating'],
                    'is_book_of_week': item.get('is_book_of_week', False),
                    'description': item['description'],
                },
            )

            # Try downloading official cover image first
            downloaded = False
            url = official_urls.get(item['title'])
            if url:
                try:
                    resp = requests.get(url, headers={'User-Agent': 'Bookeat/1.0'}, timeout=12)
                    if resp.status_code == 200 and len(resp.content) > 2000:
                        ext = 'png' if url.lower().endswith('.png') else 'jpg'
                        fname = f'official_{book.pk}.{ext}'
                        (covers_dir / fname).write_bytes(resp.content)
                        book.cover.name = f'covers/{fname}'
                        book.save(update_fields=['cover'])
                        downloaded = True
                except Exception:
                    pass

            if not downloaded:
                if use_playwright and 'cover_rel_path' in item:
                    book.cover.name = item['cover_rel_path']
                    book.save(update_fields=['cover'])
                elif created or not book.cover:
                    cover_file = _generate_pillow_cover(idx, f'book_{idx + 1}.png')
                    book.cover.save(f'book_{idx + 1}.png', cover_file, save=True)
            if created:
                created_count += 1

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@bookeat.ir', 'Admin12345')

        demo_user, user_created = User.objects.get_or_create(
            username='reader',
            defaults={
                'first_name': 'سارا',
                'last_name': 'محمدی',
                'email': 'reader@bookeat.ir',
            },
        )
        if user_created:
            demo_user.set_password('Reader12345')
            demo_user.save()
            for fav_book in Book.objects.all()[:3]:
                Favorite.objects.get_or_create(user=demo_user, book=fav_book)

        # Sample reviews if none exist yet
        if Review.objects.count() == 0:
            sample_reviews = [
                ('سووشون', 5, 'یکی از زیباترین رمان‌های فارسی که تا امروز خوانده‌ام. شخصیت‌پردازی زری و فضای شیراز فوق‌العاده است.'),
                ('شازده کوچولو', 5, 'کتابی که در هر سنی می‌توان خواند و هر بار نکته‌ای تازه از آن آموخت.'),
                ('۱۹۸۴', 5, 'اثری تکان‌دهنده و عمیق که هنوز هم پس از دهه‌ها کاملاً ملموس و هشداردهنده است.'),
                ('عادت‌های اتمی', 4, 'بسیار کاربردی و قابل اجرا در زندگی روزمره؛ مثال‌ها کمک زیادی به درک مفاهیم می‌کنند.'),
            ]
            for title, rating_val, text in sample_reviews:
                b = Book.objects.filter(title=title).first()
                if b:
                    Review.objects.create(book=b, user=demo_user, rating=rating_val, comment=text)

        self.stdout.write(
            self.style.SUCCESS(
                f'عملیات با موفقیت انجام شد: {created_count} کتاب جدید، جلد اختصاصی هر کتاب و نظرات نمونه ثبت شدند. '
                f'مجموع کتاب‌ها: {Book.objects.count()} | دسته‌بندی‌ها: {Category.objects.count()}'
            )
        )
