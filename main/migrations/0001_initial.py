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

        # Adding model 'Settings'
        db.create_table(u'main_settings', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Term'], null=True, blank=True)),
            ('display_all_terms', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_tutoring', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('registration_code', self.gf('django.db.models.fields.CharField')(default='', max_length=10)),
            ('eligibility_list', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'main', ['Settings'])

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
            ('resume', self.gf('django.db.models.fields.CharField')(default='0', max_length=1)),
            ('professor_interview', self.gf('django.db.models.fields.CharField')(default='0', max_length=1)),
            ('signature_book', self.gf('django.db.models.fields.CharField')(default='0', max_length=1)),
            ('candidate_quiz', self.gf('django.db.models.fields.CharField')(default='0', max_length=1)),
            ('other', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'main', ['HousePoints'])

        # Adding unique constraint on 'HousePoints', fields ['house', 'term']
        db.create_unique(u'main_housepoints', ['house_id', 'term_id'])

        # Adding model 'Profile'
        db.create_table(u'main_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('middle_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(default='M', max_length=1)),
            ('birthday', self.gf('django.db.models.fields.DateField')(null=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('position', self.gf('django.db.models.fields.CharField')(default='0', max_length=1)),
            ('house', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.House'], null=True, blank=True)),
            ('major', self.gf('django.db.models.fields.CharField')(default='0', max_length=1)),
            ('initiation_term', self.gf('django.db.models.fields.related.ForeignKey')(related_name='profile_initiation_term', to=orm['main.Term'])),
            ('graduation_term', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='profile_graduation_term', null=True, to=orm['main.Term'])),
            ('resume_pdf', self.gf('django.db.models.fields.files.FileField')(default=None, max_length=100, null=True, blank=True)),
            ('resume_word', self.gf('django.db.models.fields.files.FileField')(default=None, max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['Profile'])

        # Adding M2M table for field classes on 'Profile'
        m2m_table_name = db.shorten_name(u'main_profile_classes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profile', models.ForeignKey(orm[u'main.profile'], null=False)),
            ('class', models.ForeignKey(orm[u'tutoring.class'], null=False))
        ))
        db.create_unique(m2m_table_name, ['profile_id', 'class_id'])

        # Adding model 'Candidate'
        db.create_table(u'main_candidate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['main.Profile'], unique=True)),
            ('shirt_size', self.gf('django.db.models.fields.CharField')(default='M', max_length=2)),
            ('tutoring', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['tutoring.Tutoring'], unique=True, null=True, blank=True)),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Term'])),
            ('completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('bent_polish', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('candidate_quiz', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('candidate_meet_and_greet', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('signature_book', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('community_service_proof', self.gf('django.db.models.fields.files.FileField')(default=None, max_length=100, null=True, blank=True)),
            ('community_service', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('initiation_fee', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('engineering_futures', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('professor_interview', self.gf('django.db.models.fields.files.FileField')(default=None, max_length=100, null=True, blank=True)),
            ('other', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'main', ['Candidate'])

        # Adding model 'ActiveMember'
        db.create_table(u'main_activemember', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Profile'])),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Term'])),
            ('completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('requirement_choice', self.gf('django.db.models.fields.CharField')(default='0', max_length=1)),
            ('requirement_complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tutoring', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['tutoring.Tutoring'], unique=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['ActiveMember'])

        # Adding unique constraint on 'ActiveMember', fields ['profile', 'term']
        db.create_unique(u'main_activemember', ['profile_id', 'term_id'])

        # Adding model 'Officer'
        db.create_table(u'main_officer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('position', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('rank', self.gf('django.db.models.fields.IntegerField')()),
            ('mail_alias', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'main', ['Officer'])

        # Adding M2M table for field profile on 'Officer'
        m2m_table_name = db.shorten_name(u'main_officer_profile')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('officer', models.ForeignKey(orm[u'main.officer'], null=False)),
            ('profile', models.ForeignKey(orm[u'main.profile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['officer_id', 'profile_id'])

        # Adding model 'Faculty'
        db.create_table(u'main_faculty', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('dept', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('chapter', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('graduation', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal(u'main', ['Faculty'])


    def backwards(self, orm):
        # Removing unique constraint on 'ActiveMember', fields ['profile', 'term']
        db.delete_unique(u'main_activemember', ['profile_id', 'term_id'])

        # Removing unique constraint on 'HousePoints', fields ['house', 'term']
        db.delete_unique(u'main_housepoints', ['house_id', 'term_id'])

        # Removing unique constraint on 'Term', fields ['quarter', 'year']
        db.delete_unique(u'main_term', ['quarter', 'year'])

        # Deleting model 'Term'
        db.delete_table(u'main_term')

        # Deleting model 'Settings'
        db.delete_table(u'main_settings')

        # Deleting model 'House'
        db.delete_table(u'main_house')

        # Deleting model 'HousePoints'
        db.delete_table(u'main_housepoints')

        # Deleting model 'Profile'
        db.delete_table(u'main_profile')

        # Removing M2M table for field classes on 'Profile'
        db.delete_table(db.shorten_name(u'main_profile_classes'))

        # Deleting model 'Candidate'
        db.delete_table(u'main_candidate')

        # Deleting model 'ActiveMember'
        db.delete_table(u'main_activemember')

        # Deleting model 'Officer'
        db.delete_table(u'main_officer')

        # Removing M2M table for field profile on 'Officer'
        db.delete_table(db.shorten_name(u'main_officer_profile'))

        # Deleting model 'Faculty'
        db.delete_table(u'main_faculty')


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
            'Meta': {'ordering': "('term',)", 'unique_together': "(('profile', 'term'),)", 'object_name': 'ActiveMember'},
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Profile']"}),
            'requirement_choice': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'requirement_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"}),
            'tutoring': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['tutoring.Tutoring']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'main.candidate': {
            'Meta': {'ordering': "('profile__user__last_name', 'profile__user__first_name')", 'object_name': 'Candidate'},
            'bent_polish': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'candidate_meet_and_greet': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'candidate_quiz': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'community_service': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'community_service_proof': ('django.db.models.fields.files.FileField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'engineering_futures': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiation_fee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'other': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'professor_interview': ('django.db.models.fields.files.FileField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['main.Profile']", 'unique': 'True'}),
            'shirt_size': ('django.db.models.fields.CharField', [], {'default': "'M'", 'max_length': '2'}),
            'signature_book': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"}),
            'tutoring': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['tutoring.Tutoring']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'main.faculty': {
            'Meta': {'object_name': 'Faculty'},
            'chapter': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'dept': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'graduation': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'main.house': {
            'Meta': {'object_name': 'House'},
            'house': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'main.housepoints': {
            'Meta': {'ordering': "('-term', 'house')", 'unique_together': "(('house', 'term'),)", 'object_name': 'HousePoints'},
            'candidate_quiz': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'house': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.House']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'other': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'professor_interview': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'resume': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'signature_book': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"})
        },
        u'main.officer': {
            'Meta': {'ordering': "('rank',)", 'object_name': 'Officer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail_alias': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'profile': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['main.Profile']", 'symmetrical': 'False'}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
        },
        u'main.profile': {
            'Meta': {'ordering': "('position', 'user__last_name', 'user__first_name')", 'object_name': 'Profile'},
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'classes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['tutoring.Class']", 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'M'", 'max_length': '1'}),
            'graduation_term': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'profile_graduation_term'", 'null': 'True', 'to': u"orm['main.Term']"}),
            'house': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.House']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiation_term': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'profile_initiation_term'", 'to': u"orm['main.Term']"}),
            'major': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'position': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'resume_pdf': ('django.db.models.fields.files.FileField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'resume_word': ('django.db.models.fields.files.FileField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'main.settings': {
            'Meta': {'object_name': 'Settings'},
            'display_all_terms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_tutoring': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'eligibility_list': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']", 'null': 'True', 'blank': 'True'})
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
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tutoring.tutoring': {
            'Meta': {'ordering': "('-term', 'profile')", 'unique_together': "(('profile', 'term'),)", 'object_name': 'Tutoring'},
            'best_day': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'best_hour': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'day_1': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'day_2': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'hour_1': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'hour_2': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Profile']"}),
            'second_best_day': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'second_best_hour': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '1'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"}),
            'third_best_day': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'third_best_hour': ('django.db.models.fields.CharField', [], {'default': "'4'", 'max_length': '1'}),
            'week_3': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['tutoring.Week3']", 'unique': 'True'}),
            'week_4': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['tutoring.Week4']", 'unique': 'True'}),
            'week_5': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['tutoring.Week5']", 'unique': 'True'}),
            'week_6': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['tutoring.Week6']", 'unique': 'True'}),
            'week_7': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['tutoring.Week7']", 'unique': 'True'}),
            'week_8': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['tutoring.Week8']", 'unique': 'True'}),
            'week_9': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['tutoring.Week9']", 'unique': 'True'})
        },
        u'tutoring.week3': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'tutoring__profile')", 'object_name': 'Week3'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week4': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'tutoring__profile')", 'object_name': 'Week4'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week5': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'tutoring__profile')", 'object_name': 'Week5'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week6': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'tutoring__profile')", 'object_name': 'Week6'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week7': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'tutoring__profile')", 'object_name': 'Week7'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week8': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'tutoring__profile')", 'object_name': 'Week8'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week9': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'tutoring__profile')", 'object_name': 'Week9'},
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['main']