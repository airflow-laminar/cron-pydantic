# cron_pydantic.CronSchedule

### *pydantic model* cron_pydantic.CronSchedule[[source]](../../../_modules/cron_pydantic/models.html.md#CronSchedule)

Bases: `BaseModel`

Five-field Vixie/Cronie schedule.

#### *field* minute *: str | int* *= '\*'*

#### *field* hour *: str | int* *= '\*'*

#### *field* day_of_month *: str | int* *= '\*'*

#### *field* month *: str | int* *= '\*'*

#### *field* day_of_week *: str | int* *= '\*'*

#### to_cron() → str[[source]](../../../_modules/cron_pydantic/models.html.md#CronSchedule.to_cron)

#### *classmethod* from_cron(expression: str) → Self[[source]](../../../_modules/cron_pydantic/models.html.md#CronSchedule.from_cron)
