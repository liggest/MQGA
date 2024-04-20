
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
