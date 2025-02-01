variable "credentials" {
  description = "The path to the service account credentials"
  default     = "./keys/my-project-id.json"
}

variable "project" {
  description = "The project ID"
  default     = "data-engineering-zoomcamp"
}

variable "region" {
  description = "The region of the resources"
  default     = "us-central1"
}

variable "location" {
  description = "The location of the resources"
  default     = "US"

}

variable "bq_dataset_name" {
  description = "The name of the BigQuery dataset"
  default     = "demo_dataset"
}

variable "gcs_bucket_name" {
  description = "The name of the GCS bucket"
  default     = "main-bucket"
}

variable "gcs_storage_class" {
  description = "The storage class of the GCS bucket"
  default     = "STANDARD"
}