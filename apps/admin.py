from django.contrib import admin
from apps.models import Branch, Operator, Lead, Task, Penalty, SMS, Contract, Notification, Call


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created_at', 'updated_at')
    search_fields = ('name', 'location')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'status', 'gender', 'phone_number', 'salary', 'penalty', 'branch', 'photo_tag',
                    'created_at')
    search_fields = ('full_name', 'phone_number')
    list_filter = ('status', 'gender', 'branch')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('full_name',)

    def photo_tag(self, obj):
        if obj.photo:
            return f'<img src="{obj.photo.url}" width="50" height="50" />'
        return "-"

    photo_tag.allow_tags = True
    photo_tag.short_description = 'Photo'


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'status', 'operator', 'demo_date', 'last_contact_date', 'created_at',
                    'updated_at')
    search_fields = ('full_name', 'phone')
    list_filter = ('status',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'operator', 'lead', 'is_completed', 'deadline', 'penalty_points', 'created_at',
                    'updated_at')
    list_filter = ('is_completed', 'deadline')
    search_fields = ('title', 'operator__full_name', 'lead__full_name')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Notification)
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