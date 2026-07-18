# cron_pydantic.CronJobConfiguration

### *pydantic model* cron_pydantic.CronJobConfiguration

Bases: `BaseModel`

Command and schedule for one crontab entry.

#### *field* schedule *: [CronSchedule](cron_pydantic.CronSchedule.md#cron_pydantic.CronSchedule) | SpecialSchedule* *[Required]*

#### *field* command *: Command* *[Required]*

#### *field* user *: str | None* *= None*

#### *field* enabled *: bool* *= True*

#### to_cron(system: bool = False) → str
