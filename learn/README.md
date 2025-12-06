# 环境准备

## 物理服务器

```bash
conda create --name bottle_python_3_12 python=3.12 -y
conda activate bottle_python_3_12
conda deactivate

conda env list
conda env remove -n bottle_python_3_12

# 调试时选择 python 解释器
Python: Select Interpreter

pip install -e ./

find . -name __pycache__ -exec rm -rf {} \;


conda create --name bottle_python_2_7 python=2.7 -y
conda activate bottle_python_2_7

pip install -e ./
pip install -e Paste==3.6.1

# 服务端
$ python examples/howto.py
Bottle server starting up (using PasteServer (localhost:18088))...
Listening on http://localhost:18088/
Use Ctrl-C to quit.

serving on http://127.0.0.1:18088
127.0.0.1 - - [06/Dec/2025:13:41:42 +0800] "GET / HTTP/1.1" 200 - "-" "curl/7.81.0"
127.0.0.1 - - [06/Dec/2025:13:42:24 +0800] "GET /hello?name=Tim HTTP/1.1" 200 - "-" "curl/7.81.0"

# 客户端
$ curl http://127.0.0.1:18088
Hello World!

#######################

$ curl http://127.0.0.1:18088/hello?name=Tim
Hello Tim!

#######################

$ curl -vvvv -X POST http://127.0.0.1:18088/hello_post -d 'name=tom'
Note: Unnecessary use of -X or --request, POST is already inferred.
*   Trying 127.0.0.1:18088...
* Connected to 127.0.0.1 (127.0.0.1) port 18088 (#0)
> POST /hello_post HTTP/1.1
> Host: 127.0.0.1:18088
> User-Agent: curl/7.81.0
> Accept: */*
> Content-Length: 8
> Content-Type: application/x-www-form-urlencoded
>
* Mark bundle as not supporting multiuse
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Server: PasteWSGIServer/0.5 Python/2.7.18
< Date: Sat, 06 Dec 2025 07:12:55 GMT
< Content-Type: text/html
< Connection: close
<
* Closing connection 0
Hello tom!
$

#######################

$ curl http://127.0.0.1:18088/counter
You viewed this page 1 times!
$
$ curl http://127.0.0.1:18088/counter
You viewed this page 1 times!

#######################

$ curl http://127.0.0.1:18088/hello/lanzhiwang
Hello lanzhiwang!
$

#######################

$ curl http://127.0.0.1:18088/number/12345
Your number is 12345
$

#######################

$ curl http://127.0.0.1:18088/static/howto.tpl
%message = 'Hello world!'
<html>
  <head>
    <title>{{title.title()}}</title>
  </head>
  <body>
    <h1>{{title.title()}}</h1>
    <p>{{message}}</p>
    <p>Items in list: {{len(items)}}</p>
    <ul>
    %for item in items:
      <li>
      %if isinstance(item, int):
        Zahl: {{item}}
      %else:
        %try:
          Other type: ({{type(item).__name__}}) {{repr(item)}}
        %except:
          Error: Item has no string representation.
        %end try-block (yes, you may add comments here)
      %end
      </li>
    %end
    </ul>
  </body>
</html>
$

#######################

$ curl http://127.0.0.1:18088/json
{counter:0}
$

#######################

$ curl http://127.0.0.1:18088/private
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><html><head><title>Error 401: Unauthorized</title></head><body><h1>Error 401: Unauthorized</h1><p>Sorry, the requested URL /private caused an error.</p>Go away!</body></html>
$
$ curl http://127.0.0.1:18088/private?password=secret
Welcome!
$

#######################

$ curl http://127.0.0.1:18088/validate/12/3.4/qwe,asd,zxc
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><html><head><title>Error 403: Forbidden</title></head><body><h1>Error 403: Forbidden</h1><p>Sorry, the requested URL /validate/12/3.4/qwe,asd,zxc caused an error.</p>Wrong parameter format for: csv</body></html>
$
$ curl http://127.0.0.1:18088/validate/12/3.4/56,78
Int: 12, Float:3.400000, List:[56, 78]
$

#######################

$ curl http://127.0.0.1:18088/template/test
Traceback (most recent call last):<br>
&nbsp;&nbsp;File "/root/bottle/bottle.py", line 152, in WSGIHandler<br>
&nbsp;&nbsp;&nbsp;&nbsp;output = handler(**args)<br>
&nbsp;&nbsp;File "examples/howto.py", line 72, in template_test<br>
&nbsp;&nbsp;&nbsp;&nbsp;return template('howto', title='Template Test', items=[1,2,3,'fly'])<br>
&nbsp;&nbsp;File "/root/bottle/bottle.py", line 732, in template<br>
&nbsp;&nbsp;&nbsp;&nbsp;TEMPLATES[template] = template_adapter.find(template)<br>
&nbsp;&nbsp;File "/root/bottle/bottle.py", line 656, in find<br>
&nbsp;&nbsp;&nbsp;&nbsp;raise TemplateError('Template not found: %s' % repr(name))<br>
TemplateError: Template not found: 'howto'
$

#######################

$ curl http://127.0.0.1:18088/db/counter
Total hits in this page: 1!
$
$ curl http://127.0.0.1:18088/db/counter
Total hits in this page: 2!
$
$ curl http://127.0.0.1:18088/db/counter
Total hits in this page: 3!
$


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
