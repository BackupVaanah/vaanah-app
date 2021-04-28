from oscar.apps.partner.models import *  # noqa isort:skip
from oscar.apps.partner.abstract_models import AbstractPartner

class Partner(AbstractPartner):
    ispublic = models.BooleanField(default=True)