#configuration variables
class BaseConfig(object):
    '''
    Base config class (Default settings)
    '''
    DEBUG = True
    TESTING = False

class ProductionConfig(BaseConfig):
    '''
    Production specific config
    '''
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    '''
    Development enviroment specific configuration
    '''
    DEBUG = True
    TESTING = True