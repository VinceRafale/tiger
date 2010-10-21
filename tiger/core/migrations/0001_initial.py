# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    depends_on = (
        ("accounts", "0001_initial"),
    )

    def forwards(self, orm):
        
        # Adding model 'Section'
        db.create_table('core_section', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Site'])),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('ordering', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('hours', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
        ))
        db.send_create_signal('core', ['Section'])

        # Adding model 'Item'
        db.create_table('core_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Section'])),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Site'])),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['content.ItemImage'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('special', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('ordering', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('spicy', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('vegetarian', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('out_of_stock', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('taxable', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('price_list', self.gf('tiger.utils.fields.PickledObjectField')(null=True)),
            ('posting_stage', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal('core', ['Item'])

        # Adding model 'Variant'
        db.create_table('core_variant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Item'], null=True, blank=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Section'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal('core', ['Variant'])

        # Adding model 'Upgrade'
        db.create_table('core_upgrade', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Item'], null=True, blank=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Section'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal('core', ['Upgrade'])

        # Adding model 'SideDishGroup'
        db.create_table('core_sidedishgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Item'], null=True, blank=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Section'], null=True, blank=True)),
        ))
        db.send_create_signal('core', ['SideDishGroup'])

        # Adding model 'SideDish'
        db.create_table('core_sidedish', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.SideDishGroup'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
        ))
        db.send_create_signal('core', ['SideDish'])

        # Adding model 'Order'
        db.create_table('core_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Site'], null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('pickup', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('total', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('tax', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=6, decimal_places=2)),
            ('cart', self.gf('tiger.utils.fields.PickledObjectField')(null=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('method', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('unread', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('core', ['Order'])

        # Adding model 'OrderSettings'
        db.create_table('core_ordersettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['accounts.Site'], unique=True)),
            ('receive_via', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('dine_in', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('takeout', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('delivery', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('delivery_minimum', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=5, decimal_places=2)),
            ('delivery_area', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(null=True, blank=True)),
            ('payment_type', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('auth_net_api_login', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('auth_net_api_key', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('paypal_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('require_payment', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('takes_amex', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('takes_discover', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('takes_mc', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('takes_visa', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('tax_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=3)),
            ('eod_buffer', self.gf('django.db.models.fields.PositiveIntegerField')(default=30)),
            ('review_page_text', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('send_page_text', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('core', ['OrderSettings'])

        # Adding model 'Coupon'
        db.create_table('core_coupon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Site'])),
            ('short_code', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('exp_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('click_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('max_clicks', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('discount', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('core', ['Coupon'])

        # Adding unique constraint on 'Coupon', fields ['site', 'short_code']
        db.create_unique('core_coupon', ['site_id', 'short_code'])

        # Adding model 'CouponUse'
        db.create_table('core_couponuse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('coupon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Coupon'])),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Order'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal('core', ['CouponUse'])


    def backwards(self, orm):
        
        # Deleting model 'Section'
        db.delete_table('core_section')

        # Deleting model 'Item'
        db.delete_table('core_item')

        # Deleting model 'Variant'
        db.delete_table('core_variant')

        # Deleting model 'Upgrade'
        db.delete_table('core_upgrade')

        # Deleting model 'SideDishGroup'
        db.delete_table('core_sidedishgroup')

        # Deleting model 'SideDish'
        db.delete_table('core_sidedish')

        # Deleting model 'Order'
        db.delete_table('core_order')

        # Deleting model 'OrderSettings'
        db.delete_table('core_ordersettings')

        # Deleting model 'Coupon'
        db.delete_table('core_coupon')

        # Removing unique constraint on 'Coupon', fields ['site', 'short_code']
        db.delete_unique('core_coupon', ['site_id', 'short_code'])

        # Deleting model 'CouponUse'
        db.delete_table('core_couponuse')


    models = {
        'accounts.account': {
            'Meta': {'object_name': 'Account'},
            'card_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'card_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'customer_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'fax': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'referrer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.SalesRep']", 'null': 'True'}),
            'signup_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'subscription_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'accounts.salesrep': {
            'Meta': {'object_name': 'SalesRep'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan': ('django.db.models.fields.CharField', [], {'default': "'chomp3'", 'max_length': '12'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'accounts.site': {
            'Meta': {'object_name': 'Site'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Account']"}),
            'blog_address': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'custom_domain': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'enable_blog': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'enable_orders': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'fax_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'hours': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '9'}),
            'lon': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '9'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Your Restaurant Name'", 'max_length': '200'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'default': "''", 'max_length': '20'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'default': "''", 'max_length': '2'}),
            'street': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'subdomain': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'US/Eastern'", 'max_length': '100'}),
            'walkthrough_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'content.itemimage': {
            'Meta': {'object_name': 'ItemImage'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.coupon': {
            'Meta': {'unique_together': "(('site', 'short_code'),)", 'object_name': 'Coupon'},
            'click_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'discount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'exp_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_clicks': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'short_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"})
        },
        'core.couponuse': {
            'Meta': {'object_name': 'CouponUse'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '5', 'decimal_places': '2'}),
            'coupon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Coupon']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Order']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'core.item': {
            'Meta': {'object_name': 'Item'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['content.ItemImage']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ordering': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'out_of_stock': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'posting_stage': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'price_list': ('tiger.utils.fields.PickledObjectField', [], {'null': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Section']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'special': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'spicy': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'vegetarian': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'core.order': {
            'Meta': {'object_name': 'Order'},
            'cart': ('tiger.utils.fields.PickledObjectField', [], {'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'pickup': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']", 'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '6', 'decimal_places': '2'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'total': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'unread': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'core.ordersettings': {
            'Meta': {'object_name': 'OrderSettings'},
            'auth_net_api_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'auth_net_api_login': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'delivery': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'delivery_area': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'delivery_minimum': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '5', 'decimal_places': '2'}),
            'dine_in': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'eod_buffer': ('django.db.models.fields.PositiveIntegerField', [], {'default': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_type': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'paypal_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'receive_via': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'require_payment': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'review_page_text': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'send_page_text': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['accounts.Site']", 'unique': 'True'}),
            'takeout': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'takes_amex': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'takes_discover': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'takes_mc': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'takes_visa': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '3'})
        },
        'core.section': {
            'Meta': {'object_name': 'Section'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'hours': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ordering': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'core.sidedish': {
            'Meta': {'object_name': 'SideDish'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SideDishGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'})
        },
        'core.sidedishgroup': {
            'Meta': {'object_name': 'SideDishGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Item']", 'null': 'True', 'blank': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Section']", 'null': 'True', 'blank': 'True'})
        },
        'core.upgrade': {
            'Meta': {'object_name': 'Upgrade'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Item']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Section']", 'null': 'True', 'blank': 'True'})
        },
        'core.variant': {
            'Meta': {'object_name': 'Variant'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Item']", 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Section']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['core']
