DOMAIN?=localhost

format:
	autoflake --remove-all-unused-imports --remove-unused-variables --expand-star-imports --ignore-init-module-imports -ri .
	isort --profile black .
	black .
 	pylint src/peak/

patch: format
	python -m bumpver update --patch

minor: format
	python -m bumpver update --minor

major: format
	python -m bumpver update --major

publish: format
	python -m build
	twine check dist/*
	twine upload dist/*