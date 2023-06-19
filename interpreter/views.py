from django.shortcuts import render
from subprocess import Popen, PIPE
from django.contrib.auth.decorators import login_required
import chardet
import os

import docker

def execute_code(code, language):
    client = docker.from_env()

    # Используем существующий контейнер, если он существует. Если нет, создаем новый.
    try:
        container = client.containers.get('your_container_name')
    except docker.errors.NotFound:
        container = client.containers.run('your_image', name='your_container_name', detach=True)

    com_err = ''
    error = ''
    output = ''

    if language == 'python':
        _, output = container.exec_run(['python', '-c', code])
    elif language == 'kotlinc':
        container.exec_run(['bash', '-c', f'echo "{code}" > script.kt'])
        com_err, _ = container.exec_run(['kotlinc', 'script.kt', '-include-runtime', '-d', 'script.jar'])
        _, output = container.exec_run(['java', '-jar', 'script.jar'])
        container.exec_run(['rm', 'script.kt', 'script.jar'])  # Удаляем созданные файлы
    elif language == 'node':
        _, output = container.exec_run(['node', '-e', code])
    elif language == 'javac':
        container.exec_run(['bash', '-c', f'echo "{code}" > Main.java'])
        com_err, _ = container.exec_run(['javac', 'Main.java'])
        _, output = container.exec_run(['java', 'Main'])
        container.exec_run(['rm', 'Main.java', 'Main.class'])  # Удаляем созданные файлы
    else:
        return '', 'Invalid language'

    # Получение вывода и ошибок
    if output:
        output = output.decode().strip()

    if com_err:
        com_err = com_err.decode().strip()

    return output, com_err or error





def index(request):
    if request.method == 'POST':
        code = request.POST['interpreter']
        language = request.POST['language']
        posts, error = execute_code(code, language)
        context = {'posts': posts, 'error': error, 'language': language}
    else:
        context = {'posts': '', 'error': ''}
    return render(request, 'interpreter/index.html', context)
