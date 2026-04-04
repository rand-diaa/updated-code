from datetime import datetime, timezone as dt_timezone

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from . import forms
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Q, Max
from django.db.models.functions import Coalesce
from exam import models
from teacher import models as TMODEL
from student import models as SMODEL
from django.contrib.auth.models import User


def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')

def admin_login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if user is admin (superuser or staff)
            if user.is_superuser or user.is_staff:
                login(request, user)
                return HttpResponseRedirect('afterlogin')
            else:
                return render(request, 'exam/adminlogin.html', {'error': 'You are not authorized as an administrator.'})
        else:
            return render(request, 'exam/adminlogin.html', {'error': 'Invalid username or password.'})
    return render(request, 'exam/adminlogin.html')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    dict={
    'total_student':SMODEL.Student.objects.all().count(),
    'total_teacher':TMODEL.Teacher.objects.all().filter(status=True).count(),
    'total_course':models.Course.objects.all().count(),
    'total_question':models.Question.objects.filter(status='approved').count(),
    }
    return render(request,'exam/admin_dashboard.html',context=dict)

@login_required(login_url='adminlogin')
def admin_teacher_view(request):
    dict={
    'total_teacher':TMODEL.Teacher.objects.all().filter(status=True).count(),
    'pending_teacher':TMODEL.Teacher.objects.all().filter(status=False).count(),
    }
    return render(request,'exam/admin_teacher.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_teacher_view(request):
    teachers= TMODEL.Teacher.objects.all().filter(status=True)
    return render(request,'exam/admin_view_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
def delete_teacher_view(request,pk):
    teacher=TMODEL.Teacher.objects.get(id=pk)
    user=User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect('/admin-view-teacher')




@login_required(login_url='adminlogin')
def admin_view_pending_teacher_view(request):
    teachers= TMODEL.Teacher.objects.all().filter(status=False)
    return render(request,'exam/admin_view_pending_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
def approve_teacher_view(request,pk):
    teacher=TMODEL.Teacher.objects.get(id=pk)
    teacher.status=True
    teacher.save()
    return HttpResponseRedirect('/admin-view-pending-teacher')

@login_required(login_url='adminlogin')
def reject_teacher_view(request,pk):
    teacher=TMODEL.Teacher.objects.get(id=pk)
    user=User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect('/admin-view-pending-teacher')

@login_required(login_url='adminlogin')
@login_required(login_url='adminlogin')
def admin_student_view(request):
    dict={
    'total_student':SMODEL.Student.objects.all().count(),
    }
    return render(request,'exam/admin_student.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_student_view(request):
    students= SMODEL.Student.objects.all()
    return render(request,'exam/admin_view_student.html',{'students':students})



@login_required(login_url='adminlogin')
def delete_student_view(request,pk):
    student=SMODEL.Student.objects.get(id=pk)
    user=User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return HttpResponseRedirect('/admin-view-student')


@login_required(login_url='adminlogin')
def admin_exam_view(request):
    return render(request,'exam/admin_exam.html')


def _bundle_is_past(b, now):
    """Scheduled window ended, or manual exam stopped with at least one recorded result."""
    if b.uses_schedule() and b.is_schedule_ended(now):
        return True
    if not b.uses_schedule() and not b.is_active and b.submission_count > 0:
        return True
    return False


def _past_bundle_sort_key(b):
    if b.uses_schedule():
        return b.effective_schedule_end() or b.scheduled_start or timezone.now()
    return b.latest_submission or timezone.now()


@login_required(login_url='adminlogin')
def admin_manage_exam_view(request):
    now = timezone.now()
    bundles = list(
        models.ExamBundle.objects.filter(status='approved')
        .select_related('course')
        .annotate(
            submission_count=Count('results', distinct=True),
            latest_submission=Max('results__date'),
        )
        .order_by('course__course_name', 'title')
    )
    active_bundles = [b for b in bundles if not _bundle_is_past(b, now)]
    previous_bundles = [b for b in bundles if _bundle_is_past(b, now)]
    previous_bundles.sort(key=_past_bundle_sort_key, reverse=True)
    return render(
        request,
        'exam/admin_manage_exam.html',
        {
            'bundles': active_bundles,
            'previous_bundles': previous_bundles,
            'now': now,
        },
    )


@login_required(login_url='adminlogin')
def admin_exam_bundle_results_view(request, pk):
    bundle = get_object_or_404(
        models.ExamBundle.objects.select_related('course'),
        id=pk,
        status='approved',
    )
    results = list(
        models.Result.objects.filter(bundle=bundle)
        .select_related('student', 'student__user')
        .order_by('student__user__last_name', 'student__user__first_name')
    )
    student_rows = []
    for res in results:
        answers = list(
            models.StudentExamAnswer.objects.filter(bundle=bundle, student=res.student)
            .select_related('question')
            .order_by('question_id')
        )
        for a in answers:
            a.student_answer_display = a.question.choice_display(a.selected_choice)
            a.correct_answer_display = a.question.choice_display(a.question.answer)
        student_rows.append(
            {
                'student': res.student,
                'result': res,
                'answers': answers,
            }
        )
    return render(
        request,
        'exam/admin_exam_bundle_results.html',
        {
            'bundle': bundle,
            'student_rows': student_rows,
        },
    )


@login_required(login_url='adminlogin')
def admin_set_exam_schedule_view(request, pk):
    if request.method != 'POST':
        return HttpResponseRedirect('/admin-manage-exam')
    bundle = models.ExamBundle.objects.get(id=pk, status='approved')
    raw_dt = request.POST.get('scheduled_start', '').strip()
    raw_hours = request.POST.get('duration_hours', '').strip()
    try:
        hours = int(raw_hours)
        if hours < 1 or hours > 500:
            raise ValueError()
    except (TypeError, ValueError):
        messages.error(request, 'Duration must be a whole number of hours between 1 and 500.')
        return HttpResponseRedirect('/admin-manage-exam')
    naive = None
    for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M'):
        try:
            naive = datetime.strptime(raw_dt, fmt)
            break
        except ValueError:
            continue
    if naive is None:
        messages.error(request, 'Invalid start date/time.')
        return HttpResponseRedirect('/admin-manage-exam')
    raw_ms = request.POST.get('scheduled_start_utc_ms', '').strip()
    if raw_ms:
        try:
            ms = float(raw_ms)
            if ms < 0 or ms > 1e14:
                raise ValueError()
            scheduled = datetime.fromtimestamp(ms / 1000.0, tz=dt_timezone.utc)
        except (ValueError, TypeError, OSError):
            messages.error(request, 'Invalid start time. Try again or enable JavaScript in your browser.')
            return HttpResponseRedirect('/admin-manage-exam')
    else:
        if timezone.is_naive(naive):
            scheduled = timezone.make_aware(naive, timezone.get_current_timezone())
        else:
            scheduled = naive
    bundle.scheduled_start = scheduled
    bundle.schedule_duration_hours = hours
    bundle.is_active = False
    bundle.schedule_early_close_at = None
    bundle.save()
    messages.success(request, 'Exam schedule saved. Students can take it only during the window.')
    return HttpResponseRedirect('/admin-manage-exam')


@login_required(login_url='adminlogin')
def admin_clear_exam_schedule_view(request, pk):
    if request.method != 'POST':
        return HttpResponseRedirect('/admin-manage-exam')
    bundle = models.ExamBundle.objects.get(id=pk, status='approved')
    bundle.scheduled_start = None
    bundle.schedule_duration_hours = None
    bundle.schedule_early_close_at = None
    bundle.save()
    messages.success(request, 'Schedule cleared. You can use Start/Stop again for this exam.')
    return HttpResponseRedirect('/admin-manage-exam')


@login_required(login_url='adminlogin')
def admin_start_exam_view(request,pk):
    bundle = models.ExamBundle.objects.get(id=pk)
    if bundle.uses_schedule():
        messages.warning(request, 'This exam uses a date schedule. Clear the schedule to use manual Start/Stop.')
        return HttpResponseRedirect('/admin-manage-exam')
    bundle.is_active = True
    bundle.save()
    return HttpResponseRedirect('/admin-manage-exam')


@login_required(login_url='adminlogin')
def admin_stop_exam_view(request,pk):
    bundle = models.ExamBundle.objects.get(id=pk)
    if bundle.uses_schedule():
        messages.warning(request, 'This exam uses a date schedule. Clear the schedule to use manual Start/Stop.')
        return HttpResponseRedirect('/admin-manage-exam')
    bundle.is_active = False
    bundle.save()
    return HttpResponseRedirect('/admin-manage-exam')


@login_required(login_url='adminlogin')
def admin_end_scheduled_exam_session_view(request, pk):
    if request.method != 'POST':
        return HttpResponseRedirect('/admin-manage-exam')
    bundle = models.ExamBundle.objects.get(id=pk, status='approved')
    if not bundle.uses_schedule():
        messages.warning(request, 'This exam is not on a date schedule.')
        return HttpResponseRedirect('/admin-manage-exam')
    now = timezone.now()
    if now < bundle.scheduled_start:
        messages.warning(request, 'This exam has not started yet.')
        return HttpResponseRedirect('/admin-manage-exam')
    if bundle.is_schedule_ended(now):
        messages.info(request, 'This exam session is already closed.')
        return HttpResponseRedirect('/admin-manage-exam')
    bundle.schedule_early_close_at = now
    bundle.save()
    messages.success(
        request,
        'Exam session closed. Students can no longer start or submit until you set a new schedule.',
    )
    return HttpResponseRedirect('/admin-manage-exam')


@login_required(login_url='adminlogin')
def admin_question_view(request):
    return render(request,'exam/admin_question.html')


@login_required(login_url='adminlogin')
def admin_view_question_view(request):
    # Show approved exam bundles by subject (course) and exam name; no scattered questions list
    bundles = models.ExamBundle.objects.filter(status='approved').select_related('course').order_by('course__course_name', 'title')
    return render(request,'exam/admin_view_question.html',{'bundles':bundles})

@login_required(login_url='adminlogin')
def admin_view_pending_bundle_view(request):
    # Group pending bundles by subject (course)
    from itertools import groupby
    from operator import attrgetter
    bundles = list(models.ExamBundle.objects.filter(status='pending').select_related('course', 'submitted_by').order_by('course__course_name', 'title'))
    by_course = []
    for course_name, group in groupby(bundles, attrgetter('course')):
        by_course.append((course_name, list(group)))
    return render(request,'exam/admin_view_pending_bundle.html',{'by_course':by_course})

@login_required(login_url='adminlogin')
def admin_view_bundle_questions_view(request,pk):
    bundle = models.ExamBundle.objects.get(id=pk)
    questions = models.Question.objects.filter(bundle=bundle)
    return render(request,'exam/admin_view_bundle_questions.html',{'bundle':bundle,'questions':questions})

@login_required(login_url='adminlogin')
def approve_bundle_view(request,pk):
    bundle = models.ExamBundle.objects.get(id=pk)
    bundle.status = 'approved'
    bundle.save()
    models.Question.objects.filter(bundle=bundle).update(status='approved')
    return HttpResponseRedirect('/admin-view-pending-bundle')

@login_required(login_url='adminlogin')
def reject_bundle_view(request,pk):
    bundle = models.ExamBundle.objects.get(id=pk)
    bundle.delete()
    return HttpResponseRedirect('/admin-view-pending-bundle')

@login_required(login_url='adminlogin')
def delete_question_view(request,pk):
    question=models.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/admin-view-question')

@login_required(login_url='adminlogin')
def admin_view_student_marks_view(request):
    students= SMODEL.Student.objects.all()
    return render(request,'exam/admin_view_student_marks.html',{'students':students})

@login_required(login_url='adminlogin')
def admin_view_marks_view(request,pk):
    student = SMODEL.Student.objects.select_related('user').get(id=pk)
    courses = models.Course.objects.filter(academic_year=student.academic_year).order_by('course_name')
    response = render(
        request,
        'exam/admin_view_marks.html',
        {'courses': courses, 'student': student},
    )
    response.set_cookie('student_id', str(pk))
    return response

@login_required(login_url='adminlogin')
def admin_check_marks_view(request,pk):
    course = models.Course.objects.get(id=pk)
    student_id = request.COOKIES.get('student_id')
    if not student_id:
        messages.error(request, 'Select a student again from the marks list.')
        return redirect('admin-view-student-marks')
    student = SMODEL.Student.objects.get(id=student_id)
    if course.academic_year != student.academic_year:
        messages.warning(
            request,
            'That subject is for a different study year than this student.',
        )
        return redirect(reverse('admin-view-marks', kwargs={'pk': student.id}))

    results = models.Result.objects.filter(exam=course, student=student).select_related('bundle')
    result = results.first()
    if result and result.bundle_id:
        exam_answers = list(
            models.StudentExamAnswer.objects.filter(
                student=student,
                bundle_id=result.bundle_id,
            ).select_related('question').order_by('question_id')
        )
    else:
        exam_answers = list(
            models.StudentExamAnswer.objects.filter(
                student=student,
                question__course=course,
            ).select_related('question').order_by('question_id')
        )
    for a in exam_answers:
        a.student_answer_display = a.question.choice_display(a.selected_choice)
        a.correct_answer_display = a.question.choice_display(a.question.answer)
    return render(
        request,
        'exam/admin_check_marks.html',
        {
            'results': results,
            'course': course,
            'student': student,
            'exam_answers': exam_answers,
        },
    )
