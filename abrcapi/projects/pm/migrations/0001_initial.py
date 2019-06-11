# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IssueType'
        db.create_table(u'issuetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('icon', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
        ))
        db.send_create_signal('pm', ['IssueType'])

        # Adding model 'Resolution'
        db.create_table(u'resolution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('pm', ['Resolution'])

        # Adding model 'Priority'
        db.create_table(u'priority', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('icon', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('color', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('pm', ['Priority'])

        # Adding model 'Status'
        db.create_table(u'status', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('pm', ['Status'])

        # Adding model 'BuiltInEmailConfig'
        db.create_table(u'emailconfigs', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('protocol', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('port', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('pm', ['BuiltInEmailConfig'])

        # Adding model 'EmailServer'
        db.create_table(u'emailserver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('timeout', self.gf('django.db.models.fields.DecimalField')(default=300, max_digits=19, decimal_places=0)),
            ('type', self.gf('django.db.models.fields.CharField')(default='INCOMING', max_length=8)),
            ('email', self.gf('django.db.models.fields.EmailField')(default='help@abrc.osu.edu', max_length=75)),
            ('hostname', self.gf('django.db.models.fields.CharField')(default='imap.gmail.com', max_length=200)),
            ('protocol', self.gf('django.db.models.fields.CharField')(default='IMAP', max_length=4)),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=993)),
            ('username', self.gf('django.db.models.fields.CharField')(default='help@abrc.osu.edu', max_length=100)),
            ('password', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
        ))
        db.send_create_signal('pm', ['EmailServer'])

        # Adding model 'InvitedUsers'
        db.create_table(u'invitedusers', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('accepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('pm', ['InvitedUsers'])

        # Adding model 'Item'
        db.create_table('pm_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('pm', ['Item'])

        # Adding model 'Project'
        db.create_table(u'project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=6, unique=True, null=True)),
            ('primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lead', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('emailed', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('pm', ['Project'])

        # Adding model 'Issue'
        db.create_table(u'issue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='issues', to=orm['pm.Project'])),
            ('reporter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reporter', null=True, to=orm['auth.User'])),
            ('priority', self.gf('django.db.models.fields.related.ForeignKey')(default=4, to=orm['pm.Priority'], null=True)),
            ('resolution', self.gf('django.db.models.fields.related.ForeignKey')(default=6, to=orm['pm.Resolution'], null=True)),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['pm.Status'], null=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['pm.IssueType'], null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('emailed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('pm', ['Issue'])

        # Adding M2M table for field assignees on 'Issue'
        db.create_table(u'issue_assignees', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('issue', models.ForeignKey(orm['pm.issue'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(u'issue_assignees', ['issue_id', 'user_id'])

        # Adding M2M table for field watchers on 'Issue'
        db.create_table(u'issue_watchers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('issue', models.ForeignKey(orm['pm.issue'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(u'issue_watchers', ['issue_id', 'user_id'])

        # Adding model 'Comment'
        db.create_table(u'comment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comments', to=orm['pm.Issue'])),
            ('commenter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comments', to=orm['auth.User'])),
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('emailed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('only_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('pm', ['Comment'])

        # Adding model 'Event'
        db.create_table(u'event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('emailed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('pm', ['Event'])

        # Adding M2M table for field attendees on 'Event'
        db.create_table(u'event_attendees', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm['pm.event'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(u'event_attendees', ['event_id', 'user_id'])

        # Adding model 'IssueUpdate'
        db.create_table(u'issueupdate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pm.Issue'])),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('acting_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('field', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('oldvalue', self.gf('django.db.models.fields.IntegerField')()),
            ('oldstring', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('newvalue', self.gf('django.db.models.fields.IntegerField')()),
            ('newstring', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('emailed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('pm', ['IssueUpdate'])

        # Adding model 'MailHandlers'
        db.create_table(u'mailhandler', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pm.Project'])),
            ('issuetype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pm.IssueType'])),
            ('reporter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('createusers', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('notifyusers', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('pm', ['MailHandlers'])

        # Adding model 'SearchWord'
        db.create_table(u'searchword', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pm.Project'])),
            ('word', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('pm', ['SearchWord'])


    def backwards(self, orm):
        # Deleting model 'IssueType'
        db.delete_table(u'issuetype')

        # Deleting model 'Resolution'
        db.delete_table(u'resolution')

        # Deleting model 'Priority'
        db.delete_table(u'priority')

        # Deleting model 'Status'
        db.delete_table(u'status')

        # Deleting model 'BuiltInEmailConfig'
        db.delete_table(u'emailconfigs')

        # Deleting model 'EmailServer'
        db.delete_table(u'emailserver')

        # Deleting model 'InvitedUsers'
        db.delete_table(u'invitedusers')

        # Deleting model 'Item'
        db.delete_table('pm_item')

        # Deleting model 'Project'
        db.delete_table(u'project')

        # Deleting model 'Issue'
        db.delete_table(u'issue')

        # Removing M2M table for field assignees on 'Issue'
        db.delete_table('issue_assignees')

        # Removing M2M table for field watchers on 'Issue'
        db.delete_table('issue_watchers')

        # Deleting model 'Comment'
        db.delete_table(u'comment')

        # Deleting model 'Event'
        db.delete_table(u'event')

        # Removing M2M table for field attendees on 'Event'
        db.delete_table('event_attendees')

        # Deleting model 'IssueUpdate'
        db.delete_table(u'issueupdate')

        # Deleting model 'MailHandlers'
        db.delete_table(u'mailhandler')

        # Deleting model 'SearchWord'
        db.delete_table(u'searchword')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'pm.builtinemailconfig': {
            'Meta': {'object_name': 'BuiltInEmailConfig', 'db_table': "u'emailconfigs'"},
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'pm.comment': {
            'Meta': {'ordering': "['-date']", 'object_name': 'Comment', 'db_table': "u'comment'"},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'commenter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['auth.User']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'emailed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['pm.Issue']"}),
            'only_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        },
        'pm.emailserver': {
            'Meta': {'object_name': 'EmailServer', 'db_table': "u'emailserver'"},
            'description': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "'help@abrc.osu.edu'", 'max_length': '75'}),
            'hostname': ('django.db.models.fields.CharField', [], {'default': "'imap.gmail.com'", 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'password': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '993'}),
            'protocol': ('django.db.models.fields.CharField', [], {'default': "'IMAP'", 'max_length': '4'}),
            'timeout': ('django.db.models.fields.DecimalField', [], {'default': '300', 'max_digits': '19', 'decimal_places': '0'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'INCOMING'", 'max_length': '8'}),
            'username': ('django.db.models.fields.CharField', [], {'default': "'help@abrc.osu.edu'", 'max_length': '100'})
        },
        'pm.event': {
            'Meta': {'object_name': 'Event', 'db_table': "u'event'"},
            'attendees': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'emailed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        },
        'pm.invitedusers': {
            'Meta': {'object_name': 'InvitedUsers', 'db_table': "u'invitedusers'"},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'pm.issue': {
            'Meta': {'object_name': 'Issue', 'db_table': "u'issue'"},
            'assignees': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'assignees'", 'null': 'True', 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'emailed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'priority': ('django.db.models.fields.related.ForeignKey', [], {'default': '4', 'to': "orm['pm.Priority']", 'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issues'", 'to': "orm['pm.Project']"}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'reporter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reporter'", 'null': 'True', 'to': "orm['auth.User']"}),
            'resolution': ('django.db.models.fields.related.ForeignKey', [], {'default': '6', 'to': "orm['pm.Resolution']", 'null': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['pm.Status']", 'null': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['pm.IssueType']", 'null': 'True'}),
            'watchers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'watchers'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'pm.issuetype': {
            'Meta': {'object_name': 'IssueType', 'db_table': "u'issuetype'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'pm.issueupdate': {
            'Meta': {'object_name': 'IssueUpdate', 'db_table': "u'issueupdate'"},
            'acting_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'emailed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'field': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pm.Issue']"}),
            'newstring': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'newvalue': ('django.db.models.fields.IntegerField', [], {}),
            'oldstring': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'oldvalue': ('django.db.models.fields.IntegerField', [], {}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        },
        'pm.item': {
            'Meta': {'object_name': 'Item'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        'pm.mailhandlers': {
            'Meta': {'object_name': 'MailHandlers', 'db_table': "u'mailhandler'"},
            'createusers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuetype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pm.IssueType']"}),
            'notifyusers': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pm.Project']"}),
            'reporter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'pm.priority': {
            'Meta': {'object_name': 'Priority', 'db_table': "u'priority'"},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'pm.project': {
            'Meta': {'object_name': 'Project', 'db_table': "u'project'"},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'emailed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '6', 'unique': 'True', 'null': 'True'}),
            'lead': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        },
        'pm.resolution': {
            'Meta': {'object_name': 'Resolution', 'db_table': "u'resolution'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'pm.searchword': {
            'Meta': {'object_name': 'SearchWord', 'db_table': "u'searchword'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pm.Project']"}),
            'word': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'pm.status': {
            'Meta': {'object_name': 'Status', 'db_table': "u'status'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['pm']