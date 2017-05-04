import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    HOST = '0.0.0.0'
    SSL_DISABLE = os.environ.get('SSL_DISABLE', False)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    CASSANDRA_HOSTS = os.environ.get('CASSANDRA_HOSTS', 'cassandra').split(',')
    CASSANDRA_KEYSPACE = os.environ.get('CASSANDRA_KEYSPACE', 'points')
    CQLENG_ALLOW_SCHEMA_MANAGEMENT = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = False
    SSL_DISABLE = True
    CASSANDRA_KEYSPACE = 'dev'
    CASSANDRA_HOSTS = ['127.0.0.1']


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'secret'
    CASSANDRA_HOSTS = ['127.0.0.1']
    CASSANDRA_KEYSPACE = 'test'


class ProductionConfig(Config):

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'unix': UnixConfig,

    'default': DevelopmentConfig
}
