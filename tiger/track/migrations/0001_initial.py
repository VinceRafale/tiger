# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Session'
        db.create_table('track_session', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Site'])),
            ('session', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('is_closed', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('track', ['Session'])

        # Adding model 'Hit'
        db.create_table('track_hit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['track.Session'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Location'])),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('referrer', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('verb', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('response_code', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('coords', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True)),
            ('hit_number', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('track', ['Hit'])


    def backwards(self, orm):
        
        # Deleting model 'Session'
        db.delete_table('track_session')

        # Deleting model 'Hit'
        db.delete_table('track_hit')


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
        'accounts.location': {
            'Meta': {'object_name': 'Location'},
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'delivery': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'delivery_area': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'delivery_lead_time': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'delivery_minimum': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '5', 'decimal_places': '2'}),
            'dine_in': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
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
            'takeout': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '3'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'US/Eastern'", 'max_length': '100'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'})
        },
        'accounts.salesrep': {
            'Meta': {'object_name': 'SalesRep'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan': ('django.db.models.fields.CharField', [], {'default': "'chomp3'", 'max_length': '12'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'accounts.schedule': {
            'Meta': {'object_name': 'Schedule'},
            'display': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"})
        },
        'accounts.site': {
            'Meta': {'object_name': 'Site'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Account']"}),
            'custom_domain': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'enable_orders': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Your Restaurant Name'", 'max_length': '200'}),
            'subdomain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'walkthrough_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
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
        'track.hit': {
            'Meta': {'object_name': 'Hit'},
            'coords': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True'}),
            'hit_number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Location']"}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'referrer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'response_code': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['track.Session']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        },
        'track.session': {
            'Meta': {'object_name': 'Session'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_closed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'session': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Site']"})
        }
    }

    complete_apps = ['track']
