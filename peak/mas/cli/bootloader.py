import logging as _logging
import os
import sys
import time
from pathlib import Path
import importlib

from aioxmpp import JID


def boot_agent(file: Path, jid: JID, properties: Path, logging:int, verify_security: bool):
    agent_name = jid.localpart + ('_' + jid.resource if jid.resource else '')
    logs_path = os.path.join(str(file.parent.absolute()), 'logs')
    log_file = os.path.join(logs_path, agent_name + '.log')

    os.makedirs(logs_path, exist_ok = True)
    _logging.basicConfig(filename=log_file, filemode='w', level=logging)
    logger = _logging.getLogger('peak.mas.bootloader')
    logger.debug('creating agent')

    agent_class = get_class(file)
    if properties:
        properties = get_class(properties)(agent_name)
        properties = properties.extract(agent_name)
    else:
        properties = None
    
    agent_instance = agent_class(jid, properties, verify_security)
    logger.info('starting agent')
    agent_instance.start(True).result()
    logger.info('agent started')
    try:
        while agent_instance.is_alive():
            time.sleep(10)
        logger.info('execution suceeded')
    except Exception as e:
        logger.error('AGENT CRACHED')
        logger.exception(e)
        agent_instance.stop()
    except KeyboardInterrupt:
        logger.info('stoping agent... (Keyboard Interrupt)')
        agent_instance.stop()
    logger.info('agent clean exit')


def get_class(file: Path):
    module_path, module_file = os.path.split(file.absolute())
    module_name = module_file.split('.')[0]
    sys.path.append(module_path)
    module = importlib.import_module(module_name)
    return getattr(module, module_name)
