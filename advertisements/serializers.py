from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from advertisements.models import Advertisement


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )
        read_only_fields = ['creator']

    def create(self, validated_data):
        """Метод для создания"""

        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        request_user = self.context['request']
        creator = request_user.user
        request_method = request_user.method
        open_status = 'OPEN'
        limit = 10
        open_ads_limit = Advertisement.objects.filter(creator=creator, status=open_status).count()
        status_data = data.get('status', '')
        if (request_method == 'POST' and status_data == open_status) and open_ads_limit >= limit:
            raise ValidationError(f'You cannot have more than {limit} open ads')
        return data
