.PHONY: clean
clean:
	rm -rf .venv build dist ./*/__pycache__ */.egg-info
	find . -type f -name '*.pyc' -exec rm -f {} \;

.PHONY: venv
venv:
	test -d .venv || (python3 -m venv .venv && .venv/bin/pip install -r requirements.txt)

.PHONY: build
build: venv
	.venv/bin/python setup.py sdist
