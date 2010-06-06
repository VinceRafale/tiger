# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FontFace'
        db.create_table('look_fontface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('ttf', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('stack', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('look', ['FontFace'])

        # Adding model 'Background'
        db.create_table('look_background', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('color', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('repeat', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('position', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('attachment', self.gf('django.db.models.fields.CharField')(max_length=7)),
        ))
        db.send_create_signal('look', ['Background'])

        # Adding model 'Skin'
        db.create_table('look_skin', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('header_font', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['look.FontFace'], null=True, blank=True)),
            ('body_font', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('background', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['look.Background'])),
            ('css', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('look', ['Skin'])


    def backwards(self, orm):
        
        # Deleting model 'FontFace'
        db.delete_table('look_fontface')

        # Deleting model 'Background'
        db.delete_table('look_background')

        # Deleting model 'Skin'
        db.delete_table('look_skin')


    models = {
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

    complete_apps = ['look']
