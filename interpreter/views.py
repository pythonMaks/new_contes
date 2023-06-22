from django.shortcuts import render
from subprocess import Popen, PIPE
from django.contrib.auth.decorators import login_required
from .models import UserCode
import chardet
import os
import docker
import base64
import shlex



def execute_code(code, language):
    client = docker.from_env()

    volume_name = "my_code_execution_volume_"
    # Создаем том
    try:
        volume = client.volumes.get(volume_name)
    except docker.errors.NotFound:
        volume = client.volumes.create(volume_name)
    if language == 'python':
        command = 'python3 -c "{}"; rm -rf /code/*'.format(code)
    elif language == 'kotlinc':
        # Записать код в файл
        code_base64 = base64.b64encode(code.encode()).decode()

        # Собираем команду с Base64
        command = f'''
        /bin/sh -c "echo \'{code_base64}\' | base64 --decode > /code/scrip.kt && \
        kotlinc /code/scrip.kt -include-runtime -d /code/scrip.jar && \
        java -jar /code/scrip.jar && \
        rm -rf /code/*"
        '''


    elif language == 'node':       
        code_escaped = shlex.quote(code)
        command = f'node -e {code_escaped}; rm -rf /code/*'
    elif language == 'javac': 
        code_base64 = base64.b64encode(code.encode()).decode()       
        command = f'''
        /bin/sh -c "echo \'{code_base64}\' | base64 -d > /code/Main.java && \
        javac /code/Main.java && \
        java -cp /code Main && \
        rm -rf /code/*"
        '''

       
    else:
        return '', 'Invalid language'

    container = client.containers.run('pythonmaks/contest', command, volumes={volume_name: {'bind': '/code', 'mode': 'rw'}}, remove=False, detach=True,  working_dir="/code")
    exit_code = container.wait()["StatusCode"]

    # Получаем stdout и stderr
    stdout = container.logs(stdout=True, stderr=False)
    stderr = container.logs(stdout=False, stderr=True)

    # Декодирование stdout и stderr
    if stdout:
        stdout_encoding = chardet.detect(stdout)['encoding']
        stdout = stdout.decode(stdout_encoding).strip()

    if stderr:
        stderr_encoding = chardet.detect(stderr)['encoding']
        stderr = stderr.decode(stderr_encoding).strip()

 
    return stdout, stderr







@login_required
def index(request):
    if request.method == 'POST':
        code = request.POST['interpreter']
        language = request.POST['language']
        posts, error = execute_code(code, language)
        UserCode.objects.create(user=request.user, code=code, language=language)
        context = {'posts': posts, 'error': error, 'language': language}
    else:
        context = {'posts': '', 'error': ''}
    return render(request, 'interpreter/index.html', context)

