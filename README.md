<div align="center">

<img src="./assets/banner.png" width="100%"/>

</div>

<br/><br/>

<img src="./assets/hdr-about.png" width="600"/>

Aspiring DevOps & Cloud Engineer with a BSc in Mathematics, Electronics & Computer Science, plus hands-on DevOps training covering containerization, orchestration, infrastructure as code, and CI/CD automation. Deployed and hosted a serverless application on Azure Functions with an automated GitHub Actions CI/CD pipeline, including auth and cross-origin configuration. Currently pursuing the Microsoft Azure AZ-104 certification.

```
currently_building : "Production-ready auto-healing K8s infrastructure"
currently_learning  : "Azure AZ-104", "AWS Cloud Practitioner"
trained_at          : "Xtream Tech, Hyderabad — Docker, K8s, Terraform, Ansible, AWS, Azure"
ask_me_about        : "Serverless deployments, GitHub Actions CI/CD, K8s self-healing"
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=FF2800&height=2" width="100%"/>

<img src="./assets/hdr-skills.png" width="600"/>

<div align="center">

**Cloud & Infrastructure as Code**

![AWS](https://img.shields.io/badge/AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![Azure](https://img.shields.io/badge/Azure-0089D6?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![Ansible](https://img.shields.io/badge/Ansible-EE0000?style=for-the-badge&logo=ansible&logoColor=white)

**Containers & Orchestration**

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-0F1689?style=for-the-badge&logo=helm&logoColor=white)

**CI/CD & Observability**

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=jenkins&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white)

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=FF2800&height=2" width="100%"/>

<img src="./assets/hdr-projects.png" width="600"/>

**azure-resume-api** &nbsp; ![Done](https://img.shields.io/badge/DONE-2E7D32?style=flat-square) &nbsp;·&nbsp; **k8s-observability-suite** &nbsp; ![In Progress](https://img.shields.io/badge/IN_PROGRESS-FF2800?style=flat-square)

### azure-resume-api — Serverless Resume API

A cloud-native backend that serves my resume data as JSON over a REST endpoint — fully serverless on Azure, scales automatically, zero compute cost when idle.

- **Architecture:** Azure Function triggers on HTTP GET, retrieves structured resume JSON (experience, skills, certifications), returns it with a 200 OK response.
- **CI/CD:** GitHub Actions workflow deploys to Azure automatically on every push to main — no manual deployment steps.
- **API Security:** Configured CORS to explicitly allow only trusted origins after debugging a browser-side CORS block when calling the API from my portfolio frontend.
- **Debugged a real production issue:** Resolved an SCM authentication failure between GitHub Actions and Azure by correctly wiring the Function App's publish profile into GitHub Secrets.
- **Roadmap:** Migrating hardcoded data to Azure Cosmos DB, adding API Management for rate-limiting and view analytics.

<div align="center">

[![Live Endpoint](https://img.shields.io/badge/Live_Endpoint-FF2800?style=for-the-badge&logo=fastapi&logoColor=white)](https://resume-api-30847.azurewebsites.net/api/cv)
[![Source Code](https://img.shields.io/badge/Source_Code-24292F?style=for-the-badge&logo=github&logoColor=white)](https://github.com/moulisiddhu487-svg/azure-resume-api)

</div>

<br/>

### k8s-observability-suite — Production-Ready Auto-Healing K8s & Observability Suite

Production-grade infrastructure for a multi-service app, built to demonstrate reliability engineering — not just "I ran a container."

- **Infrastructure as Code:** Provisioned a managed AWS EKS cluster with dedicated VPC networking using modular Terraform scripts.
- **Self-Healing:** Packaged microservices into versioned Helm charts, configuring Liveness/Readiness probes so Kubernetes automatically detects and restarts crashed pods — zero manual intervention.
- **Zero-Downtime CI/CD:** Built a GitHub Actions pipeline that builds the Docker image, pushes it to a registry, and runs a rolling `helm upgrade` on every push — new pods come up before old ones go down.
- **Full-Stack Observability:** Deployed Prometheus & Grafana via Helm to monitor live cluster CPU, memory, and pod network traffic on a real-time dashboard.

<img src="https://capsule-render.vercel.app/api?type=rect&color=FF2800&height=2" width="100%"/>

<img src="./assets/hdr-ping.png" width="600"/>

<div align="center">

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mouli-godaba-121a4525a/)
[![Gmail](https://img.shields.io/badge/Gmail-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:moulisiddhu487@gmail.com)
[![Portfolio](https://img.shields.io/badge/Portfolio-24292F?style=for-the-badge&logo=vercel&logoColor=white)](https://mouli-portfolio-six.vercel.app/)

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=FF2800&height=2" width="100%"/>

<img src="./assets/hdr-stats.png" width="600"/>

<div align="center">


<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/moulisiddhu487-svg/moulisiddhu487-svg/output/github-contribution-grid-snake-dark.svg">
  <img alt="red contribution snake animation" src="https://raw.githubusercontent.com/moulisiddhu487-svg/moulisiddhu487-svg/output/github-contribution-grid-snake.svg">
</picture>

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:FF2800,100:0A0E27&height=4" width="100%"/>
