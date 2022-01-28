import flask
import database
import blueprints
import config

if __name__ == "__main__":

    #config
    app = flask.Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.database_url
    database.db.init_app(app)

    with app.app_context():
        database.db.create_all()           #creates tables 

    #routes
    app.register_blueprint(blueprints.agent_blueprint, url_prefix='/agent')

    app.run(debug=True)
