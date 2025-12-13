# 环境准备

## 物理服务器

```bash
conda env list

conda create --name bottle_python_2_7 python=2.7 -y
conda create --name bottle_python_3_6 python=3.6 -y
conda create --name bottle_python_3_12 python=3.12 -y

conda activate bottle_python_2_7
conda activate bottle_python_3_6
conda activate bottle_python_3_12

conda deactivate
conda env remove -n bottle_python_2_7 -y
conda env remove -n bottle_python_3_6 -y
conda env remove -n bottle_python_3_12 -y

pip install -e ./
pip install Mako==1.3.10 Jinja2==3.1.6
pip install Paste==3.6.1

# 调试时选择 python 解释器
Python: Select Interpreter

find . -name __pycache__ -exec rm -rf {} \;

####################### 测试用例

python -m unittest discover
python -m unittest test/test_environ.py
python -m unittest test/test_oorouting.py
python -m unittest test/test_config.py
python -m unittest test/test_app.py
python -m unittest test/test_formsdict.py

####################### 服务端

$ pwd
/root/bottle/examples
$ python howto.py
Bottle server starting up (using WSGIRefServer (localhost:8080))...
Listening on http://localhost:8080/
Use Ctrl-C to quit.

####################### 客户端

$ curl http://127.0.0.1:8080
Hello World!

#######################

$ curl http://127.0.0.1:8080/hello?name=Tim
Hello Tim!

#######################

$ curl -vvvv -X POST http://127.0.0.1:8080/hello_post -d 'name=tom'

#######################

$ curl http://127.0.0.1:8080/hello/lanzhiwang
Hello lanzhiwang!
$

#######################

$ curl http://127.0.0.1:8080/private
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><html><head><title>Error 401: Unauthorized</title></head><body><h1>Error 401: Unauthorized</h1><p>Sorry, the requested URL /private caused an error.</p>Go away!</body></html>
$
$ curl http://127.0.0.1:8080/private?password=secret
Welcome!
$

#######################

```

## codespaces

```bash
 $ python -m venv .venv
 $ source .venv/bin/activate
(.venv)  $ pip freeze
(.venv)  $
(.venv)  $ pip install -e ./
(.venv)  $
(.venv)  $ pip freeze
-e git+https://github.com/lanzhiwang/bottlepy-bottle@dad5ebd08a6672ca334aa14a3a10331978e5d2ed#egg=bottle
(.venv)  $
(.venv)  $ deactivate
 $

```
