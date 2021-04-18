import logging
import sys
from app.lib.controller import Controller
from app.lib.config import read_from_env


if __name__ == "__main__":
    config = read_from_env()
    print(f"debug: {config.debug}")
    if config.debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    controller = Controller(config)
    controller.run_forever()