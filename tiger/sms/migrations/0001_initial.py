# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SmsSettings'
        db.create_table('sms_smssettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sms_number', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20, null=True)),
            ('sid', self.gf('django.db.models.fields.CharField')(max_length=34, null=True)),
            ('send_intro', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('intro_sms', self.gf('django.db.models.fields.CharField')(max_length=160, null=True)),
        ))
        db.send_create_signal('sms', ['SmsSettings'])

        # Adding model 'SmsSubscriber'
        db.create_table('sms_smssubscriber', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('settings', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sms.SmsSettings'])),
            ('phone_number', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('state', self.gf('django.contrib.localflavor.us.models.USStateField')(max_length=2, null=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
            ('menus_first', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('signed_up_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('unsubscribed_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('sms', ['SmsSubscriber'])

        # Adding model 'SMS'
        db.create_table('sms_sms', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('destination', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('logged', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('settings', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sms.SmsSettings'])),
            ('subscriber', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sms.SmsSubscriber'])),
            ('sid', self.gf('django.db.models.fields.CharField')(max_length=34)),
            ('body', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('sms', ['SMS'])


    def backwards(self, orm):
        
        # Deleting model 'SmsSettings'
        db.delete_table('sms_smssettings')

        # Deleting model 'SmsSubscriber'
        db.delete_table('sms_smssubscriber')

        # Deleting model 'SMS'
        db.delete_table('sms_sms')


    models = {
        'sms.sms': {
            'Meta': {'object_name': 'SMS'},
            'body': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'settings': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.SmsSettings']"}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '34'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.SmsSubscriber']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'sms.smssettings': {
            'Meta': {'object_name': 'SmsSettings'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro_sms': ('django.db.models.fields.CharField', [], {'max_length': '160', 'null': 'True'}),
            'send_intro': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '34', 'null': 'True'}),
            'sms_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True'})
        },
        'sms.smssubscriber': {
            'Meta': {'object_name': 'SmsSubscriber'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'menus_first': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'phone_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'settings': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.SmsSettings']"}),
            'signed_up_at': ('django.db.models.fields.DateTimeField', [], {}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True'}),
            'unsubscribed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'})
        }
    }

    complete_apps = ['sms']
