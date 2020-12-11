# Addons

# Develop Addons
resource "heroku_addon" "database_staging" {
  app = heroku_app.staging.name
  plan = var.heroku_staging_database
}

resource "heroku_addon" "scheduler_staging" {
  app = heroku_app.staging.name
  plan = var.heroku_staging_scheduler_plan
}

# Production Addons
resource "heroku_addon" "database_production" {
  app = heroku_app.production.name
  plan = var.heroku_production_database
}

resource "heroku_addon" "scheduler_production" {
  app = heroku_app.production.name
  plan = var.heroku_production_scheduler_plan
}