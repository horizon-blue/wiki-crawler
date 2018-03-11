# Crawler

A Wikipedia crawler that extract information from actor pages and movie pages and store in database

## Install packages

It is recommended that you install all requirements in virtual environment.

To create a virtual environment, cd into the project root directory, and do

```bash
virtualenv venv
```

(The project is written in Python 3, and might not be compatible with Python 2. Make sure that you are creating an virtualenv using Python 3)

Then you can activate your virtual env by

```bash
source venv/bin/activate
```

Install packages via pip

```bash
pip install -r requirements.txt
```

Then you can begin exploring the project. When you are done, deactivate the environment by

```bash
deactivate
```

## Initialize database

You need to initialize the database the first time you run the crawler. To do so, start a python console, and execute the following code

```python
from database import init_db
init_db()
```

Then you can start running the spider by

```bash
python spider.py
```
