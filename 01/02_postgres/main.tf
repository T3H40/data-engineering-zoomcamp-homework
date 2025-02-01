terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "6.18.1"
    }
  }
}

provider "google" {
  # Alternatively to hard coding the credentials,
  # you can use `gcloud default auth-login` to authenticate
  # you can also use the `GOOGLE_CREDENTIALS` environment variable.
  credentials = "./keys/my-project-id.json" # Replace this with the real path!
  project     = "my-project-id"             # Replace this with the real ID!
  region      = "us-central1"
}

resource "google_storage_bucket" "auto-expire" {
    name          = "main-bucket" # this needs to be globally unique
    location      = "US"
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