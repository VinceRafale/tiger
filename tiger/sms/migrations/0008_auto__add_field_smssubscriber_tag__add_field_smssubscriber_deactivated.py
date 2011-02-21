# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'SmsSubscriber.tag'
        db.add_column('sms_smssubscriber', 'tag', self.gf('django.db.models.fields.CharField')(default='', max_length=15), keep_default=False)

        # Adding field 'SmsSubscriber.deactivated'
        db.add_column('sms_smssubscriber', 'deactivated', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Thread.tag'
        db.add_column('sms_thread', 'tag', self.gf('django.db.models.fields.CharField')(default='', max_length=15), keep_default=False)

        # Adding field 'SmsSettings.keywords'
        db.add_column('sms_smssettings', 'keywords', self.gf('picklefield.fields.PickledObjectField')(default=''), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'SmsSubscriber.tag'
        db.delete_column('sms_smssubscriber', 'tag')

        # Deleting field 'SmsSubscriber.deactivated'
        db.delete_column('sms_smssubscriber', 'deactivated')

        # Deleting field 'Thread.tag'
        db.delete_column('sms_thread', 'tag')

        # Deleting field 'SmsSettings.keywords'
        db.delete_column('sms_smssettings', 'keywords')


    models = {
        'sms.campaign': {
            'Meta': {'object_name': 'Campaign'},
            'body': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'filter_on': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'filter_value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sent_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'settings': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.SmsSettings']"}),
            'starred': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'subscribers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sms.SmsSubscriber']", 'symmetrical': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'sms.sms': {
            'Meta': {'object_name': 'SMS'},
            'body': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.Campaign']", 'null': 'True'}),
            'conversation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'settings': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.SmsSettings']"}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '34'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.SmsSubscriber']", 'null': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'sms.smssettings': {
            'Meta': {'object_name': 'SmsSettings'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro_sms': ('django.db.models.fields.CharField', [], {'max_length': '160', 'null': 'True'}),
            'keywords': ('picklefield.fields.PickledObjectField', [], {'default': "['in']"}),
            'send_intro': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '34', 'null': 'True'}),
            'sms_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True'})
        },
        'sms.smssubscriber': {
            'Meta': {'object_name': 'SmsSubscriber'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'deactivated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'menus_first': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'phone_number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'settings': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.SmsSettings']"}),
            'signed_up_at': ('django.db.models.fields.DateTimeField', [], {}),
            'starred': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'unsubscribed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'})
        },
        'sms.thread': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'Thread'},
            'body': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'settings': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.SmsSettings']"}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'unread': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        }
    }

    complete_apps = ['sms']
