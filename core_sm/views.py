from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from .models import Cost, DateMonthYear
from django.db.models import Avg, Max, Min, Sum
from .forms import data_generate_form
from django.core.urlresolvers import reverse
from bokeh.plotting import figure
from bokeh.embed import components
from django.utils.safestring import mark_safe
from bokeh.resources import CDN
import calendar
import datetime
import pprint

def costs_list(request, datemonthyear_slug = None):
    datemonthyear = None
    datesmonthsyears = DateMonthYear.objects.all()
    costs = Cost.objects.all()
    if datemonthyear_slug:
        datemonthyear = get_object_or_404(DateMonthYear, slug=datemonthyear_slug)
        costs = costs.filter(datemonthyear=datemonthyear)
    return render(request, 'core_sm/costs/list.html', {'costs': costs,
                                                 'datemonthyear': datemonthyear,
                                                 'datesmonthsyears': datesmonthsyears},)

def costs_month_detail(request, id, slug):
    cost = get_object_or_404(Cost, id=id, slug=slug)
    return render(request, 'core_sm/costs/detail.html', {'cost': cost})
#{% url 'core_sm:stats_detail' %}
def costs_stats(request):
    if request.method == "GET":
        form = data_generate_form()
    else:
        form = data_generate_form(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            return HttpResponseRedirect(reverse('core_sm:stats_detail', args=(cd['year'], cd['month'])))
    return render(request, 'core_sm/costs/stats.html', {'form': form})

def stats_detail(request, year, month):
    mr = calendar.monthrange(int(year), int(month))
    x = [x for x in range(mr[1]+1)][1:]
    y = []
    for item in Cost.objects.values('publish'):
        for day in x:
            if item['publish'].date() == datetime.date(int(year), int(month), day):
                y.append(Cost.objects.filter(publish__year=year, publish__month=month, publish__day=day).aggregate(Sum('value'))['value__sum'])
                
            else:
                y.append(0)
    p = figure(title="simple line example", x_axis_label='x', y_axis_label='y')
    p.line(x, y, legend="Temp.", line_width=2)
    script, div = components(p, CDN)
    sum_cost = Cost.objects.filter(publish__year=year, publish__month=month).aggregate(Sum('value'))
    min_cost = Cost.objects.filter(publish__year=year, publish__month=month).aggregate(Min('value'))
    max_cost = Cost.objects.filter(publish__year=year, publish__month=month).aggregate(Max('value'))
    avg_cost = Cost.objects.filter(publish__year=year, publish__month=month).aggregate(Avg('value'))
    return render(request, 'core_sm/costs/stats_detail.html', {'year': year,
                                                               'month': month,
                                                               'sum_cost': sum_cost['value__sum'],
                                                               'min_cost': min_cost['value__min'],
                                                               'max_cost': max_cost['value__max'],
                                                               'avg_cost': avg_cost['value__avg'],
                                                               'script': mark_safe(script),
                                                               'div': mark_safe(div),
                                                               'y': y})