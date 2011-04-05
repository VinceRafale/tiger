# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Invoice.date'
        db.add_column('sales_invoice', 'date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today, null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Invoice.date'
        db.delete_column('sales_invoice', 'date')


    models = {
        'accounts.site': {
            'Meta': {'object_name': 'Site'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sales.Account']"}),
            'custom_domain': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'managed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sales.Plan']", 'null': 'True'}),
            'reseller_network': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'signup_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'sms': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.SmsSettings']", 'null': 'True'}),
            'subdomain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stork.Theme']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'walkthrough_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sales.account': {
            'Meta': {'object_name': 'Account', 'db_table': "'accounts_account'"},
            'basic_price': ('django.db.models.fields.DecimalField', [], {'default': "'40.00'", 'max_digits': '5', 'decimal_places': '2'}),
            'card_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'card_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'customer_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'ecomm_price': ('django.db.models.fields.DecimalField', [], {'default': "'67.50'", 'max_digits': '5', 'decimal_places': '2'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'fax': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'fax_price': ('django.db.models.fields.DecimalField', [], {'default': "'0.07'", 'max_digits': '5', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'multi_price': ('django.db.models.fields.DecimalField', [], {'default': "'85.50'", 'max_digits': '5', 'decimal_places': '2'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'signup_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'sms': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.SmsSettings']", 'null': 'True'}),
            'sms_line_price': ('django.db.models.fields.DecimalField', [], {'default': "'2.00'", 'max_digits': '5', 'decimal_places': '2'}),
            'sms_price': ('django.db.models.fields.DecimalField', [], {'default': "'0.02'", 'max_digits': '5', 'decimal_places': '2'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'subscription_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'sales.charge': {
            'Meta': {'object_name': 'Charge'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'charge_type': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sales.Invoice']"})
        },
        'sales.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sales.Account']"}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subinvoice_set'", 'null': 'True', 'to': "orm['sales.Invoice']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']", 'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'sales.payment': {
            'Meta': {'object_name': 'Payment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'sales.plan': {
            'Meta': {'object_name': 'Plan'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sales.Account']", 'null': 'True'}),
            'fax_cap': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fax_cap_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'has_online_ordering': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_sms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'multiple_locations': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sms_cap': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sms_cap_type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'sales.salesrep': {
            'Meta': {'object_name': 'SalesRep', 'db_table': "'accounts_salesrep'"},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '12'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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

    complete_apps = ['sales']
