# project/server/config.py

class DevelopmentConfig:
    """Development configuration."""
    DEBUG = True
    API_USERNAME = 'a@pi.com'
    API_PWD = 'api123'
    URL = 'http://127.0.0.1:5000/'
    TEAM_SERVER = 'PIEREK-PC'
    TEAM_DATABASE = 'TeamExport'
    TEAM_USER = 'test'
    TEAM_PWD = 'test'

class DevelopmentSlawekConfig:
    """Development slawek configuration."""
    DEBUG = True
    API_USERNAME = 'a@pi.com'
    API_PWD = 'api123'
    URL = 'http://127.0.0.1:5000/'
    TEAM_SERVER = 'localhost\MSSQLSERVER01'
    TEAM_DATABASE = 'TeamExport'
    TEAM_USER = 'teampolska'
    TEAM_PWD = 'teampolska'

class ProductionConfig:
    """Development slawek configuration."""
    DEBUG = True
    API_USERNAME = 'a@pi.com'
    API_PWD = 'api123'
    URL = 'http://127.0.0.1:5000/'
    TEAM_SERVER = 'localhost\MSSQLSERVER01'
    TEAM_DATABASE = 'TeamExport'
    TEAM_USER = 'teampolska'
    TEAM_PWD = 'teampolska'

    

