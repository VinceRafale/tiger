# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        # Adding field 'TimeSlot.section'
        db.add_column('accounts_timeslot', 'section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Section'], null=True), keep_default=False)
    
    
    def backwards(self, orm):
        # Deleting field 'TimeSlot.section'
        db.delete_column('accounts_timeslot', 'section_id')
    
    
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
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'subscription_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'accounts.faxlist': {
            'Meta': {'object_name': 'FaxList'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'accounts.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Account']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'accounts.lineitem': {
            'Meta': {'object_name': 'LineItem'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Invoice']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'qty': ('django.db.models.fields.IntegerField', [], {}),
            'total': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'})
        },
        'accounts.salesrep': {
            'Meta': {'object_name': 'SalesRep'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'default': "''", 'max_length': '20'}),
            'skin': ('django.db.models.fields.related.ForeignKey', [], {'default': '11', 'to': "orm['look.Skin']"}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'default': "''", 'max_length': '2'}),
            'street': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'subdomain': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'US/Eastern'", 'max_length': '100'}),
            'zip': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'})
        },
        'accounts.subscriber': {
            'Meta': {'object_name': 'Subscriber'},
            'fax': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'fax_list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.FaxList']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'send_updates': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"})
        },
        'accounts.timeslot': {
            'Meta': {'object_name': 'TimeSlot'},
            'dow': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Section']", 'null': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'start': ('django.db.models.fields.TimeField', [], {}),
            'stop': ('django.db.models.fields.TimeField', [], {})
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
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        'look.background': {
            'Meta': {'object_name': 'Background'},
            'attachment': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'repeat': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'look.fontface': {
            'Meta': {'object_name': 'FontFace'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'stack': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ttf': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'look.skin': {
            'Meta': {'object_name': 'Skin'},
            'background': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['look.Background']"}),
            'body_font': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'css': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'header_font': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['look.FontFace']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        }
    }
    
    complete_apps = ['accounts']
