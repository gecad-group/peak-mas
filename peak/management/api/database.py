import flask_sqlalchemy

#a base de dados encontra-se num ficheiro a parte para evitar 
#dependencia circular
db = flask_sqlalchemy.SQLAlchemy()