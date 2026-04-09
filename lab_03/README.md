# Лабораторная работа №3 Развертывание приложения в Kubernetes
![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white)

**Выполнила**: Пришлецова Кристина Сергеевна

**Группа**: АДЭУ-221

**Вариант**: 11

| Основной сервис (App) | Вспомогательный сервис (DB/Tool) | Задача |
| :--- | :---: | :---: |
| MinIO | MinIO Client (Job) | Развернуть S3-хранилище MinIO. Открыть доступ к консоли. Опционально: запустить Job, создающий бакет. |

---

## 1. Цель работы
Освоить процесс оркестрации контейнеров. Научиться разворачивать связки сервисов (аналитическое приложение + база данных/интерфейс) в кластере Kubernetes, управлять их масштабированием (Deployment) и сетевой доступностью (Service).

## 2. Технический стек и окружение
- **ОС**: Ubuntu 24.04 LTS 
- **Контейнеризация**: Docker 24.x
- **Оркестрация**: Minikube
- **Инструмент управления**: kubectl с алиасом aliac kubectl='microk8s kubectl'
- **Основной сервис (App)**: MinIO S3-совеместимое объектное хранилище
- **Вспомогательный сервис**: MinIO Client (mc) в виде Kubernetes Job
- **Доступ к консоли**: MinIO Console веб-интерфейс на порту 9001
- **Хранение данных**: hostPath или PVC для сохранения объектов MinIO

---

## 3. Архитектура решения
```mermaid
graph TD
    %% Определение цветов
    classDef config fill:#f9f9f9,stroke:#333,stroke-width:1px;
    classDef db fill:#e1f5fe,stroke:#0277bd,stroke-width:2px;
    classDef app fill:#fff3e0,stroke:#ef6c00,stroke-width:2px;
    classDef batch fill:#f1f8e9,stroke:#558b2f,stroke-width:2px;
    classDef user fill:#ffebee,stroke:#c62828,stroke-width:2px;

    subgraph K8s_Cluster ["K8s Cluster (Minikube)"]
        
        subgraph Configs ["Конфигурация"]
            SEC["Secret"]
            CM["ConfigMap"]
            SA["ServiceAccount"]
        end

        subgraph Database ["Слой данных"]
            PVC["PersistentVolumeClaim"]
            DB_POD("MinIO Pod")
            DB_SVC{"MinIO_Service"}
        end

        subgraph Analytics ["Слой аналитики"]
            APP_POD("MinIO Console Pod")
            APP_SVC{"Console_Service"}
        end

        subgraph Data ["Загрузка"]
            JOB("MinIO Client Job")
        end

        %% Связи
        SEC -.-> DB_POD:::config
        SEC -.-> APP_POD:::config
        CM -.-> DB_POD:::config
        CM -.-> APP_POD:::config
        SA -.-> JOB:::config
        PVC --- DB_POD:::db
        DB_POD --- DB_SVC:::db
        JOB -->|"mc mb /analytics"| DB_SVC:::batch
        APP_POD -->|Reads| DB_SVC:::app
    end

    User(("Аналитик")) -->|Port 30901| APP_SVC:::user

    %% Применение стилей
    class SEC,CM,SA config;
    class PVC,DB_POD,DB_SVC db;
    class APP_POD,APP_SVC app;
    class JOB batch;
    class User user;
```

## Таблица пояснения компонентов архитектуры
| Блок | Компонент | Краткое пояснение |
|:----:|-----------|-------------------|
| **Configs** | Secret / ConfigMap / ServiceAccount | Secret хранит пароли MinIO. ConfigMap содержит конфигурацию подключения. ServiceAccount дает права MinIO Client Job на создание бакета. |
| **Data** | PVC / MinIO Pod / MinIO_Service | PVC для постоянного хранения объектов. MinIO Pod — S3-хранилище (порты 9000/9001). MinIO_Service для внутреннего доступа. |
| **Analytics** | MinIO Console Pod / Console_Service | Веб-интерфейс для управления бакетами и объектами. Console_Service (NodePort) открывает доступ наружу на порт 30901. |
| **Load** | MinIO Client Job | Однократный процесс, выполняющий `mc mb` для создания бакета `analytics`. |
| **User** | Аналитик | Внешний пользователь, заходящий в MinIO Console через браузер по адресу `http://<IP-ВМ>:30901`. |

---

## 6. Порядок выполнения работы
**Запуск**: ```minikube start --driver=docker```
