from bottle import Router, HTTPError

print("1", "---" * 30)
# 1. 基础场景: 静态路由与 O(1) 查找
# 静态路由是最简单的场景, Router 会将其存入 self.static 字典, 实现极速查找.


router = Router()


# 添加静态路由
router.add("/index", "GET", "index_handler")
router.add("/contact", "GET", "contact_handler")

print(f"router.rules: {router.rules}")
print(f"router._groups: {router._groups}")
print(f"router.builder: {router.builder}")
print(f"router.static: {router.static}")
print(f"router.dyna_routes: {router.dyna_routes}")
print(f"router.dyna_regexes: {router.dyna_regexes}")
print(f"router.strict_order: {router.strict_order}")
print(f"router.filters: {router.filters}")
# router.rules: []
# router._groups: {}
# router.builder:
# {
#     '/index': [(None, '/index')],
#     '/contact': [(None, '/contact')]
# }
# router.static: {
#     'GET': {
#         '/index': ('index_handler', None),
#         '/contact': ('contact_handler', None)
#     }
# }
# router.dyna_routes: {}
# router.dyna_regexes: {}
# router.strict_order: False
# router.filters: {
#     're': <function Router.__init__.<locals>.<lambda> at 0x7fafa60f2340>,
#     'int': <function Router.__init__.<locals>.<lambda> at 0x7fafa5e75f80>,
#     'float': <function Router.__init__.<locals>.<lambda> at 0x7fafa5e76c00>,
#     'path': <function Router.__init__.<locals>.<lambda> at 0x7fafa599ce00>
# }


# 模拟请求匹配
print(router.match({"REQUEST_METHOD": "GET", "PATH_INFO": "/index"}))
# 输出: ('index_handler', {})

print("2", "---" * 30)
# 2. 核心场景: 动态通配符与过滤器
# 演示 int、float 和 path 过滤器的使用, 以及它们如何自动转换 Python 类型.


# 1. 整数过滤器: 匹配 /user/123
router.add("/user/<id:int>", "GET", "user_detail")

# 2. 浮点数过滤器: 匹配 /item/19.99
router.add("/item/<price:float>", "GET", "item_price")

# 3. 路径过滤器: 匹配 /static/css/style.css(允许斜杠)
router.add("/static/<file:path>", "GET", "static_file")

print(f"router.rules: {router.rules}")
print(f"router._groups: {router._groups}")
print(f"router.builder: {router.builder}")
print(f"router.static: {router.static}")
print(f"router.dyna_routes: {router.dyna_routes}")
print(f"router.dyna_regexes: {router.dyna_regexes}")
print(f"router.strict_order: {router.strict_order}")
print(f"router.filters: {router.filters}")
# router.rules: []
# router._groups: {
#     ('/user/(?:-?\\d+)', 'GET'): 0,
#     ('/item/(?:-?[\\d.]+)', 'GET'): 1,
#     ('/static/(?:.+?)', 'GET'): 2
# }
# router.builder:
# {
#     '/index': [(None, '/index')],
#     '/contact': [(None, '/contact')],
#     '/user/<id:int>': [
#         (None, '/user/'),
#         ('id', <function Router.__init__.<locals>.<lambda>.<locals>.<lambda> at 0x7fafa5124720>)
#     ],
#     '/item/<price:float>': [
#         (None, '/item/'),
#         ('price', <function Router.__init__.<locals>.<lambda>.<locals>.<lambda> at 0x7fafa51249a0>)
#     ],
#     '/static/<file:path>': [
#         (None, '/static/'),
#         ('file', <class 'str'>)
#     ]
# }
# router.static: {
#     'GET': {
#         '/index': ('index_handler', None),
#         '/contact': ('contact_handler', None)
#     }
# }
# router.dyna_routes: {
#     'GET': [
#         ('/user/<id:int>', '/user/(?:-?\\d+)', 'user_detail', <function Router.add.<locals>.getargs at 0x7fafa51247c0>),
#         ('/item/<price:float>', '/item/(?:-?[\\d.]+)', 'item_price', <function Router.add.<locals>.getargs at 0x7fafa5124900>),
#         ('/static/<file:path>', '/static/(?:.+?)', 'static_file', <function Router.add.<locals>.getargs at 0x7fafa5124ae0>)
#     ]
# }
# router.dyna_regexes: {
#     'GET': [
#         (
#             <built-in method match of re.Pattern object at 0x35ad4520>,
#             [
#                 ('user_detail', <function Router.add.<locals>.getargs at 0x7fafa51247c0>),
#                 ('item_price', <function Router.add.<locals>.getargs at 0x7fafa5124900>),
#                 ('static_file', <function Router.add.<locals>.getargs at 0x7fafa5124ae0>)
#             ]
#         )
#     ]
# }
# router.strict_order: False
# router.filters: {
#     're': <function Router.__init__.<locals>.<lambda> at 0x7fafa60f2340>,
#     'int': <function Router.__init__.<locals>.<lambda> at 0x7fafa5e75f80>,
#     'float': <function Router.__init__.<locals>.<lambda> at 0x7fafa5e76c00>,
#     'path': <function Router.__init__.<locals>.<lambda> at 0x7fafa599ce00>
# }

# 匹配测试
print(router.match({"REQUEST_METHOD": "GET", "PATH_INFO": "/user/123"}))
# 输出: ('user_detail', {'id': 123})  <-- 注意: 123 是 int 类型

print(router.match({"REQUEST_METHOD": "GET", "PATH_INFO": "/item/19.99"}))
# 输出: ('item_price', {'price': 19.99})

print(router.match({"REQUEST_METHOD": "GET", "PATH_INFO": "/static/img/logo.png"}))
# 输出: ('static_file', {'file': 'img/logo.png'})


print("3", "---" * 30)
# 3. 高级场景: 自定义过滤器与匿名通配符
# 演示如何添加自定义正则过滤器, 以及使用不带名字的通配符.


# 添加自定义过滤器: 匹配 4 位年份, 并转为 int
router.add_filter("year", lambda conf: (r"\d{4}", int, str))

router.add("/archive/<y:year>", "GET", "archive_handler")

# 匿名通配符: 不关心变量名, 只关心格式
# < :int > 会被自动命名为 anon0, anon1...
router.add("/page/<:int>", "GET", "page_handler")

print(f"router.rules: {router.rules}")
print(f"router._groups: {router._groups}")
print(f"router.builder: {router.builder}")
print(f"router.static: {router.static}")
print(f"router.dyna_routes: {router.dyna_routes}")
print(f"router.dyna_regexes: {router.dyna_regexes}")
print(f"router.strict_order: {router.strict_order}")
print(f"router.filters: {router.filters}")
# router.rules: []
# router._groups: {
#     ('/user/(?:-?\\d+)', 'GET'): 0,
#     ('/item/(?:-?[\\d.]+)', 'GET'): 1,
#     ('/static/(?:.+?)', 'GET'): 2,
#     ('/archive/(?:\\d{4})', 'GET'): 3,
#     ('/page/(?:-?\\d+)', 'GET'): 4
# }
# router.builder: {
#     '/index': [(None, '/index')],
#     '/contact': [(None, '/contact')],
#     '/user/<id:int>': [
#         (None, '/user/'),
#         ('id', <function Router.__init__.<locals>.<lambda>.<locals>.<lambda> at 0x7ff397042200>)
#     ],
#     '/item/<price:float>': [
#         (None, '/item/'),
#         ('price', <function Router.__init__.<locals>.<lambda>.<locals>.<lambda> at 0x7ff397042480>)
#     ],
#     '/static/<file:path>': [
#         (None, '/static/'),
#         ('file', <class 'str'>)
#     ],
#     '/archive/<y:year>': [
#         (None, '/archive/'),
#         ('y', <class 'str'>)
#     ],
#     '/page/<:int>': [
#         (None, '/page/'),
#         ('anon0', <function Router.__init__.<locals>.<lambda>.<locals>.<lambda> at 0x7ff397042a20>)
#     ]
# }
# router.static: {
#     'GET': {
#         '/index': ('index_handler', None),
#         '/contact': ('contact_handler', None)
#     }
# }
# router.dyna_routes: {
#     'GET': [
#         ('/user/<id:int>', '/user/(?:-?\\d+)', 'user_detail', <function Router.add.<locals>.getargs at 0x7ff3970422a0>),
#         ('/item/<price:float>', '/item/(?:-?[\\d.]+)', 'item_price', <function Router.add.<locals>.getargs at 0x7ff3970423e0>),
#         ('/static/<file:path>', '/static/(?:.+?)', 'static_file', <function Router.add.<locals>.getargs at 0x7ff3970425c0>),
#         ('/archive/<y:year>', '/archive/(?:\\d{4})', 'archive_handler', <function Router.add.<locals>.getargs at 0x7ff3970428e0>),
#         ('/page/<:int>', '/page/(?:-?\\d+)', 'page_handler', <function Router.add.<locals>.getargs at 0x7ff397042980>)
#     ]
# }
# router.dyna_regexes: {
#     'GET': [
#         (
#             <built-in method match of re.Pattern object at 0xaecfc90>,
#             [
#                 ('user_detail', <function Router.add.<locals>.getargs at 0x7ff3970422a0>),
#                 ('item_price', <function Router.add.<locals>.getargs at 0x7ff3970423e0>),
#                 ('static_file', <function Router.add.<locals>.getargs at 0x7ff3970425c0>),
#                 ('archive_handler', <function Router.add.<locals>.getargs at 0x7ff3970428e0>),
#                 ('page_handler', <function Router.add.<locals>.getargs at 0x7ff397042980>)
#             ]
#         )
#     ]
# }
# router.strict_order: False
# router.filters: {
#     're': <function Router.__init__.<locals>.<lambda> at 0x7ff397eca340>,
#     'int': <function Router.__init__.<locals>.<lambda> at 0x7ff397beafc0>,
#     'float': <function Router.__init__.<locals>.<lambda> at 0x7ff397d7d120>,
#     'path': <function Router.__init__.<locals>.<lambda> at 0x7ff3970420c0>,
#     'year': <function <lambda> at 0x7ff397042840>
# }

print(router.match({"REQUEST_METHOD": "GET", "PATH_INFO": "/archive/2024"}))
# 输出: ('archive_handler', {'y': 2024})

# print(router.match({"REQUEST_METHOD": "GET", "PATH_INFO": "/page/5"}))
# 输出: ('page_handler', {'anon0': 5})

print("4", "---" * 30)
# 4. 反向解析: URL 生成(URL Builder)
# 演示如何根据路由规则或名称, 反向生成完整的 URL 字符串.


router.add("/blog/<id:int>", "GET", "view_post", name="blog_post")

print(f"router.rules: {router.rules}")
print(f"router._groups: {router._groups}")
print(f"router.builder: {router.builder}")
print(f"router.static: {router.static}")
print(f"router.dyna_routes: {router.dyna_routes}")
print(f"router.dyna_regexes: {router.dyna_regexes}")
print(f"router.strict_order: {router.strict_order}")
print(f"router.filters: {router.filters}")
# router.rules: []
# router._groups: {
#     ('/user/(?:-?\\d+)', 'GET'): 0,
#     ('/item/(?:-?[\\d.]+)', 'GET'): 1,
#     ('/static/(?:.+?)', 'GET'): 2,
#     ('/archive/(?:\\d{4})', 'GET'): 3,
#     ('/page/(?:-?\\d+)', 'GET'): 4,
#     ('/blog/(?:-?\\d+)', 'GET'): 5
# }
# router.builder: {
#     '/index': [(None, '/index')],
#     '/contact': [(None, '/contact')],
#     '/user/<id:int>': [
#         (None, '/user/'),
#         ('id', <function Router.__init__.<locals>.<lambda>.<locals>.<lambda> at 0x7fedbbe7c720>)
#     ],
#     '/item/<price:float>': [
#         (None, '/item/'),
#         ('price', <function Router.__init__.<locals>.<lambda>.<locals>.<lambda> at 0x7fedbbe7c9a0>)
#     ],
#     '/static/<file:path>': [
#         (None, '/static/'),
#         ('file', <class 'str'>)
#     ],
#     '/archive/<y:year>': [
#         (None, '/archive/'),
#         ('y', <class 'str'>)
#     ],
#     '/page/<:int>': [
#         (None, '/page/'),
#         ('anon0', <function Router.__init__.<locals>.<lambda>.<locals>.<lambda> at 0x7fedbbe7cea0>)
#     ],
#     '/blog/<id:int>': [
#         (None, '/blog/'),
#         ('id', <function Router.__init__.<locals>.<lambda>.<locals>.<lambda> at 0x7fedbbe7cb80>)
#     ],
#     'blog_post': [
#         (None, '/blog/'),
#         ('id', <function Router.__init__.<locals>.<lambda>.<locals>.<lambda> at 0x7fedbbe7cb80>)
#     ]
# }
# router.static: {
#     'GET': {
#         '/index': ('index_handler', None),
#         '/contact': ('contact_handler', None)
#     }
# }
# router.dyna_routes: {
#     'GET': [
#         ('/user/<id:int>', '/user/(?:-?\\d+)', 'user_detail', <function Router.add.<locals>.getargs at 0x7fedbbe7c7c0>),
#         ('/item/<price:float>', '/item/(?:-?[\\d.]+)', 'item_price', <function Router.add.<locals>.getargs at 0x7fedbbe7c900>),
#         ('/static/<file:path>', '/static/(?:.+?)', 'static_file', <function Router.add.<locals>.getargs at 0x7fedbbe7cae0>),
#         ('/archive/<y:year>', '/archive/(?:\\d{4})', 'archive_handler', <function Router.add.<locals>.getargs at 0x7fedbbe7ce00>),
#         ('/page/<:int>', '/page/(?:-?\\d+)', 'page_handler', <function Router.add.<locals>.getargs at 0x7fedbbe7cf40>),
#         ('/blog/<id:int>', '/blog/(?:-?\\d+)', 'view_post', <function Router.add.<locals>.getargs at 0x7fedbbe7ca40>)
#     ]
# }
# router.dyna_regexes: {
#     'GET': [
#         (
#             <built-in method match of re.Pattern object at 0x7fedbbe15300>,
#             [
#                 ('user_detail', <function Router.add.<locals>.getargs at 0x7fedbbe7c7c0>),
#                 ('item_price', <function Router.add.<locals>.getargs at 0x7fedbbe7c900>)
#             ]
#         ),
#         (
#             <built-in method match of re.Pattern object at 0x7fedbc6c6710>,
#             [
#                 ('static_file', <function Router.add.<locals>.getargs at 0x7fedbbe7cae0>),
#                 ('archive_handler', <function Router.add.<locals>.getargs at 0x7fedbbe7ce00>)
#             ]
#         ),
#         (
#             <built-in method match of re.Pattern object at 0x7fedbc73fa40>,
#             [
#                 ('page_handler', <function Router.add.<locals>.getargs at 0x7fedbbe7cf40>),
#                 ('view_post', <function Router.add.<locals>.getargs at 0x7fedbbe7ca40>)
#             ]
#         )
#     ]
# }
# router.strict_order: False
# router.filters: {
#     're': <function Router.__init__.<locals>.<lambda> at 0x7fedbcc42340>,
#     'int': <function Router.__init__.<locals>.<lambda> at 0x7fedbc9c1f80>,
#     'float': <function Router.__init__.<locals>.<lambda> at 0x7fedbc9c2c00>,
#     'path': <function Router.__init__.<locals>.<lambda> at 0x7fedbc83ce00>,
#     'year': <function <lambda> at 0x7fedbbe7cd60>
# }

# 使用规则名生成
url1 = router.build("/blog/<id:int>", id=100)
print(url1)  # 输出: /blog/100

# 使用自定义名称生成, 并添加查询参数
url2 = router.build("blog_post", id=100, section="comments")
print(url2)  # 输出: /blog/100?section=comments

url3 = router.build("/page/<:int>", 10, section="comments")
print(url3)  # 输出: /page/10?section=comments

print("5", "---" * 30)
# 5. 错误处理: 404 与 405 (Method Not Allowed)
# 演示路由匹配失败时的逻辑.


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

print("6", "---" * 30)
# 6. 核心性能演示: 正则合并 (Merged Regex)
# 说明 _compile 逻辑是如何将多个动态路由合并成一个正则, 并通过 lastindex 区分的.


# 连续添加多个动态路由, 超过 99 个会触发分块
router.add("/alpha/<v1>", "GET", "target1")
router.add("/beta/<v2>", "GET", "target2")
router.add("/gamma/<v3>", "GET", "target3")

# 我们可以观察内部结构(演示用)
method_regexes = router.dyna_regexes["GET"]
for combined, rules in method_regexes:
    # 这里 combined 是一个编译好的正则 match 函数
    # 它内部类似于 ( ^/alpha/(?P<v1>[^/]+)$ ) | ( ^/beta/(?P<v2>[^/]+)$ ) | ...
    print(f"combined: {combined}")
    print(f"rules: {rules}")

# 当访问 /beta/hello 时
# 正则引擎一次扫描发现第二个分组匹配成功, lastindex = 2
# 对应 rules[2-1] 即 'target2'
print(router.match({"REQUEST_METHOD": "GET", "PATH_INFO": "/beta/hello"}))
# 输出: ('target2', {'v2': 'hello'})
