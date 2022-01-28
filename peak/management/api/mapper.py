import domain
import models

class AgentMapper:

    @staticmethod
    def domain_to_model(agent_domain: domain.Agent) -> models.Agent:
        return models.Agent(jid = agent_domain.jid, player_type = agent_domain.player_type)

    @staticmethod
    def model_to_domain(agent_model: models.Agent) -> domain.Agent:
        return domain.Agent(agent_model.jid, agent_model.player_type)

    @staticmethod
    def dto_to_domain(agent_dto: dict) -> domain.Agent:
        return domain.Agent(agent_dto['jid'], agent_dto['player_type'])

    @staticmethod
    def domain_to_dto(agent_domain: domain.Agent) -> dict:
        return {'jid': agent_domain.jid, 'player_type': agent_domain.player_type}