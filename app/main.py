from app.lib.controller import Controller
from app.lib.config import read_from_env


if __name__ == "__main__":
    config = read_from_env()
    controller = Controller(config)
    controller.run_forever()