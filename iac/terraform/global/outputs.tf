output "tgw_id" {
  value = module.tgw.ec2_transit_gateway_id
}

output "ssh_private_key" {
  value = tls_private_key.global_admins.private_key_pem
  sensitive = true
}

output "ssh_public_key" {
  value = tls_private_key.global_admins.public_key_pem
}

output "route53_zone_id" {
  value = aws_route53_zone.main.zone_id
}

output "acm_certificate_arn" {
  value = aws_acm_certificate.main_wildcard.arn
}

output "ipv4_cidr_blocks" {
  value = local.ip_cidrs
}