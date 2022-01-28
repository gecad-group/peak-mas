import flask
import jsonschema
import services
import schemas

agent_blueprint = flask.Blueprint('agent_blueprint', __name__)

@agent_blueprint.route('', methods=['POST'])
def register_agents():
    request_json = flask.request.json
    jsonschema.validate(request_json, schema=schemas.agent_schema)
    return services.register_agent(request_json)