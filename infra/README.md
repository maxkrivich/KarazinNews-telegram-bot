# RSS bot infrastructure
Infrastructure for the application has been built on top of the PaaS cloud (Heroku) and provisioned by Terraform Cloud. The current setup has two environments (staging/production) with additional Heroku-addons for a database (Heroku-PostgreSQL) and Scheduler (Heroku-Scheduler).

![image](https://user-images.githubusercontent.com/12199867/101882427-2792d700-3b96-11eb-9650-65a5b05dda42.png)
![image](https://user-images.githubusercontent.com/12199867/101882368-177af780-3b96-11eb-9a03-b12803a934e2.png)
![image](https://user-images.githubusercontent.com/12199867/102593988-ec545300-4115-11eb-833d-32378af2816d.png)


### terraform.tfvars example
```tf
heroku_pipeline_name = "pipeline"

heroku_staging_app = "<app-name>-staging"
heroku_production_app = "<app-name>-production"

heroku_region = "eu"

heroku_staging_database       = "heroku-postgresql:hobby-dev"
heroku_staging_scheduler_plan = "scheduler:standard"

heroku_production_database       = "heroku-postgresql:hobby-dev"
heroku_production_scheduler_plan = "scheduler:standard"

heroku_app_buildpacks = [
  "heroku/python",
]
```


#
> Note:
>
> In order to use terraform scripts, you have to have a Heroku account and some tool for state management either Terraform Cloud or any other storage services (such as AWS S3/GCP Storage, etc.).