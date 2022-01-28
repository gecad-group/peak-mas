import repositories
import mapper

def register_agent(agent_dto: dict) -> dict:
    agent_domain = mapper.AgentMapper.dto_to_domain(agent_dto)
    repo = repositories.AgentRepository()
    agent_domain = repo.add(agent_domain)
    new_dto = mapper.AgentMapper.domain_to_dto(agent_domain)
    return new_dto

