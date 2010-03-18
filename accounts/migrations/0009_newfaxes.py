
from south.db import db
from django.db import models
from tiger.accounts.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'ScheduledUpdate.name'
        db.add_column('accounts_scheduledupdate', 'name', orm['accounts.scheduledupdate:name'])
        
        # Adding field 'ScheduledUpdate.column_height'
        db.add_column('accounts_scheduledupdate', 'column_height', orm['accounts.scheduledupdate:column_height'])
        
        # Adding field 'ScheduledUpdate.title'
        db.add_column('accounts_scheduledupdate', 'title', orm['accounts.scheduledupdate:title'])
        
        # Adding field 'ScheduledUpdate.columns'
        db.add_column('accounts_scheduledupdate', 'columns', orm['accounts.scheduledupdate:columns'])
        
        # Changing field 'Site.phone'
        # (to signature: django.contrib.localflavor.us.models.PhoneNumberField(max_length=20))
        db.alter_column('accounts_site', 'phone', orm['accounts.site:phone'])
        
        # Changing field 'Site.fax_number'
        # (to signature: django.contrib.localflavor.us.models.PhoneNumberField(max_length=20, blank=True))
        db.alter_column('accounts_site', 'fax_number', orm['accounts.site:fax_number'])
        
        # Changing field 'Site.state'
        # (to signature: django.contrib.localflavor.us.models.USStateField(max_length=2))
        db.alter_column('accounts_site', 'state', orm['accounts.site:state'])
        
        # Changing field 'Subscriber.fax'
        # (to signature: django.contrib.localflavor.us.models.PhoneNumberField(max_length=20, blank=True))
        db.alter_column('accounts_subscriber', 'fax', orm['accounts.subscriber:fax'])
        
        # Changing field 'Account.fax'
        # (to signature: django.contrib.localflavor.us.models.PhoneNumberField(max_length=20))
        db.alter_column('accounts_account', 'fax', orm['accounts.account:fax'])
        
        # Changing field 'Account.phone'
        # (to signature: django.contrib.localflavor.us.models.PhoneNumberField(max_length=20))
        db.alter_column('accounts_account', 'phone', orm['accounts.account:phone'])
        
        # Changing field 'Account.state'
        # (to signature: django.contrib.localflavor.us.models.USStateField(max_length=2))
        db.alter_column('accounts_account', 'state', orm['accounts.account:state'])
        
        # Changing field 'ScheduledUpdate.footer'
        # (to signature: django.db.models.fields.TextField(blank=True))
        db.alter_column('accounts_scheduledupdate', 'footer', orm['accounts.scheduledupdate:footer'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'ScheduledUpdate.name'
        db.delete_column('accounts_scheduledupdate', 'name')
        
        # Deleting field 'ScheduledUpdate.column_height'
        db.delete_column('accounts_scheduledupdate', 'column_height')
        
        # Deleting field 'ScheduledUpdate.title'
        db.delete_column('accounts_scheduledupdate', 'title')
        
        # Deleting field 'ScheduledUpdate.columns'
        db.delete_column('accounts_scheduledupdate', 'columns')
        
        # Adding field 'Site.google_analytics'
        db.add_column('accounts_site', 'google_analytics', orm['accounts.site:google_analytics'])
        
        # Changing field 'Site.phone'
        # (to signature: django.contrib.localflavor.us.models.PhoneNumberField())
        db.alter_column('accounts_site', 'phone', orm['accounts.site:phone'])
        
        # Changing field 'Site.fax_number'
        # (to signature: django.contrib.localflavor.us.models.PhoneNumberField(blank=True))
        db.alter_column('accounts_site', 'fax_number', orm['accounts.site:fax_number'])
        
        # Changing field 'Site.state'
        # (to signature: django.contrib.localflavor.us.models.USStateField(max_length=255))
        db.alter_column('accounts_site', 'state', orm['accounts.site:state'])
        
        # Changing field 'Subscriber.fax'
        # (to signature: django.contrib.localflavor.us.models.PhoneNumberField(blank=True))
        db.alter_column('accounts_subscriber', 'fax', orm['accounts.subscriber:fax'])
        
        # Changing field 'Account.fax'
        # (to signature: django.contrib.localflavor.us.models.PhoneNumberField())
        db.alter_column('accounts_account', 'fax', orm['accounts.account:fax'])
        
        # Changing field 'Account.phone'
        # (to signature: django.contrib.localflavor.us.models.PhoneNumberField())
        db.alter_column('accounts_account', 'phone', orm['accounts.account:phone'])
        
        # Changing field 'Account.state'
        # (to signature: django.contrib.localflavor.us.models.USStateField())
        db.alter_column('accounts_account', 'state', orm['accounts.account:state'])
        
        # Changing field 'ScheduledUpdate.footer'
        # (to signature: django.db.models.fields.TextField())
        db.alter_column('accounts_scheduledupdate', 'footer', orm['accounts.scheduledupdate:footer'])
        
    
    
    models = {
        'accounts.account': {
            'auth_net_api_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'auth_net_api_login': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'cc_last_4': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'customer_profile_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'fax': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_profile_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'signup_date': ('django.db.models.fields.DateField', [], {}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'accounts.invoice': {
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Account']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'accounts.lineitem': {
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Invoice']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'qty': ('django.db.models.fields.IntegerField', [], {}),
            'total': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'})
        },
        'accounts.scheduledupdate': {
            'Meta': {'unique_together': "(('site', 'weekday'),)"},
            'column_height': ('django.db.models.fields.DecimalField', [], {'default': "'7.0'", 'max_digits': '3', 'decimal_places': '1'}),
            'columns': ('django.db.models.fields.SmallIntegerField', [], {'default': '2'}),
            'footer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'show_descriptions': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'weekday': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'accounts.site': {
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Account']"}),
            'blog_address': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'custom_domain': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'enable_blog': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'fax_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'default': "''", 'max_length': '20'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'default': "''", 'max_length': '2'}),
            'street': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'tld': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'zip': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'})
        },
        'accounts.subscriber': {
            'fax': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'send_updates': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'update_via': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'accounts.timeslot': {
            'dow': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'start': ('django.db.models.fields.TimeField', [], {}),
            'stop': ('django.db.models.fields.TimeField', [], {})
        },
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['accounts']
