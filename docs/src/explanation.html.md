# Why modeling and installation are separate

`cron-pydantic` treats a crontab as data: schedules and commands are validated,
serialized, parsed, and written to an explicit path. It does not treat the
current user’s installed crontab as a private resource it can replace.

That boundary matters because traditional crontabs rarely record ownership.
Several people and deployment tools may edit the same file, while `crontab -r`
and whole-file installation operate on all entries. A model library cannot know
which unmanaged lines are safe to remove. Keeping installation outside the
package makes that ownership decision visible to the caller.

## Cron in the process-management family

Cron starts commands according to wall-clock schedules. It does not supervise a
process after launch or expose a lifecycle API for long-running work.

[supervisor-pydantic](https://github.com/airflow-laminar/supervisor-pydantic)
models a dedicated supervisord process tree.
[systemd-pydantic](https://github.com/airflow-laminar/systemd-pydantic) models
services and timers managed by the host service manager. Timers stay in the
systemd package because they activate and share lifecycle with service units.

For Airflow, [airflow-cron](https://github.com/airflow-laminar/airflow-cron)
translates compatible cron jobs into `airflow-pydantic` DAG models. Airflow then
owns scheduling and execution; no crontab is installed.

## Round-trip metadata

Named jobs render with `# cron-pydantic: <name>` comments. Those comments let a
later parse recover stable dictionary keys and disabled entries. Unnamed entries
from arbitrary crontabs receive generated names such as `job-1`; the command and
schedule remain the authoritative cron data.
