import models
import domain
import mapper

class AgentRepository:

    def add(self, agent_domain: domain.Agent) -> domain.Agent:
        agent_model = models.Agent.query.filter_by(jid = agent_domain.jid).first()
        if agent_model:
            agent_model.player_type = agent_domain.player_type
            models.db.session.commit()
        else:
            agent_model = mapper.AgentMapper.domain_to_model(agent_domain)
            models.db.session.add(agent_model)
            models.db.session.commit()
        return mapper.AgentMapper.model_to_domain(agent_model)