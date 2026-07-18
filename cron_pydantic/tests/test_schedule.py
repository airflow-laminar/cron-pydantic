import pytest
from pydantic import ValidationError

from cron_pydantic import CronJobConfiguration, CronSchedule


def test_schedule_round_trip() -> None:
    expression = "*/15 9-17 1,15 jan-mar mon-fri"

    schedule = CronSchedule.from_cron(expression)

    assert schedule.to_cron() == expression


@pytest.mark.parametrize("random_range", ["~", "~5", "5~", "1~5"])
def test_schedule_accepts_integer_and_cronie_random_range(random_range: str) -> None:
    schedule = CronSchedule(minute=5, hour=random_range)

    assert schedule.to_cron() == f"5 {random_range} * * *"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("minute", 60),
        ("hour", 24),
        ("day_of_month", 0),
        ("month", 13),
        ("day_of_week", 8),
        ("minute", "1 2"),
        ("minute", "*/0"),
        ("minute", "1/2/3"),
        ("minute", "bad"),
        ("minute", "-5"),
        ("minute", "5-"),
    ],
)
def test_schedule_rejects_invalid_fields(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        CronSchedule.model_validate({field: value})


def test_schedule_requires_five_fields() -> None:
    with pytest.raises(ValueError, match="exactly five fields"):
        CronSchedule.from_cron("0 1 * *")


def test_job_accepts_schedule_expression() -> None:
    job = CronJobConfiguration(schedule="0 2 * * *", command="  backup  ")

    assert isinstance(job.schedule, CronSchedule)
    assert job.command == "backup"
    assert job.to_cron() == "0 2 * * * backup"


def test_job_accepts_special_schedule() -> None:
    job = CronJobConfiguration(schedule="@reboot", command="start")

    assert job.to_cron() == "@reboot start"


def test_system_job_requires_user() -> None:
    job = CronJobConfiguration(schedule="@daily", command="backup")

    with pytest.raises(ValueError, match="require a user"):
        job.to_cron(system=True)


def test_system_job_renders_user() -> None:
    job = CronJobConfiguration(schedule="@daily", command="backup", user="root")

    assert job.to_cron(system=True) == "@daily root backup"


@pytest.mark.parametrize("user", ["", "two words"])
def test_job_rejects_invalid_user(user: str) -> None:
    with pytest.raises(ValidationError, match="user cannot"):
        CronJobConfiguration(schedule="@daily", command="backup", user=user)


def test_job_rejects_empty_command() -> None:
    with pytest.raises(ValidationError):
        CronJobConfiguration(schedule="@daily", command="  ")
