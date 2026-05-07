from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from app.models import Booking, Hotel, Review, Room
from app.permission import (
    IsAdminForUnsafe,
    IsHotelOwnerForRoom,
    IsObjectUser,
    IsObjectUserOrReadOnly,
    IsOwnerOrReadOnly,
)
from app.serializers import (
    BookingSerializer,
    HotelSerializer,
    LoginSerializer,
    RegistrationSerializer,
    ReviewSerializer,
    RoomSerializer,
    UserSerializer,
)


class AuthRegisterViewSets(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(methods=["POST"], detail=False)
    def register(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "detail": "Вы успешно зарегистрировались",
                "user": UserSerializer(user).data,
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["POST"], detail=False)
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(**serializer.validated_data)
        if not user:
            return Response(
                {"detail": "Пользователь не зарегистрирован или пароль некорректный"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "detail": "Вы успешно вошли",
                "user": UserSerializer(user).data,
                "token": token.key,
            }
        )

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response(UserSerializer(request.user).data)


class HotelViewSets(viewsets.ModelViewSet):
    serializer_class = HotelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Hotel.objects.prefetch_related("rooms", "hotel_reviews").all()
        title = self.request.query_params.get("title")
        address = self.request.query_params.get("address")
        min_rating = self.request.query_params.get("min_rating")
        room_type = self.request.query_params.get("type")
        max_price = self.request.query_params.get("max_price")

        if title:
            queryset = queryset.filter(title__icontains=title)
        if address:
            queryset = queryset.filter(address__icontains=address)
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)
        if room_type:
            queryset = queryset.filter(rooms__type=room_type)
        if max_price:
            queryset = queryset.filter(rooms__price_on_one_day__lte=max_price)

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class RoomViewSets(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsHotelOwnerForRoom]

    def get_queryset(self):
        queryset = Room.objects.select_related("hotel", "hotel__owner").all()
        hotel_id = self.request.query_params.get("hotel")
        room_type = self.request.query_params.get("type")
        max_price = self.request.query_params.get("max_price")

        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)
        if room_type:
            queryset = queryset.filter(type=room_type)
        if max_price:
            queryset = queryset.filter(price_on_one_day__lte=max_price)

        return queryset

    def perform_create(self, serializer):
        hotel = serializer.validated_data["hotel"]
        if hotel.owner != self.request.user and not self.request.user.is_admin:
            self.permission_denied(self.request, message="Вы не можете создавать номера в чужих гостиницах")
        serializer.save()


class BookingViewSets(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsObjectUser]

    def get_queryset(self):
        queryset = Booking.objects.select_related("user", "room", "room__hotel")
        if self.request.user.is_admin:
            return queryset
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=["GET"], detail=False)
    def my(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class ReviewViewSets(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsObjectUserOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.select_related("hotel", "user").all()
        hotel_id = self.request.query_params.get("hotel")
        if hotel_id:
            queryset = queryset.filter(hotel_id=hotel_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
