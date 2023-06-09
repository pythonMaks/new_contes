from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Task, Submission
from .forms import SubmissionForm, TaskForm
from django.contrib.auth.decorators import login_required


@login_required
def task_create(request):
    if request.user.choice != '2':
        # Если пользователь не является преподавателем, перенаправляем на страницу с ошибкой.
        return render(request, 'core/error.html', {'message': 'Вы не имеете прав для создания задач.'})
    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            return redirect('task_detail', pk=task.pk)

    return render(request, 'core/task_create.html', {'form': form})


def task_list(request):
    tasks = Task.objects.all()
    print(tasks)
    return render(request, 'core/task_list.html', {'tasks': tasks})


def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = SubmissionForm()

    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            submission = Submission.objects.create(
                task=task,
                code=code,
            )
            return redirect('submission_detail', pk=submission.pk)
    
    return render(request, 'core/task_detail.html', {'task': task, 'form': form})


@login_required
def submission_detail(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    task = submission.task

    if request.user.choice != '1':
        # Если пользователь не является студентом, перенаправляем на страницу с ошибкой.
        return render(request, 'core/error.html', {'message': 'Вы не имеете прав для выполнения задач.'})

    # Оставшаяся часть кода.


    # # Проверяем, что задание имеет данные ввода и вывода
    # if not task.input or not task.output:
    #     raise Http404

    # Получаем данные ввода из задания
    input_data = task.input.strip()

    # Выполняем код студента в отдельном процессе с использованием входных данных
    # и получаем результат выполнения
    from subprocess import Popen, PIPE
    process = Popen(['python', '-c', submission.code], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, error = process.communicate(input=input_data.encode())
    output = output.decode().strip()
    error = error.decode().strip()

    # Сравниваем полученный результат с ожидаемым результатом из задания
    expected_output = task.output.strip()
    passed = (output == expected_output)

    return render(request, 'core/submission_detail.html', {'submission': submission, 'output': output, 'error': error, 'passed': passed})




