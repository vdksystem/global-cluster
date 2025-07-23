provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "helm_release" "argocd" {
  name = "argocd"

  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  namespace        = "argocd"
  create_namespace = true
  version          = "8.1.4"

  values = [file("${path.module}/argocd.yaml")]
}

data "http" "argocd_application" {
  url = "https://raw.githubusercontent.com/vdksystem/global-cluster/refs/heads/main/gitops/applications.yaml"
}

resource "kubectl_manifest" "application" {
  yaml_body = data.http.argocd_application.response_body
  depends_on = [
    helm_release.argocd
  ]
}
