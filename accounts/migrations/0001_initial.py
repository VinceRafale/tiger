
from south.db import db
from django.db import models
from tiger.accounts.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Site'
        db.create_table('accounts_site', (
            ('id', orm['accounts.Site:id']),
            ('account', orm['accounts.Site:account']),
            ('name', orm['accounts.Site:name']),
            ('domain', orm['accounts.Site:domain']),
            ('tld', orm['accounts.Site:tld']),
            ('enable_blog', orm['accounts.Site:enable_blog']),
            ('blog_address', orm['accounts.Site:blog_address']),
        ))
        db.send_create_signal('accounts', ['Site'])
        
        # Adding model 'Subscriber'
        db.create_table('accounts_subscriber', (
            ('id', orm['accounts.Subscriber:id']),
            ('user', orm['accounts.Subscriber:user']),
            ('site', orm['accounts.Subscriber:site']),
            ('organization', orm['accounts.Subscriber:organization']),
            ('send_updates', orm['accounts.Subscriber:send_updates']),
            ('update_via', orm['accounts.Subscriber:update_via']),
            ('fax', orm['accounts.Subscriber:fax']),
        ))
        db.send_create_signal('accounts', ['Subscriber'])
        
        # Adding model 'LineItem'
        db.create_table('accounts_lineitem', (
            ('id', orm['accounts.LineItem:id']),
            ('invoice', orm['accounts.LineItem:invoice']),
            ('description', orm['accounts.LineItem:description']),
            ('price', orm['accounts.LineItem:price']),
            ('qty', orm['accounts.LineItem:qty']),
            ('total', orm['accounts.LineItem:total']),
        ))
        db.send_create_signal('accounts', ['LineItem'])
        
        # Adding model 'Invoice'
        db.create_table('accounts_invoice', (
            ('id', orm['accounts.Invoice:id']),
            ('account', orm['accounts.Invoice:account']),
            ('date', orm['accounts.Invoice:date']),
        ))
        db.send_create_signal('accounts', ['Invoice'])
        
        # Adding model 'Account'
        db.create_table('accounts_account', (
            ('id', orm['accounts.Account:id']),
            ('user', orm['accounts.Account:user']),
            ('company_name', orm['accounts.Account:company_name']),
            ('email', orm['accounts.Account:email']),
            ('phone', orm['accounts.Account:phone']),
            ('fax', orm['accounts.Account:fax']),
            ('street', orm['accounts.Account:street']),
            ('state', orm['accounts.Account:state']),
            ('zip', orm['accounts.Account:zip']),
            ('auth_net_api_login', orm['accounts.Account:auth_net_api_login']),
            ('auth_net_api_key', orm['accounts.Account:auth_net_api_key']),
            ('signup_date', orm['accounts.Account:signup_date']),
            ('customer_profile_id', orm['accounts.Account:customer_profile_id']),
            ('payment_profile_id', orm['accounts.Account:payment_profile_id']),
            ('cc_last_4', orm['accounts.Account:cc_last_4']),
        ))
        db.send_create_signal('accounts', ['Account'])
        
        # Adding model 'ScheduledUpdate'
        db.create_table('accounts_scheduledupdate', (
            ('id', orm['accounts.ScheduledUpdate:id']),
            ('site', orm['accounts.ScheduledUpdate:site']),
            ('start_time', orm['accounts.ScheduledUpdate:start_time']),
            ('weekday', orm['accounts.ScheduledUpdate:weekday']),
        ))
        db.send_create_signal('accounts', ['ScheduledUpdate'])
        
        # Creating unique_together for [site, weekday] on ScheduledUpdate.
        db.create_unique('accounts_scheduledupdate', ['site_id', 'weekday'])
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [site, weekday] on ScheduledUpdate.
        db.delete_unique('accounts_scheduledupdate', ['site_id', 'weekday'])
        
        # Deleting model 'Site'
        db.delete_table('accounts_site')
        
        # Deleting model 'Subscriber'
        db.delete_table('accounts_subscriber')
        
        # Deleting model 'LineItem'
        db.delete_table('accounts_lineitem')
        
        # Deleting model 'Invoice'
        db.delete_table('accounts_invoice')
        
        # Deleting model 'Account'
        db.delete_table('accounts_account')
        
        # Deleting model 'ScheduledUpdate'
        db.delete_table('accounts_scheduledupdate')
        
    
    
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'weekday': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'accounts.site': {
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Account']"}),
            'blog_address': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'enable_blog': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tld': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        'accounts.subscriber': {
            'fax': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'send_updates': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'update_via': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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
