from rest_framework import serializers
from apps.models import Payment, OperatorMonthlySalary, Lead


class PaymentCreateSerializer(serializers.ModelSerializer):
    lead_id = serializers.IntegerField(write_only=True)

    # Leaddan olinadigan maydonlar (saqlanmaydi, faqat ko‘rinadi)
    full_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    operator = serializers.SerializerMethodField()

    # Coursetan olinadigan maydonlar
    course_name = serializers.SerializerMethodField()
    course_price = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'lead_id', 'full_name', 'phone', 'operator', 'amount', 'note', 'created_at', 'course_name', 'course_price'
        ]
        read_only_fields = ['id', 'created_at', 'full_name', 'phone', 'operator', 'course_name', 'course_price']


    def validate_lead_id(self, value):
        try:
            lead = Lead.objects.get(pk=value)
        except Lead.DoesNotExist:
            raise serializers.ValidationError("Lead topilmadi.")
        return value

    def create(self, validated_data):
        lead_id = validated_data.pop("lead_id")
        lead = Lead.objects.get(pk=lead_id)

        payment = Payment.objects.create(
            lead=lead,
            **validated_data
        )

        return payment

    def get_full_name(self, obj):
        return obj.lead.full_name

    def get_phone(self, obj):
        return obj.lead.phone

    def get_operator(self, obj):
        return obj.lead.operator.user.username

    def get_course_name(self, obj):
        return obj.lead.course.title if obj.lead.course else None

    def get_course_price(self, obj):
        return obj.lead.course.price if obj.lead.course else None



class OperatorSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = OperatorMonthlySalary
        fields = "__all__"