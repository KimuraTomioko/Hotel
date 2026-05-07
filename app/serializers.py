from rest_framework import serializers

from app.models import Booking, CustomAuthenticationUser, Hotel, Review, Room


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomAuthenticationUser
        fields = ["id", "email", "full_name", "phone", "is_admin"]
        read_only_fields = fields


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    phone = serializers.CharField(max_length=20)

    class Meta:
        model = CustomAuthenticationUser
        fields = [
            "id",
            "email",
            "full_name",
            "phone",
            "is_admin",
            "password",
        ]
        read_only_fields = ["id", "is_admin"]

    def validate_password(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Пароль должен быть больше 5 символов")
        return value

    def validate_phone(self, value):
        if not value.startswith("+7"):
            raise serializers.ValidationError("Номер телефона должен начинаться с +7")
        return value

    def create(self, validated_data):
        return CustomAuthenticationUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            "id",
            "hotel",
            "room_images",
            "type",
            "price_on_one_day",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_price_on_one_day(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть больше 0")
        return value


class HotelSerializer(serializers.ModelSerializer):
    rooms = serializers.SerializerMethodField()
    hotel_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = [
            "id",
            "owner",
            "hostel_images",
            "title",
            "description",
            "address",
            "rating",
            "created_at",
            "rooms",
            "hotel_reviews",
        ]
        read_only_fields = ["id", "owner", "created_at", "rating", "rooms", "hotel_reviews"]

    def get_rooms(self, obj):
        request = self.context.get("request")
        kwargs = getattr(request, "parser_context", {}).get("kwargs", {}) if request else {}
        if kwargs.get("pk"):
            return RoomSerializer(obj.rooms.all(), many=True, context=self.context).data
        return []

    def get_hotel_reviews(self, obj):
        request = self.context.get("request")
        kwargs = getattr(request, "parser_context", {}).get("kwargs", {}) if request else {}
        if kwargs.get("pk"):
            return ReviewSerializer(obj.hotel_reviews.all(), many=True, context=self.context).data
        return []


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "user",
            "room",
            "check_in",
            "check_out",
            "total_price",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at", "total_price"]

    def validate(self, attrs):
        check_in = attrs.get("check_in", getattr(self.instance, "check_in", None))
        check_out = attrs.get("check_out", getattr(self.instance, "check_out", None))
        room = attrs.get("room", getattr(self.instance, "room", None))

        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError("Дата выезда должна быть позже даты заезда")

        if room and check_in and check_out:
            bookings = Booking.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in,
            )
            if self.instance:
                bookings = bookings.exclude(pk=self.instance.pk)
            if bookings.exists():
                raise serializers.ValidationError("Номер уже забронирован на выбранные даты")

        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "hotel",
            "user",
            "text",
            "created_at",
            "score",
        ]
        read_only_fields = ["id", "user", "created_at"]

    def validate_score(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Рейтинг должен быть в промежутке от 1 до 5")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        hotel = attrs.get("hotel", getattr(self.instance, "hotel", None))

        if request and request.user.is_authenticated and hotel and not self.instance:
            if Review.objects.filter(hotel=hotel, user=request.user).exists():
                raise serializers.ValidationError("Вы уже оставили отзыв этому отелю")

        return attrs
