
from typing_extensions import Self
from typing import ClassVar
from pathlib import Path

import tomli_w
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, TomlConfigSettingsSource

from mqga.log import log

def SimpleConfig(paths: str | Path | list[Path] = "plugin.toml"):
    if isinstance(paths, str):
        paths = Path(paths)
    main_file = paths if isinstance(paths, Path) else paths[0]

    class BaseConfig(BaseSettings):
        model_config = SettingsConfigDict(toml_file=paths)

        _instance: ClassVar[Self | None] = None

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            return (TomlConfigSettingsSource(settings_cls), init_settings)
        
        @classmethod
        def is_init(cls):
            return cls._instance is not None

        @classmethod
        def get(cls):
            """ 创建或获取一个配置对象 """
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

        def save(self, path: Path = None):
            """ 如果当前配置不为空，保存至配置文件 """
            if path is None:
                path = main_file
            config = self.model_dump(exclude_none=True)
            if config:
                with path.open("wb") as f:
                    tomli_w.dump(config, f)
                log.debug(f"已更新配置文件：{path.as_posix()}")
    return BaseConfig


__all__ = ["SimpleConfig"]
