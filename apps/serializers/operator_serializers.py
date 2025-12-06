from rest_framework import serializers

from user.serializers import RegisterSerializer
from apps.models import Operator


# ==========================
# Operator Serializer
# =========================
class OperatorSerializer(serializers.ModelSerializer):
    user = RegisterSerializer()
    # photo = serializers.ImageField(required=False)

    class Meta:
        model = Operator
        fields = [
            'id', 'user', 'status',
            'salary', 'penalty', 'gender', 'branch'
        ]

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = RegisterSerializer().create(user_data)
        operator = Operator.objects.create(user=user, **validated_data)
        return operator


    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['user'] = {
            "id": instance.user.id,
            "username": instance.user.username,
            "full_name": instance.user.first_name + " " + instance.user.last_name
        }
        rep['branch'] = instance.branch.name if instance.branch else None
        # rep['photo'] = instance.photo.url if instance.photo else None
        return rep
