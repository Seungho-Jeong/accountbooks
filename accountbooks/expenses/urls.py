from django.urls import path

from . import views

urlpatterns = [
    path('', views.ExpenseListView.as_view()),
    path('new/', views.ExpenseNewView.as_view()),
    path('<int:expense_id>/', views.ExpenseDetailView.as_view()),
    path('deleted/', views.DeletedExpenseListView.as_view()),
    path('deleted/<int:d_expense_id>/', views.DeletedDetailView.as_view()),
]
