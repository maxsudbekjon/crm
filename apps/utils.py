from datetime import date

def first_day_of_month(dt: date):
    return date(dt.year, dt.month, 1)


def get_or_create_operator_salary(operator, dt):
    """Oyning birinchi kuni bo‘yicha maosh yozuvi"""
    from apps.models import OperatorMonthlySalary

    month = first_day_of_month(dt)

    salary, created = OperatorMonthlySalary.objects.get_or_create(
        operator=operator,
        month=month,
    )
    return salary
