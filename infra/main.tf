terraform {
  required_providers {
    heroku = {
      source  = "heroku/heroku"
      version = "~> 3.10"
    }
  }
}

provider "heroku" {
  email = var.heroku_email
  api_key = var.heroku_api_key
}