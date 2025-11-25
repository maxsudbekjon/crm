from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.models import Branch, Operator, Lead, Task, Penalty, SMS, Contract, Notification, Call, Course, Enrollment
from .tasks import process_lead_commission

from django.contrib import admin
from apps.models import Branch, Operator, Lead, Task, Penalty, SMS, Contract


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created_at', 'updated_at')
    search_fields = ('name', 'location')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)


from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Operator, Lead, Course


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'status', 'total_lead_amount','commission_rate', 'gender', 'salary', 'penalty', 'branch', 'photo_tag', 'created_at'
    )

    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('status', 'gender', 'branch', 'course')  # kurs bo‘yicha filter qo‘shildi
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
    list_display = ('full_name', 'phone', 'course', 'operator', 'status', 'source', 'demo_date', 'last_contact_date', 'amount')
    list_filter = ('status', 'course', 'operator', 'source')
    search_fields = ('full_name', 'phone', 'operator__user__username')
    ordering = ('-demo_date',)
    readonly_fields = ('created_at', 'updated_at')
    fields = ('full_name', 'phone', 'course', 'operator', 'amount', 'status', 'source', 'demo_date', 'last_contact_date')



@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'operator', 'lead', 'is_completed', 'deadline', 'penalty_points', 'created_at',
                    'updated_at')
    list_filter = ('is_completed', 'deadline')
    search_fields = ('title', 'operator__full_name', 'lead__full_name')
    readonly_fields = ('created_at', 'updated_at')



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
    search_fields = ('course_name', 'lead__user__first_name', 'lead__user__last_name')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Notification)

@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('call_time', 'duration_seconds', 'result')
    list_filter = ('call_time', 'duration_seconds', 'result')
    search_fields = ('call_time', 'duration_seconds', 'result')
    readonly_fields = ('call_time', 'duration_seconds')



@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'created_at')  # admin panelida ko‘rinadigan ustunlar
    search_fields = ('title',)  # qidiruv maydoni
    list_filter = ('created_at',)  # filtrlash maydoni
    ordering = ('created_at',)

from django.contrib import admin
from .models import Enrollment

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

