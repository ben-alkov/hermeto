TOX_ENVLIST ?= py39
TOX_ARGS ?=
GENERATE_TEST_DATA = false
TEST_LOCAL_PYPISERVER = false

.PHONY: clean pip-compile
all: venv

clean:
	rm -rf dist venv .tox *.egg-info *.log*

venv:
	/usr/bin/env python3 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt -r requirements-extras.txt
	venv/bin/pip install tox
	venv/bin/pip install -e .

# Run everything in tox.ini's "tox.env_list" in tox venvs with system Python
#   (except where other Python explicitly requested)
test: venv
	venv/bin/tox

# Run unit tests with tox py39 venv
# To make good use of TOX_ARGS, e.g. when developing locally, try something like
#   `make TOX_ARGS=tests/unit/package_managers/test_pip.py test-unit` which will
#   run *only* the unit tests for 'test_pip.py' (you can further drill down
#   using standard pytest notation, i.e. "::")
test-unit: venv
	venv/bin/tox -e $(TOX_ENVLIST) -- $(TOX_ARGS)

# Run integration tests in tox venv with system Python
test-integration: venv
	CACHI2_GENERATE_TEST_DATA=$(GENERATE_TEST_DATA) \
	CACHI2_TEST_LOCAL_PYPISERVER=$(TEST_LOCAL_PYPISERVER) \
		venv/bin/tox -e integration -- $(TOX_ARGS)

mock-go-unittest-data:
	hack/mock-unittest-data/gomod.sh

build-image:
	podman build -t localhost/cachi2:latest .

# If you're worried that your local image may be outdated
# (old base image, old rpms cached in the microdnf install layer)
build-pristine-image:
	podman build --pull-always --no-cache -t localhost/cachi2:latest .

# pip-compile dependencies *specifically* using Py3.9 and a fresh venv
pip-compile:
	@podman run \
	--rm \
	--volume ${PWD}:/cachi2:rw,Z \
	--workdir /cachi2 \
	docker.io/library/python:3.9-alpine sh -c \
		"apk add git && \
		pip3 install pip-tools && \
		pip-compile \
			--allow-unsafe \
			--generate-hashes \
			--output-file=requirements.txt \
			pyproject.toml && \
		pip-compile \
			--all-extras \
			--allow-unsafe \
			--generate-hashes \
			--output-file=requirements-extras.txt pyproject.toml"
