from aldryn_client import forms

class Form(forms.BaseForm):

    hide_related_events = forms.CheckboxField(
        "Hide Specific Event Selector",
        required=False,
        initial=False)
    summary_richtext = forms.CheckboxField(
        "Use rich text for Summary",
        required=False,
        initial=False)

    def to_settings(self, data, settings):

        if data['hide_related_events']:
            settings['EVENTS_HIDE_RELATED_EVENTS'] = int(data['hide_related_events'])
        if data['summary_richtext']:
            settings['EVENTS_SUMMARY_RICHTEXT'] = int(data['summary_richtext'])

        return settings
