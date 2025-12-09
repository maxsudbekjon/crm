from django.contrib import admin
from django.utils.safestring import mark_safe
from apps.models import Branch, Operator, Lead, Task, Penalty, SMS, Contract, Notification, Call, Course, Enrollment
from apps.tasks import process_lead_commission

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created_at', 'updated_at')
    search_fields = ('name', 'location')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_lead_amount','commission_rate', 'gender', 'salary', 'penalty', 'branch', 'photo_tag',
                    'created_at')
    search_fields = ('user', )
    list_filter = ('status', 'gender', 'branch')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('user',)

    def total_lead_amount(self, obj):
        from django.db.models import Sum
        total = Lead.objects.filter(operator=obj, status='sold').aggregate(total=Sum('amount'))['total']
        return total or 0

    total_lead_amount.short_description = "Umumiy Amount"

    def photo_tag(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="50" height="50" style="border-radius:5px;" />')
        return "-"

    photo_tag.short_description = 'Photo'

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'status', 'course', 'operator', 'source', 'demo_date', 'last_contact_date', 'created_at',
                    'updated_at')
    list_filter = ('status', 'course', 'operator', 'source')
    search_fields = ('full_name', 'phone', 'operator__user__username')
    ordering = ('-demo_date',)
    readonly_fields = ('created_at', 'updated_at')
    fields = ('full_name', 'phone', 'course', 'operator', 'status', 'source', 'demo_date', 'last_contact_date')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'operator', 'lead', 'is_completed', 'deadline', 'created_at',
                    'updated_at')
    list_filter = ('is_completed', 'deadline')
    search_fields = ('title', 'operator__full_name', 'lead__full_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_operator_username', 'message', 'created_at', 'is_read')

    def get_operator_username(self, obj):
        return obj.user.user.username  # operator → customuser → username

    get_operator_username.short_description = 'Operator'

    # Filter qilish uchun
    list_filter = ('is_read', 'created_at', 'user')


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('call_time', 'duration_seconds', 'result')
    list_filter = ('call_time', 'duration_seconds', 'result')
    search_fields = ('call_time', 'duration_seconds', 'result')
    readonly_fields = ('call_time', 'duration_seconds')


@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ('operator', 'task', 'reason', 'points', 'created_at')
    search_fields = ('operator__full_name', 'task__title', 'reason')
    readonly_fields = ('created_at',)



@admin.register(SMS)
class SMSAdmin(admin.ModelAdmin):
    list_display = ('lead', 'operator', 'content', 'sent_at', 'delivered', 'error_message')
    search_fields = ('lead__full_name', 'operator__full_name', 'content')
    list_filter = ('delivered',)
    readonly_fields = ('sent_at',)



@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'operator', 'lead', 'start_date', 'end_date', 'amount_paid', 'created_at',
                    'updated_at')
    search_fields = ('course_name', 'operator__full_name', 'lead__full_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'created_at')  # admin panelida ko‘rinadigan ustunlar
    search_fields = ('title',)  # qidiruv maydoni
    list_filter = ('created_at',)  # filtrlash maydoni
    ordering = ('created_at',)



@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'operator', 'course', 'price_paid', 'created_at')
    ordering = ('-created_at',)  # yangi -> eski
    list_filter = ('operator', 'course', 'created_at')
    search_fields = ('student_name', 'operator__user__first_name', 'operator__user__last_name')


@admin.action(description="Run lead commission calculation")
def run_commission(modeladmin, request, queryset):
    from apps.tasks import process_lead_commission
    process_lead_commission()
    modeladmin.message_user(request, "Komissiya hisoblandi")