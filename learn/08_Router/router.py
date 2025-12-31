from bottle import Router, HTTPError


# 1. 基础场景: 静态路由与 O(1) 查找
# 静态路由是最简单的场景, Router 会将其存入 self.static 字典, 实现极速查找.
router = Router()

# 添加静态路由
router.add("/index", "GET", "index_handler")
print("---" * 10)
router.add("/contact", "GET", "contact_handler")
print("---" * 10)

# 模拟请求匹配
print(router.match({"REQUEST_METHOD": "GET", "PATH_INFO": "/index"}))
# 输出: ('index_handler', {})
print("---" * 10)

# 2. 核心场景: 动态通配符与过滤器
# 演示 int、float 和 path 过滤器的使用, 以及它们如何自动转换 Python 类型.

# router = Router()

# 1. 整数过滤器: 匹配 /user/123
router.add("/user/<id:int>", "GET", "user_detail")
print("---" * 10)

# 2. 浮点数过滤器: 匹配 /item/19.99
router.add("/item/<price:float>", "GET", "item_price")
print("---" * 10)

# 3. 路径过滤器: 匹配 /static/css/style.css（允许斜杠）
router.add("/static/<file:path>", "GET", "static_file")
print("---" * 10)

router.add("/hello/<name>", "GET", "hello_detail")
print("---" * 10)

router.add("/<action>/<user>", "GET", "action_handler1")
print("---" * 10)

router.add("/action2/<action>/<user>", "GET", "action_handler2")
print("---" * 10)

router.add("/show/<name:re:[a-z]+>", "GET", "show_handler")
print("---" * 10)

# 匹配测试
print(router.match({"REQUEST_METHOD": "GET", "PATH_INFO": "/user/123"}))
# 输出: ('user_detail', {'id': 123})  <-- 注意: 123 是 int 类型

print(router.match({"REQUEST_METHOD": "GET", "PATH_INFO": "/item/19.99"}))
# 输出: ('item_price', {'price': 19.99})

print(router.match({"REQUEST_METHOD": "GET", "PATH_INFO": "/static/img/logo.png"}))
# 输出: ('static_file', {'file': 'img/logo.png'})
print("---" * 10)

# 3. 高级场景: 自定义过滤器与匿名通配符
# 演示如何添加自定义正则过滤器, 以及使用不带名字的通配符.
# router = Router()

# 添加自定义过滤器: 匹配 4 位年份, 并转为 int
router.add_filter("year", lambda conf: (r"\d{4}", int, str))

router.add("/archive/<y:year>", "GET", "archive_handler")

# 匿名通配符: 不关心变量名, 只关心格式
# < :int > 会被自动命名为 anon0, anon1...
router.add("/page/<:int>", "GET", "page_handler")

print(router.match({"REQUEST_METHOD": "GET", "PATH_INFO": "/archive/2024"}))
# 输出: ('archive_handler', {'y': 2024})

# print(router.match({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/page/5'}))
# 输出: ('page_handler', {'anon0': 5})

# 4. 反向解析: URL 生成（URL Builder）
# 演示如何根据路由规则或名称, 反向生成完整的 URL 字符串.
# router = Router()
router.add("/blog/<id:int>", "GET", "view_post", name="blog_post")

# 使用规则名生成
url1 = router.build("/blog/<id:int>", id=100)
print(url1)  # 输出: /blog/100

# 使用自定义名称生成, 并添加查询参数
url2 = router.build("blog_post", id=100, section="comments")
print(url2)  # 输出: /blog/100?section=comments

# 5. 错误处理: 404 与 405 (Method Not Allowed)
# 演示路由匹配失败时的逻辑.

# router = Router()
router.add("/api/data", "POST", "post_handler")
router.add("/api/data", "GET", "get_handler")

# 1. 404 错误: 路径不存在
try:
    router.match({"REQUEST_METHOD": "GET", "PATH_INFO": "/missing"})
except HTTPError as e:
    print(e)  # 404 Not found: '/missing'

# 2. 405 错误: 路径存在但方法不支持
try:
    router.match({"REQUEST_METHOD": "DELETE", "PATH_INFO": "/api/data"})
except HTTPError as e:
    print(f"{e} Allow: {e.headers['Allow']}")
    # 输出: 405 Method not allowed. Allow: GET,POST


# 6. 核心性能演示: 正则合并 (Merged Regex)
# 说明 _compile 逻辑是如何将多个动态路由合并成一个正则, 并通过 lastindex 区分的.
# router = Router()
# 连续添加多个动态路由, 超过 99 个会触发分块
router.add("/alpha/<v1>", "GET", "target1")
router.add("/beta/<v2>", "GET", "target2")
router.add("/gamma/<v3>", "GET", "target3")

# 我们可以观察内部结构（演示用）
method_regexes = router.dyna_regexes["GET"]
for combined, rules in method_regexes:
    # 这里 combined 是一个编译好的正则 match 函数
    # 它内部类似于 ( ^/alpha/(?P<v1>[^/]+)$ ) | ( ^/beta/(?P<v2>[^/]+)$ ) | ...
    pass

# 当访问 /beta/hello 时
# 正则引擎一次扫描发现第二个分组匹配成功, lastindex = 2
# 对应 rules[2-1] 即 'target2'
print(router.match({"REQUEST_METHOD": "GET", "PATH_INFO": "/beta/hello"}))
# 输出: ('target2', {'v2': 'hello'})
