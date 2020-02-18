import os
import logging.config

LOGLEVEL = os.environ.get('LOGLEVEL', 'info').upper()
LOGGING_CONFIG = None

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        '': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
        'results': {
            'level': LOGLEVEL,
            'handlers': ['console'],
            'propagate': False,
        },
    },
})
