from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0015_student_exam_answer_result_bundle'),
    ]

    operations = [
        migrations.AddField(
            model_name='exambundle',
            name='schedule_early_close_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Set by admin to end the scheduled window before the natural end time.',
                null=True,
            ),
        ),
    ]
