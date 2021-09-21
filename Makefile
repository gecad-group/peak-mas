.PHONY: prosody prosody_stop prosody_start example1

.SILENT: example1 prosody kill

PYTHON = ~/Documentos/miniconda3/envs/spade/bin/python

prosody:
	@tail -f -n 50 /var/log/prosody/prosody.log

prosody_stop:
	@sudo /etc/init.d/prosody stop

prosody_start:
	@sudo /etc/init.d/prosody start

e1:
	@echo 'Exemplo 1'
	@echo ''
	@echo '' 
	@$(PYTHON) exemplo_basico.py

e2:
	@echo 'Exemplo Emissor/Recetor'
	@echo ''
	@echo '' 
	@$(PYTHON) examples/exemplo_emissor_recetor/recetor.py > examples/outputs/exemplo_emissor_recetor/recetor.out &
	@$(PYTHON) examples/exemplo_emissor_recetor/emissor.py > examples/outputs/exemplo_emissor_recetor/emissor.out &

e3:
	@echo 'Exemplo com Sincronizador'
	@echo ''
	@echo '' 
	@$(PYTHON) examples/exemplo_sincronizacao/sincronizador.py > examples/outputs/exemplo_sincronizacao/sincronizador.out &
	@$(PYTHON) examples/exemplo_sincronizacao/gestor.py > examples/outputs/exemplo_sincronizacao/gestor.out &
	@$(PYTHON) examples/exemplo_sincronizacao/consumidor.py alfredo > examples/outputs/exemplo_sincronizacao/consumidor.out &
	@$(PYTHON) examples/exemplo_sincronizacao/consumidor.py antonio > examples/outputs/exemplo_sincronizacao/consumidor.out &

kill:
	-pkill -f recetor.py
	-pkill -f emissor.py
	-pkill -f sincronizador.py
	-pkill -f gestor.py
	-pkill -f consumidor.py
