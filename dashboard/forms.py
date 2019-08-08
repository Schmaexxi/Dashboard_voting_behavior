from django import forms
import datetime
from dateutil.relativedelta import relativedelta


class DateForm(forms.Form):
    """
    form used in every view to handle aggregation after time
    :param date_config: date format as string
    :param now: today as datetime.date
    :param start_date: today six months ago as datetime.date
    :param end_date: today as datetime.date
    """
    date_config: str = '%d-%m-%Y'
    now: datetime.date = datetime.date.today()
    start_date: datetime.date = forms.DateField(initial=(now + relativedelta(months=-6)).strftime(date_config), required=True,
                                 input_formats=[date_config], widget=forms.TextInput(attrs={'id': 'start_date'}))
    end_date: datetime.date = forms.DateField(initial=now.strftime(date_config), required=True, input_formats=[date_config],
                               widget=forms.TextInput(attrs={'id': 'end_date'}))
