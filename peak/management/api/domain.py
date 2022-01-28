import re

class Agent:

    PLAYER_TYPE = ['consumer', 'prosumer', 'producer']

    def __init__(self, jid, player_type) -> None:
        self.jid = jid
        self.player_type = player_type

    @property
    def jid(self):
        return self.__jid

    @jid.setter
    def jid(self, value : str):
        jid = value.lower()
        self.validate_jid(jid)
        self.__jid = jid


    def validate_jid(self, jid):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\b'
        if not re.fullmatch(regex, jid):
            raise ValueError('JID wrong format')

    @property
    def player_type(self):
        return self.__player_type

    @player_type.setter
    def player_type(self, value : str):
        player_type = value.lower()
        self.validate_player_type(player_type)
        self.__player_type = player_type

    def validate_player_type(self, player_type):
        if player_type not in self.PLAYER_TYPE:
            raise ValueError("Player Type not valid")

