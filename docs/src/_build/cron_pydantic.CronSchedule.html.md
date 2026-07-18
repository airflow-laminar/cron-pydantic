# cron_pydantic.CronSchedule

### *pydantic model* cron_pydantic.CronSchedule

Bases: `BaseModel`

Five-field Vixie/Cronie schedule.

#### *field* minute *: str | int* *= '\*'*

#### *field* hour *: str | int* *= '\*'*

#### *field* day_of_month *: str | int* *= '\*'*

#### *field* month *: str | int* *= '\*'*

#### *field* day_of_week *: str | int* *= '\*'*

#### to_cron() → str

#### *classmethod* from_cron(expression: str) → Self
