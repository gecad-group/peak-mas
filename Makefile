.PHONY: prosody prosody_stop prosody_start example1

.SILENT: example1 prosody

PYTHON = ~/Documentos/miniconda3/envs/masman/bin/python

prosody:
	@tail -f -n 50 /var/log/prosody/prosody.log

prosody_stop:
	@sudo /etc/init.d/prosody stop

prosody_start:
	@sudo /etc/init.d/prosody start

example1:
	@echo 'Exemplo 1'
	@echo ''
	@echo '' 
	@$(PYTHON) exemplo_basico.py
