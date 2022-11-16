all: single_agent single_group group_hierarchy group_tags data_extraction dataset simulation

single_agent: 
	peak run examples\hello_world_agent\agent.py -j agent@localhost

single_group:
	peak start examples\agent_groups\hello_world_group\agents.yaml

group_hierarchy:
	peak run examples\agent_groups\group_hierarchy\agent.py -j agent@localhost

group_tags:
	peak start examples\agent_groups\group_tags\agents.yaml

data_extraction:
	peak run examples\data_extraction\agent.py -j agent@localhost

dataset:
	peak run examples\data_providers\dataset\agent.py -j agent@localhost -p examples\data_providers\dataset\dataset.py

simulation:
	peak start examples\simulation\start.yaml

patch:
	python -m bumpver update --patch

minor:
	python -m bumpver update --minor

major:
	python -m bumpver update --major

publish:
	python -m build
	twine check dist/*
	twine upload dist/*