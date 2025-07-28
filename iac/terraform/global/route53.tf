resource "aws_route53_zone" "main" {
  name = var.domain_name
}

resource "aws_acm_certificate" "main_wildcard" {
  domain_name       = "*.${aws_route53_zone.main.name}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.main_wildcard.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  name    = each.value.name
  type    = each.value.type
  zone_id = aws_route53_zone.main.zone_id
  records = [each.value.record]
  ttl     = 60
}

resource "aws_acm_certificate_validation" "wildcard" {
  certificate_arn         = aws_acm_certificate.main_wildcard.arn
  validation_record_fqdns = [
    for record in aws_acm_certificate.main_wildcard.domain_validation_options :record.resource_record_name
  ]
}
