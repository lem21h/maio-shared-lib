from dataclasses import (
    asdict,
    dataclass,
)


@dataclass(frozen=True)
class WorkerConfig:
    __slots__ = ('interval', 'retries', 'try_again_interval')

    interval: int
    retries: int
    try_again_interval: int

    @classmethod
    def from_json(cls, json_data: dict):
        return WorkerConfigJsonMapper.from_json(json_data)

    def to_dict(self) -> dict:
        return asdict(self)


class WorkerConfigJsonMapper:
    __slots__ = ()

    class Fields:
        __slots__ = ()
        INTERVAL = 'interval'
        RETRIES = 'retries'
        TRY_AGAIN_INTERVAL = 'tryAgainInterval'

    @classmethod
    def from_json(cls, json_data: dict) -> WorkerConfig:
        _ = cls.Fields

        interval = int(json_data[_.INTERVAL])
        retries = int(json_data[_.RETRIES])
        try_again_interval = int(json_data[_.TRY_AGAIN_INTERVAL])

        return WorkerConfig(interval, retries, try_again_interval)
