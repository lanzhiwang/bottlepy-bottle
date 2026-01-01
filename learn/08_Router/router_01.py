from bottle import Router

router = Router()
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
for i in range(len(rules)):
    if i % 3 == 0:
        method = "GET"
    elif i % 3 == 1:
        method = "POST"
    else:
        method = "PUT"
    router.add(rules[i], method, f"handler_{i}", name=f"name_{i}")
