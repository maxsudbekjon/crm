from django.contrib import admin
from apps.models import (
    Branch, Call, Contract, Course, Lead, Operator,
    Payment, OperatorMonthlySalary, SMS, Task, Notification, Penalty
)

# ===========================
# INLINE CONFIGURATIONS
# ===========================

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ("amount", "created_at", "commission_added")


class CallInline(admin.TabularInline):
    model = Call
    extra = 0
    readonly_fields = ("call_time",)


class SMSInline(admin.TabularInline):
    model = SMS
    extra = 0
    readonly_fields = ("sent_at", "delivered")


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    readonly_fields = ("deadline", "is_completed")





@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "location", "created_at")
    search_fields = ("name", "location")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "created_at")
    search_fields = ("title",)
    list_filter = ("created_at",)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "id", "full_name", "phone", "status", "operator", "course",
        "demo_date", "last_contact_date", "created_at", 'commission_added'
    )
    search_fields = ("full_name", "phone")
    list_filter = ("status", "operator", "course", "created_at")
    inlines = [PaymentInline, CallInline, SMSInline, TaskInline]


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "status", "gender", "branch",
        "salary", "commission_rate", "penalty", "created_at"
    )
    search_fields = ("user__username",)
    list_filter = ("status", "gender", "branch")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "amount", "commission_added", "created_at")
    list_filter = ("commission_added", "created_at")
    search_fields = ("lead__full_name",)
    readonly_fields = ("created_at", "commission_added")




@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ("id", "operator", "task", "reason", "points", "created_at")
    list_filter = ("operator", "task", "created_at")
    search_fields = ("operator__full_name", "reason")
    readonly_fields = ("created_at",)

    ordering = ("-created_at",)


@admin.register(OperatorMonthlySalary)
class OperatorMonthlySalaryAdmin(admin.ModelAdmin):
    list_display = ("id", "operator", "month", "commission", "updated_at")
    search_fields = ("operator__user__username",)
    list_filter = ("month", "operator")


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = (
        "id", "operator", "lead", "result",
        "call_time", "duration_seconds"
    )
    search_fields = ("lead__full_name", "operator__user__username")
    list_filter = ("result", "operator", "call_time")


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "course_name", "amount_paid", "start_date", "end_date")
    search_fields = ("lead__full_name", "course_name")
    list_filter = ("start_date", "end_date")


@admin.register(SMS)
class SMSAdmin(admin.ModelAdmin):
    list_display = (
        "id", "lead", "operator", "sent_at",
        "delivered", "provider_sms_sid"
    )
    search_fields = ("lead__phone", "operator__user__username")
    list_filter = ("delivered", "sent_at")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "operator", "lead",
        "deadline", "is_completed", "penalty_given"
    )
    search_fields = ("title", "operator__user__username")
    list_filter = ("is_completed", "deadline")
    readonly_fields = ("completed_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "task", "is_read", "created_at")
    search_fields = ("user__username",)
    list_filter = ("is_read",)
