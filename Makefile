.PHONY: docs examples

docs:
	mkdocs build

test:
	pytest tests/unit/
	pytest tests/issues/
	pytest --nbval tests/notebooks/
	ydata_profiling -h

test_spark:
	pytest --spark_home=${SPARK_HOME} tests/backends/spark_backend/
	ydata_profiling -h

test_cov:
	pytest --cov=. tests/unit/
	pytest --cov=. --cov-append tests/issues/
	pytest --cov=. --cov-append --nbval tests/notebooks/
	ydata_profiling -h

examples:
	find ./examples -maxdepth 2 -type f -name "*.py" -execdir python {} \;

package:
	rm -rf build dist
	echo "$(version)" > VERSION
	python setup.py sdist bdist_wheel
	twine check dist/*

install:
	pip install -e ".[notebook]"

install-docs: install ### Installs regular and docs dependencies
	pip install -e ".[docs]"

install-spark-ci:
	sudo apt-get update
	sudo apt-get -y install openjdk-8-jdk
	curl https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
	--output ${SPARK_DIRECTORY}/spark.tgz
	cd ${SPARK_DIRECTORY} && tar -xvzf spark.tgz && mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} spark

publish-docs: examples ### Publishes the documentation
	mkdir docs/examples
	rsync -R examples/*/*.html docs
	mike deploy --push --update-aliases $(version) latest

lint:
	pre-commit run --all-files

clean:
	git rm --cached `git ls-files -i --exclude-from=.gitignore`

all:
	make lint
	make install
	make examples
	make docs
	make test
