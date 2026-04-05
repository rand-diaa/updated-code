from django.shortcuts import render, redirect, reverse, get_object_or_404
from . import forms, models
from django.contrib import messages
from django.contrib.auth.models import Group
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, Q
from django.db.models.functions import Coalesce
from django.db.models import Exists, OuterRef
from exam import models as QMODEL


# for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return redirect('afterlogin')
    return render(request, 'student/studentclick.html')


def student_signup_view(request):
    userForm = forms.StudentUserForm()
    studentForm = forms.StudentForm()
    mydict = {'userForm': userForm, 'studentForm': studentForm}
    if request.method == 'POST':
        userForm = forms.StudentUserForm(request.POST)
        studentForm = forms.StudentForm(request.POST, request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()
            student = studentForm.save(commit=False)
            student.user = user
            student.save()
            if not student.student_id:
                student.student_id = f"STU{str(student.id).zfill(5)}"
                student.save(update_fields=['student_id'])
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
            return HttpResponseRedirect('studentlogin')
    return render(request, 'student/studentsignup.html', context=mydict)


def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    student = models.Student.objects.get(user_id=request.user.id)
    my_courses = QMODEL.Course.objects.filter(
        academic_year=student.academic_year
    ).order_by('course_name')
    grades_count = QMODEL.Result.objects.filter(student=student).count()
    return render(
        request,
        'student/student_dashboard.html',
        {
            'student': student,
            'total_course': my_courses.count(),
            'my_courses': my_courses,
            'grades_count': grades_count,
        },
    )


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_courses_view(request):
    student = models.Student.objects.get(user_id=request.user.id)
    has_any_exam = QMODEL.ExamBundle.objects.filter(
        course_id=OuterRef('pk'),
        status='approved',
    )
    courses = list(
        QMODEL.Course.objects.filter(
            academic_year=student.academic_year
        ).annotate(
            any_exam_exists=Exists(has_any_exam),
        ).order_by('course_name')
    )
    live_ids = QMODEL.get_course_ids_with_live_exam([c.id for c in courses])
    for c in courses:
        c.active_exam_exists = c.id in live_ids
    return render(
        request,
        'student/student_courses.html',
        {'courses': courses, 'student': student},
    )


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_course_detail_view(request, course_id):
    student = models.Student.objects.get(user_id=request.user.id)
    course = get_object_or_404(
        QMODEL.Course,
        id=course_id,
        academic_year=student.academic_year,
    )

    candidates = QMODEL.ExamBundle.objects.filter(
        course=course,
        status='approved',
    ).annotate(
        total_questions=Count('question', filter=Q(question__status='approved')),
        total_marks=Coalesce(Sum('question__marks', filter=Q(question__status='approved')), 0),
    ).order_by('title')
    active_bundles = [b for b in candidates if b.is_effectively_active()]

    # Find which bundles the student has already submitted
    submitted_bundle_ids = set(QMODEL.Result.objects.filter(
        student=student, exam=course, bundle__isnull=False
    ).values_list('bundle_id', flat=True))

    for b in active_bundles:
        b.has_submitted = b.id in submitted_bundle_ids

    any_exam_exists = QMODEL.ExamBundle.objects.filter(course=course, status='approved').exists()

    return render(
        request,
        'student/student_course_detail.html',
        {
            'course': course,
            'student': student,
            'active_bundles': active_bundles,
            'any_exam_exists': any_exam_exists,
        },
    )


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_start_exam_view(request, pk):
    student = models.Student.objects.get(user_id=request.user.id)
    bundle = QMODEL.ExamBundle.objects.get(id=pk, status='approved')
    if bundle.course.academic_year != student.academic_year:
        return redirect('student-courses')
    if not bundle.is_effectively_active():
        messages.warning(request, 'This exam is not open right now.')
        return redirect('student-course-detail', course_id=bundle.course_id)
    if QMODEL.Result.objects.filter(student=student, bundle=bundle).exists():
        messages.info(request, 'You have already submitted this course exam. Retakes are not allowed.')
        return redirect('student-grades')
    questions = QMODEL.Question.objects.filter(bundle=bundle, status='approved')
    return render(request, 'student/student_start_exam.html', {'bundle': bundle, 'questions': questions})


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_submit_exam_view(request, pk):
    if request.method != 'POST':
        return redirect('student-dashboard')

    student = models.Student.objects.get(user_id=request.user.id)
    bundle = QMODEL.ExamBundle.objects.get(id=pk, status='approved')
    if bundle.course.academic_year != student.academic_year:
        return redirect('student-courses')
    if not bundle.is_effectively_active():
        messages.warning(request, 'This exam is no longer open. Your answers were not saved.')
        return redirect('student-course-detail', course_id=bundle.course_id)

    if QMODEL.Result.objects.filter(student=student, bundle=bundle).exists():
        messages.warning(request, 'You have already submitted this course exam.')
        return redirect('student-grades')

    questions = list(QMODEL.Question.objects.filter(bundle=bundle, status='approved'))
    marks = 0
    answer_rows = []
    for q in questions:
        chosen = request.POST.get(f"q_{q.id}") or ''
        correct = bool(chosen) and chosen == q.answer
        if correct:
            marks += q.marks
        answer_rows.append(
            QMODEL.StudentExamAnswer(
                student=student,
                bundle=bundle,
                question=q,
                selected_choice=chosen,
                is_correct=correct,
            )
        )

    try:
        with transaction.atomic():
            QMODEL.Result.objects.create(
                student=student,
                exam=bundle.course,
                bundle=bundle,
                marks=marks,
            )
            QMODEL.StudentExamAnswer.objects.bulk_create(answer_rows)
    except IntegrityError:
        messages.warning(request, 'This exam was already submitted.')
        return redirect('student-grades')
    messages.success(request, 'Exam submitted successfully.')
    return redirect('student-grades')


def _result_total_possible_marks(result):
    """Sum of marks for all approved questions in the exam attempt (bundle or legacy course)."""
    if result.bundle_id:
        agg = QMODEL.Question.objects.filter(
            bundle_id=result.bundle_id,
            status='approved',
        ).aggregate(s=Sum('marks'))
    else:
        agg = QMODEL.Question.objects.filter(
            course=result.exam,
            status='approved',
        ).aggregate(s=Sum('marks'))
    total = agg['s'] or 0
    return int(total)


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_grades_view(request):
    student = models.Student.objects.get(user_id=request.user.id)
    results = list(
        QMODEL.Result.objects.filter(student=student)
        .select_related('exam', 'bundle')
        .order_by('-date')
    )
    for r in results:
        r.total_possible_marks = _result_total_possible_marks(r)
    return render(request, 'student/student_grades.html', {'results': results})


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_profile_view(request):
    student = models.Student.objects.select_related('user').get(user_id=request.user.id)
    return render(request, 'student/student_profile.html', {'student': student})
