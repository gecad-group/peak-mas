.PHONY: prosody prosody_stop prosody_start example1

.SILENT: example1 prosody kill

PEAK = ~/Documentos/miniconda3/envs/peak/bin/python -m mas

restart: prosody_stop prosody_start prosody

prosody:
	@tail -f -n 50 /var/log/prosody/prosody.log

prosody_restart:
	@sudo /etc/init.d/prosody stop
	@sudo /etc/init.d/prosody start

e1:
	@echo 'Exemplo Emissor/Recetor'
	@echo ''
	@echo '' 
	@$(PEAK) examples/exemplo_emissor_recetor/recetor.py Recetor localhost -r 3 &
	@$(PEAK) examples/exemplo_emissor_recetor/emissor.py Emissor localhost

e2:
	@echo 'Exemplo com Sincronizador'
	@echo ''
	@echo '' 
	@$(PEAK) examples/exemplo_sincronizacao/sincronizador.py Sync localhost &
	@$(PEAK) examples/exemplo_sincronizacao/gestor.py Gestor localhost &
	@$(PEAK) examples/exemplo_sincronizacao/consumidor.py consumidor localhost -r 2 

kill:
	-pkill -f recetor.py
	-pkill -f emissor.py
	-pkill -f sincronizador.py
	-pkill -f gestor.py
	-pkill -f consumidor.py
