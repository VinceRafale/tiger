# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Section.no_online_orders'
        db.add_column('core_section', 'no_online_orders', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Section.no_online_orders'
        db.delete_column('core_section', 'no_online_orders')


    models = {
        'accounts.location': {
            'Meta': {'object_name': 'Location'},
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'delivery': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'delivery_area': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'delivery_lead_time': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'delivery_minimum': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '5', 'decimal_places': '2'}),
            'dine_in': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'enable_orders': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'eod_buffer': ('django.db.models.fields.PositiveIntegerField', [], {'default': '30'}),
            'fax_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '9'}),
            'lead_time': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'lon': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '9'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'order_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'order_fax': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'default': "''", 'max_length': '20'}),
            'receive_via': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Schedule']", 'null': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'default': "''", 'max_length': '2'}),
            'street': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'takeout': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '3'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'US/Eastern'", 'max_length': '100'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'})
        },
        'accounts.schedule': {
            'Meta': {'object_name': 'Schedule'},
            'display': ('django.db.models.fields.TextField', [], {'default': "'default schedule'", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"})
        },
        'accounts.site': {
            'Meta': {'object_name': 'Site'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sales.Account']"}),
            'credit_card': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sales.CreditCard']", 'null': 'True'}),
            'custom_domain': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'google_analytics': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'managed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mobile_on': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sales.Plan']", 'null': 'True'}),
            'reseller_network': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'signup_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'sms': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.SmsSettings']", 'null': 'True'}),
            'subdomain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stork.Theme']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'walkthrough_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'webmaster_tools': ('django.db.models.fields.TextField', [], {'max_length': '255', 'null': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.coupon': {
            'Meta': {'unique_together': "(('site', 'short_code'),)", 'object_name': 'Coupon'},
            'click_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'discount_type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'dollars_off': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'exp_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fb_share_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_clicks': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'percent_off': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'require_sharing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'short_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'twitter_share_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'view_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
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
            'Meta': {'ordering': "('ordering',)", 'object_name': 'Item'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'available_online': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['content.ItemImage']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ordering': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'posting_stage': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'price_list': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Schedule']", 'null': 'True', 'blank': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Section']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'special': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'spicy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'text_price': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'vegetarian': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'core.locationstockinfo': {
            'Meta': {'object_name': 'LocationStockInfo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Item']"}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Location']"}),
            'out_of_stock': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'core.order': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'Order'},
            'cart': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Location']"}),
            'method': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'ready_by': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']", 'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '6', 'decimal_places': '2'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'total': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'unread': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'core.ordersettings': {
            'Meta': {'object_name': 'OrderSettings'},
            'auth_net_api_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'auth_net_api_login': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'paypal_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'require_payment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'review_page_text': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'send_page_text': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['accounts.Site']", 'unique': 'True'}),
            'takes_amex': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'takes_discover': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'takes_mc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'takes_visa': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'core.section': {
            'Meta': {'ordering': "('ordering',)", 'object_name': 'Section'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'no_online_orders': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ordering': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Schedule']", 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'core.sidedish': {
            'Meta': {'object_name': 'SideDish'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SideDishGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'})
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
            'Meta': {'ordering': "['price']", 'object_name': 'Variant'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Item']", 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Schedule']", 'null': 'True', 'blank': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Section']", 'null': 'True', 'blank': 'True'})
        },
        'sales.account': {
            'Meta': {'object_name': 'Account', 'db_table': "'accounts_account'"},
            'basic_price': ('django.db.models.fields.DecimalField', [], {'default': "'40.00'", 'max_digits': '5', 'decimal_places': '2'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'credit_card': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sales.CreditCard']", 'null': 'True'}),
            'ecomm_price': ('django.db.models.fields.DecimalField', [], {'default': "'67.50'", 'max_digits': '5', 'decimal_places': '2'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'fax': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'fax_price': ('django.db.models.fields.DecimalField', [], {'default': "'0.07'", 'max_digits': '5', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'multi_price': ('django.db.models.fields.DecimalField', [], {'default': "'85.50'", 'max_digits': '5', 'decimal_places': '2'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32'}),
            'signup_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'sms': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.SmsSettings']", 'null': 'True'}),
            'sms_line_price': ('django.db.models.fields.DecimalField', [], {'default': "'2.00'", 'max_digits': '5', 'decimal_places': '2'}),
            'sms_price': ('django.db.models.fields.DecimalField', [], {'default': "'0.02'", 'max_digits': '5', 'decimal_places': '2'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'trial_period': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'sales.creditcard': {
            'Meta': {'object_name': 'CreditCard'},
            'card_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'card_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'customer_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signup_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'subscription_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'})
        },
        'sales.plan': {
            'Meta': {'object_name': 'Plan'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sales.Account']", 'null': 'True'}),
            'fax_cap': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fax_cap_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fax_rate': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'has_mobile': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_online_ordering': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_sms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'multiple_locations': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2'}),
            'promo_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32'}),
            'sms_cap': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sms_cap_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sms_rate': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'sms.smssettings': {
            'Meta': {'object_name': 'SmsSettings'},
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro_sms': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True'}),
            'keywords': ('picklefield.fields.PickledObjectField', [], {'default': "''"}),
            'reseller_network': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'send_intro': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '34', 'null': 'True'}),
            'sms_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True'})
        },
        'stork.theme': {
            'Meta': {'object_name': 'Theme'},
            'bundled_css': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'saved_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'screenshot': ('django.db.models.fields.files.ImageField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['core']
