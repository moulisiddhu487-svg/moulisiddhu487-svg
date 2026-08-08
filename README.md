<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0A0E27,50:151A3D,100:E63946&height=220&section=header&text=Mouli%20Godaba&fontSize=55&fontColor=FFFFFF&fontAlignY=38&desc=DevOps%20Engineer%20%7C%20Cloud%20%26%20Infrastructure%20Automation&descAlignY=58&descSize=18&animation=fadeIn" width="100%"/>

<img src="https://capsule-render.vercel.app/api?type=rect&color=E63946&height=3" width="100%"/>

<br/>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mouli-godaba-121a4525a/)
[![Portfolio](https://img.shields.io/badge/Portfolio-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://mouli-portfolio-six.vercel.app/)
[![Gmail](https://img.shields.io/badge/Gmail-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:moulisiddhu487@gmail.com)

</div>

<br/>

## 🛠️ Technical Stack

<div align="center">

**Cloud & Infrastructure as Code**

![AWS](https://img.shields.io/badge/AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![Azure](https://img.shields.io/badge/Azure-0089D6?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)

**Containers & Orchestration**

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-0F1689?style=for-the-badge&logo=helm&logoColor=white)

**CI/CD & Observability**

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white)

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=E63946&height=3" width="100%"/>

## ⚡ Featured Project — Serverless Resume API

A cloud-native backend that serves my resume data as JSON over a REST endpoint — fully serverless on Azure, scales automatically, zero compute cost when idle.

- **Architecture:** Azure Function triggers on HTTP GET, retrieves structured resume JSON (experience, skills, certifications), returns it with a 200 OK response.
- **CI/CD:** GitHub Actions workflow deploys to Azure automatically on every push to main — no manual deployment steps.
- **API Security:** Configured CORS to explicitly allow only trusted origins after debugging a browser-side CORS block when calling the API from my portfolio frontend.
- **Debugged a real production issue:** Resolved an SCM authentication failure between GitHub Actions and Azure by correctly wiring the Function App's publish profile into GitHub Secrets.
- **Roadmap:** Migrating hardcoded data to Azure Cosmos DB, adding API Management for rate-limiting and view analytics.

<div align="center">

[![Live Endpoint](https://img.shields.io/badge/Live_Endpoint-E63946?style=for-the-badge&logo=fastapi&logoColor=white)](https://resume-api-30847.azurewebsites.net/api/cv)
[![Source Code](https://img.shields.io/badge/Source_Code-24292F?style=for-the-badge&logo=github&logoColor=white)](https://github.com/moulisiddhu487-svg/azure-resume-api)

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=E63946&height=3" width="100%"/>

## 🚀 Production-Ready Auto-Healing K8s & Observability Suite

Production-grade infrastructure for a multi-service app, built to demonstrate reliability engineering — not just "I ran a container."

- **Infrastructure as Code:** Provisioned a managed AWS EKS cluster with dedicated VPC networking using modular Terraform scripts.
- **Self-Healing:** Packaged microservices into versioned Helm charts, configuring Liveness/Readiness probes so Kubernetes automatically detects and restarts crashed pods — zero manual intervention.
- **Zero-Downtime CI/CD:** Built a GitHub Actions pipeline that builds the Docker image, pushes it to a registry, and runs a rolling `helm upgrade` on every push — new pods come up before old ones go down.
- **Full-Stack Observability:** Deployed Prometheus & Grafana via Helm to monitor live cluster CPU, memory, and pod network traffic on a real-time dashboard.

<div align="center">

![In Progress](https://img.shields.io/badge/Status-In_Progress-E63946?style=for-the-badge&logo=progress&logoColor=white)

</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=E63946&height=3" width="100%"/>

## 📌 Also Building

- **[job-track-hub](https://github.com/moulisiddhu487-svg/job-track-hub)** — Full-stack job application tracker (React/TypeScript, Node.js/Express, Supabase), Docker-deployed on AWS EC2.
- **[Mouli-Portfolio](https://github.com/moulisiddhu487-svg/Mouli-Portfolio)** — Personal portfolio site, live at [mouli-portfolio-six.vercel.app](https://mouli-portfolio-six.vercel.app/).

<br/>

<div align="center">

## 📊 GitHub Stats

<img height="165" src="https://github-readme-stats.vercel.app/api?username=moulisiddhu487-svg&show_icons=true&hide_border=true&bg_color=0A0E27&title_color=E63946&icon_color=E63946&text_color=FFFFFF&ring_color=E63946"/>
<img height="165" src="https://github-readme-streak-stats.herokuapp.com/?user=moulisiddhu487-svg&hide_border=true&background=0A0E27&stroke=E63946&ring=E63946&fire=E63946&currStreakLabel=E63946&sideNums=FFFFFF&sideLabels=FFFFFF&dates=FFFFFF"/>

<img src="https://github-readme-stats.vercel.app/api/top-langs/?username=moulisiddhu487-svg&layout=compact&hide_border=true&bg_color=0A0E27&title_color=E63946&text_color=FFFFFF"/>

</div>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:E63946,100:0A0E27&height=100&section=footer" width="100%"/>
