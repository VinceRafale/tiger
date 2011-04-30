# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from tiger.stork import Stork

class Migration(DataMigration):

    def forwards(self, orm):
        for theme in orm.Theme.objects.all():
            stork = Stork(theme)
            for key, component in stork.component_cache:
                try:
                    instance = component.instance
                    assert instance
                except:
                    break
                instance.component = component.id
                instance.save()

    def backwards(self, orm):
        "Write your backwards methods here."


    models = {
        'stork.css': {
            'Meta': {'object_name': 'CSS'},
            'component': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'css': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stork.Theme']"})
        },
        'stork.font': {
            'Meta': {'object_name': 'Font'},
            'component': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'font': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stork.FontStack']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stork.Theme']"})
        },
        'stork.fontstack': {
            'Meta': {'object_name': 'FontStack'},
            'eot': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'stack': ('django.db.models.fields.TextField', [], {'max_length': '255'}),
            'svg': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'ttf': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'woff': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'})
        },
        'stork.html': {
            'Meta': {'object_name': 'Html'},
            'component': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalid_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'staged_html': ('django.db.models.fields.TextField', [], {}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stork.Theme']"})
        },
        'stork.image': {
            'Meta': {'object_name': 'Image'},
            'component': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'staged_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stork.Theme']"}),
            'tiling': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'stork.swatch': {
            'Meta': {'object_name': 'Swatch'},
            'alpha': ('django.db.models.fields.DecimalField', [], {'default': "'1.0'", 'max_digits': '2', 'decimal_places': '1'}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'component': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stork.Theme']"})
        },
        'stork.theme': {
            'Meta': {'object_name': 'Theme'},
            'bundled_css': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'saved_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'screenshot': ('django.db.models.fields.files.ImageField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['stork']
