# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Term'
        db.create_table(u'main_term', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('quarter', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'main', ['Term'])

        # Adding unique constraint on 'Term', fields ['quarter', 'year']
        db.create_unique(u'main_term', ['quarter', 'year'])

        # Adding model 'Current'
        db.create_table(u'main_current', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Term'], null=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['Current'])

        # Adding model 'House'
        db.create_table(u'main_house', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('house', self.gf('django.db.models.fields.CharField')(unique=True, max_length=1)),
        ))
        db.send_create_signal(u'main', ['House'])

        # Adding model 'HousePoints'
        db.create_table(u'main_housepoints', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('house', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.House'])),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Term'])),
            ('resume', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('professor_interview', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('other', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'main', ['HousePoints'])

        # Adding unique constraint on 'HousePoints', fields ['house', 'term']
        db.create_unique(u'main_housepoints', ['house_id', 'term_id'])

        # Adding model 'Profile'
        db.create_table(u'main_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('position', self.gf('django.db.models.fields.CharField')(default='0', max_length=1)),
            ('house', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.House'], null=True, blank=True)),
            ('major', self.gf('django.db.models.fields.CharField')(default='0', max_length=1)),
            ('initiation_term', self.gf('django.db.models.fields.related.ForeignKey')(related_name='profile_initiation_term', to=orm['main.Term'])),
            ('graduation_term', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='profile_graduation_term', null=True, to=orm['main.Term'])),
            ('resume', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('professor_interview', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['Profile'])

        # Adding model 'Candidate'
        db.create_table(u'main_candidate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Profile'], unique=True)),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Term'])),
            ('tutoring', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutoring.Tutoring'])),
            ('bent_polish', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('candidate_quiz', self.gf('django.db.models.fields.CharField')(default='0', max_length=1)),
            ('candidate_meet_and_greet', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('signature_book', self.gf('django.db.models.fields.CharField')(default='0', max_length=1)),
            ('community_service', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('initiation_fee', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('engineering_futures', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('other', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'main', ['Candidate'])

        # Adding model 'ActiveMember'
        db.create_table(u'main_activemember', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Profile'])),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Term'])),
            ('requirement_choice', self.gf('django.db.models.fields.CharField')(default='0', max_length=1)),
            ('requirement_complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tutoring', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutoring.Tutoring'], null=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['ActiveMember'])

        # Adding unique constraint on 'ActiveMember', fields ['profile', 'term']
        db.create_unique(u'main_activemember', ['profile_id', 'term_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ActiveMember', fields ['profile', 'term']
        db.delete_unique(u'main_activemember', ['profile_id', 'term_id'])

        # Removing unique constraint on 'HousePoints', fields ['house', 'term']
        db.delete_unique(u'main_housepoints', ['house_id', 'term_id'])

        # Removing unique constraint on 'Term', fields ['quarter', 'year']
        db.delete_unique(u'main_term', ['quarter', 'year'])

        # Deleting model 'Term'
        db.delete_table(u'main_term')

        # Deleting model 'Current'
        db.delete_table(u'main_current')

        # Deleting model 'House'
        db.delete_table(u'main_house')

        # Deleting model 'HousePoints'
        db.delete_table(u'main_housepoints')

        # Deleting model 'Profile'
        db.delete_table(u'main_profile')

        # Deleting model 'Candidate'
        db.delete_table(u'main_candidate')

        # Deleting model 'ActiveMember'
        db.delete_table(u'main_activemember')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'main.activemember': {
            'Meta': {'unique_together': "(('profile', 'term'),)", 'object_name': 'ActiveMember'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Profile']"}),
            'requirement_choice': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'requirement_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"}),
            'tutoring': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutoring.Tutoring']", 'null': 'True', 'blank': 'True'})
        },
        u'main.candidate': {
            'Meta': {'ordering': "('profile__user__last_name', 'profile__user__first_name')", 'object_name': 'Candidate'},
            'bent_polish': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'candidate_meet_and_greet': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'candidate_quiz': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'community_service': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'engineering_futures': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiation_fee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'other': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Profile']", 'unique': 'True'}),
            'signature_book': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"}),
            'tutoring': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutoring.Tutoring']"})
        },
        u'main.current': {
            'Meta': {'object_name': 'Current'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']", 'null': 'True', 'blank': 'True'})
        },
        u'main.house': {
            'Meta': {'object_name': 'House'},
            'house': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'main.housepoints': {
            'Meta': {'ordering': "('-term', 'house')", 'unique_together': "(('house', 'term'),)", 'object_name': 'HousePoints'},
            'house': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.House']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'other': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'professor_interview': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resume': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"})
        },
        u'main.profile': {
            'Meta': {'ordering': "('position', 'user__last_name', 'user__first_name')", 'object_name': 'Profile'},
            'graduation_term': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'profile_graduation_term'", 'null': 'True', 'to': u"orm['main.Term']"}),
            'house': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.House']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiation_term': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'profile_initiation_term'", 'to': u"orm['main.Term']"}),
            'major': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'position': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'professor_interview': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'resume': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'main.term': {
            'Meta': {'ordering': "['-year', '-quarter']", 'unique_together': "(('quarter', 'year'),)", 'object_name': 'Term'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quarter': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        u'tutoring.class': {
            'Meta': {'object_name': 'Class'},
            'course_number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tutoring.tutoring': {
            'Meta': {'ordering': "('-term', 'profile')", 'unique_together': "(('profile', 'term'),)", 'object_name': 'Tutoring'},
            'classes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['tutoring.Class']", 'null': 'True', 'blank': 'True'}),
            'day_1': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'day_2': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'hour_1': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'hour_2': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Profile']"}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"}),
            'week_3': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutoring.Week3']"}),
            'week_4': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutoring.Week4']"}),
            'week_5': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutoring.Week5']"}),
            'week_6': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutoring.Week6']"}),
            'week_7': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutoring.Week7']"}),
            'week_8': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutoring.Week8']"}),
            'week_9': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tutoring.Week9']"})
        },
        u'tutoring.week3': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'profile')", 'object_name': 'Week3'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Profile']"}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week4': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'profile')", 'object_name': 'Week4'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Profile']"}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week5': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'profile')", 'object_name': 'Week5'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Profile']"}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week6': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'profile')", 'object_name': 'Week6'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Profile']"}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week7': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'profile')", 'object_name': 'Week7'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Profile']"}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week8': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'profile')", 'object_name': 'Week8'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Profile']"}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week9': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'profile')", 'object_name': 'Week9'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Profile']"}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['main']