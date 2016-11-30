from django.shortcuts import render, HttpResponseRedirect
from .models import Cost, Budget
from django.db.models import Avg, Max, Min, Sum
from .forms import data_generate_form, data_add_form, multiadd_generate_form, comp_form, StatusFormEdit, BudgetForm
from django.core.urlresolvers import reverse
import datetime
from bokeh.embed import components
from django.utils.safestring import mark_safe
from bokeh.resources import CDN
from bokeh.charts import Bar
import calendar
from django.forms import modelformset_factory
from core_sm.functions import month_day_calculations, month_category_calculation, \
    day_day_calculation, day_category_calculation, year_data_calculation, year_month_calculation, \
    year_categories_calculation, comp_categories_calculation


def budget_setup(request):
    add = False

    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            add = True
            form.save()
    else:
        form = BudgetForm()

    summary = Budget.budget_year
    return render(request, 'core_sm/costs/budget.html', {'add': add,
                                                         'form': form,
                                                         'summary': summary})


def edit_status(request):
    delete = False
    add = False
    data = Cost.STATUS_CHOICES

    if request.method == 'POST' and 'add' in request.POST:
        form_add = StatusFormEdit(request.POST)
        if form_add.is_valid():
            add = True
            cd = form_add.cleaned_data
            Cost.STATUS_CHOICES.append([cd['status'], cd['status']])
            Cost.STATUS_CHOICES.sort()
    else:
        form_add = StatusFormEdit()

    if request.method == 'POST' and 'delete' in request.POST:
        form_delete = StatusFormEdit(request.POST)
        if form_delete.is_valid():
            delete = True
            cd = form_delete.cleaned_data
            Cost.STATUS_CHOICES.remove(cd['status'])
            Cost.STATUS_CHOICES.sort()
    else:
        form_delete = StatusFormEdit()

    return render(request, 'core_sm/costs/status_edit.html', {'data': data,
                                                              'add': add,
                                                              'form_add': form_add,
                                                              'form_delete': form_delete,
                                                              'delete': delete})


def day_data_multiadd(request, no_of_lines=0):
    no_of_lines = int(no_of_lines)
    CostFormSet = modelformset_factory(Cost, form=data_add_form, extra=no_of_lines)

    if request.method == 'POST' and 'form' in request.POST:
        formset = CostFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
    else:
        formset = CostFormSet(queryset=Cost.objects.none())

    if request.method == 'POST' and 'no_line' in request.POST:
        generate_form = multiadd_generate_form(request.POST)
        if generate_form.is_valid():
            cd = generate_form.cleaned_data
            return HttpResponseRedirect(reverse('core_sm:day_data_multiadd', args=(str(cd['formy']))))
    else:
        generate_form = multiadd_generate_form()

    return render(request, 'core_sm/costs/multi_add.html', {'formset': formset,
                                                            'no_of_lines': no_of_lines,
                                                            'generate_form': generate_form})


def day_data_delete(request, id):
    Message = "Rekord '{}' został usunięty z bazy danych".format(Cost.objects.filter(id=id).values('title')[0]['title'])
    Cost.objects.filter(id=id).delete()
    return render(request, 'core_sm/costs/day_delete.html', {'Message': Message})


def costs_stats(request):
    if request.method == "GET":
        form = data_generate_form()
    else:
        form = data_generate_form(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            return HttpResponseRedirect(reverse('core_sm:month_stats_detail', args=(cd['year'], cd['month'])))
    return render(request, 'core_sm/costs/stats.html', {'form': form})


def current_detail(request):
    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day
    return render(request, 'core_sm/costs/start.html', {'year': year,
                                                        'month': month,
                                                        'day': day})


def stats_comp(request, date_x=datetime.date.today(), date_y=datetime.date.today()):
    start_date = date_x
    end_date = date_y
    data = Cost.objects.filter(publish__range=(start_date, end_date))
    categories = []
    for item in Cost.STATUS_CHOICES:
        categories.append(item[0])
    categories_data = []
    comp_categories_calculation(categories, categories_data, start_date, end_date)
    vis_data = {
        'money': [float(x) for x in categories_data],
        'labels': categories
    }
    p = Bar(vis_data, values='money', label='labels')
    script, div = components(p, CDN)
    categories_res = zip(categories, categories_data)
    data_sum = Cost.objects.filter(publish__range=(start_date, end_date)).aggregate(Sum('value'))['value__sum']
    data_avg = Cost.objects.filter(publish__range=(start_date, end_date)).aggregate(Avg('value'))['value__avg']
    data_min = Cost.objects.filter(publish__range=(start_date, end_date)).aggregate(Min('value'))['value__min']
    data_max = Cost.objects.filter(publish__range=(start_date, end_date)).aggregate(Max('value'))['value__max']

    if request.method == 'POST':
        form = comp_form(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            return HttpResponseRedirect(reverse('core_sm:stats_comp', args=(cd['date_x'], cd['date_y'])))
    else:
        form = comp_form()
    return render(request, 'core_sm/costs/stats_comp.html', {'data': data,
                                                             'data_sum': data_sum,
                                                             'data_avg': data_avg,
                                                             'data_min': data_min,
                                                             'data_max': data_max,
                                                             'script': mark_safe(script),
                                                             'div': mark_safe(div),
                                                             'categories_res': categories_res,
                                                             'form': form,
                                                             'date_x': date_x,
                                                             'date_y': date_y})


def year_stats_detail(request, year):
    Months = []
    Months_data = []
    Months_url = [str(x).zfill(2) for x in range(13)[1:]]
    year_month_calculation(Months)
    year_data_calculation(Months_data, year)
    data = {
        'Miesiące': Months,
        'ZŁ': Months_data
    }
    p = Bar(data, values='ZŁ', label='Miesiące')
    script, div = components(p, CDN)
    all_data = zip(Months, Months_data, Months_url)
    year_sum = Cost.objects.filter(publish__year=year).aggregate(Sum('value'))['value__sum']
    categories = []
    for item in Cost.STATUS_CHOICES:
        categories.append(item[0])
    categories_data = []
    year_categories_calculation(year, categories, categories_data)
    data1 = {
        'money': [float(x) for x in categories_data],
        'labels': categories
    }
    p1 = Bar(data1, values='money', label='labels')
    script1, div1 = components(p1, CDN)
    categories_res = zip(categories, categories_data)
    return render(request, 'core_sm/costs/year_stats_detail.html', {'year': year,
                                                                    'Months': Months,
                                                                    'Months_data': Months_data,
                                                                    'script': mark_safe(script),
                                                                    'div': mark_safe(div),
                                                                    'all_data': all_data,
                                                                    'year_sum': year_sum,
                                                                    'script1': mark_safe(script1),
                                                                    'div1': mark_safe(div1),
                                                                    'categories_res': categories_res})


def month_stats_detail(request, year, month):
    mr = calendar.monthrange(int(year), int(month))
    day_numbers = [str(x).zfill(2) for x in range(mr[1]+1)][1:]
    day_sum = []
    day_min = []
    day_max = []
    day_avg = []
    month_day_calculations(day_numbers, year, month, day_sum, day_min, day_max, day_avg)
    day_data = zip(day_numbers, day_sum, day_max, day_min, day_avg)
    data = {
        'Dni': day_numbers,
        'ZŁ': [float(x) for x in day_sum]
    }
    p = Bar(data, plot_width=1250, values='ZŁ', legend=False)
    script, div = components(p, CDN)
    max_month_value = (max(day_max))
    max_month_day = day_numbers[day_max.index(max(day_max))]
    min_month_value = (min(day_min))
    min_month_day = day_numbers[day_min.index(min(day_min))]
    categories = []
    for item in Cost.STATUS_CHOICES:
        categories.append(item[0])
    categories_data = []
    month_category_calculation(year, month, categories, categories_data)
    data1 = {
        'money': [float(x) for x in categories_data],
        'labels': categories
    }
    p1 = Bar(data1, values='money', label='labels')
    script1, div1 = components(p1, CDN)
    categories_res = zip(categories, categories_data)
    sum_cost = Cost.objects.filter(publish__year=year, publish__month=month).aggregate(Sum('value'))
    min_cost = Cost.objects.filter(publish__year=year, publish__month=month).aggregate(Min('value'))
    max_cost = Cost.objects.filter(publish__year=year, publish__month=month).aggregate(Max('value'))
    avg_cost = Cost.objects.filter(publish__year=year, publish__month=month).aggregate(Avg('value'))['value__avg']
    return render(request, 'core_sm/costs/month_stats_detail.html', {'year': year,
                                                                     'month': month,
                                                                     'sum_cost': sum_cost['value__sum'],
                                                                     'min_cost': min_cost['value__min'],
                                                                     'max_cost': max_cost['value__max'],
                                                                     'avg_cost': avg_cost,
                                                                     'day_numbers': day_numbers,
                                                                     'day_data': day_data,
                                                                     'max_month_value': max_month_value,
                                                                     'max_month_day': max_month_day,
                                                                     'min_month_value': min_month_value,
                                                                     'min_month_day': min_month_day,
                                                                     'script': mark_safe(script),
                                                                     'div': mark_safe(div),
                                                                     'script1': mark_safe(script1),
                                                                     'div1': mark_safe(div1),
                                                                     'categories_res': categories_res,
                                                                     'day_sum': day_avg})


def day_stats_detail(request, year, month, day):
    day_data = Cost.objects.filter(publish__year=year, publish__month=month, publish__day=day)
    title = []
    value = []
    category = []
    id = []
    day_day_calculation(day_data, title, value, category, id)
    all_data = zip(title, value, category, id)
    try:
        day_max = [title[value.index(max(value))], max(value), category[value.index(max(value))]]
    except(ValueError, TypeError):
        day_max = 0
    try:
        day_min = [title[value.index(min(value))], min(value), category[value.index(min(value))]]
    except(ValueError, TypeError):
        day_min = 0
    day_sum = day_data.aggregate(Sum('value'))
    day_avg = day_data.aggregate(Avg('value'))['value__avg']
    categories = []
    for item in Cost.STATUS_CHOICES:
        categories.append(item[0])
    categories_data = []
    day_category_calculation(year, month, day, categories, categories_data)
    data = {
        'money': [float(x) for x in categories_data],
        'labels': categories
    }
    p = Bar(data, values='money', label='labels')
    script, div = components(p, CDN)
    return render(request, 'core_sm/costs/day_stats_detail.html',
                  {'year': year,
                   'month': month,
                   'day': day,
                   'day_data': day_data,
                   'all_data': all_data,
                   'day_sum': day_sum['value__sum'],
                   'day_avg': day_avg,
                   'script': mark_safe(script),
                   'div': mark_safe(div),
                   'day_max': day_max,
                   'day_min': day_min})