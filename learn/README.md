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
