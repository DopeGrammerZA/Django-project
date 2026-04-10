from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment, Submission, Choice, Learner

def extract_answers(request):
    submitted_choice_ids = []
    for key in request.POST:
        if key.startswith('choice_'):
            choice_id = int(request.POST[key])
            submitted_choice_ids.append(choice_id)
    return submitted_choice_ids

@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    learner = Learner.objects.get(user=request.user)
    enrollment = Enrollment.objects.get(learner=learner, course=course)
    
    submission = Submission.objects.create(enrollment=enrollment)
    selected_choice_ids = extract_answers(request)
    selected_choices = Choice.objects.filter(id__in=selected_choice_ids)
    submission.choices.set(selected_choices)
    submission.save()
    
    return HttpResponseRedirect(
        reverse('onlinecourse:exam_result', args=(course_id, submission.id))
    )

@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, id=submission_id)
    
    total_score = 0
    question_results = []
    
    for question in course.question_set.all():
        selected_choices = submission.choices.filter(question=question)
        selected_ids = list(selected_choices.values_list('id', flat=True))
        
        if question.is_get_score(selected_ids):
            total_score += question.grade
            question_results.append({
                'question': question,
                'correct': True,
                'selected': selected_choices,
                'score': question.grade
            })
        else:
            question_results.append({
                'question': question,
                'correct': False,
                'selected': selected_choices,
                'score': 0
            })
    
    max_score = sum(question.grade for question in course.question_set.all())
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    passed = percentage >= 70
    
    context = {
        'course': course,
        'submission': submission,
        'total_score': total_score,
        'possible': possible,  
        'max_score': max_score,
        'percentage': percentage,
        'passed': passed,
        'question_results': question_results,
    }
    
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)