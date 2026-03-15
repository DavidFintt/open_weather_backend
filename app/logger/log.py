import logging
import logging.config
import threading
import yaml

from pathlib import Path


class Log:
    _configured = False
    _lock = threading.Lock()

    @classmethod
    def configure(
        cls,
        config_filename: str = "logging.yaml",
    ) -> None:
        if cls._configured:
            return
        with cls._lock:
            if cls._configured:
                return
            config_path = Path(__file__).with_name(config_filename)
            with open(config_path, "rt", encoding="utf-8") as f:
                config = yaml.safe_load(f.read())
            for handler in config.get("handlers", {}).values():
                if "filename" in handler:
                    Path(handler["filename"]).parent.mkdir(parents=True, exist_ok=True)
            logging.config.dictConfig(config)
            cls._configured = True

    @classmethod
    def get_logger(cls, name: str | None = None) -> logging.Logger:
        cls.configure()
        return logging.getLogger(name)
