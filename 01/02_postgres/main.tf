terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.18.1"
    }
  }
}

provider "google" {
  # Alternatively to hard coding the credentials,
  # you can use `gcloud default auth-login` to authenticate
  # you can also use the `GOOGLE_CREDENTIALS` environment variable.
  credentials = file(var.credentials) # Replace this with the real path!
  project     = var.project           # Replace this with the real ID!
  region      = var.region
}

resource "google_storage_bucket" "auto-expire" {
  name          = var.gcs_bucket_name # this needs to be globally unique
  location      = var.location
  storage_class = var.gcs_storage_class
  force_destroy = true

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "demo-dataset" {
  dataset_id = var.bq_dataset_name
  location   = var.location

  delete_contents_on_destroy = true
}