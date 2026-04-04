from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.forms import formset_factory
from django.db.models import Count, Sum, Q
from django.db.models.functions import Coalesce
from exam import models as QMODEL
from student import models as SMODEL
from exam import forms as QFORM  # For CourseForm


#for showing signup/login button for teacher
def teacherclick_view(request):
    if request.user.is_authenticated:
        return redirect('afterlogin')
    return render(request,'teacher/teacherclick.html')


def teacher_afterlogin_redirect(request):
    return redirect('/afterlogin')

def teacher_signup_view(request):
    userForm=forms.TeacherUserForm()
    teacherForm=forms.TeacherForm()
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        teacherForm=forms.TeacherForm(request.POST,request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()
            teacher=teacherForm.save(commit=False)
            teacher.user=user
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
            return HttpResponseRedirect('teacherlogin')
    return render(request,'teacher/teachersignup.html',context=mydict)



def is_teacher(user):
    if user.groups.filter(name='TEACHER').exists():
        return True
    return models.Teacher.objects.filter(user=user).exists()

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    dict={
    'total_course':QMODEL.Course.objects.all().count(),
    'total_student':SMODEL.Student.objects.all().count()
    }
    return render(request,'teacher/teacher_dashboard.html',context=dict)


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_students_view(request):
    students = SMODEL.Student.objects.all().select_related('user')
    return render(request, 'teacher/teacher_view_students.html', {'students': students})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_exam_view(request):
    return render(request,'teacher/teacher_exam.html')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_exam_view(request):
    courseForm=QFORM.CourseForm()
    if request.method=='POST':
        courseForm=QFORM.CourseForm(request.POST)
        if courseForm.is_valid():        
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-exam')
    return render(request,'teacher/teacher_add_exam.html',{'courseForm':courseForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_exam_view(request):
    courses = QMODEL.Course.objects.annotate(
        total_questions=Count('question', filter=Q(question__status='approved')),
        total_marks=Coalesce(Sum('question__marks', filter=Q(question__status='approved')), 0),
    )
    return render(request,'teacher/teacher_view_exam.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def delete_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/teacher/teacher-view-exam')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    teacher = models.Teacher.objects.get(user_id=request.user.id)
    if not teacher.status:
        return render(request,'teacher/teacher_wait_for_approval.html')
    bundle_form = forms.ExamBundleForm()
    QuestionFormSet = formset_factory(forms.TeacherQuestionForm, extra=1, can_delete=False)
    submit_error = False
    if request.method == 'POST':
        bundle_form = forms.ExamBundleForm(request.POST)
        formset = QuestionFormSet(request.POST)
        if bundle_form.is_valid() and formset.is_valid():
            bundle = bundle_form.save(commit=False)
            bundle.submitted_by = teacher
            bundle.status = 'pending'
            bundle.save()
            saved_count = 0
            for form in formset:
                if not form.cleaned_data:
                    continue
                question = form.save(commit=False)
                question.course = bundle.course
                question.bundle = bundle
                question.submitted_by = teacher
                question.status = 'pending'
                question.save()
                saved_count += 1
            if saved_count == 0:
                bundle.delete()
                return HttpResponseRedirect('/teacher/teacher-add-question?error=1')
            return HttpResponseRedirect('/teacher/teacher-add-question?submitted=1')
        return HttpResponseRedirect('/teacher/teacher-add-question?error=1')
    else:
        formset = QuestionFormSet()
    submitted = request.GET.get('submitted') == '1'
    error = request.GET.get('error') == '1'
    return render(request,'teacher/teacher_add_question.html',{'formset':formset,'bundle_form':bundle_form,'submitted':submitted,'submit_error':submit_error,'error':error})


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_profile_view(request):
    teacher = models.Teacher.objects.select_related('user').get(user_id=request.user.id)
    return render(request, 'teacher/teacher_profile.html', {'teacher': teacher})
