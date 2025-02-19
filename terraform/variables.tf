terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Provider for us-east-1 (required for ACM certificate for CloudFront)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

variable "app_name" {
  description = "Name of the application"
  type        = string
  default     = "credix-case-fabricio"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "domain_name" {
  # Your custom domain name
  description = "Your custom domain name"
  type        = string
  default     = "credix.pixelbreeders.com"
}

variable "route53_zone_id" {
  # Route 53 Hosted Zone ID for your domain
  description = "Route 53 Hosted Zone ID for your domain"
  type        = string
  default     = "Z00844003U2NSP9OY74Y8"
}

# Frontend dist folder
locals {
  source_dir = "../front/dist"
  files      = fileset(local.source_dir, "**")
}
