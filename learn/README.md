# 环境准备

## 物理服务器

```bash
conda create --name bottle python=3.12 -y
conda activate bottle
conda deactivate

# 调试时选择 python 解释器
Python: Select Interpreter

pip install -e ./

find . -name __pycache__ -exec rm -rf {} \;

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
