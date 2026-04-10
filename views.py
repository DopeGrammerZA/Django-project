from django.shortcuts import render, get_object_or_404, redirect
from .models import Lesson, Question, Choice, Submission, Student
from django.contrib.auth.decorators import login_required

@login_required
def submit(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    student, _ = Student.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        score = 0
        total = 0
        for question in lesson.questions.all():
            total += 1
            chosen_id = request.POST.get(f'q_{question.id}')
            if chosen_id:
                choice = Choice.objects.get(id=chosen_id)
                is_correct = choice.is_correct
                if is_correct:
                    score += 1
                Submission.objects.create(
                    student=student,
                    question=question,
                    chosen_choice=choice,
                    is_correct=is_correct
                )
        return redirect('show_exam_result', lesson_id=lesson.id)
    
    # GET request
    questions = lesson.questions.prefetch_related('choices')
    return render(request, 'exam.html', {'lesson': lesson, 'questions': questions})

@login_required
def show_exam_result(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    student = Student.objects.get(user=request.user)
    submissions = Submission.objects.filter(student=student, question__lesson=lesson)
    
    total = submissions.count()
    correct = submissions.filter(is_correct=True).count()
    score = (correct / total * 100) if total > 0 else 0
    
    return render(request, 'exam_result.html', {
        'lesson': lesson,
        'score': score,
        'correct': correct,
        'total': total,
        'message': 'Congratulations!' if score >= 70 else 'Try again.'
    })