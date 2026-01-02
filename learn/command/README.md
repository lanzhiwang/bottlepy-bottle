```bash

$ ./bottle.py --debug learn.command.mymodule:app
6074 __main__
main qwe

$ python -m bottle --debug learn.command.mymodule:app
6074 __main__
main qwe

$ /root/miniconda3/envs/bottle_python_3_12/bin/bottle --debug learn.command.mymodule:app
6074 bottle
main qwe

$ bottle --debug learn.command.mymodule:app
6074 bottle
main qwe


```
