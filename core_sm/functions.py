from core_sm.models import Cost
from django.db.models import Avg, Max, Sum, Min
import calendar
import datetime


def month_day_calculations(day_numbers, year, month, day_sum, day_min, day_max, day_avg):
    for day in day_numbers:
        val_1 = Cost.objects.filter(publish__year=year, publish__month=month, publish__day=day).aggregate(Sum('value'))[
            'value__sum']
        val_2 = Cost.objects.filter(publish__year=year, publish__month=month, publish__day=day).aggregate(Min('value'))[
            'value__min']
        val_3 = Cost.objects.filter(publish__year=year, publish__month=month, publish__day=day).aggregate(Max('value'))[
            'value__max']
        val_4 = Cost.objects.filter(publish__year=year, publish__month=month, publish__day=day).aggregate(Avg('value'))[
            'value__avg']
        if val_1 and val_2 and val_3 and val_4 is not None:
            day_sum.append(val_1)
            day_min.append(val_2)
            day_max.append(val_3)
            day_avg.append("%.2f" % val_4)
        else:
            day_sum.append(0)
            day_min.append(0)
            day_max.append(0)
            day_avg.append(0)
    return day_sum, day_min, day_max, day_avg


def month_category_calculation(year, month, categories, categories_data):
    for item in categories:
        val = Cost.objects.filter(publish__year=year, publish__month=month, category=item).aggregate(Sum('value')
                                                                                                     )['value__sum']
        if val is not None:
            categories_data.append(val)
        else:
            categories_data.append(0)

def day_day_calculation(day_data, title, value, category, id):
        for item in day_data.values('title'):
            title.append(item['title'])
        for item in day_data.values('value'):
            value.append(float(item['value']))
        for item in day_data.values('category'):
            category.append(item['category'])
        for item in day_data.values('id'):
            id.append(item['id'])
        return title, value, category, id


def day_category_calculation(year, month, day, categories, categories_data):
    for data in categories:
        val = Cost.objects.filter(publish__year=year, publish__month=month, publish__day=day, category=data).aggregate(Sum('value'))['value__sum']
        if val is not None:
            categories_data.append(val)
        else:
            categories_data.append(0)
    return categories_data


def year_month_calculation(Months):
    for item in range(13)[1:]:
        Months.append(calendar.month_name[item])
    return Months


def year_data_calculation(Months_data, year):
    for item in range(13)[1:]:
        val = Cost.objects.filter(publish__year=year, publish__month=item).aggregate(Sum('value'))['value__sum']
        if val is not None:
            Months_data.append(float(val))
        else:
            Months_data.append(0)
    return Months_data


def year_categories_calculation(year, categories, categories_data):
    for data in categories:
        val = Cost.objects.filter(publish__year=year, category=data).aggregate(Sum('value'))['value__sum']
        if val is not None:
            categories_data.append(val)
        else:
            categories_data.append(0)
    return categories_data