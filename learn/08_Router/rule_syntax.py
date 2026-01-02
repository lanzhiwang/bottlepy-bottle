r"""
你好! 作为一名高级开发人员, 我非常乐意为你拆解 Python 正则表达式(re 模块)中最核心的 Match 对象.

在 _itertokens 这个方法里, finditer 是整个路由解析器的"眼睛", 它负责在长长的路由字符串中精准地定位出每一个通配符(如 <id:int>).

以下是这些方法的详细含义和在代码中的具体作用:

1. match 是什么含义?

self.rule_syntax.finditer(rule) 会返回一个迭代器, 其中的每一个元素 match 都是一个 re.Match 对象.
这个对象代表了正则表达式在 rule 字符串中找到的一个成功匹配实例. 它不仅包含了匹配到的字符串, 还包含了匹配发生的位置信息以及正则表达式中括号定义的捕获组信息.

2. 核心方法解析

为了方便理解, 我们假设 rule = "/user/<id:int>". 当正则扫描到 <id:int> 时:

2.1. match.group(0)
含义: 返回正则表达式整体匹配到的字符串.
在本代码中: 它是"转义符 + 完整通配符".
例子: 如果匹配的是 <id:int>, group(0) 就是 "<id:int>". 如果前面有转义符如 \\<id:int>, group(0) 就是 "\\<id:int>".

2.2. match.groups()
含义: 返回一个元组, 包含正则表达式中所有捕获组(即括号 () 括起来的部分)匹配到的内容.

在本代码中: rule_syntax 定义了 7 个捕获组:

(\\\\*): 前面的反斜杠.

([a-zA-Z_][a-zA-Z_0-9]*): 旧语法的名称.

(): 旧语法的标记位.

(.*?): 旧语法的正则.

([a-zA-Z_][a-zA-Z_0-9]*): 新语法的名称.

([a-zA-Z_]*): 新语法的过滤器类型.

((?:\\\\.|[^\\\\>])+): 新语法的配置参数.

作用: 代码通过 g = match.groups() 一次性拿到所有零件, 然后通过 g[4:7] 提取出新语法的名、过滤器和配置.

2.3. match.start()
含义: 返回当前匹配在原始字符串中开始的索引位置.

2.4. match.end()
含义: 返回当前匹配在原始字符串中结束的下一个索引位置.

3. 图解说明

假设 rule = "/api/<id:int>/"
初始状态: offset = 0.
正则发现匹配: 匹配到了 <id:int>.
match.start() 是 5(即 < 的位置).
match.end() 是 13(即 > 后面一个字符 / 的位置).
match.group(0) 是 "<id:int>".
提取前缀: rule[0:5] 得到 "/api/". 这就是通配符前面的静态路径.
提取通配符信息: 从 match.groups() 中提取出 name='id', filtr='int', conf=None.
更新偏移量: offset 变为 13.
最后一段: 循环结束, 处理剩下的 rule[13:], 得到最后的 "/".

高级开发人员的专业建议
为什么用 finditer 而不是 findall?
findall 会直接返回一个包含所有捕获组字符串的列表, 它丢失了位置信息(start/end). 在写 Router 时, 我们需要位置信息来切分出通配符之间的"静态部分"(prefix), 所以 finditer 是唯一的正确选择.
捕获组的编号:
在使用复杂的正则表达式(如 rule_syntax)时, 捕获组很多. 在 _itertokens 方法中, 代码使用了 g = match.groups() 后通过切片 g[4:7] 访问, 这虽然高效, 但对维护者不友好. 在更现代的 Python 代码中, 我们会倾向于使用 命名捕获组 (?P<name>...), 然后通过 match.group('name') 来访问, 这样代码的可读性会更高.
"""

import re
from bottle import Router

rule_syntax = re.compile(
    "(\\\\*)"  # 匹配转义斜杠
    "(?:(?::([a-zA-Z_][a-zA-Z_0-9]*)?()(?:#(.*?)#)?)"  # 兼容旧语法 :name#re#
    "|(?:<([a-zA-Z_][a-zA-Z_0-9]*)?(?::([a-zA-Z_]*)"  # 新语法 <name:filter:conf>
    "(?::((?:\\\\.|[^\\\\>])+)?)?)?>))"
)

rules = [
    "/index",
    "/contact",
    "/user1/<id:int>/name/<name1:re:[a-z]+>",
    "/user2/:id/name/:re",
    "/<its0>/<:re:.+>/<test>/<name:re:[a-z]+>",
    "/\<its1>/<:re:.+>/<test>/<name:re:[a-z]+>",
    "/\\<its2>/<:re:.+>/<test>/<name:re:[a-z]+>",
    "/\\\<its3>/<:re:.+>/<test>/<name:re:[a-z]+>",
    "/\\\\<its4>/<:re:.+>/<test>/<name:re:[a-z]+>",
]

r = Router()

for rule in rules:
    print(f"rule: {rule}")

    offset, prefix = 0, ""
    print(f"rule_syntax.finditer(rule): {list(rule_syntax.finditer(rule))}")
    print(f"rule_syntax.finditer(rule): {len(list(rule_syntax.finditer(rule)))}")
    for match in rule_syntax.finditer(rule):
        print(f"match: {match}")
        print(f"match.group(0): {match.group(0)}")
        print(f"match.start(): {match.start()}")
        print(f"match.end(): {match.end()}")
        print(f"match.groups(): {match.groups()}")

    print(f"rule: {list(r._itertokens(rule))}")
    print("---" * 10)
