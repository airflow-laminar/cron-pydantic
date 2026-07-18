# How-to guides

These guides cover common crontab modeling and integration tasks.

## How to load a YAML crontab

Create `cron.yaml`:

```yaml
environment:
  PATH: /usr/local/bin:/usr/bin
job:
  cleanup:
    schedule: "30 3 * * sun"
    command: /opt/jobs/cleanup
```

Load and render it:

```python
from cron_pydantic import CronConfiguration

config = CronConfiguration.load("cron.yaml")
print(config.to_cron())
```

Use `.yaml` or `.yml` for model input. Other suffixes are parsed as crontab
text.

## How to render a system crontab

Set `system=True` and provide a user for every job:

```python
from cron_pydantic import CronConfiguration

config = CronConfiguration.model_validate(
    {
        "system": True,
        "job": {
            "index": {
                "schedule": "@hourly",
                "user": "search",
                "command": "/opt/search/reindex",
            }
        },
    }
)

print(config.to_cron())
```

The rendered entry contains the system-crontab user column:

```text
@hourly search /opt/search/reindex
```

## How to convert jobs for airflow-config

Install `airflow-cron` and `airflow-config`, then place generated DAG models in
an Airflow configuration:

```python
from airflow_config import Configuration
from airflow_cron import create_dags
from cron_pydantic import CronConfiguration

cron = CronConfiguration.load("cron.yaml")
config = Configuration(dags=create_dags(cron))
config.generate("generated_dags")
```

Refer to the [airflow-cron how-to guides](https://github.com/airflow-laminar/airflow-cron/blob/main/docs/src/how-to.md)
for Airflow-specific defaults and compatibility limits.

## How to deploy rendered content

Write to a staging path first:

```python
staged = config.write("build/my-crontab")
```

Pass `staged` to the deployment mechanism that owns the destination, such as a
configuration-management system or a reviewed `crontab` command. This avoids
silently replacing entries managed by another tool.
