import configparser
from dataclasses import dataclass
from pathlib import Path


@dataclass
class IniFile:
    path: Path
    config: configparser.ConfigParser

    @classmethod
    def load(cls, path: Path) -> "IniFile":
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(path, encoding="utf-8")
        return cls(path=path, config=config)

    def add_section(self, name: str) -> None:
        if not self.config.has_section(name):
            self.config.add_section(name)

    def get_key_value(self, section: str, key: str) -> str:
        return self.config.get(section, key)

    def set_key_value(self, section: str, key: str, value: str) -> None:
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as file_handle:
            self.config.write(file_handle)
