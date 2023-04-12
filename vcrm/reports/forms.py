from django import forms
from django.utils import timezone
from django.utils.dates import MONTHS


YEAR_CHOICES = [
    (y, y) for y in range(timezone.now().year-4, timezone.now().year+1)
]


class HoursReportForm(forms.Form):
    month = forms.ChoiceField(label='Месяц',
                              choices=MONTHS.items(),
                              initial=timezone.now().month)
    year = forms.ChoiceField(label='Год',
                             choices=YEAR_CHOICES,
                             initial=timezone.now().year)
