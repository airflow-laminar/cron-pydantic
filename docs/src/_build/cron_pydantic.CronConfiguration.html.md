# cron_pydantic.CronConfiguration

### *pydantic model* cron_pydantic.CronConfiguration[[source]](../../../_modules/cron_pydantic/models.html.md#CronConfiguration)

Bases: `BaseModel`

Environment and named jobs rendered as one crontab file.

#### *field* job *: dict[str, [CronJobConfiguration](cron_pydantic.CronJobConfiguration.html.md#cron_pydantic.CronJobConfiguration)]* *[Required]*

#### *field* environment *: dict[str, str]* *[Optional]*

#### *field* system *: bool* *= False*

#### *field* path *: Path | None* *= None*

#### to_cron() → str[[source]](../../../_modules/cron_pydantic/models.html.md#CronConfiguration.to_cron)

#### write(path: Path | str | None = None) → Path[[source]](../../../_modules/cron_pydantic/models.html.md#CronConfiguration.write)

#### *classmethod* from_cron(contents: str, , system: bool = False, path: Path | None = None) → Self[[source]](../../../_modules/cron_pydantic/models.html.md#CronConfiguration.from_cron)

#### *classmethod* load(path: Path | str) → Self[[source]](../../../_modules/cron_pydantic/models.html.md#CronConfiguration.load)
