# Heroku Provider variables
variable "heroku_email" {}
variable "heroku_api_key" {}

# Pipeline variables
variable "heroku_pipeline_name" {}

# Apps variables
variable "heroku_staging_app" {}
variable "heroku_production_app" {}
variable "heroku_region" {}
variable "heroku_app_buildpacks" {
  type = list
}

# Addons variable develop
variable "heroku_staging_database" {}
variable "heroku_staging_scheduler_plan" {}

# Addons variable production
variable "heroku_production_database" {}
variable "heroku_production_scheduler_plan" {}
