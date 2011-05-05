import time
from datetime import datetime, date
from decimal import Decimal
import random

from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.contrib.gis.db import models
from django.contrib.localflavor.us.models import *
from django.contrib.sessions.models import Session
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.http import int_to_base36, base36_to_int
from django.utils.safestring import mark_safe

from paypal.standard.ipn.models import PayPalIPN
from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
from picklefield.fields import PickledObjectField
from pytz import timezone

from tiger.content.handlers import pdf_caching_handler
from tiger.core.exceptions import SectionNotAvailable, ItemNotAvailable, PricePointNotAvailable
from tiger.core.messages import *
from tiger.notify.fax import FaxMachine
from tiger.notify.handlers import item_social_handler
from tiger.utils.hours import *
from tiger.utils.pdf import render_to_pdf


def get_price_list(obj):
    """Produces a string representing the price variants available for a given
    section or item.  
    """
    if obj.variant_set.count() == 1:
        price_list = ['$%.2f' % obj.variant_set.all()[0].price]  
    else:
        price_list = [
            '%s: $%.2f' % (v.description, v.price)
            for v in obj.variant_set.all()
        ]
    return price_list


class Section(models.Model):
    """Acts as a container for menu items. Example: "Burritos".
    """
    name = models.CharField(max_length=50)
    site = models.ForeignKey('accounts.Site', editable=False)
    description = models.TextField()
    slug = models.SlugField(editable=False)
    ordering = models.PositiveIntegerField(editable=False, default=1)
    schedule = models.ForeignKey('accounts.Schedule', null=True, blank=True)

    class Meta:
        verbose_name = 'menu section'
        ordering = ('ordering',)

    def natural_key(self):
        return (self.name,) + self.site.natural_key()
    natural_key.dependencies = ['accounts.site']

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if not self.id:
            self.ordering = 1
        super(Section, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('menu_section', kwargs={'section_id': self.id, 'section_slug': self.slug})

    def price_list(self):
        return get_price_list(self)

    def is_available(self, location):
        if self.schedule is None:
            return True
        if self.schedule.is_open(location) != TIME_OPEN:
            raise SectionNotAvailable(SECTION_NOT_AVAILABLE % (
                self.name, self.schedule.display), self.get_absolute_url())
        return True

    def for_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "items": [i.for_json() for i in self.item_set.all()]
        }


class ItemManager(models.Manager):
    use_for_related_fields = True

    def render_specials_to_string(self, site, template='core/specials_fax.html'):
        items = self.filter(special=True, site=site)
        return render_to_string(template, {'site': site, 'items': items})

    def active(self):
        return self.filter(archived=False, price_list__isnull=False).exclude(price_list=[])


class Item(models.Model):
    """Represents a single item on the menu in its most basic form.
    """
    STAGE_PRE = 0
    STAGE_READY = 1
    STAGE_POST = 2
    STAGE_CHOICES = (
        (STAGE_PRE, 'Cannot post to social media'),
        (STAGE_READY, 'Ready to post to social media'),
        (STAGE_POST, 'Has been posted to social media'),
    )
    name = models.CharField(max_length=100)
    section = models.ForeignKey(Section)
    site = models.ForeignKey('accounts.Site', editable=False)
    schedule = models.ForeignKey('accounts.Schedule', null=True, blank=True)
    image = models.ForeignKey('content.ItemImage', blank=True, null=True)
    description = models.TextField(blank=True)
    special = models.BooleanField('is this menu item currently a special?', default=False)
    slug = models.SlugField(editable=False)
    ordering = models.PositiveIntegerField(editable=False, default=1)
    spicy = models.BooleanField(default=False)
    vegetarian = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    taxable = models.BooleanField(default=True)
    price_list = PickledObjectField(null=True, editable=False)
    posting_stage = models.SmallIntegerField(default=0, choices=STAGE_CHOICES, editable=False)
    objects = ItemManager()

    class Meta:
        verbose_name = 'menu item'
        ordering = ('ordering',)

    def natural_key(self):
        return (self.name,) + self.section.natural_key()
    natural_key.dependencies = ['core.section']

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        new = False
        if not self.id:
            new = True
            self.slug = slugify(self.name)[:50]
            self.price_list = []
        if len(self.price_list) and self.posting_stage != Item.STAGE_POST:
            self.posting_stage += 1
        super(Item, self).save(*args, **kwargs)
        if new:
            for loc in self.site.location_set.all():
                LocationStockInfo.objects.create(location=loc, item=self)

    def get_absolute_url(self):
        return reverse('menu_item', 
            kwargs={
                'section_id': self.section.id, 
                'section_slug': self.section.slug, 
                'item_id': self.id,
                'item_slug': self.slug
        })

    def get_short_url(self):
        return reverse('short_code', kwargs={'item_id': int_to_base36(self.id)})

    def is_available(self, location):
        assert self.section.is_available(location)
        if self.schedule and self.schedule.is_open(location) != TIME_OPEN:
            raise ItemNotAvailable(ITEM_NOT_AVAILABLE_SCHEDULE % (self.name, self.schedule.display), 
                self.get_absolute_url())
        if self.archived or self.out_of_stock(location):
            raise ItemNotAvailable(ITEM_NOT_AVAILABLE % self.name, redirect_to=self.get_absolute_url())
        return True

    def out_of_stock(self, location):
        return self.locationstockinfo_set.get(location=location).out_of_stock

    def update_price(self):
        self.price_list = get_price_list(self)
        self.save()

    @property
    def incomplete(self):
        return self.price_list in (None, [])

    def for_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "spicy": self.spicy,
            "vegetarian": self.vegetarian,
            #"image": self.image,
            "prices": [p.for_json() for p in self.variant_set.all()],
            "extras": [x.for_json() for x in self.upgrade_set.all()],
            "choices": [c.for_json() for c in self.sidedishgroup_set.all()]
        }


class LocationStockInfo(models.Model):
    item = models.ForeignKey(Item)
    location = models.ForeignKey('accounts.Location')
    out_of_stock = models.BooleanField(default=False)


class Variant(models.Model):
    """Represents "column-level" extra data about a menu item.  This means
    information like "Extra large" and the corresponding price.  This is what a
    customer will actually be selecting when ordering a menu item.  All menu
    items must have at least one.  
    """
    item = models.ForeignKey(Item, null=True, blank=True)
    section = models.ForeignKey(Section, null=True, blank=True)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    schedule = models.ForeignKey('accounts.Schedule', null=True, blank=True)

    class Meta:
        ordering = ['price']

    def natural_key(self):
        return (self.price,) + self.item.natural_key()
    natural_key.dependencies = ['core.item']

    def __unicode__(self):
        s = '%s ($<span>%s</span>)' % (self.description, self.price)
        return mark_safe(s)

    def save(self, *args, **kwargs):
        new = False
        if not self.id:
            new = True
        self.price = self.price.quantize(Decimal('0.01'))
        super(Variant, self).save(*args, **kwargs)
        if self.item:
            self.item.update_price()

    def delete(self, *args, **kwargs):
        item = self.item
        super(Variant, self).delete(*args, **kwargs)
        item.update_price()

    def is_available(self, location):
        if self.schedule is None:
            return True
        if self.schedule.is_open(location) != TIME_OPEN:
            raise PricePointNotAvailable(PRICEPOINT_NOT_AVAILABLE % (
                self.description, self.schedule.display), self.item.get_absolute_url())
        return True

    def for_json(self):
        return {
            'id': self.id,
            'description': self.description,
            'price': str(self.price)
        }


class Upgrade(models.Model):
    """Provides additional cost data and/or order processing instructions. For
    example, "Subsitute seasoned frieds for $.50" or "Add extra cheese for
    $1.00." 
    """
    item = models.ForeignKey(Item, null=True, blank=True)
    section = models.ForeignKey(Section, null=True, blank=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = 'upgrade/substitution'
        verbose_name_plural = 'upgrades/substitutions'

    def __unicode__(self):
        s = 'Add %s for $<span>%.02f</span> more' % (self.name, float(self.price))
        return mark_safe(s)

    def save(self, *args, **kwargs):
        self.price = '%.02f' % self.price
        super(Upgrade, self).save(*args, **kwargs)

    def for_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': str(self.price)
        }


class SideDishGroup(models.Model):
    item = models.ForeignKey(Item, null=True, blank=True)
    section = models.ForeignKey(Section, null=True, blank=True)

    def __unicode__(self):
        sides = [unicode(side) for side in self.sidedish_set.all()]
        if len(sides) <= 2:
            sides = ' or '.join(sides)
        else:
            last = sides[-1]
            sides = ' '.join('%s,' % side for side in sides[:-1])
            sides = '%s or %s' % (sides, last)
        return 'Choice of ' + sides

    def for_json(self):
        return {
            "id": self.id,
            "sidedishes": [side.for_json() for side in self.sidedish_set.all()]
        }


class SideDish(models.Model):
    group = models.ForeignKey(SideDishGroup)
    name = models.CharField(max_length=100)
    price = models.DecimalField('Additional cost', max_digits=5, decimal_places=2, default='0.00', blank=True)

    def __unicode__(self):
        if self.price > 0:
            return mark_safe('%s (add $<span>%.02f</span>)' % (self.name, self.price))
        return self.name

    def for_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': str(self.price)
        }

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
    STATUS_PENDING = 6
    STATUS_REFUNDED = 7
    STATUS_CHOICES = (
        (STATUS_INCOMPLETE, 'Incomplete'),
        (STATUS_SENT, 'On arrival'),
        (STATUS_PAID, 'Paid online'),
        (STATUS_FULFILLED, 'Fulfilled'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_PENDING, 'Payment pending'),
        (STATUS_REFUNDED, 'Refunded'),
    )
    site = models.ForeignKey('accounts.Site', null=True, editable=False)
    session_key = models.CharField(max_length=40, null=True)
    location = models.ForeignKey('accounts.Location', editable=False)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zip = models.CharField(max_length=10, blank=True, null=True)
    ready_by = models.DateTimeField('Have order ready by:', null=True)
    total = models.DecimalField(editable=False, max_digits=6, decimal_places=2)
    tax = models.DecimalField(editable=False, max_digits=6, decimal_places=2, default='0.00')
    cart = PickledObjectField(editable=False, null=True)
    timestamp = models.DateTimeField(default=datetime.now, editable=False)
    method = models.IntegerField('This order is for', default=1, choices=METHOD_CHOICES)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_INCOMPLETE)
    unread = models.BooleanField(default=True)

    class Meta:
        ordering = ('-timestamp',)

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
        if self.status in (Order.STATUS_SENT, Order.STATUS_PAID):
            self.get_cart().clear()

    @models.permalink
    def get_absolute_url(self):
        return 'order_detail', [self.id], {}

    def notify_restaurant(self, status):
        """Sends a message to the restaurant with the information about the order
        and flags the order as either sent or paid.
        """
        self.status = status
        content = self.get_pdf_invoice()
        location = self.site.location_set.all()[0]
        if location.receive_via == OrderSettings.RECEIPT_EMAIL:
            email = EmailMessage('Takeout Tiger Order #%d' % self.id, 'Your order details are attached as PDF.', 'do-not-reply@takeouttiger.com', [location.order_email])
            email.attach('order-%d.pdf' % self.id, content, 'application/pdf')
            email.send()
        else:
            fax_machine = FaxMachine(self.site)
            fax_machine.send(self.site.fax_number, content)
        self.save()

    def get_pdf_invoice(self):
        return render_to_pdf('notify/order.html', {
            'order': self,
            'cart': self.get_cart(),
            'order_no': self.id,
        })

    def total_plus_tax(self):
        return self.total + self.tax

    def coupon(self):
        cart = self.get_cart()
        if cart.has_coupon:
            coupon = self.couponuse_set.all()[0].coupon
            return coupon
        return ''

    def get_cart(self):
        from tiger.core.middleware import Cart
        try:
            session = Session.objects.get(session_key=self.session_key)
        except Session.DoesNotExist:
            session = None
        return Cart(session=session, contents=self.cart)

    def localized_timestamp(self):
        server_tz = timezone(settings.TIME_ZONE)
        site_tz = timezone(self.location.timezone)
        timestamp = server_tz.localize(self.timestamp)
        return timestamp.astimezone(site_tz)

    def localized_ready_by(self):
        server_tz = timezone(settings.TIME_ZONE)
        site_tz = timezone(self.location.timezone)
        timestamp = server_tz.localize(self.ready_by)
        return timestamp.astimezone(site_tz)

    def paypal_transaction(self):
        try:
            return PayPalIPN.objects.get(invoice=unicode(self.id), payment_status='Completed')
        except PayPalIPN.DoesNotExist:
            try:
                return PayPalIPN.objects.get(invoice=unicode(self.id), payment_status='Refunded')
            except PayPalIPN.DoesNotExist:
                return None


class OrderSettings(models.Model):
    PAYMENT_NONE = 0
    PAYMENT_PAYPAL = 1
    PAYMENT_AUTHNET = 2
    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_NONE, 'Do not take payments online'), 
        (PAYMENT_PAYPAL, 'PayPal'), 
        (PAYMENT_AUTHNET, 'Authorize.net'),
    )
    RECEIPT_EMAIL = 1
    RECEIPT_FAX = 2
    RECEIPT_CHOICES = (
        (RECEIPT_EMAIL, 'E-mail'),
        (RECEIPT_FAX, 'Fax'),
    )
    site = models.OneToOneField('accounts.Site')
    # customer's authorize.net information for online orders
    payment_type = models.IntegerField('Collect payment via', null=True, choices=PAYMENT_TYPE_CHOICES, default=PAYMENT_NONE)
    auth_net_api_login = models.CharField('API Login ID', max_length=255, blank=True, null=True)
    auth_net_api_key = models.CharField('Transaction Key', max_length=255, blank=True, null=True)
    paypal_email = models.EmailField(blank=True, null=True)
    require_payment = models.BooleanField('Make online payment required for online orders', default=False)
    takes_amex = models.BooleanField(default=False)
    takes_discover = models.BooleanField(default=False)
    takes_mc = models.BooleanField(default=False)
    takes_visa = models.BooleanField(default=False)
    review_page_text = models.TextField('Additional text for the "Review your order" page', blank=True, default='')
    send_page_text = models.TextField('Additional text for the "Contact Information" page', blank=True, default='')

    @property
    def choices(self):
        choice_list = []
        #TODO: make this list of options and the associated numbers
        # sit somewhere in one place in case more options are added 
        # in the future
        location = self.site.location_set.all()[0]
        for i, choice in enumerate(('takeout', 'dine_in', 'delivery',)):
            if getattr(location, choice, None):
                choice_list.append(i + 1)
        min_order = ' (minimum order of %.2f)' % location.delivery_minimum \
            if location.delivery_minimum else ''
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

    def can_receive_orders(self):
        return all(loc.can_receive_orders() for loc in self.site.location_set.all())

    @property
    def tax_rate(self):
        location = self.site.location_set.all()[0]
        return location.tax_rate

COUPON_ID_PADDING = 100

class CouponManager(models.Manager):
    def get_by_coupon_id(self, b36):
        """Retrieves a coupon via the base 36 representation of its primary key + a 
        padding value to keep the coupons created from looking too sparse.
        """
        return self.get(id=(base36_to_int(b36)-COUPON_ID_PADDING))
    

class Coupon(models.Model):
    DISCOUNT_DOLLARS = 1
    DISCOUNT_PERCENT = 2
    DISCOUNT_CHOICES = (
        (DISCOUNT_DOLLARS, 'Dollar amount'),
        (DISCOUNT_PERCENT, 'Percentage of order'),
    )
    site = models.ForeignKey('accounts.Site', editable=False)
    short_code = models.CharField(max_length=20, help_text='Uppercase letters and numbers only. Leave this blank to have a randomly generated coupon code.', blank=True)
    exp_date = models.DateField('Expiration date (optional)', null=True, blank=True)
    click_count = models.IntegerField('Number of uses', editable=False, default=0)
    max_clicks = models.PositiveIntegerField('Max. allowed uses (optional)', null=True, blank=True)
    discount_type = models.PositiveIntegerField(choices=DISCOUNT_CHOICES)
    dollars_off = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    percent_off = models.PositiveIntegerField(null=True, blank=True)
    require_sharing = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0, editable=False)
    twitter_share_count = models.PositiveIntegerField(default=0, editable=False)
    fb_share_count = models.PositiveIntegerField(default=0, editable=False)
    objects = CouponManager()

    class Meta:
        unique_together = ('site', 'short_code',)

    def __unicode__(self):
        return self.short_code

    def save(self, *args, **kwargs):
        if not self.id and not self.short_code:
            self.short_code = '%02d' % random.randint(1,99) + int_to_base36(int(time.time())).upper()
        super(Coupon, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if self.require_sharing:
            return self.tiger_url()
        return self.add_coupon_url()

    def add_coupon_url(self):
        return '%s?cc=%d' % (reverse('add_coupon', urlconf='tiger.urls'), self.id)

    def tiger_url(self):
        return 'http://tkti.gr' + reverse(
            'share_coupon', 
            kwargs={'coupon_id': int_to_base36(self.id + COUPON_ID_PADDING)},
            urlconf='tiger.tiger_urls'
        )

    def log_use(self, order, amount):
        if self.max_clicks:
            self.click_count += 1
        self.save()
        CouponUse.objects.create(order=order, coupon=self, amount=amount)

    def remaining_clicks(self):
        if self.max_clicks is None:
            return None
        return self.max_clicks - self.click_count

    def boilerplate(self):
        msg = 'Get %s off your online order at %s with coupon code %s!' % (
            self.discount, self.site.name, self.short_code)
        if self.exp_date or self.max_clicks:
            msg += ' Valid '
            if self.max_clicks:
                msg += 'for the first %d customers ' % self.max_clicks
            if self.exp_date:
                msg += 'until %s' % self.exp_date.strftime('%m/%d/%y')
        return msg

    @property
    def discount(self):
        if self.discount_type == Coupon.DISCOUNT_DOLLARS:
            return '$%s' % self.dollars_off
        return '%d%%' % self.percent_off

    @property
    def is_open(self):
        date_is_valid = self.exp_date is None or self.exp_date >= date.today()
        has_clicks_available = self.max_clicks is None or self.click_count < self.max_clicks
        if not (date_is_valid and has_clicks_available):
            return False
        return True


class CouponUse(models.Model):
    coupon = models.ForeignKey(Coupon)
    order = models.ForeignKey(Order)
    timestamp = models.DateTimeField(default=datetime.now)
    amount = models.DecimalField(max_digits=5, decimal_places=2, default='0.00')


def register_paypal_payment(sender, **kwargs):
    ipn_obj = sender
    # Because of django-paypal's reliance on settings variables, payments 
    # come through as completed and verified,
    # but are still flagged with receiver_email as invalid.  This signal
    # handler is thus used for both payment_was_successful and 
    # payment_was_flagged.
    order = Order.objects.get(id=ipn_obj.invoice)
    if ipn_obj.payment_status == 'Completed':
        from tiger.notify.tasks import DeliverOrderTask
        DeliverOrderTask.delay(order.id, Order.STATUS_PAID)
    elif ipn_obj.payment_status == 'Refunded':
        order.status = Order.STATUS_REFUNDED
        order.save()


def new_site_setup(sender, instance, created, **kwargs):
    if created:
        Site = models.get_model('accounts', 'site')
        if isinstance(instance, Site):
            OrderSettings.objects.create(site=instance)

def create_defaults(sender, instance, created, **kwargs):
    if created:
        section = instance.section
        for variant in section.variant_set.all():
            Variant.objects.create(
                item=instance, 
                price=variant.price, 
                description=variant.description
            )
        for upgrade in section.upgrade_set.all():
            Upgrade.objects.create(
                item=instance, 
                price=upgrade.price, 
                name=upgrade.name
            )
        for sidedishgroup in section.sidedishgroup_set.all():
            new_group = SideDishGroup.objects.create(item=instance)
            for dish in sidedishgroup.sidedish_set.all():
                SideDish.objects.create(
                    group=new_group,
                    name=dish.name,
                    price=dish.price
                )


payment_was_successful.connect(register_paypal_payment)
payment_was_flagged.connect(register_paypal_payment)
post_save.connect(new_site_setup)
post_save.connect(item_social_handler, sender=Item)
post_save.connect(pdf_caching_handler, sender=Item)
post_save.connect(create_defaults, sender=Item)
