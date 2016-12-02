from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
import datetime


class Budget(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True)
    value = models.DecimalField(decimal_places=2, max_digits=10)
    year = models.IntegerField(default=datetime.datetime.now().year)
    month = models.IntegerField(default=datetime.datetime.now().month)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-year',)

    def __str__(self):
        return self.title


class Cost(models.Model):
    STATUS_CHOICES = [
        ['Domowe', 'Domowe'],
        ['Jedzenie', 'Jedzenie'],
        ['Kosmetyki i Chemia', 'Kosmetyki i Chemia'],
        ['Rozrywka', 'Rozrywka'],
        ['Okazyjne', 'Okazyjne'],
        ['Inne', 'Inne']
    ]
    budget = models.ForeignKey(Budget, related_name='cost')
    title = models.CharField(max_length=200, db_index=True)
    publish = models.DateField(default=timezone.now)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        ordering = ('-publish',)

    def get_absolute_url(self):
        return reverse('core_sm:stats_detail', args=[self.publish.year,
                                            self.publish.strftime('%y'),
                                            self.publish.strftime('%m'),
                                            self.publish.strftime('%d')])

    def __str__(self):
        return self.title