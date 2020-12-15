from aldryn_client import forms

class Form(forms.BaseForm):

    summary_richtext = forms.CheckboxField(
        "Use rich text for Summary",
        required=False,
        initial=False)

    enable_price = forms.CheckboxField(
        "Enable Price",
        required=False,
        initial=False)

    enable_cpd = forms.CheckboxField(
        "Enable CPD points",
        required=False,
        initial=False)

    translate_is_published = forms.CheckboxField(
        'Translate Is published and Is featured fields', required=False, initial=False
    )

    def to_settings(self, data, settings):

        if data['summary_richtext']:
            settings['EVENTS_SUMMARY_RICHTEXT'] = int(data['summary_richtext'])
        if data['summary_richtext']:
            settings['EVENTS_ENABLE_PRICE'] = int(data['enable_price'])
        if data['summary_richtext']:
            settings['EVENTS_EVENTS_ENABLE_CPD'] = int(data['enable_cpd'])
        if data['translate_is_published']:
            settings['EVENTS_TRANSLATE_IS_PUBLISHED'] = int(data['translate_is_published'])
        settings['INSTALLED_APPS'].append('django_filters')
        settings['INSTALLED_APPS'].append('crispy_forms')
        return settings
