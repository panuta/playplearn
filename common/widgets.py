from django import forms


class EmailWidget(forms.widgets.Input):
    input_type = 'email'