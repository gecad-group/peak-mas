from abc import ABCMeta as _ABCMeta
from abc import abstractmethod
from datetime import datetime

from aioxmpp import JID

from peak import Agent, Template

from .behaviors import StepBehaviour


class SyncAgent(Agent, metaclass=_ABCMeta):
    """Is synchronized by the Synchronizer.

    Every agent that needs to be synchronized needs
    to extend this class.
    """

    def __init__(self, jid: JID, verify_security: bool = False):
        """Inits the SyncAgent with the JID provided.

        Args:
            jid (:obj:`JID`): Agent's XMPP identifier.
            verify_security (bool, optional): If True, verifies the SSL certificates.
                Defaults to False.
        """
        super().__init__(jid, verify_security)
        template_step = Template()
        template_step.set_metadata("sync", "step")
        template_stop = Template()
        template_stop.set_metadata("sync", "stop")
        template = template_step | template_stop
        self.add_behaviour(StepBehaviour(), template)

    @abstractmethod
    async def step(self, period: int, time: datetime = None):
        """Executed at each tick of the Synchronizer clock.

        To be implemented by the user.

        Args:
            period (int): Number of the current period.
            time (datetime, optional): Current datetime inside the simulation. It must be
                configured in the Synchronizer."""
        raise NotImplementedError()
