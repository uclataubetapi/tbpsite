from django.core.files.storage import FileSystemStorage

MAJOR_CHOICES = (
    ('0', 'Aerospace Engineering'),
    ('1', 'Bioengineering'),
    ('2', 'Chemical Engineering'),
    ('3', 'Civil Engineering'),
    ('4', 'Computer Science'),
    ('5', 'Computer Science and Engineering'),
    ('6', 'Electrical Engineering'),
    ('7', 'Materials Engineering'),
    ('8', 'Mechanical Engineering'),
)
DEPT_CHOICES = (
    ('0', 'Bioengineering'),
    ('1', 'Chemical Engineering'),
    ('2', 'Civil and Environmental Engineering'),
    ('3', 'Computer Science'),
    ('4', 'Electrical Engineering'),
    ('5', 'Mechanical and Aerospace Engineering'),
    ('6', 'Materials Science and Engineering'),
)
PROFILE_DAY_CHOICES = (
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
)
PROFILE_HOUR_CHOICES = (
    ('0', '10am-12pm'),
    ('1', '11am-1pm'),
    ('2', '12pm-2pm'),
    ('3', '1pm-3pm'),
    ('4', '2pm-4pm'),
    ('5', '3pm-5pm'),
)
TUTORING_DAY_CHOICES = (
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
)
TUTORING_HOUR_CHOICES = (
    ('0', '10am'),
    ('1', '11am'),
    ('2', '12pm'),
    ('3', '1pm'),
    ('4', '2pm'),
    ('5', '3pm'),
    ('6', '4pm'),
    #('7', '5pm'),
)
TWO_HOUR_CHOICES = (
    ('0', '10am-12pm'),
    ('1', '11am-1pm'),
    ('2', '12pm-2pm'),
    ('3', '1pm-3pm'),
    ('4', '2pm-4pm'),
    ('5', '3pm-5pm'),
    #('6', '4pm-6pm'),
)



#default save locations for files
resume_pdf_fs = FileSystemStorage(location='/media/resumes_pdf')
resume_word_fs = FileSystemStorage(location='/media/resumes_word')
professor_interview_fs = FileSystemStorage(location='/media/professor_interviews')
community_service_fs = FileSystemStorage(location='/media/community_service_proof')
