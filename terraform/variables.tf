variable "db_username" {
  description = "Username for the RDS instance"
  type        = string
  default     = "appuser"
}

variable "db_password" {
  description = "Password for the RDS instance"
  type        = string
  default     = "AppPass123!"
}

variable "git_repo" {
  description = "Git repository to clone for the Flask app"
  type        = string
  default     = "https://github.com/your-username/FlaskApp-withDbConnect.git"
}
