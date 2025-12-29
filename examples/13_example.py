"""
SimpleTemplate
"""

from bottle import SimpleTemplate

tpl = SimpleTemplate("Hello {{name}}!")
print(tpl.render(name="World"))


from bottle import template

print(template("Hello {{name}}!", name="World"))


from bottle import template

my_dict = {"number": "123", "street": "Fake St.", "city": "Fakeville"}
print(template("I live at {{number}} {{street}}, {{city}}", **my_dict))


print(template("Hello {{name}}!", name="World"))

print(template('Hello {{name.title() if name else "stranger"}}!', name=None))

print(template('Hello {{name.title() if name else "stranger"}}!', name="mArC"))


print(template("Hello {{name}}!", name="<b>World</b>"))

print(template("Hello {{!name}}!", name="<b>World</b>"))
