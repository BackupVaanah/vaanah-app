from django import forms
from django.utils.translation import gettext_lazy as _

from oscar.apps.partner.forms import PartnerCreateForm 
from oscar.core.compat import (existing_partner_fields, get_partner_model)
from django.conf import settings

from django.contrib.auth import get_user_model

class PartnerCreateForm(PartnerCreateForm):
    class Meta:
        model = Partner
        fields = ('is active',)
