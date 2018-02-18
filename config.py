import os

# Project sections

class Platform(object):
    pass

class Plugins(object):
    pass

class UI(object):
    pass


# General

class Config(Platform, Plugins, UI):
    DEFAULT_ENVIRONMENT = 'Production'


# Environments

class Development(Config):
    DEBUG = True

class Testing(Config):
    pass

class Production(Config):
    pass