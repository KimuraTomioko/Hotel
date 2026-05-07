Ниже представлено полное техническое задание (ТЗ) на основе твоего финального кода и требований, оформленное в формате Markdown (.md).
------------------------------
## Техническое Задание (ТЗ) на разработку API системы бронирования отелей## 1. Общее описание
Разработка серверной части (API) для платформы, позволяющей владельцам размещать отели и номера, а пользователям — бронировать их и оставлять отзывы.
## 2. Стек технологий

* Язык: Python 3.x
* Фреймворк: Django + Django REST Framework (DRF)
* Аутентификация: Bearer Token (на базе TokenAuthentication)
* Формат ID: UUID для всех сущностей

------------------------------
## 3. Модели данных## 3.1. Пользователь (CustomAuthenticationUser)
Модель расширяет AbstractUser.

* id: UUID (Primary Key, editable=False).
* email: EmailField (Unique, используется как логин).
* full_name: CharField (ФИО пользователя).
* phone: CharField (Unique, номер телефона).
* is_admin: BooleanField (Флаг администратора).
* password: Хэшированная строка.

## 3.2. Отель (Hotel)

* id: UUID (Primary Key).
* owner: ForeignKey (Связь с User, related_name='hotels').
* hostel_images: ImageField (Главное фото отеля).
* title: CharField (Unique, название).
* description: TextField (Описание отеля).
* address: TextField (Адрес).
* rating: FloatField (Средняя оценка отеля, авторасчет).

## 3.3. Номер (Room)

* id: UUID (Primary Key).
* hotel: ForeignKey (Связь с Hotel, related_name='rooms').
* room_images: ImageField (Фото номера).
* type: CharField (Choices: standard, deluxe).
* price_on_one_day: IntegerField (Цена за 1 сутки).
* description: TextField (Описание конкретного номера).

## 3.4. Бронирование (Booking)

* id: UUID (Primary Key).
* user: ForeignKey (Связь с User, related_name='user_bookings').
* room: ForeignKey (Связь с Room, related_name='room_bookings').
* check_in: DateField (Дата заезда).
* check_out: DateField (Дата выезда).
* total_price: IntegerField (Итоговая стоимость).

## 3.5. Отзыв (Review)

* id: UUID (Primary Key).
* hotel: ForeignKey (Связь с Hotel, related_name='hotel_reviews').
* user: ForeignKey (Связь с User, related_name='user_reviews').
* text: TextField (Текст комментария).
* score: SmallIntegerField (Оценка от 1 до 5).
* created_at: DateTimeField (Дата создания, auto_now_add=True).

------------------------------
## 4. Эндпоинты API (URLs)

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| POST | /api/auth/register/ | Регистрация пользователя | Всем |
| POST | /api/auth/login/ | Получение Bearer Token | Всем |
| GET | /api/hotels/ | Список отелей (с фильтрами) | Всем |
| POST | /api/hotels/ | Создание отеля | Авторизован |
| GET | /api/hotels/{id}/ | Детали отеля и список его номеров | Всем |
| POST | /api/bookings/ | Создание бронирования | Авторизован |
| GET | /api/bookings/my/ | История броней текущего пользователя | Авторизован |
| POST | /api/reviews/ | Оставить отзыв | Авторизован |


