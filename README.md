# Setup

## System Tools

Pdf tools for use on mac
`brew install poppler pyenv uv`


## Python Environment

```
pyenv version
pyenv install 3.13
pyenv global 3.13

cd transcripts
uv venv
source ./venv/bin/activate
uv pip install -r requirements.txt
```

## EDA and Model Creation

Look at Transcripts Notebook

Stage files in `samples` directory, a bit messy, because of time constraints.

## Inference

`python infer.py`

Output:
```
page: R11963430-25840119-file0001.pdf_1.png
Coppel High School: 99.928914%
page: R11963430-25840119-file0001.pdf_2.png
Coppel High School: 99.837972%
page: R11963430-25840119-file0001.pdf_3.png
Coppel High School: 99.887026%
```
