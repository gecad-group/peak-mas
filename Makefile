.PHONY: prosody prosody_stop prosody_start example1

.SILENT: example1 prosody kill

PYTHON = ~/Documentos/miniconda3/envs/spade/bin/python

restart: prosody_stop prosody_start prosody

prosody:
	@tail -f -n 50 /var/log/prosody/prosody.log

prosody_stop:
	@sudo /etc/init.d/prosody stop

prosody_start:
	@sudo /etc/init.d/prosody start

e1:
	@echo 'Exemplo Emissor/Recetor'
	@echo ''
	@echo '' 
	@$(PYTHON) -m mas examples/exemplo_emissor_recetor/recetor.py Recetor localhost -r 3 &
	@$(PYTHON) -m mas examples/exemplo_emissor_recetor/emissor.py Emissor localhost

e2:
	@echo 'Exemplo com Sincronizador'
	@echo ''
	@echo '' 
	@$(PYTHON) -m mas examples/exemplo_sincronizacao/sincronizador.py Sync localhost &
	@$(PYTHON) -m mas examples/exemplo_sincronizacao/gestor.py Gestor localhost &
	@$(PYTHON) -m mas examples/exemplo_sincronizacao/consumidor.py consumidor localhost -r 2 

kill:
	-pkill -f recetor.py
	-pkill -f emissor.py
	-pkill -f sincronizador.py
	-pkill -f gestor.py
	-pkill -f consumidor.py
