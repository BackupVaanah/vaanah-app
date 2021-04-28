from django.views import generic
from oscar.core.loading import get_class, get_model, get_classes
from oscar.views import sort_queryset
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from oscar.apps.catalogue.views import CatalogueView
from django.core.paginator import InvalidPage
from django.views.generic import DetailView, TemplateView

Product = get_model('catalogue', 'product')
Category = get_model('catalogue', 'category')
ProductAlert = get_model('customer', 'ProductAlert')
ProductAlertForm = get_class('customer.forms', 'ProductAlertForm')
get_product_search_handler_class = get_class(
    'catalogue.search_handlers', 'get_product_search_handler_class')

(ProductForm,
 ProductClassSelectForm,
 ProductSearchForm,
 ProductClassForm,
 CategoryForm,
 StockAlertSearchForm,
 AttributeOptionGroupForm,
 OptionForm) \
    = get_classes('dashboard.catalogue.forms',
                  ('ProductForm',
                   'ProductClassSelectForm',
                   'ProductSearchForm',
                   'ProductClassForm',
                   'CategoryForm',
                   'StockAlertSearchForm',
                   'AttributeOptionGroupForm',
                   'OptionForm'))
(StockRecordFormSet,
 ProductCategoryFormSet,
 ProductImageFormSet,
 ProductRecommendationFormSet,
 ProductAttributesFormSet,
 AttributeOptionFormSet) \
    = get_classes('dashboard.catalogue.formsets',
                  ('StockRecordFormSet',
                   'ProductCategoryFormSet',
                   'ProductImageFormSet',
                   'ProductRecommendationFormSet',
                   'ProductAttributesFormSet',
                   'AttributeOptionFormSet'))
ProductTable, CategoryTable, AttributeOptionGroupTable, OptionTable \
    = get_classes('dashboard.catalogue.tables',
                  ('ProductTable', 'CategoryTable',
                   'AttributeOptionGroupTable', 'OptionTable'))
(PopUpWindowCreateMixin,
 PopUpWindowUpdateMixin,
 PopUpWindowDeleteMixin) \
    = get_classes('dashboard.views',
                  ('PopUpWindowCreateMixin',
                   'PopUpWindowUpdateMixin',
                   'PopUpWindowDeleteMixin'))
PartnerProductFilterMixin = get_class('dashboard.catalogue.mixins', 'PartnerProductFilterMixin')
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
ProductImage = get_model('catalogue', 'ProductImage')
ProductCategory = get_model('catalogue', 'ProductCategory')
ProductClass = get_model('catalogue', 'ProductClass')
StockRecord = get_model('partner', 'StockRecord')
StockAlert = get_model('partner', 'StockAlert')
Partner = get_model('partner', 'Partner')
AttributeOptionGroup = get_model('catalogue', 'AttributeOptionGroup')
Option = get_model('catalogue', 'Option')
Product = get_model('catalogue', 'Product')

Partner = get_model('partner', 'Partner')
(
    PartnerSearchForm, PartnerCreateForm, PartnerAddressForm,
    NewUserForm, UserEmailForm, ExistingUserForm
) = get_classes(
    'dashboard.partners.forms',
    ['PartnerSearchForm', 'PartnerCreateForm', 'PartnerAddressForm',
     'NewUserForm', 'UserEmailForm', 'ExistingUserForm'])
Boutique = get_model('boutique', 'Boutique')

class BoutiqueListView(generic.ListView):
    model = Partner
    context_object_name = 'partners'
    template_name = 'boutique/boutique_list.html'
    form_class = PartnerSearchForm

    def get_queryset(self):
        qs = self.model._default_manager.all()
        qs = sort_queryset(qs, self.request, ['name'])

        self.description = ("All boutiques")


        # We track whether the queryset is filtered to determine whether we
        # show the search form 'reset' button.
        self.is_filtered = False
        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return qs

        data = self.form.cleaned_data

        if data['name']:
            qs = qs.filter(name__icontains=data['name'])
            self.description = _("Partners matching '%s'") % data['name']
            self.is_filtered = True
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['queryset_description'] = self.description
        ctx['form'] = self.form
        ctx['is_filtered'] = self.is_filtered

        activPartner = []
        partners = self.model._default_manager.all()
        # print(partners)

        # Only first user in partner user is verified because it's the main user (boutique owner)
        for partner in partners:
            if partner.users.all() and partner.users.first().is_active:
                activPartner.append(partner)
                # print(activPartner)
            # else:
            #     print("inac :" ,partner)
           

        ctx['activPartner'] = activPartner
        return ctx



class BoutiqueDetailView(generic.DetailView):
    context_object_name1 = "partners"
    context_object_name2 = "products"
    template_name = 'boutique/boutique_details.html'
    form_class = PartnerAddressForm
    success_url = reverse_lazy('boutique:boutique-list')
    def get_object(self, queryset=None):
        self.partner = get_object_or_404(Partner, pk=self.kwargs['pk'])
        address = self.partner.primary_address

        if address is None:
            address = self.partner.addresses.model(partner=self.partner)
        return address

    def get_initial(self):
        return {'name': self.partner.name}

    def get(self, request, *args, **kwargs):
        try:
            self.search_handler = self.get_search_handler(
                self.request.GET, request.get_full_path(), [])
        except InvalidPage:
            # Redirect to page one.
            messages.error(request, _('The given page number was invalid.'))
            return redirect('catalogue:index')
        return super().get(request, *args, **kwargs)

    def get_search_handler(self, *args, **kwargs):
        return get_product_search_handler_class()(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['partner'] = self.partner
        ctx['title'] = self.partner.name
        ctx['users'] = self.partner.users.all()
        ctx['products'] = ("All products")

        search_context = self.search_handler.get_search_context_data(
            self.context_object_name2)
       
        ctx.update(search_context)
        return ctx
