DOMAIN?=localhost

lint:
	pylint src/peak/

format:
	autoflake --remove-all-unused-imports --remove-unused-variables --expand-star-imports --ignore-init-module-imports -ri .
	isort --profile black .
	black .

patch: 
	python -m bumpver update --patch

minor: 
	python -m bumpver update --minor

major: 
	python -m bumpver update --major

publish: 
	python -m build
	twine check dist/*
	twine upload --skip-existing dist/*