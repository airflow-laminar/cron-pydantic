from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated, Literal, Self, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator

SpecialSchedule = Literal[
    "@reboot",
    "@yearly",
    "@annually",
    "@monthly",
    "@weekly",
    "@daily",
    "@midnight",
    "@hourly",
]
Command = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

_MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
_WEEKDAYS = {"sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6}


def _value(value: str, minimum: int, maximum: int, names: dict[str, int]) -> None:
    normalized = value.lower()
    if normalized in names:
        return
    if not normalized.isdigit() or not minimum <= int(normalized) <= maximum:
        raise ValueError(f"value {value!r} must be between {minimum} and {maximum}")


def _field(value: object, minimum: int, maximum: int, names: dict[str, int] | None = None) -> str:
    names = names or {}
    text = str(value).strip()
    if not text or any(character.isspace() for character in text):
        raise ValueError("cron fields cannot be empty or contain whitespace")
    for item in text.split(","):
        base, separator, step = item.partition("/")
        if separator and (not step.isdigit() or int(step) <= 0 or "/" in step):
            raise ValueError(f"invalid step in cron field: {item!r}")
        if base == "*":
            continue
        range_separator = "~" if "~" in base else "-" if "-" in base else ""
        if range_separator:
            start, end = base.split(range_separator, maxsplit=1)
            if range_separator == "~" and not start and not end:
                continue
            if range_separator == "-" and (not start or not end):
                raise ValueError(f"invalid range in cron field: {item!r}")
            if start:
                _value(start, minimum, maximum, names)
            if end:
                _value(end, minimum, maximum, names)
            continue
        _value(base, minimum, maximum, names)
    return text


class CronSchedule(BaseModel):
    """Five-field Vixie/Cronie schedule."""

    model_config = ConfigDict(extra="forbid")

    minute: str | int = "*"
    hour: str | int = "*"
    day_of_month: str | int = "*"
    month: str | int = "*"
    day_of_week: str | int = "*"

    @field_validator("minute")
    @classmethod
    def _minute(cls, value: object) -> str:
        return _field(value, 0, 59)

    @field_validator("hour")
    @classmethod
    def _hour(cls, value: object) -> str:
        return _field(value, 0, 23)

    @field_validator("day_of_month")
    @classmethod
    def _day_of_month(cls, value: object) -> str:
        return _field(value, 1, 31)

    @field_validator("month")
    @classmethod
    def _month(cls, value: object) -> str:
        return _field(value, 1, 12, _MONTHS)

    @field_validator("day_of_week")
    @classmethod
    def _day_of_week(cls, value: object) -> str:
        return _field(value, 0, 7, _WEEKDAYS)

    def to_cron(self) -> str:
        return f"{self.minute} {self.hour} {self.day_of_month} {self.month} {self.day_of_week}"

    @classmethod
    def from_cron(cls, expression: str) -> Self:
        fields = expression.split()
        if len(fields) != 5:
            raise ValueError("a cron expression requires exactly five fields")
        return cls(minute=fields[0], hour=fields[1], day_of_month=fields[2], month=fields[3], day_of_week=fields[4])


class CronJobConfiguration(BaseModel):
    """Command and schedule for one crontab entry."""

    model_config = ConfigDict(extra="forbid")

    schedule: CronSchedule | SpecialSchedule
    command: Command
    user: str | None = None
    enabled: bool = True

    @field_validator("schedule", mode="before")
    @classmethod
    def _schedule(cls, value: object) -> object:
        if isinstance(value, str) and not value.startswith("@"):
            return CronSchedule.from_cron(value)
        return value

    @field_validator("user")
    @classmethod
    def _user(cls, value: str | None) -> str | None:
        if value is not None and (not value or any(character.isspace() for character in value)):
            raise ValueError("user cannot be empty or contain whitespace")
        return value

    def to_cron(self, system: bool = False) -> str:
        schedule = self.schedule if isinstance(self.schedule, str) else self.schedule.to_cron()
        if system:
            if self.user is None:
                raise ValueError("system crontab jobs require a user")
            return f"{schedule} {self.user} {self.command}"
        return f"{schedule} {self.command}"


def _environment_value(value: str) -> str:
    if not value or value != value.strip() or any(character.isspace() for character in value) or "#" in value:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


class CronConfiguration(BaseModel):
    """Environment and named jobs rendered as one crontab file."""

    model_config = ConfigDict(extra="forbid")

    job: dict[str, CronJobConfiguration]
    environment: dict[str, str] = Field(default_factory=dict)
    system: bool = False
    path: Path | None = None

    @field_validator("environment")
    @classmethod
    def _environment(cls, value: dict[str, str]) -> dict[str, str]:
        for name in value:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                raise ValueError(f"invalid environment variable name: {name!r}")
        return value

    @model_validator(mode="after")
    def _system_users(self) -> Self:
        if self.system and any(item.user is None for item in self.job.values()):
            raise ValueError("system crontab jobs require a user")
        return self

    def to_cron(self) -> str:
        lines = ["# Generated by cron-pydantic"]
        lines.extend(f"{name}={_environment_value(value)}" for name, value in self.environment.items())
        if self.environment and self.job:
            lines.append("")
        for name, item in self.job.items():
            lines.append(f"# cron-pydantic: {name}")
            rendered = item.to_cron(system=self.system)
            lines.append(rendered if item.enabled else f"# {rendered}")
        return "\n".join(lines) + "\n"

    def write(self, path: Path | str | None = None) -> Path:
        destination = Path(path) if path is not None else self.path
        if destination is None:
            raise ValueError("a path is required to write a crontab")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.to_cron())
        return destination

    @classmethod
    def from_cron(cls, contents: str, *, system: bool = False, path: Path | None = None) -> Self:
        environment: dict[str, str] = {}
        jobs: dict[str, CronJobConfiguration] = {}
        pending_name: str | None = None
        for raw_line in contents.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("# cron-pydantic:"):
                pending_name = line.partition(":")[2].strip()
                continue
            if line.startswith("# "):
                if pending_name is None:
                    continue
                enabled = False
                line = line[2:].strip()
            elif line.startswith("#"):
                continue
            else:
                enabled = True
            assignment = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)", line)
            if assignment:
                value = assignment.group(2)
                if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                    value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
                environment[assignment.group(1)] = value
                continue
            fields = line.split(None, 2 if line.startswith("@") and system else 1 if line.startswith("@") else 6 if system else 5)
            expected = 3 if line.startswith("@") and system else 2 if line.startswith("@") else 7 if system else 6
            if len(fields) != expected:
                raise ValueError(f"invalid crontab line: {raw_line!r}")
            if line.startswith("@"):
                schedule: CronSchedule | SpecialSchedule = cast(SpecialSchedule, fields[0])
                user = fields[1] if system else None
                command = fields[2] if system else fields[1]
            else:
                schedule = CronSchedule.from_cron(" ".join(fields[:5]))
                user = fields[5] if system else None
                command = fields[6] if system else fields[5]
            name = pending_name or f"job-{len(jobs) + 1}"
            jobs[name] = CronJobConfiguration(schedule=schedule, command=command, user=user, enabled=enabled)
            pending_name = None
        return cls(job=jobs, environment=environment, system=system, path=path)

    @classmethod
    def load(cls, path: Path | str) -> Self:
        source = Path(path)
        if source.suffix.lower() in {".yaml", ".yml"}:
            return cls.model_validate(yaml.safe_load(source.read_text()))
        return cls.from_cron(source.read_text(), path=source)


load_config = CronConfiguration.load
