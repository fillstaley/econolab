"""...
"""


import logging
import logging.config


def setup_logging(default_level=logging.INFO):
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": default_level,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": default_level,
        },
        "loggers": {
            "econolab": {
                "handlers": ["console"],
                "level": default_level,
                "propagate": False,
            },
        },
    }
    logging.config.dictConfig(logging_config)
