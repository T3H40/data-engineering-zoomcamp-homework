terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "6.18.1"
    }
  }
}

provider "google" {
  # Configuration options
  project     = "my-project-id" # Replace this with the real ID!
  region      = "us-central1"
}