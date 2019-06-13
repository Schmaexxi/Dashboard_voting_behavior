from django import forms
from datetime import datetime
from dateutil.relativedelta import relativedelta


class DateForm(forms.Form):
    date_config = '%d-%m-%Y'
    now = datetime.now()
    start_date = forms.DateField(initial=(now + relativedelta(months=-6)).strftime(date_config), required=True,
                                 input_formats=[date_config], widget=forms.TextInput(attrs={'id': 'start_date'}))
    end_date = forms.DateField(initial=now.strftime(date_config), required=True, input_formats=[date_config],
                               widget=forms.TextInput(attrs={'id': 'end_date'}))
