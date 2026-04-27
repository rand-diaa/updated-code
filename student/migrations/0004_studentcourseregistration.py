from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0011_exambundle_question_bundle'),
        ('student', '0003_student_student_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentCourseRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registered_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_registrations', to='exam.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_registrations', to='student.student')),
            ],
            options={
                'ordering': ['-registered_at'],
                'unique_together': {('student', 'course')},
            },
        ),
    ]
