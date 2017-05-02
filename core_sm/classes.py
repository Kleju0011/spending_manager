from django.db.models import Avg, Sum
from core_sm.models import Cost, Budget, Category
from bokeh.embed import components
from bokeh.charts import Donut, Line
from bokeh.resources import CDN
from django.contrib.auth.models import User
import calendar


class DayView(object):

    def __init__(self, year, month, day, request):
        """Init data"""
        self.year = year
        self.month = month
        self.day = day
        self.request = request
        self.day_data_conf = {}
        self.day_data = Cost.objects.filter(publish__year=year, publish__month=month, publish__day=day, user_id=request.user.id)
        '''DATA CONTAINERS'''
        self.title, self.value, self.category, self.budget, self.cost_id = [], [], [], [], []
        self.day_sum = self.day_data.aggregate(Sum('value'))['value__sum']
        self.day_avg = self.day_data.aggregate(Avg('value'))['value__avg']
        self.day_max, self.day_min = 0, 0
        self.categories_title, self.categories_id, self.categories_values = [], [], []
        self.budget_titles, self.budget_values, self.budget_id = [], [], []
        self.category_percent = []
        self.another, self.back = None, None
        '''ZIP Data'''
        self.category_zip = zip(self.categories_title, self.categories_values, self.categories_id, self.category_percent)
        self.budget_zip = zip(self.budget_titles, self.budget_values, self.budget_id)

    def day_calculation(self):
        for item in self.day_data.values('title', 'value', 'category_id', 'id', 'budget_id'):
            self.title.append(item['title'])
            self.value.append(float(item['value']))
            self.category.append(Category.objects.get(id=item['category_id']).title)
            self.cost_id.append(item['id'])
            self.budget.append(Budget.objects.get(id=item['budget_id']).title)

        for item in Category.objects.filter(user_id=self.request.user.id).values('title', 'id'):
            val = Cost.objects.filter(publish__year=self.year, publish__month=self.month, publish__day=self.day, user=self.request.user,
                                      category_id=item['id']).aggregate(Sum('value'))['value__sum']
            if val is not None:
                self.categories_values.append(val)
                self.categories_title.append(item['title'])
                self.categories_id.append(item['id'])
            else:
                pass

        for item in Budget.objects.filter(user_id=self.request.user.id).values('title', 'id'):
            val = Cost.objects.filter(budget_id=item['id'], publish__year=self.year, publish__month=self.month, publish__day=self.day,
                                      user_id=self.request.user.id).aggregate(Sum('value'))['value__sum']
            if val is not None:
                self.budget_titles.append(item['title'])
                self.budget_values.append(val)
                self.budget_id.append(item['id'])
            else:
                pass

    def day_max_min(self):
        try:
            self.day_max = [self.title[self.value.index(max(self.value))], max(self.value), self.category[self.value.index(max(self.value))],
                       self.budget[self.value.index(max(self.value))]]
        except(ValueError, TypeError):
            self.day_max = 0

        try:
            self.day_min = [self.title[self.value.index(min(self.value))], min(self.value), self.category[self.value.index(min(self.value))],
                       self.budget[self.value.index(min(self.value))]]
        except(ValueError, TypeError):
            self.day_min = 0

    def day_figure(self):
        if not self.categories_title:
            self.script = "<h2>Aby wykres się pojawił, musisz dodać wydatek oraz kategorie</h2>"
            self.div = "<h1>Brak wydatków!</h1>"
            return self.script, self.div
        else:
            for item in self.categories_values:
                val = 100 * float(item / (sum(self.categories_values)))
                self.category_percent.append(int(val))

            data = {
                'money': self.category_percent,
                'label': self.categories_title
            }

            p = Donut(data, values='money', label='label', plot_width=390, plot_height=600, responsive=True)
            p.logo = None
            p.toolbar_location = None
            self.script, self.div = components(p, CDN)

    def back_next_day(self):
        mr = calendar.monthrange(int(self.year), int(self.month))
        next_year = int(self.year)
        next_month = int(self.month)
        next_day = int(self.day) + 1
        if next_day > mr[1]:
            next_day = str(1).zfill(2)
            next_month = str(next_month + 1).zfill(2)
        if int(next_month) > 12:
            next_month = str(1).zfill(2)
            next_year += 1
        self.another = "/costs/{}/{}/{}/".format(next_year, next_month, next_day)

        back_year = int(self.year)
        back_month = int(self.month)
        back_day = int(self.day) - 1
        if back_day < 1:
            back_day = calendar.monthrange(int(self.year), int(self.month) - 1)[1]
            back_month = "%.2f" % (back_month - 1)
        self.back = "/costs/{}/{}/{}/".format(back_year, back_month, back_day)


class DayViewCategory(DayView):

    def __init__(self, year, month, day, category_id, request):
        super().__init__(year, month, day, request)
        self.category_id = category_id
        self.category_title = Category.objects.get(id=category_id).title
        self.day_data = Cost.objects.filter(publish__year=year, publish__month=month, publish__day=day,
                                            user=request.user.id, category_id=category_id)
        self.day_sum = self.day_data.aggregate(Sum('value'))['value__sum']
        self.day_avg = self.day_data.aggregate(Avg('value'))['value__avg']
        self.budget_title, self.budget_titles, self.budget_values, self.budget_id = [], [], [], []
        self.category_budget_zip = zip(self.day_data, self.budget_title)
        self.budget_zip = zip(self.budget_titles, self.budget_values, self.budget_id)

    def budget_title_calculation(self):
        for item in self.day_data.values('budget_id'):
            self.budget_title.append(Budget.objects.get(id=item['budget_id']).title)

    def day_calculation(self):
        for item in Budget.objects.values('title', 'id'):
            val = Cost.objects.filter(budget_id=item['id'], publish__year=self.year, publish__month=self.month,
                                      publish__day=self.day, category_id=self.category_id,
                                      user_id=self.request.user.id).aggregate(Sum('value'))['value__sum']
            if val is not None:
                self.budget_titles.append(item['title'])
                self.budget_values.append(val)
                self.budget_id.append(item['id'])
            else:
                pass


class DayViewBudget(DayView):
    def __init__(self, year, month, day, budget_id, request):
        super().__init__(year, month, day, request)
        self.budget_id = budget_id
        self.day_data = Cost.objects.filter(publish__year=year, publish__month=month, publish__day=day,
                                            user_id=request.user.id, budget_id=budget_id)
        self.budget_title = Budget.objects.get(id=budget_id).title
        self.budget_owner = User.objects.get(id=Budget.objects.get(id=budget_id).user_id).username
        self.day_data = Cost.objects.filter(publish__year=year, publish__month=month, publish__day=day,
                                            user=request.user.id, budget_id=budget_id)
        self.day_sum = self.day_data.aggregate(Sum('value'))['value__sum']
        self.day_avg = self.day_data.aggregate(Avg('value'))['value__avg']
        self.category_title = []
        self.categories_title = []
        self.categories_id = []
        self.categories_values = []
        self.category_percent = []
        self.script = None
        self.div = None
        self.day_data_zip = zip(self.day_data, self.category_title)
        self.category_zip = zip(self.categories_title, self.categories_values, self.categories_id, self.category_percent)
        try:
            self.total_budget = Budget.objects.get(id=budget_id).value - Cost.objects.filter(budget_id=budget_id, user=request.user).aggregate(Sum('value'))['value__sum']
        except(TypeError):
            self.total_budget = 0

    def category_title_calculation(self):
        for item in self.day_data.values('category_id'):
            self.category_title.append(Category.objects.get(id=item['category_id']).title)

    def day_calculation(self):
        for item in Category.objects.filter(user_id=self.request.user.id).values('title', 'id'):
            val = Cost.objects.filter(publish__year=self.year, publish__month=self.month, publish__day=self.day,
                                      user_id=self.request.user.id, budget_id=self.budget_id,
                                      category_id=item['id']).aggregate(Sum('value'))['value__sum']
            if val is not None:
                self.categories_title.append(item['title'])
                self.categories_values.append(val)
                self.categories_id.append(item['id'])

    def day_figure(self):
        if not self.categories_title:
            self.script = "<h2>Aby wykres się pojawił, musisz dodać wydatek oraz kategorie</h2>"
            self.div = "<h1>Brak wydatków!</h1>"
        else:
            for item in self.categories_values:
                val = 100 * float(item / (sum(self.categories_values)))
                self.category_percent.append(int(val))

            data = {
                'money': self.category_percent,
                'label': self.categories_title
            }

            p = Donut(data, values='money', label='label', plot_width=390, plot_height=600, responsive=True)
            p.logo = None
            p.toolbar_location = None
            self.script, self.div = components(p, CDN)


class MonthView(object):

    def __init__(self, year, month, request):
        self.year = year
        self.month = month
        self.request = request
        self.monthrange = calendar.monthrange(int(self.year), int(self.month))
        self.days_in_month = [str(x).zfill(2) for x in range(self.monthrange[1]+1)][1:]
        self.month_sum = Cost.objects.filter(publish__year=year, publish__month=month,
                                             user_id=request.user.id).aggregate(Sum('value'))['value__sum']
        self.month_avg = Cost.objects.filter(publish__year=self.year, publish__month=self.month,
                                             user_id=self.request.user.id).aggregate(Avg('value'))['value__avg']
        self.days_sums, self.days_avgs = [], []
        self.categories_titles, self.categories_id, self.categories_values, self.category_percent = [], [], [], []
        self.budget_titles, self.budget_id, self.budget_values, self.budget_percent = [], [], [], []
        self.script, self.div, self.script_2, self.div_2 = None, None, None, None
        self.day_data = zip(self.days_in_month, self.days_sums, self.days_avgs)
        self.category_zip = zip(self.categories_titles, self.categories_id, self.categories_values, self.category_percent)
        self.budget_zip = zip(self.budget_titles, self.budget_id, self.budget_values, self.budget_percent)

    def month_calculation(self):
        for item in self.days_in_month:
            val_sum = Cost.objects.filter(publish__year=self.year, publish__month=self.month,
                                          publish__day=item, user_id=self.request.user.id).aggregate(Sum('value'))['value__sum']
            val_avg = Cost.objects.filter(publish__year=self.year, publish__month=self.month,
                                          publish__day=item, user_id=self.request.user.id).aggregate(Avg('value'))['value__avg']
            if val_sum and val_avg is not None:
                self.days_sums.append(val_sum)
                self.days_avgs.append("%.2f" % val_avg)
            else:
                self.days_sums.append(0)
                self.days_avgs.append(0)

    def month_category_calculation(self):
        for item in Category.objects.values('title', 'id'):
            val = Cost.objects.filter(publish__year=self.year, publish__month=self.month, user_id=self.request.user.id,
                                      category_id=item['id']).aggregate(Sum('value'))['value__sum']
            if val is not None:
                self.categories_titles.append(item['title'])
                self.categories_id.append(item['id'])
                self.categories_values.append(val)
            else:
                pass

        for item in self.categories_values:
            val = 100 * float(item / (sum(self.categories_values)))
            self.category_percent.append(int(val))

    def month_budget_calculation(self):
        for item in Budget.objects.values('title', 'id'):
            val = Cost.objects.filter(publish__year=self.year, publish__month=self.month, user_id=self.request.user.id,
                                      budget_id=item['id']).aggregate(Sum('value'))['value__sum']
            if val is not None:
                self.budget_titles.append(item['title'])
                self.budget_id.append(item['id'])
                self.budget_values.append(val)
            else:
                pass

        for item in self.budget_values:
            val = 100 * float(item / (sum(self.budget_values)))
            self.budget_percent.append(int(val))

    def month_figures_days(self):
        data = {
            'Dni': self.days_in_month,
            'Zł': [float(x) for x in self.days_sums]
        }
        p = Line(data, ylabel='Zł', xlabel='Dni', plot_width=390, plot_height=400, legend=None, responsive=True)
        p.logo = None
        p.toolbar_location = None
        self.script, self.div = components(p, CDN)

    def month_figures_category(self):
        if not self.categories_titles:
            self.script_2 = "<h2>Aby wykres się pojawił, musisz dodać wydatek oraz kategorie</h2>"
            self.div_2 = "<h1>Brak wydatków!</h1>"
        else:
            data = {
                'money': self.category_percent,
                'label': self.categories_titles
            }

            p = Donut(data, values='money', label='label', plot_width=390, plot_height=400, responsive=True)
            p.logo = None
            p.toolbar_location = None
            self.script_2, self.div_2 = components(p, CDN)


class MonthViewCategory(MonthView):

    def __init__(self, request, year, month, category_id):
        super().__init__(year, month, request)
        self.category_id = category_id
        self.category_title = Category.objects.get(id=category_id).title
        self.month_sum = Cost.objects.filter(publish__year=self.year, publish__month=self.month,
                                             category_id=self.category_id,
                                             user_id=self.request.user.id).aggregate(Sum('value'))['value__sum']
        self.month_avg = Cost.objects.filter(publish__year=self.year, publish__month=self.month,
                                             category_id=self.category_id,
                                             user_id=self.request.user.id).aggregate(Avg('value'))['value__avg']

    def month_calculation(self):
        for item in self.days_in_month:
            val_sum = Cost.objects.filter(publish__year=self.year, publish__month=self.month, category_id=self.category_id,
                                          publish__day=item, user_id=self.request.user.id).aggregate(Sum('value'))['value__sum']
            val_avg = Cost.objects.filter(publish__year=self.year, publish__month=self.month, category_id=self.category_id,
                                          publish__day=item, user_id=self.request.user.id).aggregate(Avg('value'))['value__avg']
            if val_sum and val_avg is not None:
                self.days_sums.append(val_sum)
                self.days_avgs.append("%.2f" % val_avg)
            else:
                self.days_sums.append(0)
                self.days_avgs.append(0)

    def month_budget_calculation(self):
        for item in Budget.objects.values('title', 'id'):
            val = Cost.objects.filter(publish__year=self.year, publish__month=self.month, user_id=self.request.user.id,
                                      category_id=self.category_id, budget_id=item['id']).aggregate(Sum('value'))['value__sum']
            if val is not None:
                self.budget_titles.append(item['title'])
                self.budget_id.append(item['id'])
                self.budget_values.append(val)
            else:
                pass
        for item in self.budget_values:
            val = 100 * float(item / (sum(self.budget_values)))
            self.budget_percent.append(int(val))


