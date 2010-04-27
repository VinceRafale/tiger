import time
from datetime import datetime, date
from decimal import Decimal

from django.core.urlresolvers import reverse
from django.contrib.gis.db import models
from django.contrib.localflavor.us.models import *
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.utils.http import int_to_base36
from django.utils.safestring import mark_safe

from paypal.standard.ipn.signals import payment_was_successful

from tiger.content.handlers import pdf_caching_handler
from tiger.notify.handlers import item_social_handler, coupon_social_handler
from tiger.notify.tasks import SendFaxTask
from tiger.utils.fields import PickledObjectField
from tiger.utils.pdf import render_to_pdf


class Section(models.Model):
    """Acts as a container for menu items. Example: "Burritos".
    """
    name = models.CharField(max_length=50)
    site = models.ForeignKey('accounts.Site', editable=False)
    description = models.TextField()
    slug = models.SlugField(editable=False)
    ordering = models.PositiveIntegerField(editable=False, default=1)

    class Meta:
        verbose_name = 'menu section'
        ordering = ('ordering',)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if not self.id:
            self.ordering = 1
        super(Section, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('menu_section', kwargs={'section': self.slug})

    def has_specials(self):
        return any(item.special for item in self.item_set.all())


class ItemManager(models.Manager):
    use_for_related_fields = True

    def render_specials_to_string(self, site, template='core/specials_fax.html'):
        items = self.filter(special=True, site=site)
        return render_to_string(template, {'site': site, 'items': items})

    def active(self):
        return self.filter(archived=False)


class Item(models.Model):
    """Represents a single item on the menu in its most basic form.
    """
    name = models.CharField(max_length=100)
    section = models.ForeignKey(Section)
    site = models.ForeignKey('accounts.Site', editable=False)
    image = models.ForeignKey('content.ItemImage', blank=True, null=True)
    description = models.TextField(blank=True)
    special = models.BooleanField('is this menu item currently a special?', default=False)
    slug = models.SlugField(editable=False)
    ordering = models.PositiveIntegerField(editable=False, default=1)
    spicy = models.BooleanField(default=False)
    vegetarian = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    out_of_stock = models.BooleanField(default=False)
    price_list = PickledObjectField(null=True, editable=False)
    objects = ItemManager()

    class Meta:
        verbose_name = 'menu item'
        ordering = ('ordering',)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
            self.price_list = []
        super(Item, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('menu_item', 
            kwargs={'section': self.section.slug, 'item': self.slug})

    def get_short_url(self):
        return reverse('short_code', kwargs={'item_id': int_to_base36(self.id)})

    @property
    def available(self):
        return not (self.archived or self.out_of_stock)

    def update_price(self):
        if self.variant_set.count() == 1:
            self.price_list = ['$%.2f' % self.variant_set.all()[0].price]  
        else:
            self.price_list = [
                '%s: $%.2f' % (v.description, v.price)
                for v in self.variant_set.all()
            ]
        self.save()


class Variant(models.Model):
    """Represents "column-level" extra data about a menu item.  This means
    information like "Extra large" and the corresponding price.  This is what a
    customer will actually be selecting when ordering a menu item.  All menu
    items must have at least one.  
    """
    item = models.ForeignKey(Item)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ['price']

    def __unicode__(self):
        s = '%s ($<span>%s</span>)' % (self.description, self.price)
        return mark_safe(s)

    def save(self, *args, **kwargs):
        new = False
        if not self.id:
            new = True
        self.price = self.price.quantize(Decimal('0.01'))
        super(Variant, self).save(*args, **kwargs)
        if new:
            self.item.update_price()


class Upgrade(models.Model):
    """Provides additional cost data and/or order processing instructions. For
    example, "Subsitute seasoned frieds for $.50" or "Add extra cheese for
    $1.00." 
    """
    item = models.ForeignKey(Item)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    substitute = models.BooleanField('Check here for the display text \
        for this item to say "Substitute" instead of "Add"')

    class Meta:
        verbose_name = 'upgrade/substitution'
        verbose_name_plural = 'upgrades/substitutions'

    def __unicode__(self):
        s = '%s %s for $<span>%.02f</span> more' % (
            'Substitute' if self.substitute else 'Add', 
            self.name, self.price)
        return mark_safe(s)

    def save(self, *args, **kwargs):
        self.price = '%.2f' % self.price
        super(Variant, self).save(*args, **kwargs)


class SideDishGroup(models.Model):
    item = models.ForeignKey(Item)


class SideDish(models.Model):
    group = models.ForeignKey(SideDishGroup)
    name = models.CharField(max_length=100)
    price = models.DecimalField('Additional cost', max_digits=5, decimal_places=2, null=True)

    def __unicode__(self):
        if self.price:
            return mark_safe('%s (add $<span>%.02f</span>)' % (self.name, self.price))
        return self.name


class Order(models.Model):
    METHOD_TAKEOUT = 1
    METHOD_DINEIN = 2
    METHOD_DELIVERY = 3
    METHOD_CHOICES = (
        (METHOD_TAKEOUT, 'Takeout'),
        (METHOD_DINEIN, 'Dine in'),
        (METHOD_DELIVERY, 'Delivery'),
    )
    STATUS_INCOMPLETE = 1
    STATUS_SENT = 2
    STATUS_PAID = 3
    STATUS_FULFILLED = 4
    STATUS_CANCELLED = 5
    STATUS_CHOICES = (
        (STATUS_INCOMPLETE, 'Incomplete'),
        (STATUS_SENT, 'Sent'),
        (STATUS_PAID, 'Paid'),
        (STATUS_FULFILLED, 'Fulfilled'),
        (STATUS_CANCELLED, 'Cancelled'),
    )
    site = models.ForeignKey('accounts.Site', null=True, editable=False)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zip = models.CharField(max_length=10, blank=True, null=True)
    pickup = models.CharField('Time you will pick up your order', max_length=20)
    total = models.DecimalField(editable=False, max_digits=6, decimal_places=2)
    cart = models.TextField(editable=False)
    timestamp = models.DateTimeField(default=datetime.now, editable=False)
    method = models.IntegerField('This order is for', default=1, choices=METHOD_CHOICES)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_INCOMPLETE)

    @models.permalink
    def get_absolute_url(self):
        return 'order_detail', [self.id], {}

    def notify_restaurant(self, status):
        """Sends a message to the restaurant with the information about the order
        and flags the order as either sent or paid.
        """
        content = render_to_pdf('notify/order.html', {
            'order': self,
            'cart': self.cart,
            'order_no': self.id,
        })
        site = self.site
        SendFaxTask.delay(site, site.fax_number, content, IsFineRendering=True)
        self.status = status
        self.save()

class OrderSettings(models.Model):
    PAYMENT_PAYPAL = 1
    PAYMENT_AUTHNET = 2
    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_PAYPAL, 'PayPal'), 
        (PAYMENT_AUTHNET, 'Authorize.net'),
    )
    site = models.OneToOneField('accounts.Site')
    dine_in = models.BooleanField(default=True) 
    takeout = models.BooleanField(default=True) 
    delivery = models.BooleanField(default=True) 
    delivery_minimum = models.DecimalField('minimum amount for delivery orders', max_digits=5, decimal_places=2, default='0.00') 
    delivery_area = models.MultiPolygonField(null=True, blank=True) 
    # customer's authorize.net information for online orders
    payment_type = models.IntegerField('Collect payment via', null=True, choices=PAYMENT_TYPE_CHOICES)
    auth_net_api_login = models.CharField(max_length=255, blank=True, null=True)
    auth_net_api_key = models.CharField(max_length=255, blank=True, null=True)
    paypal_email = models.EmailField(blank=True, null=True)
    require_payment = models.BooleanField('Make online payment required for online orders', default=False)
    takes_amex = models.BooleanField(default=False)
    takes_discover = models.BooleanField(default=False)
    takes_mc = models.BooleanField(default=False)
    takes_visa = models.BooleanField(default=False)

    @property
    def choices(self):
        choice_list = []
        #TODO: make this list of options and the associated numbers
        # sit somewhere in one place in case more options are added 
        # in the future
        for i, choice in enumerate(('takeout', 'dine_in', 'delivery',)):
            if getattr(self, choice, None):
                choice_list.append(i + 1)
        min_order = ' (minimum order of %.2f)' % self.delivery_minimum \
            if self.delivery_minimum else ''
        return [
            c if c[0] != Order.METHOD_DELIVERY else (c[0], c[1] + min_order)
            for c in Order.METHOD_CHOICES 
            if c[0] in choice_list
        ]

    @property
    def _takes_paypal(self):
        return self.payment_type == OrderSettings.PAYMENT_PAYPAL and self.paypal_email

    @property
    def _takes_authnet(self):
        return all([
            self.payment_type == OrderSettings.PAYMENT_AUTHNET,
            self.auth_net_api_key,
            self.auth_net_api_login
        ])

    @property
    def takes_payment(self):
        return self._takes_paypal or self._takes_authnet

    def payment_url(self, cart_id=None, order_id=None):
        if self._takes_paypal:
            return reverse('payment_paypal')
        if self._takes_authnet:
            # authorize.net requires an SSL connection, so we use the
            # wildcard cert available for takeouttiger.com subdomains and pass
            # the card id as a GET parameter so the middleware correctly carries
            # over the contents of the user's cart
            domain = self.site.tiger_domain(secure=(not settings.DEBUG))
            path = reverse('payment_authnet')
            return '%s%s?cs=%s&o=%d' % (domain, path, cart_id, order_id)
        assert False
    

class Coupon(models.Model):
    site = models.ForeignKey('accounts.Site', editable=False)
    short_code = models.CharField(max_length=20, help_text='Uppercase letters and numbers only. Leave this blank to have a randomly generated coupon code.')
    exp_date = models.DateField('Expiration date', null=True, blank=True)
    click_count = models.IntegerField('Number of uses', editable=False, default=0)
    max_clicks = models.IntegerField('Max. allowed uses', null=True, blank=True)
    discount = models.IntegerField()

    def __unicode__(self):
        return self.short_code

    def save(self, *args, **kwargs):
        if not self.id and not self.short_code:
            self.short_code = int_to_base36(int(time.time())).upper()
        super(Coupon, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '%s?cc=%d' % (reverse('add_coupon'), self.id)

    def log_use(self, order):
        if self.max_clicks:
            self.click_count += 1
        self.save()
        CouponUse.objects.create(order=order, coupon=self)

    def boilerplate(self):
        msg = 'Get %d%% off your online order at %s with coupon code %s!' % (
            self.discount, self.site.name, self.short_code)
        if self.exp_date or self.max_clicks:
            msg += ' Valid '
            if self.max_clicks:
                msg += 'for the first %d customers ' % self.max_clicks
            if self.exp_date:
                msg += 'until %s' % self.exp_date.strftime('%m/%d/%y')
        return msg

    @property
    def is_open(self):
        date_is_valid = self.exp_date is None or self.exp_date <= date.today()
        has_clicks_available = self.max_clicks is None or self.click_count < self.max_clicks
        if not (date_is_valid and has_clicks_available):
            return False
        return True


class CouponUse(models.Model):
    coupon = models.ForeignKey(Coupon)
    order = models.ForeignKey(Order)
    timestamp = models.DateTimeField(default=datetime.now)


def register_paypal_payment(sender, **kwargs):
    ipn_obj = sender
    order = Order.objects.get(id=ipn_obj.invoice)
    order.notify_restaurant(Order.STATUS_PAID)


def new_site_setup(sender, instance, created, **kwargs):
    if instance.__class__.__name__ == 'Site' and created:
        OrderSettings.objects.create(site=instance)


payment_was_successful.connect(register_paypal_payment)
post_save.connect(new_site_setup)
post_save.connect(item_social_handler, sender=Item)
post_save.connect(pdf_caching_handler, sender=Item)
post_save.connect(coupon_social_handler, sender=Coupon)
