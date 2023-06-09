from django.shortcuts import render
from subprocess import Popen, PIPE
from django.contrib.auth.decorators import login_required
import chardet
import os

os.environ['_JAVA_OPTIONS'] = ''
 
def execute_code(code, language):
    if language == 'python':
        process = Popen(['python', '-c', code], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    elif language == 'kotlinc':
        # Сохраняем код в файл и компилируем его с помощью kotlinc
        with open('scrip.kt', 'w') as f:
            f.write(code)
        com_process = Popen(['kotlinc', 'scrip.kt', '-include-runtime', '-d', 'scrip.jar'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        com_out, com_err = com_process.communicate()
        if com_err:
            encoding = chardet.detect(com_err)['encoding']  
            return [], com_err.decode(encoding).strip()
        process = Popen(['java', '-jar', 'scrip.jar'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    elif language == 'node':
        process = Popen(['node', '-e', code], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    elif language == 'javac':
        with open('Main.java','w') as f:
            f.write(code)
        compile = Popen(['javac', 'Main.java'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        compile_out, compile_err = compile.communicate()
        if compile_err:
            encoding = chardet.detect(compile_err)['encoding']  
            return [], compile_err.decode(encoding).strip()
        process = Popen(['java', 'Main'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    else:
        return '', 'Invalid language'
    output, error = process.communicate()
    if error:
        encoding = chardet.detect(error)['encoding']  
        return [], error.decode(encoding).strip()
    posts = []
    try:
        encoding = chardet.detect(output)['encoding']
        posts.append(output.decode(encoding).strip())
    except:
        pass   
    return posts, ''




def index(request):
    if request.method == 'POST':
        code = request.POST['interpreter']
        language = request.POST['language']
        posts, error = execute_code(code, language)
        context = {'posts': posts, 'error': error, 'language': language}
    else:
        context = {'posts': '', 'error': ''}
    return render(request, 'interpreter/index.html', context)
