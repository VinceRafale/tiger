# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Social.mailchimp_from_email'
        db.add_column('notify_social', 'mailchimp_from_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Social.mailchimp_from_email'
        db.delete_column('notify_social', 'mailchimp_from_email')


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
            'lat': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '9'}),
            'lon': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '9'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'default': "''", 'max_length': '20'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'default': "''", 'max_length': '2'}),
            'street': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'subdomain': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'US/Eastern'", 'max_length': '100'}),
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
        'content.pdfmenu': {
            'Meta': {'object_name': 'PdfMenu'},
            'column_height': ('django.db.models.fields.DecimalField', [], {'default': "'7.0'", 'max_digits': '3', 'decimal_places': '1'}),
            'columns': ('django.db.models.fields.SmallIntegerField', [], {'default': '2'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'footer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'orientation': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'page_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'sections': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Section']", 'symmetrical': 'False'}),
            'show_descriptions': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.coupon': {
            'Meta': {'object_name': 'Coupon'},
            'click_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'discount': ('django.db.models.fields.IntegerField', [], {}),
            'exp_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_clicks': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'short_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"})
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
        'notify.fax': {
            'Meta': {'object_name': 'Fax'},
            'completion_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logged': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'page_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent_transaction': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'transaction': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'notify.release': {
            'Meta': {'object_name': 'Release'},
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'body_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'coupon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Coupon']", 'null': 'True', 'blank': 'True'}),
            'facebook': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'fax_transaction': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailchimp': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'pdf': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['content.PdfMenu']", 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'time_sent': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'twitter': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'notify.social': {
            'Meta': {'object_name': 'Social'},
            'facebook_auto_items': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'facebook_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailchimp_allow_signup': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'mailchimp_api_key': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mailchimp_from_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'mailchimp_list_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'mailchimp_list_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mailchimp_send_blast': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['accounts.Site']", 'unique': 'True'}),
            'twitter_auto_items': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'twitter_screen_name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'twitter_secret': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'twitter_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['notify']
