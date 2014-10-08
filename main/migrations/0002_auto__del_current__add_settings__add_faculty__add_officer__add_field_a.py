# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Current'
        db.delete_table(u'main_current')

        # Adding model 'Settings'
        db.create_table(u'main_settings', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current', null=True, to=orm['main.Term'])),
            ('signup_term', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='signup', null=True, to=orm['main.Term'])),
            ('display_all_terms', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_tutoring', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('registration_code', self.gf('django.db.models.fields.CharField')(default='', max_length=10)),
            ('eligibility_list', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'main', ['Settings'])

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

        # Adding field 'ActiveMember.completed'
        db.add_column(u'main_activemember', 'completed',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'ActiveMember.other'
        db.add_column(u'main_activemember', 'other',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


        # Changing field 'ActiveMember.tutoring'
        db.alter_column(u'main_activemember', 'tutoring_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['tutoring.Tutoring'], unique=True, null=True))
        # Adding unique constraint on 'ActiveMember', fields ['tutoring']
        db.create_unique(u'main_activemember', ['tutoring_id'])

        # Deleting field 'Profile.professor_interview'
        db.delete_column(u'main_profile', 'professor_interview')

        # Deleting field 'Profile.resume'
        db.delete_column(u'main_profile', 'resume')

        # Adding field 'Profile.middle_name'
        db.add_column(u'main_profile', 'middle_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30, blank=True),
                      keep_default=False)

        # Adding field 'Profile.nickname'
        db.add_column(u'main_profile', 'nickname',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30, blank=True),
                      keep_default=False)

        # Adding field 'Profile.gender'
        db.add_column(u'main_profile', 'gender',
                      self.gf('django.db.models.fields.CharField')(default='M', max_length=1),
                      keep_default=False)

        # Adding field 'Profile.birthday'
        db.add_column(u'main_profile', 'birthday',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)

        # Adding field 'Profile.phone_number'
        db.add_column(u'main_profile', 'phone_number',
                      self.gf('django.db.models.fields.CharField')(default=0, max_length=25),
                      keep_default=False)

        # Adding field 'Profile.resume_pdf'
        db.add_column(u'main_profile', 'resume_pdf',
                      self.gf('django.db.models.fields.files.FileField')(default=None, max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Profile.resume_word'
        db.add_column(u'main_profile', 'resume_word',
                      self.gf('django.db.models.fields.files.FileField')(default=None, max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding M2M table for field classes on 'Profile'
        m2m_table_name = db.shorten_name(u'main_profile_classes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profile', models.ForeignKey(orm[u'main.profile'], null=False)),
            ('class', models.ForeignKey(orm[u'tutoring.class'], null=False))
        ))
        db.create_unique(m2m_table_name, ['profile_id', 'class_id'])


        # Changing field 'Profile.user'
        db.alter_column(u'main_profile', 'user_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True))
        # Deleting field 'HousePoints.resume'
        db.delete_column(u'main_housepoints', 'resume')

        # Deleting field 'HousePoints.professor_interview'
        db.delete_column(u'main_housepoints', 'professor_interview')

        # Adding field 'HousePoints.professor_interview_and_resume'
        db.add_column(u'main_housepoints', 'professor_interview_and_resume',
                      self.gf('django.db.models.fields.CharField')(default='4', max_length=1),
                      keep_default=False)

        # Adding field 'Term.start_date'
        db.add_column(u'main_term', 'start_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Term.due_date'
        db.add_column(u'main_term', 'due_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Candidate.completed'
        db.add_column(u'main_candidate', 'completed',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Candidate.shirt_size'
        db.add_column(u'main_candidate', 'shirt_size',
                      self.gf('django.db.models.fields.CharField')(default='M', max_length=2),
                      keep_default=False)

        # Adding field 'Candidate.community_service_proof'
        db.add_column(u'main_candidate', 'community_service_proof',
                      self.gf('django.db.models.fields.files.FileField')(default=None, max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Candidate.professor_interview'
        db.add_column(u'main_candidate', 'professor_interview',
                      self.gf('django.db.models.fields.files.FileField')(default=None, max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Candidate.tbp_event'
        db.add_column(u'main_candidate', 'tbp_event',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Candidate.professor_interview_on_time'
        db.add_column(u'main_candidate', 'professor_interview_on_time',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Candidate.resume_on_time'
        db.add_column(u'main_candidate', 'resume_on_time',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Candidate.quiz_first_try'
        db.add_column(u'main_candidate', 'quiz_first_try',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # Changing field 'Candidate.profile'
        db.alter_column(u'main_candidate', 'profile_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['main.Profile'], unique=True))

        # Changing field 'Candidate.signature_book'
        db.alter_column(u'main_candidate', 'signature_book', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Candidate.candidate_quiz'
        db.alter_column(u'main_candidate', 'candidate_quiz', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Candidate.tutoring'
        db.alter_column(u'main_candidate', 'tutoring_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['tutoring.Tutoring'], unique=True, null=True))
        # Adding unique constraint on 'Candidate', fields ['tutoring']
        db.create_unique(u'main_candidate', ['tutoring_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Candidate', fields ['tutoring']
        db.delete_unique(u'main_candidate', ['tutoring_id'])

        # Removing unique constraint on 'ActiveMember', fields ['tutoring']
        db.delete_unique(u'main_activemember', ['tutoring_id'])

        # Adding model 'Current'
        db.create_table(u'main_current', (
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Term'], null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'main', ['Current'])

        # Deleting model 'Settings'
        db.delete_table(u'main_settings')

        # Deleting model 'Faculty'
        db.delete_table(u'main_faculty')

        # Deleting model 'Officer'
        db.delete_table(u'main_officer')

        # Removing M2M table for field profile on 'Officer'
        db.delete_table(db.shorten_name(u'main_officer_profile'))

        # Deleting field 'ActiveMember.completed'
        db.delete_column(u'main_activemember', 'completed')

        # Deleting field 'ActiveMember.other'
        db.delete_column(u'main_activemember', 'other')


        # Changing field 'ActiveMember.tutoring'
        db.alter_column(u'main_activemember', 'tutoring_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutoring.Tutoring'], null=True))
        # Adding field 'Profile.professor_interview'
        db.add_column(u'main_profile', 'professor_interview',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Profile.resume'
        db.add_column(u'main_profile', 'resume',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Profile.middle_name'
        db.delete_column(u'main_profile', 'middle_name')

        # Deleting field 'Profile.nickname'
        db.delete_column(u'main_profile', 'nickname')

        # Deleting field 'Profile.gender'
        db.delete_column(u'main_profile', 'gender')

        # Deleting field 'Profile.birthday'
        db.delete_column(u'main_profile', 'birthday')

        # Deleting field 'Profile.phone_number'
        db.delete_column(u'main_profile', 'phone_number')

        # Deleting field 'Profile.resume_pdf'
        db.delete_column(u'main_profile', 'resume_pdf')

        # Deleting field 'Profile.resume_word'
        db.delete_column(u'main_profile', 'resume_word')

        # Removing M2M table for field classes on 'Profile'
        db.delete_table(db.shorten_name(u'main_profile_classes'))


        # Changing field 'Profile.user'
        db.alter_column(u'main_profile', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True))
        # Adding field 'HousePoints.resume'
        db.add_column(u'main_housepoints', 'resume',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'HousePoints.professor_interview'
        db.add_column(u'main_housepoints', 'professor_interview',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Deleting field 'HousePoints.professor_interview_and_resume'
        db.delete_column(u'main_housepoints', 'professor_interview_and_resume')

        # Deleting field 'Term.start_date'
        db.delete_column(u'main_term', 'start_date')

        # Deleting field 'Term.due_date'
        db.delete_column(u'main_term', 'due_date')

        # Deleting field 'Candidate.completed'
        db.delete_column(u'main_candidate', 'completed')

        # Deleting field 'Candidate.shirt_size'
        db.delete_column(u'main_candidate', 'shirt_size')

        # Deleting field 'Candidate.community_service_proof'
        db.delete_column(u'main_candidate', 'community_service_proof')

        # Deleting field 'Candidate.professor_interview'
        db.delete_column(u'main_candidate', 'professor_interview')

        # Deleting field 'Candidate.tbp_event'
        db.delete_column(u'main_candidate', 'tbp_event')

        # Deleting field 'Candidate.professor_interview_on_time'
        db.delete_column(u'main_candidate', 'professor_interview_on_time')

        # Deleting field 'Candidate.resume_on_time'
        db.delete_column(u'main_candidate', 'resume_on_time')

        # Deleting field 'Candidate.quiz_first_try'
        db.delete_column(u'main_candidate', 'quiz_first_try')


        # Changing field 'Candidate.profile'
        db.alter_column(u'main_candidate', 'profile_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Profile'], unique=True))

        # Changing field 'Candidate.signature_book'
        db.alter_column(u'main_candidate', 'signature_book', self.gf('django.db.models.fields.CharField')(max_length=1))

        # Changing field 'Candidate.candidate_quiz'
        db.alter_column(u'main_candidate', 'candidate_quiz', self.gf('django.db.models.fields.CharField')(max_length=1))

        # User chose to not deal with backwards NULL issues for 'Candidate.tutoring'
        raise RuntimeError("Cannot reverse this migration. 'Candidate.tutoring' and its values cannot be restored.")

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
            'Meta': {'ordering': "('term', 'profile__user__last_name', 'profile__user__first_name')", 'unique_together': "(('profile', 'term'),)", 'object_name': 'ActiveMember'},
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'other': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Profile']"}),
            'requirement_choice': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'requirement_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.Term']"}),
            'tutoring': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['tutoring.Tutoring']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'main.candidate': {
            'Meta': {'ordering': "('term', 'profile__user__last_name', 'profile__user__first_name')", 'object_name': 'Candidate'},
            'bent_polish': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'candidate_meet_and_greet': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'candidate_quiz': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'community_service': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'community_service_proof': ('django.db.models.fields.files.FileField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'engineering_futures': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiation_fee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'other': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'professor_interview': ('django.db.models.fields.files.FileField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'professor_interview_on_time': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['main.Profile']", 'unique': 'True'}),
            'quiz_first_try': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'resume_on_time': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shirt_size': ('django.db.models.fields.CharField', [], {'default': "'M'", 'max_length': '2'}),
            'signature_book': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tbp_event': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'house': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.House']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'other': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'professor_interview_and_resume': ('django.db.models.fields.CharField', [], {'default': "'4'", 'max_length': '1'}),
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
            'signup_term': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'signup'", 'null': 'True', 'to': u"orm['main.Term']"}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current'", 'null': 'True', 'to': u"orm['main.Term']"})
        },
        u'main.term': {
            'Meta': {'ordering': "['-year', '-quarter']", 'unique_together': "(('quarter', 'year'),)", 'object_name': 'Term'},
            'due_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quarter': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        u'tutoring.class': {
            'Meta': {'ordering': "('department', 'course_number')", 'object_name': 'Class'},
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
            'frozen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hour_1': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'hour_2': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_tutoring': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 4, 8, 0, 0)'}),
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
            'classes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['tutoring.Class']", 'null': 'True', 'blank': 'True'}),
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'no_makeup': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week4': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'tutoring__profile')", 'object_name': 'Week4'},
            'classes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['tutoring.Class']", 'null': 'True', 'blank': 'True'}),
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'no_makeup': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week5': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'tutoring__profile')", 'object_name': 'Week5'},
            'classes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['tutoring.Class']", 'null': 'True', 'blank': 'True'}),
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'no_makeup': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week6': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'tutoring__profile')", 'object_name': 'Week6'},
            'classes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['tutoring.Class']", 'null': 'True', 'blank': 'True'}),
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'no_makeup': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week7': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'tutoring__profile')", 'object_name': 'Week7'},
            'classes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['tutoring.Class']", 'null': 'True', 'blank': 'True'}),
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'no_makeup': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week8': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'tutoring__profile')", 'object_name': 'Week8'},
            'classes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['tutoring.Class']", 'null': 'True', 'blank': 'True'}),
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'no_makeup': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'tutoring.week9': {
            'Meta': {'ordering': "('tutoring__day_1', 'tutoring__hour_1', 'tutoring__day_2', 'tutoring__hour_2', 'tutoring__profile')", 'object_name': 'Week9'},
            'classes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['tutoring.Class']", 'null': 'True', 'blank': 'True'}),
            'hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'no_makeup': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tutees': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['main']