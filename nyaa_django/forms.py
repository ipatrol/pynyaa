from django import forms
from lxml.html.clean import Cleaner
from nyaa_django import models

def get_pairs():
    qs = models.SubCategory.objects.all()
    tb = list()
    for qv in qs:
        tb.append(('{}_{}'.format(qv.parent.id,qv.id),
                '{} - {}'.format(qv.parent.name, qv.name)))
    return tuple(tb)

cleaner = Cleaner(
    scripts = True,
    javascript = True,
    comments = False,
    style = True,
    inline_style = False,
    links = True,
    meta = True,
    page_structure = True,
    processing_instructions = True,
    embedded = True,
    frames = True,
    forms = True,
    annoying_tags = True,
    remove_unknown_tags = True,
    add_nofollow = True
    )

class UploadForm(forms.Form):
    torrent = forms.FileField(max_length=512 * 2**10) # 512KiB
    category = forms.ChoiceField(choices=get_pairs)
    website = forms.URLField(required=False)
    description = forms.CharField(widget=forms.Textarea)
    def clean_description(self):
        data = self.cleaned_data['description']
        return cleaner.clean_html(data)