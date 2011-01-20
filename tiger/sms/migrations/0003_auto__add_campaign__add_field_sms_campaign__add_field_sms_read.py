# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Campaign'
        db.create_table('sms_campaign', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('settings', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sms.SmsSettings'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('body', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('filter_on', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('filter_value', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('starred', self.gf('django.db.models.fields.NullBooleanField')(default=None, null=True, blank=True)),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('sms', ['Campaign'])

        # Adding M2M table for field subscribers on 'Campaign'
        db.create_table('sms_campaign_subscribers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('campaign', models.ForeignKey(orm['sms.campaign'], null=False)),
            ('smssubscriber', models.ForeignKey(orm['sms.smssubscriber'], null=False))
        ))
        db.create_unique('sms_campaign_subscribers', ['campaign_id', 'smssubscriber_id'])

        # Adding field 'SMS.campaign'
        db.add_column('sms_sms', 'campaign', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sms.Campaign'], null=True), keep_default=False)

        # Adding field 'SMS.read'
        db.add_column('sms_sms', 'read', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'Campaign'
        db.delete_table('sms_campaign')

        # Removing M2M table for field subscribers on 'Campaign'
        db.delete_table('sms_campaign_subscribers')

        # Deleting field 'SMS.campaign'
        db.delete_column('sms_sms', 'campaign_id')

        # Deleting field 'SMS.read'
        db.delete_column('sms_sms', 'read')


    models = {
        'sms.campaign': {
            'Meta': {'object_name': 'Campaign'},
            'body': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'filter_on': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'filter_value': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'settings': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.SmsSettings']"}),
            'starred': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'subscribers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sms.SmsSubscriber']", 'symmetrical': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'sms.sms': {
            'Meta': {'object_name': 'SMS'},
            'body': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms.Campaign']", 'null': 'True'}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'starred': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True'}),
            'unsubscribed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'})
        }
    }

    complete_apps = ['sms']
