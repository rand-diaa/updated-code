from datetime import timedelta

from django.db import models
from django.utils import timezone

from student.models import Student
from teacher.models import Teacher

ACADEMIC_YEAR_CHOICES = (
    (1, 'Year 1'),
    (2, 'Year 2'),
    (3, 'Year 3'),
    (4, 'Year 4'),
)


class Course(models.Model):
   course_name = models.CharField(max_length=50)
   academic_year = models.PositiveSmallIntegerField(choices=ACADEMIC_YEAR_CHOICES, default=1)
   is_active = models.BooleanField(default=False)
   duration_minutes = models.PositiveIntegerField(default=60)
   per_question_seconds = models.PositiveIntegerField(default=60)
   def __str__(self):
        return self.course_name

class ExamBundle(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    )
    title = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=False)
    duration_minutes = models.PositiveIntegerField(default=60)
    per_question_seconds = models.PositiveIntegerField(default=60)
    scheduled_start = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the exam window opens (use admin Manage Exams to set).',
    )
    schedule_duration_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='How many hours the exam stays open after the start time.',
    )
    schedule_early_close_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Set by admin to end the scheduled window before the natural end time.',
    )

    def uses_schedule(self):
        return (
            self.scheduled_start is not None
            and self.schedule_duration_hours is not None
            and self.schedule_duration_hours > 0
        )

    def schedule_end(self):
        if not self.uses_schedule():
            return None
        return self.scheduled_start + timedelta(hours=int(self.schedule_duration_hours))

    def effective_schedule_end(self):
        """End of the open window (shortened if admin closed the session early)."""
        end = self.schedule_end()
        if end is None:
            return None
        if self.schedule_early_close_at is not None:
            return min(end, self.schedule_early_close_at)
        return end

    def is_schedule_ended(self, when=None):
        when = when or timezone.now()
        end = self.effective_schedule_end()
        return end is not None and when >= end

    def is_effectively_active(self, when=None):
        """Whether students may open / submit this exam right now."""
        when = when or timezone.now()
        if self.status != 'approved':
            return False
        if self.uses_schedule():
            end = self.effective_schedule_end()
            return self.scheduled_start <= when < end
        return self.is_active

    @property
    def schedule_status_label(self):
        """For admin UI: upcoming / live / ended / manual."""
        when = timezone.now()
        if not self.uses_schedule():
            return 'manual'
        if when < self.scheduled_start:
            return 'upcoming'
        if self.is_schedule_ended(when):
            return 'ended'
        return 'live'

    def __str__(self):
        return f"{self.title} ({self.course.course_name})"


def get_course_ids_with_live_exam(course_id_list=None):
    """Course IDs that have at least one approved bundle open for students right now."""
    when = timezone.now()
    qs = ExamBundle.objects.filter(status='approved')
    if course_id_list is not None:
        qs = qs.filter(course_id__in=course_id_list)
    live = set()
    for b in qs.iterator():
        if b.is_effectively_active(when):
            live.add(b.course_id)
    return live


class Question(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    bundle=models.ForeignKey(ExamBundle, on_delete=models.CASCADE, null=True, blank=True)
    marks=models.PositiveIntegerField()
    question=models.CharField(max_length=600)
    QUESTION_TYPES = (
        ('mcq', 'Multiple Choice'),
        ('tf', 'True/False'),
    )
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='mcq')
    option1=models.CharField(max_length=200, blank=True)
    option2=models.CharField(max_length=200, blank=True)
    option3=models.CharField(max_length=200, blank=True)
    option4=models.CharField(max_length=200, blank=True)
    cat=(
        ('Option1','Option1'),
        ('Option2','Option2'),
        ('Option3','Option3'),
        ('Option4','Option4'),
        ('True','True'),
        ('False','False'),
    )
    answer=models.CharField(max_length=200,choices=cat)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    submitted_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)

    def choice_display(self, choice_value):
        """Human-readable text for a stored answer key (Option1, True, …)."""
        if not choice_value:
            return '(no answer)'
        if choice_value in ('True', 'False'):
            return choice_value
        opt_map = {
            'Option1': self.option1,
            'Option2': self.option2,
            'Option3': self.option3,
            'Option4': self.option4,
        }
        return opt_map.get(choice_value, choice_value)


class Result(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Course,on_delete=models.CASCADE)
    bundle = models.ForeignKey(
        ExamBundle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='results',
    )
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'exam'], name='unique_student_course_result'),
        ]


class StudentExamAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_answers')
    bundle = models.ForeignKey(ExamBundle, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    selected_choice = models.CharField(max_length=200, blank=True)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question_id']
        constraints = [
            models.UniqueConstraint(fields=['student', 'question'], name='unique_student_question_answer'),
        ]

