# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Logo'
        db.create_table('look_logo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('look', ['Logo'])

        # Deleting field 'Skin.staged_logo'
        db.delete_column('look_skin', 'staged_logo')

        # Deleting field 'Skin.logo'
        db.delete_column('look_skin', 'logo')


    def backwards(self, orm):
        
        # Deleting model 'Logo'
        db.delete_table('look_logo')

        # Adding field 'Skin.staged_logo'
        db.add_column('look_skin', 'staged_logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True), keep_default=False)

        # Adding field 'Skin.logo'
        db.add_column('look_skin', 'logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True), keep_default=False)


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
            'plan': ('django.db.models.fields.CharField', [], {'default': "'chomp3'", 'max_length': '12'}),
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
            'name': ('django.db.models.fields.CharField', [], {'default': "'Your Restaurant Name'", 'max_length': '200'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'default': "''", 'max_length': '20'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'default': "''", 'max_length': '2'}),
            'street': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'subdomain': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'US/Eastern'", 'max_length': '100'}),
            'walkthrough_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
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
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'look.background': {
            'Meta': {'object_name': 'Background'},
            'attachment': ('django.db.models.fields.CharField', [], {'default': "'scroll'", 'max_length': '7', 'blank': 'True'}),
            'color': ('django.db.models.fields.CharField', [], {'default': "'D9D4D9'", 'max_length': '6', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'default': "'top left'", 'max_length': '20', 'blank': 'True'}),
            'repeat': ('django.db.models.fields.CharField', [], {'default': "'repeat'", 'max_length': '9', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['accounts.Site']", 'unique': 'True', 'null': 'True'}),
            'staged_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'look.fontface': {
            'Meta': {'object_name': 'FontFace'},
            'eot': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'stack': ('django.db.models.fields.TextField', [], {'max_length': '255'}),
            'svg': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'ttf': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'woff': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'look.logo': {
            'Meta': {'object_name': 'Logo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'look.skin': {
            'Meta': {'object_name': 'Skin'},
            'background': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['look.Background']"}),
            'body_color': ('django.db.models.fields.CharField', [], {'default': "'000000'", 'max_length': '6'}),
            'body_font': ('django.db.models.fields.TextField', [], {'default': '\'Frutiger, "Frutiger Linotype", Univers, Calibri, "Gill Sans", "Gill Sans MT", "Myriad Pro", Myriad, "DejaVu Sans Condensed", "Liberation Sans", "Nimbus Sans L", Tahoma, Geneva, "Helvetica Neue", Helvetica, Arial, sans-serif\'', 'max_length': '255'}),
            'button_color': ('django.db.models.fields.CharField', [], {'default': "'C76218'", 'max_length': '6'}),
            'button_text_color': ('django.db.models.fields.CharField', [], {'default': "'f7f7f7'", 'max_length': '6'}),
            'center_color': ('django.db.models.fields.CharField', [], {'default': "'f5f5f5'", 'max_length': '6'}),
            'css': ('django.db.models.fields.TextField', [], {'default': "'\\n#masthead h2 {\\n    font-size:37px;\\n    margin:23px 0;\\n}\\n\\n#menuWrap {\\n    border-top:3px solid #301613;\\n    border-bottom:4px solid #301613;\\n    margin-bottom:20px;\\n    height:34px;\\n}\\n\\n#mainWrap, #sidebarWrap {\\n    border:1px solid rgba(0,0,0,0.25);\\n    -moz-border-radius:5px;\\n    -webkit-border-radius:5px;\\n    border-radius:5px;\\n}\\n\\n#main, #sidebar {\\n    margin:12px;\\n}\\n\\n#newsitems li, #menuitems li{\\n    -moz-border-radius:5px;\\n    -webkit-border-radius:5px;\\n    border-radius:5px;\\n}\\n\\n#menu a, #menuitems li a {font-size:14px; font-weight:bold; text-transform:uppercase; text-decoration:none; }\\na.lightlink:hover {color:#fff;}\\n\\na#viewCart {margin-right:12px;}\\na.add.top {font-weight:bold; text-transform:uppercase; text-decoration:none; margin-bottom:10px;}\\n#orderForm {\\n    border:none;\\n    padding:20px;\\n    margin-bottom:15px;\\n}\\n#orderForm h3 {\\n    margin-bottom:5px;\\n}\\nform input {\\n    border: 1px grey solid;\\n}\\n\\n#orderPreview td {border-top:1px grey solid;}\\n#orderPreview td ul {margin-bottom:0;}\\n#orderPreview td.remove, #orderPreview tr.total td.remove {border-top:none;}\\na.button:hover {text-decoration:underline;}\\nform.send label {display:block;}\\n.footer {background-color:black; color:white;}\\n#masthead h2 {\\n    font-size:37px;\\n    margin:23px 0;\\n}\\n\\n#menuWrap {\\n    border-top:3px solid #301613;\\n    border-bottom:4px solid #301613;\\n    margin-bottom:20px;\\n    height:34px;\\n}\\n\\n#mainWrap, #sidebarWrap {\\n    border:1px solid rgba(0,0,0,0.25);\\n    -moz-border-radius:5px;\\n    -webkit-border-radius:5px;\\n    border-radius:5px;\\n}\\n\\n#main, #sidebar {\\n    margin:12px;\\n}\\n\\n#menuitems li{\\n    -moz-border-radius:5px;\\n    -webkit-border-radius:5px;\\n    border-radius:5px;\\n}\\n\\n#menu a, #menuitems li a {font-size:14px; font-weight:bold; text-transform:uppercase; text-decoration:none; }\\na.lightlink:hover {color:#fff;}\\n\\na#viewCart {margin-right:12px;}\\na.add.top {font-weight:bold; text-transform:uppercase; text-decoration:none; margin-bottom:10px;}\\n#orderForm {\\n    border:none;\\n    padding:20px;\\n    margin-bottom:15px;\\n}\\n#orderForm h3 {\\n    margin-bottom:5px;\\n}\\nform input {\\n    border: 1px grey solid;\\n}\\n\\n#orderPreview td {border-top:1px grey solid;}\\n#orderPreview td ul {margin-bottom:0;}\\n#orderPreview td.remove, #orderPreview tr.total td.remove {border-top:none;}\\na.button:hover {text-decoration:underline;}\\nform.send label {display:block;}\\n.footer {background-color:black; color:white;}\\n\\n#masthead h2 {\\n    font-size:37px;\\n    margin:23px 0;\\n}\\n\\n#menuWrap {\\n    border-top:3px solid #301613;\\n    border-bottom:4px solid #301613;\\n    margin-bottom:20px;\\n    height:34px;\\n}\\n\\n#mainWrap, #sidebarWrap {\\n    border:1px solid rgba(0,0,0,0.25);\\n    -moz-border-radius:5px;\\n    -webkit-border-radius:5px;\\n    border-radius:5px;\\n}\\n\\n#main, #sidebar {\\n    margin:12px;\\n}\\n\\n#menuitems li{\\n    -moz-border-radius:5px;\\n    -webkit-border-radius:5px;\\n    border-radius:5px;\\n}\\n\\n#menu a, #menuitems li a {font-size:14px; font-weight:bold; text-transform:uppercase; text-decoration:none; }\\na.lightlink:hover {color:#fff;}\\n\\na#viewCart {margin-right:12px;}\\na.add.top {font-weight:bold; text-transform:uppercase; text-decoration:none; margin-bottom:10px;}\\n#orderForm {\\n    border:none;\\n    padding:20px;\\n    margin-bottom:15px;\\n}\\n#orderForm h3 {\\n    margin-bottom:5px;\\n}\\nform input {\\n    border: 1px grey solid;\\n}\\n\\n#orderPreview td {border-top:1px grey solid;}\\n#orderPreview td ul {margin-bottom:0;}\\n#orderPreview td.remove, #orderPreview tr.total td.remove {border-top:none;}\\na.button:hover {text-decoration:underline;}\\nform.send label {display:block;}\\n.footer {background-color:black; color:white;}\\n#orderPreview tr.total td {border-top:4px solid;}\\n#submit {\\n    border:none;\\n    float:right;\\n    clear:right;\\n}\\na.add, #submit {\\n    -moz-border-radius:4px;\\n    -webkit-border-radius:4px;\\n    padding:4px 8px;\\n}\\na.button {font-size:16px; padding:4px; text-decoration:none;\\n-moz-border-radius:5px;\\n-webkit-border-radius:5px;\\n}\\n'", 'blank': 'True'}),
            'header_color': ('django.db.models.fields.CharField', [], {'default': "'301613'", 'max_length': '6'}),
            'header_font': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['look.FontFace']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'masthead_color': ('django.db.models.fields.CharField', [], {'default': "'121012'", 'max_length': '6'}),
            'masthead_font_color': ('django.db.models.fields.CharField', [], {'default': "'E3E3BE'", 'max_length': '6'}),
            'menu_color': ('django.db.models.fields.CharField', [], {'default': "'2B292B'", 'max_length': '6'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'shaded_color': ('django.db.models.fields.CharField', [], {'default': "'bfccd1'", 'max_length': '6'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['accounts.Site']", 'unique': 'True', 'null': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['look']
