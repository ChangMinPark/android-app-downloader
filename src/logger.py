import logging as lg
import sys


class Logger:
    _instance = None

    @staticmethod
    def get_instance():
        if Logger._instance == None:
            Logger()
        return Logger._instance

    def __init__(self):
        if Logger._instance != None:
            raise Exception("Singleton class cannot be instantiated more \
                    than once.")
        self._logger = lg.getLogger()
        self._logger.setLevel(lg.INFO)

        handler = lg.StreamHandler(sys.stdout)
        handler.setLevel(lg.INFO)
        formatter = lg.Formatter('%(asctime)s - %(levelname)s : %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        Logger._instance = self

    def info(self, msg: str) -> None:
        self._logger.info(msg)

    def debug(self, msg: str) -> None:
        self._logger.debug(msg)

    def warning(self, msg: str) -> None:
        self._logger.warning(msg)
