from django.urls import path
from . import views

urlpatterns = [
    # ... your existing paths ...
    path('exam/submit/<int:lesson_id>/', views.submit, name='submit'),
    path('exam/result/<int:lesson_id>/', views.show_exam_result, name='show_exam_result'),
]