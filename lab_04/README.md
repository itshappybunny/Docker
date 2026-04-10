# Лабораторная работа 4.1. Создание и развертывание полнофункционального приложения
![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white)

**Выполнила**: Пришлецова Кристина Сергеевна

**Группа**: АДЭУ-221

**Вариант**: 11

| Название системы | Бизнес-задача | Данные (Пример) |
| :--- | :---: | :---: |
| Recipe Base | База знаний (рецептов/алгоритмов). | Название, ингредиенты/шаги, автор, время приготовления. |

---

## 1. Цель работы
Применить полученные знания по созданию и развертыванию трехзвенного приложения (Frontend + Backend + Database) в кластере Kubernetes. Научиться организовывать взаимодействие между микросервисами.

## 2. Архитектура решения
```mermaid
graph TD
    subgraph Local Environment [Локальная среда Ubuntu 22.04]
        DEV[Разработчик Recipe Base] -->|1. git push| GV_REPO[(GitVerse Repo)]
        DEV -->|2. git push| GL_REPO[(GitLab Repo)]
        DEV -->|3. git push| GH_REPO[(GitHub Repo)]
        
        DEV -->|docker build| LOCAL_IMG[Локальные образы<br/>recipe-backend:v1<br/>recipe-frontend:v1]
        LOCAL_IMG -->|microk8s ctr image import| K8S_CLUSTER[MicroK8s Cluster]
    end

    subgraph GitVerse Cloud [GitVerse Cloud - Проблемный раннер]
        GV_REPO --> GV_RUNNER[gv02-runner02]
        GV_RUNNER -->|docker build| ERROR[❌ Ошибка: Docker daemon not running]
        ERROR -->|результат| DEV
    end

    subgraph GitLab Cloud [GitLab Cloud - Успешная сборка]
        GL_REPO --> GL_RUNNER[Shared Runner с сервисом dind]
        GL_RUNNER --> GL_BUILD[🐳 Docker Build<br/>recipe-backend<br/>recipe-frontend]
        GL_BUILD --> GL_TEST[🧪 Run Tests<br/>- API Health Check<br/>- Database Connection<br/>- Pydantic Validation]
        GL_TEST -->|✅ Успех| GL_PUSH[Push to Registry]
        GL_TEST -->|❌ Провал| GL_CLEAN[after_script: Clean Up]
        GL_PUSH --> GL_DEPLOY[🚀 Deploy to K8s]
    end

    subgraph GitHub Cloud [GitHub Cloud - Альтернативный pipeline]
        GH_REPO --> GH_RUNNER[ubuntu-latest VM with Native Docker]
        GH_RUNNER --> GH_BUILD[🐳 Docker Build<br/>Multi-stage build]
        GH_BUILD --> GH_TEST[🧪 Run Tests<br/>- Unit tests<br/>- Integration tests]
        GH_TEST -->|✅ Успех| GH_PUSH[Push to GHCR]
        GH_TEST -->|❌ Провал| GH_CLEAN[if: always - Clean Up]
        GH_PUSH --> GH_DEPLOY[Deploy to K8s]
    end

    subgraph Kubernetes Cluster [K8s Cluster - MicroK8s]
        K8S_CLUSTER --> NAMESPACE[Namespace: recipe-base]
        
        subgraph Database Tier
            POSTGRES_DEP[PostgreSQL Deployment<br/>replicas: 1]
            POSTGRES_SVC[Service: postgres-service<br/>ClusterIP: 5432]
            POSTGRES_PVC[PVC: 5Gi]
        end
        
        subgraph Backend Tier
            BACKEND_DEP[FastAPI Deployment<br/>replicas: 2]
            BACKEND_SVC[Service: backend-service<br/>ClusterIP: 8000]
            BACKEND_CONFIG[ConfigMap + Secrets]
        end
        
        subgraph Frontend Tier
            FRONTEND_DEP[Streamlit Deployment<br/>replicas: 1]
            FRONTEND_SVC[Service: frontend-service<br/>NodePort: 30080]
        end
        
        POSTGRES_SVC <--> BACKEND_DEP
        BACKEND_SVC <--> FRONTEND_DEP
    end

    subgraph External Access [Внешний доступ]
        BROWSER[🌐 Браузер пользователя] -->|http://VM_IP:30080| FRONTEND_SVC
        API_CLIENT[📱 API Client] -->|http://VM_IP:8000| BACKEND_SVC
    end

    GL_DEPLOY --> K8S_CLUSTER
    GH_DEPLOY --> K8S_CLUSTER
    
    style ERROR fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style GL_BUILD fill:#51cf66,stroke:#2f9e44
    style GH_BUILD fill:#51cf66,stroke:#2f9e44
    style LOCAL_IMG fill:#74c0fc,stroke:#3b5bdb
    style BROWSER fill:#ffd43b,stroke:#e67700
```
