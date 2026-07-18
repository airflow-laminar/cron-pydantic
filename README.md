# cron-pydantic

Typed, YAML-friendly models for cron schedules, jobs, and crontab files.

[![Build Status](https://github.com/airflow-laminar/cron-pydantic/actions/workflows/build.yaml/badge.svg?branch=main&event=push)](https://github.com/airflow-laminar/cron-pydantic/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/airflow-laminar/cron-pydantic/branch/main/graph/badge.svg)](https://codecov.io/gh/airflow-laminar/cron-pydantic)
[![License](https://img.shields.io/github/license/airflow-laminar/cron-pydantic)](https://github.com/airflow-laminar/cron-pydantic)
[![PyPI](https://img.shields.io/pypi/v/cron-pydantic.svg)](https://pypi.python.org/pypi/cron-pydantic)

```python
from cron_pydantic import CronConfiguration

config = CronConfiguration.model_validate(
    {
        "environment": {"PATH": "/usr/local/bin:/usr/bin"},
        "job": {
            "backup": {
                "schedule": "0 2 * * *",
                "command": "/opt/jobs/backup",
            }
        },
    }
)

print(config.to_cron())
```

`cron-pydantic` validates five-field and special schedules, renders user and
system crontabs, parses existing crontab text, and loads YAML. File output is
explicit; the package never installs or replaces a host crontab.

## Documentation

- [Tutorial: build a crontab](docs/src/tutorial.md)
- [How-to guides](docs/src/how-to.md)
- [Why modeling and installation are separate](docs/src/explanation.md)
- [API reference](docs/src/api.md)

Published documentation is available at
[airflow-laminar.github.io/cron-pydantic](https://airflow-laminar.github.io/cron-pydantic/).

## Ecosystem

- [supervisor-pydantic](https://github.com/airflow-laminar/supervisor-pydantic) models supervisord processes.
- [systemd-pydantic](https://github.com/airflow-laminar/systemd-pydantic) models systemd services and timers.
- [airflow-supervisor](https://github.com/airflow-laminar/airflow-supervisor) manages supervisord jobs from Airflow.
- [airflow-cron](https://github.com/airflow-laminar/airflow-cron) converts cron jobs into Airflow DAG models.
- [airflow-systemd](https://github.com/airflow-laminar/airflow-systemd) manages systemd services from Airflow.
- [airflow-pydantic](https://github.com/airflow-laminar/airflow-pydantic) supplies declarative Airflow models.
- [airflow-config](https://github.com/airflow-laminar/airflow-config) loads YAML-based Airflow configurations.

> [!NOTE]
> This library was generated using [copier](https://copier.readthedocs.io/en/stable/) from the [Base Python Project Template repository](https://github.com/python-project-templates/base).
