resource "tls_private_key" "global_admins" {
  algorithm = "RSA"
  rsa_bits  = 4096
}
