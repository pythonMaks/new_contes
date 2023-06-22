from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Task, Submission
from .forms import SubmissionForm, TaskForm
from django.contrib.auth.decorators import login_required
import chardet
from django.core.paginator import Paginator
from django.db.models import Q
import docker
import shlex
import base64
import logging

@login_required
def task_create(request):
    if request.user.choice != '2':
        # Если пользователь не является преподавателем, перенаправляем на страницу с ошибкой.
        return render(request, 'core/error.html', {'message': 'Вы не имеете прав для создания задач.'})
    user_language = request.user.language or 'python'   
    form = TaskForm(user_language=user_language) 
    if request.method == 'POST':
        form = TaskForm(request.POST, user_language=user_language)
        if form.is_valid():
            form.prepod = request.user.username
            task = form.save()
            task.prepod = request.user.username
            task.save()
            return redirect('task_detail', slug=task.slug)

    return render(request, 'core/task_create.html', {'form': form})

@login_required
def task_list(request):
    
    sort = request.GET.get('sort', 'name')  # получаем параметр сортировки из GET-запроса
    if sort == 'prepod':
        tasks = Task.objects.all().order_by('prepod')  # сортируем по полю "prepod"
    else:
        tasks = Task.objects.all().order_by('name')  # сортируем по умолчанию по полю "name"
    q = request.GET.get('q')
    if q:
        tasks = tasks.filter(Q(name__icontains=q) | Q(language__icontains=q) | Q(prepod__icontains=q))

    paginator = Paginator(tasks,5)
    page_number = request.GET.get('page', 1)

    page = paginator.get_page(page_number)
    
    context = {
        'tasks': page.object_list,
        'page': page,
        'sort': sort, 
        'q': q,
        }
    return render(request, 'core/task_list.html', context)


def author_tasks_view(request, prepod):
    tasks = Task.objects.filter(prepod=prepod).order_by('-created_at')
    paginator = Paginator(tasks, 5)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    context = {
        'tasks': page,
        'page': page,
        'sort': request.GET.get('sort', ''),
        'q': request.GET.get('q', ''),
    }
    return render(request, 'core/task_list.html', context)

def task_detail(request, slug):
    task = get_object_or_404(Task, slug=slug)
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
#'kotlinc', '-script'
#'python', '-c'
#'node', '-e'

def execute_code(code, language, input_data):
    client = docker.from_env()
    logger = logging.getLogger(__name__)
    volume_name = "my_code_execution_volume_"
    try:
        volume = client.volumes.get(volume_name)
    except docker.errors.NotFound:
        volume = client.volumes.create(volume_name)

    image_name = 'pythonmaks/contest'

    if language == 'python':
        code_command = f'python3 -c {shlex.quote(f"""{code}""")} < /code/input.txt'
    elif language == 'java':
        code_command = (f'echo {shlex.quote(code)} > /code/Main.java && '
                        f'javac /code/Main.java && '
                        f'java -cp /code Main < /code/input.txt')
    elif language == 'node':
        code_command = f'node -e {shlex.quote(code)} < /code/input.txt'
    elif language == 'kotlinc':
        code_command = (f'echo {shlex.quote(code)} > /code/Main.kt && '
                        f'kotlinc /code/Main.kt -include-runtime -d /code/main.jar && '
                        f'java -jar /code/main.jar < /code/input.txt')
   '''  elif language == 'kotlinc':
        code_command = (f'echo {shlex.quote(code)} > /code/Main.kts && '
                        f'kotlinc -script /code/Main.kts < /code/input.txt')
                        
                        '''
    else:
        raise ValueError(f'Unsupported language: {language}')

    input_data_command = f'echo {shlex.quote(input_data)} > /code/input.txt; {code_command}; rm -rf /code/*'

    container = client.containers.run(image_name,
                                      volumes={volume_name: {'bind': '/code', 'mode': 'rw'}},
                                      command=['/bin/sh', '-c', input_data_command],
                                      detach=True, working_dir="/code")

    container.wait()

    stdout = container.logs(stdout=True, stderr=False)
    stderr = container.logs(stdout=False, stderr=True)

    container.remove()

    if stdout:
        if isinstance(stdout, bytes):
            stdout_encoding = chardet.detect(stdout)['encoding']
            stdout = stdout.decode(stdout_encoding).strip()

    if stderr:
        if isinstance(stderr, bytes):
            stderr_encoding = chardet.detect(stderr)['encoding']
            stderr = stderr.decode(stderr_encoding).strip()
        logger.info(stderr)

    return stdout, stderr




    
@login_required
def submission_detail(request, pk):
    logger = logging.getLogger(__name__)
    submission = get_object_or_404(Submission, pk=pk)
    task = submission.task
    submission.prepod = submission.task.prepod
    language = {'python': '-c',
                'node': '-e',
                'java': 'Main',
                'kotlinc': '-script'
    }
    
    input_data = (task.input.strip(), task.input1.strip(), task.input2.strip(),)
    expected_output = (task.output.strip(), task.output1.strip(), task.output2.strip(),)
                        
    passed = []   
    error = [] 
    output = []

    for i in range(3):
        
        if input_data[i] and expected_output[i]:   
            output_i, error_i = execute_code(submission.code, task.language, input_data[i])
            logger.info(output_i)
            try:
                if isinstance(output_i, bytes):
                    encoding = chardet.detect(output_i)['encoding']
                    output_i = output_i.decode(encoding).strip()

                output.append(output_i)
                logger.info(output)
                passed.append(output_i == expected_output[i])
            except Exception as e:
                logger.info(e)
            try:
                if isinstance(error_i, bytes):
                        encoding = chardet.detect(error_i)['encoding']
                        error_i = error_i.decode(encoding).strip()
                error.append(error_i)
            except:
                pass
                        
    if False in passed:
        passed = False
    for i in error:
        if i:
            error = i.strip()  
            break                 
    else:
        error = ''
    if error:
        submission.status = 'E'
    elif passed:
        submission.status = 'AC'
    else:
        submission.status = 'WA'
    if request.method == 'POST':
        submission.student = request.user.username
        submission.save()
        
    return render(request, 'core/submission_detail.html', {'submission': submission, 'output': ', '.join(output), 'error': error, 'passed': passed})






