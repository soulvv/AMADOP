# AMADOP 

AMADOP is an advanced, AI-driven microservices platform designed for social connectivity, content generation, and autonomous self-healing. 

It functions as a modern ecosystem with deeply integrated artificial intelligence to automate security, moderation, and infrastructure management.

## 🌟 Key Features

### 🏗️ Microservices Architecture
The platform is broken down into independent, containerized services:
- **Auth Service:** User registration, login, and secure token-based authentication.
- **Post Service:** Creation, retrieval, and management of user-generated content.
- **Comment Service:** Discussions and replies attached to posts.
- **Notification Service:** Centralized hub for real-time user alerts.

### 🤖 AI Integration
The dedicated **AI Service** acts as the intelligent brain of the platform:
- **Autonomous Security Agent:** Continuously queries system metrics to detect active cyber threats (like brute-force attempts or DDoS spikes).
- **Autonomous DevOps Agent:** A background loop that continuously monitors internal service health, latency trends, and CPU/memory anomalies.
- **Content Moderation & Summarization:** Automatically analyzes posts to flag toxic content and generate summaries.

### 📊 Enterprise-Grade Observability
- **Prometheus Metrics:** Every microservice exposes deep performance metrics.
- **Grafana Dashboards:** Visualizes live traffic, error rates, pod health, and AI background agent statuses.
- **Kubernetes-Ready:** Deployed via K8s, the system can automatically restart failing pods and scale services using Horizontal Pod Autoscalers (HPA).

## 🚀 Getting Started

*Note: The complete source code and deployment manifests are located on the `feature` branch of this repository.*
