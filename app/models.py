import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import Avg


class Manager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Отсутствует email')
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_admin', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')

        return self.create_user(email, password, **kwargs)


class CustomAuthenticationUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name='Почта')
    full_name = models.CharField(max_length=64, verbose_name='Полное имя')
    phone = models.CharField(max_length=20, unique=True, verbose_name='Номер телефона')
    is_admin = models.BooleanField(default=False, verbose_name='админ?')

    username = None
    objects = Manager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Hotel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(CustomAuthenticationUser, on_delete=models.CASCADE, related_name='hotels', verbose_name='Владелец')
    hostel_images = models.ImageField(upload_to='hotels/', verbose_name='Фотографии')
    title = models.CharField(max_length=128, unique=True, verbose_name='Название')
    description = models.TextField(verbose_name='Описание отеля')
    address = models.TextField(verbose_name='Адрес')
    rating = models.FloatField(default=0.0, verbose_name='Рейтинг')
    created_at = models.DateField(auto_now_add=True, verbose_name='Дата создания отеля')

    def update_rating(self):
        average = self.hotel_reviews.aggregate(value=Avg('score'))['value'] or 0
        self.rating = round(average, 2)
        self.save(update_fields=['rating'])

    def __str__(self):
        return self.title


TYPE = [
    ('standard', 'Стандартный'),
    ('deluxe', 'Люкс')
]


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms', verbose_name='Отель')
    room_images = models.ImageField(upload_to='rooms/', verbose_name='Фотографии номера')
    type = models.CharField(max_length=20, choices=TYPE, verbose_name='Тип номера')
    price_on_one_day = models.IntegerField(verbose_name='Цена номера за день')
    description = models.TextField(verbose_name='Описание номера')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания комнаты')

    def __str__(self):
        return f'{self.hotel}: {self.get_type_display()}'


class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomAuthenticationUser, on_delete=models.CASCADE, related_name='user_bookings', verbose_name='Пользователь')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_bookings', verbose_name='Номер бронирования')
    check_in = models.DateField(verbose_name='Дата заезда')
    check_out = models.DateField(verbose_name='Дата выезда')
    total_price = models.IntegerField(verbose_name='Итоговая цена', default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания бронирования')

    def save(self, *args, **kwargs):
        days = (self.check_out - self.check_in).days
        self.total_price = max(days, 0) * self.room.price_on_one_day
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Пользователь {self.user} забронировал с {self.check_in} до {self.check_out}'


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_reviews', verbose_name='Отель')
    user = models.ForeignKey(CustomAuthenticationUser, on_delete=models.CASCADE, related_name='user_reviews', verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания комментария')
    score = models.SmallIntegerField(verbose_name='рейтинг')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.hotel.update_rating()

    def delete(self, *args, **kwargs):
        hotel = self.hotel
        super().delete(*args, **kwargs)
        hotel.update_rating()

    def __str__(self):
        return f'Пользователь {self.user} оставил отзыв гостинице {self.hotel}'
