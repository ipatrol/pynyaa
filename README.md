
# PyNyaa

Based on [nyaapantsu](https://github.com/ewhal/nyaa).

## Requirements

- Python3.6 (cause f-strings)
- PostgreSQL

## Installation

```bash
$ git clone https://github.com/nitori/pynyaa
$ cd pynyaa
$ python3.6 -m venv ./.venv
$ . ./.venv/bin/activate
$ pip install -U pip
$ pip install pip-tools
$ pip-sync
```

More details on:
- create db
- create config file (config/development.py)
- import data dump


```bash
$ python manage.py run
```