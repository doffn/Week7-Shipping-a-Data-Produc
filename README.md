# 10 Academy: Artificial Intelligence Mastery - Week 7 Challenge
## Shipping a Data Product: From Raw Telegram Data to an Analytical API


This project implements an end-to-end data pipeline designed to extract, transform, and analyze data from public Telegram channels related to Ethiopian medical businesses. It leverages modern data engineering tools to build a robust, observable, and scalable data platform, culminating in an analytical API for business insights.

## 1. Introduction
This project implements a robust, containerized data pipeline for extracting, enriching, transforming, and serving insights from Telegram channel data. It supports scraping messages and images, detecting objects in media using YOLOv8, and structuring the data using dbt and PostgreSQL, while offering an analytical API via FastAPI. Dagster orchestrates all components for scheduled execution.

## 2. Key Features
Modular Pipeline: Extraction → Storage → Transformation → Enrichment → API

Image Detection: Detects objects in Telegram images using YOLOv8

Staging & Marts: dbt handles clean staging and dimensional modeling

API Access: Query enriched data using FastAPI

Containerized: All components are Dockerized for portability

Orchestrated: Dagster manages scheduling and monitoring

## 3. System Architecture Overview
Data Flow Overview:

```
Telegram → Telethon → MongoDB → PostgreSQL → dbt → FastAPI API
                                   ↑
                                YOLOv8
```
Components:

- Telethon: Telegram scraper

- MongoDB: Raw, flexible document store

- PostgreSQL: Analytical warehouse

- dbt: Data transformation and modeling

- YOLOv8: Object detection engine

- FastAPI: REST API for analytics

Dagster: Pipeline scheduler and monitor
## 4. Technologies Used

- **Python:** Core language for scripting, API, and orchestration.
- **Telethon:** Telegram API client for data extraction.
- **MongoDB & PyMongo:** Document database for raw data storage.
- **PostgreSQL & Psycopg2:** Relational database for the data warehouse.
- **dbt (Data Build Tool):** For data transformation and modeling in PostgreSQL.
- **YOLOv8 (Ultralytics):** Object detection for image enrichment.
- **FastAPI:** Python web framework for building the analytical API.
- **Pydantic:** Data validation and serialization for FastAPI.
- **Dagster:** Data orchestrator for defining, scheduling, and monitoring the pipeline.
- **Docker & Docker Compose:** For containerization and environment management.
- **python-dotenv:** For managing environment variables and secrets.


## 5. Project Setup & Environment Management

### Prerequisites

- Docker and Docker Compose installed.
- Git installed.


### Steps

1. **Clone the Repository:**

```shellscript
git clone <your-repo-url>
cd <your-repo-name>
```


2. **Configure Environment Variables:**

1. Copy the example environment file:

```shellscript
cp .env.example .env
```


2. Edit the `.env` file and fill in your actual credentials:

1. `TELEGRAM_API_ID`, `TELEGRAM_API_HASH` (from [my.telegram.org](https://my.telegram.org/apps))
2. `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
3. `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD`
4. `MONGO_DB` (e.g., `telegram_raw_data`)






3. **Build and Start Docker Containers:**

```shellscript
docker-compose build
docker-compose up -d
```

This will start your PostgreSQL database, MongoDB database, and the `app` container (which contains all your Python scripts and dbt).


4. **Configure dbt Profiles:**

1. dbt needs a `profiles.yml` file to connect to your PostgreSQL database. This file is typically located in `~/.dbt/profiles.yml` on your host machine.
2. Create or update `~/.dbt/profiles.yml` with the following content, ensuring it matches your `.env` settings:


```yaml
# ~/.dbt/profiles.yml
telegram_data_warehouse:
  target: dev
  outputs:
    dev:
      type: postgres
      host: "{{ env_var('POSTGRES_HOST') }}"
      port: "{{ env_var('POSTGRES_PORT') | int }}"
      user: "{{ env_var('POSTGRES_USER') }}"
      password: "{{ env_var('POSTGRES_PASSWORD') }}"
      dbname: "{{ env_var('POSTGRES_DB') }}"
      schema: public # Or a specific schema for dbt's internal use
      threads: 1
```




## 6. Code Structure

The project is organized into several directories, each serving a specific purpose within the data pipeline.

```plaintext
.
├── .env.example                 # Template for environment variables and secrets
├── Dockerfile                   # Defines the Docker image for the application container
├── docker-compose.yml           # Orchestrates Docker services (app, db, mongo)
├── requirements.txt             # Lists all Python dependencies
├── data/                        # Directory for raw data storage
│   └── raw/
│       ├── telegram_messages/   # Stores raw Telegram messages as JSON files (YYYY-MM-DD/channel_name.json)
│       └── telegram_images/     # Stores raw images scraped from Telegram (YYYY-MM-DD/channel_name/message_id.jpg)
├── scripts/                     # Contains Python scripts for various pipeline stages
│   ├── setup_env.py             # Utility to load and verify environment variables
│   ├── telegram_scraper.py      # Extracts data from Telegram channels and saves to data lake
│   ├── load_json_to_mongodb.py  # Loads raw JSON data from data lake into MongoDB
│   ├── load_mongo_to_postgres.py# Loads raw data from MongoDB into PostgreSQL's raw schema
│   └── yolo_enrichment.py       # Performs object detection on images and loads results to PostgreSQL
├── dbt_project/                 # dbt project for data transformation and modeling
│   ├── dbt_project.yml          # dbt project configuration
│   ├── models/                  # Contains dbt SQL models
│   │   ├── staging/             # Staging models for initial cleaning and restructuring
│   │   │   └── stg_telegram_messages.sql # Cleans and extracts key fields from raw messages
│   │   └── marts/               # Data mart models (star schema) for analytical queries
│   │       ├── dim_channels.sql # Dimension table for Telegram channels
│   │       ├── fct_messages.sql # Fact table for Telegram messages
│   │       └── fct_image_detections.sql # Fact table for YOLO image detection results
│   │       └── fct_messages.yml # dbt tests and documentation for fct_messages
│   └── tests/                   # Custom dbt tests
│       └── messages_with_text_and_no_media.sql # Example custom test for a business rule
├── fastapi_app/                 # FastAPI application for analytical API endpoints
│   ├── main.py                  # Main FastAPI application definition and API endpoints
│   ├── database.py              # Database connection utility for FastAPI (PostgreSQL)
│   └── schemas.py               # Pydantic schemas for API request/response validation
└── dagster_project/             # Dagster project for pipeline orchestration
    ├── repository.py            # Defines Dagster jobs and schedules
    └── ops.py                   # Defines individual Dagster operations (ops)
```

### File Descriptions:

- **`.env.example`**:

- A template file listing all environment variables required for the project, including API keys and database credentials. Users should copy this to `.env` and fill in their specific values.



- **`Dockerfile`**:

- Defines the Docker image for the `app` service. It specifies the base Python image, installs system dependencies, copies `requirements.txt` to install Python packages, and then copies the rest of the application code.



- **`docker-compose.yml`**:

- Defines and configures the multi-container Docker application. It sets up three services:

- `db`: A PostgreSQL database container.
- `mongo`: A MongoDB database container.
- `app`: The main application container where Python scripts, dbt, and FastAPI run. It depends on `db` and `mongo` to ensure they start first.






- **`requirements.txt`**:

- Lists all Python packages required for the project, including `telethon`, `pymongo`, `psycopg2-binary`, `dbt-postgres`, `ultralytics`, `fastapi`, `uvicorn`, `python-dotenv`, `pydantic`, and `dagster`.



- **`data/`**:

- The root directory for storing raw data.
- **`data/raw/telegram_messages/`**: Stores raw JSON files scraped from Telegram, organized by date and channel. This serves as the immutable source of truth.
- **`data/raw/telegram_images/`**: Stores raw image files downloaded from Telegram messages, organized similarly. These images are used for object detection.



- **`scripts/`**:

- Contains standalone Python scripts that perform specific tasks within the pipeline.
- **`scripts/setup_env.py`**: A simple script to load environment variables from `.env` and print a confirmation, useful for debugging environment setup.
- **`scripts/telegram_scraper.py`**:

- Connects to the Telegram API using `Telethon`.
- Scrapes messages from specified public Telegram channels.
- Saves the raw message data as JSON files into `data/raw/telegram_messages/`.
- Includes a placeholder for downloading images into `data/raw/telegram_images/`.



- **`scripts/load_json_to_mongodb.py`**:

- Reads the raw JSON message files from `data/raw/telegram_messages/`.
- Connects to MongoDB using `pymongo`.
- Inserts the raw message documents into the `raw_telegram_messages` collection in MongoDB.



- **`scripts/load_mongo_to_postgres.py`**:

- Connects to MongoDB to retrieve raw message documents.
- Connects to PostgreSQL using `psycopg2`.
- Creates the `raw.telegram_messages` table in PostgreSQL if it doesn't exist.
- Loads the raw message data from MongoDB into this PostgreSQL table, performing an upsert to handle duplicates.



- **`scripts/yolo_enrichment.py`**:

- Loads a pre-trained YOLOv8 model (`yolov8n.pt`).
- Scans `data/raw/telegram_images/` for images.
- Performs object detection on each image.
- Connects to PostgreSQL and inserts the detection results (object class, confidence, bounding box) into the `marts.fct_image_detections` table.






- **`dbt_project/`**:

- The root directory for the dbt project.
- **`dbt_project.yml`**:

- The main configuration file for the dbt project.
- Defines the project name, version, profile to use (`telegram_data_warehouse`), and paths for models, tests, etc.
- Sets default materializations and schemas for models (e.g., `staging` for staging models, `marts` for mart models).



- **`models/`**:

- Contains all SQL files that define dbt models.
- **`models/staging/stg_telegram_messages.sql`**:

- A staging model that selects data from the `raw.telegram_messages` table in PostgreSQL.
- Performs initial data cleaning, type casting, and extraction of relevant fields from the JSONB `message_data` column.



- **`models/marts/`**:

- Contains the final analytical models, forming the star schema.
- **`models/marts/dim_channels.sql`**: A dimension table for Telegram channels, derived from distinct channel IDs in the staging messages.
- **`models/marts/fct_messages.sql`**: The central fact table for messages, joining `stg_telegram_messages` with `dim_channels` and calculating metrics like message length.
- **`models/marts/fct_image_detections.sql`**: A fact table that directly queries the `marts.fct_image_detections` table populated by the YOLO enrichment script, making it available for dbt's lineage and documentation.
- **`models/marts/fct_messages.yml`**: Defines dbt tests (e.g., `unique`, `not_null`, `relationships`) and documentation for the `fct_messages` model's columns.






- **`tests/`**:

- Contains custom dbt tests written as SQL queries.
- **`tests/messages_with_text_and_no_media.sql`**: An example custom test that checks for specific business rules (e.g., messages mentioning 'product' should have an associated image detection).






- **`fastapi_app/`**:

- The directory for the FastAPI analytical API.
- **`fastapi_app/main.py`**:

- The main entry point for the FastAPI application.
- Defines the FastAPI app instance.
- Implements the analytical API endpoints (e.g., `/api/reports/top-products`, `/api/channels/{channel_name}/activity`, `/api/search/messages`, `/api/reports/visual-content-channels`).
- Queries the dbt-transformed tables in PostgreSQL (`marts` schema).



- **`fastapi_app/database.py`**:

- A utility module for establishing and managing PostgreSQL database connections for FastAPI.



- **`fastapi_app/schemas.py`**:

- Defines Pydantic `BaseModel` classes that represent the data structures for API request bodies and response models. This ensures data validation and clear API contracts.






- **`dagster_project/`**:

- The root directory for the Dagster orchestration project.
- **`dagster_project/repository.py`**:

- Defines the Dagster repository, which groups jobs and schedules.
- `full_data_pipeline_job`: A Dagster job that orchestrates the entire end-to-end data pipeline by defining the execution order of the individual ops (scrape -> load to Mongo -> load to Postgres -> dbt -> YOLO).
- `daily_telegram_pipeline_schedule`: A schedule definition that configures the `full_data_pipeline_job` to run automatically at a specified cron interval (e.g., daily).



- **`dagster_project/ops.py`**:

- Defines individual Dagster "ops" (operations). Each op is a Python function decorated with `@op` that encapsulates a specific, atomic step in the data pipeline (e.g., `scrape_telegram_data_op`, `load_json_to_mongodb_op`, `run_dbt_transformations_op`).
- These ops use `subprocess.run` to execute the Python scripts and dbt commands defined elsewhere in the project.








## 7. Running the Pipeline Components

Access the `app` container's shell to run the scripts:

```shellscript
docker-compose exec app bash
```

Once inside the container, you'll be in the `/app` directory.

### 7.1. Data Scraping and Loading

1. **Scrape Telegram Data (to local JSON data lake):**

```shellscript
python scripts/telegram_scraper.py
```

1. This will create JSON files in `data/raw/telegram_messages/` and (conceptually) images in `data/raw/telegram_images/`.



2. **Load JSON to MongoDB:**

```shellscript
python scripts/load_json_to_mongodb.py
```

1. This script reads the JSON files from the local data lake and inserts them into the `raw_telegram_messages` collection in your MongoDB instance.



3. **Load MongoDB to PostgreSQL (Raw Schema):**

```shellscript
python scripts/load_mongo_to_postgres.py
```

1. This script reads data from MongoDB and loads it into the `raw.telegram_messages` table in your PostgreSQL database.





### 7.2. Data Transformation (dbt)

1. **Navigate to dbt project:**

```shellscript
cd dbt_project
```


2. **Test dbt Connection:**

```shellscript
dbt debug
```


3. **Build dbt Models and Run Tests:**

```shellscript
dbt build
```

1. This command will execute all staging and mart models, creating tables/views in your PostgreSQL `staging` and `marts` schemas, and run all defined tests.



4. **Generate dbt Documentation:**

```shellscript
dbt docs generate
dbt docs serve # To view in browser (accessible via container's port if mapped)
```




### 7.3. Data Enrichment (YOLOv8)

1. **Navigate back to `/app`:**

```shellscript
cd ..
```


2. **Run YOLO Object Detection:**

```shellscript
python scripts/yolo_enrichment.py
```

1. This script scans `data/raw/telegram_images` (ensure you have images here, either manually placed or scraped by `telegram_scraper.py`) and populates the `marts.fct_image_detections` table in PostgreSQL.





### 7.4. Analytical API (FastAPI)

1. **Start FastAPI Application:**

```shellscript
uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8000
```

1. The API will be accessible from your host machine at `http://localhost:8000`.



2. **Access API Documentation:**

1. Open your web browser and navigate to `http://localhost:8000/docs` for the interactive Swagger UI.





### 7.5. Pipeline Orchestration (Dagster)

1. **Navigate to Dagster project:**

```shellscript
cd dagster_project
```


2. **Launch Dagster UI:**

```shellscript
dagster dev
```

1. Open your web browser and navigate to `http://localhost:3000` (or the port Dagster indicates).
2. From the UI, you can inspect the `full_data_pipeline_job`, manually launch runs, and configure the `daily_telegram_pipeline_schedule`.





## 8. Data Model: Star Schema

The analytical data warehouse in PostgreSQL is structured as a star schema for efficient querying.

```mermaid
Dimensional Star Schema.download-icon {
            cursor: pointer;
            transform-origin: center;
        }
        .download-icon .arrow-part {
            transition: transform 0.35s cubic-bezier(0.35, 0.2, 0.14, 0.95);
             transform-origin: center;
        }
        button:has(.download-icon):hover .download-icon .arrow-part, button:has(.download-icon):focus-visible .download-icon .arrow-part {
          transform: translateY(-1.5px);
        }
        #mermaid-diagram-rnct{font-family:var(--font-geist-sans);font-size:12px;fill:#000000;}#mermaid-diagram-rnct .error-icon{fill:#552222;}#mermaid-diagram-rnct .error-text{fill:#552222;stroke:#552222;}#mermaid-diagram-rnct .edge-thickness-normal{stroke-width:1px;}#mermaid-diagram-rnct .edge-thickness-thick{stroke-width:3.5px;}#mermaid-diagram-rnct .edge-pattern-solid{stroke-dasharray:0;}#mermaid-diagram-rnct .edge-thickness-invisible{stroke-width:0;fill:none;}#mermaid-diagram-rnct .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-diagram-rnct .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-diagram-rnct .marker{fill:#666;stroke:#666;}#mermaid-diagram-rnct .marker.cross{stroke:#666;}#mermaid-diagram-rnct svg{font-family:var(--font-geist-sans);font-size:12px;}#mermaid-diagram-rnct p{margin:0;}#mermaid-diagram-rnct .label{font-family:var(--font-geist-sans);color:#000000;}#mermaid-diagram-rnct .cluster-label text{fill:#333;}#mermaid-diagram-rnct .cluster-label span{color:#333;}#mermaid-diagram-rnct .cluster-label span p{background-color:transparent;}#mermaid-diagram-rnct .label text,#mermaid-diagram-rnct span{fill:#000000;color:#000000;}#mermaid-diagram-rnct .node rect,#mermaid-diagram-rnct .node circle,#mermaid-diagram-rnct .node ellipse,#mermaid-diagram-rnct .node polygon,#mermaid-diagram-rnct .node path{fill:#eee;stroke:#999;stroke-width:1px;}#mermaid-diagram-rnct .rough-node .label text,#mermaid-diagram-rnct .node .label text{text-anchor:middle;}#mermaid-diagram-rnct .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#mermaid-diagram-rnct .node .label{text-align:center;}#mermaid-diagram-rnct .node.clickable{cursor:pointer;}#mermaid-diagram-rnct .arrowheadPath{fill:#333333;}#mermaid-diagram-rnct .edgePath .path{stroke:#666;stroke-width:2.0px;}#mermaid-diagram-rnct .flowchart-link{stroke:#666;fill:none;}#mermaid-diagram-rnct .edgeLabel{background-color:white;text-align:center;}#mermaid-diagram-rnct .edgeLabel p{background-color:white;}#mermaid-diagram-rnct .edgeLabel rect{opacity:0.5;background-color:white;fill:white;}#mermaid-diagram-rnct .labelBkg{background-color:rgba(255, 255, 255, 0.5);}#mermaid-diagram-rnct .cluster rect{fill:hsl(0, 0%, 98.9215686275%);stroke:#707070;stroke-width:1px;}#mermaid-diagram-rnct .cluster text{fill:#333;}#mermaid-diagram-rnct .cluster span{color:#333;}#mermaid-diagram-rnct div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:var(--font-geist-sans);font-size:12px;background:hsl(-160, 0%, 93.3333333333%);border:1px solid #707070;border-radius:2px;pointer-events:none;z-index:100;}#mermaid-diagram-rnct .flowchartTitleText{text-anchor:middle;font-size:18px;fill:#000000;}#mermaid-diagram-rnct .flowchart-link{stroke:hsl(var(--gray-400));stroke-width:1px;}#mermaid-diagram-rnct .marker,#mermaid-diagram-rnct marker,#mermaid-diagram-rnct marker *{fill:hsl(var(--gray-400))!important;stroke:hsl(var(--gray-400))!important;}#mermaid-diagram-rnct .label,#mermaid-diagram-rnct text,#mermaid-diagram-rnct text>tspan{fill:hsl(var(--black))!important;color:hsl(var(--black))!important;}#mermaid-diagram-rnct .background,#mermaid-diagram-rnct rect.relationshipLabelBox{fill:hsl(var(--white))!important;}#mermaid-diagram-rnct .entityBox,#mermaid-diagram-rnct .attributeBoxEven{fill:hsl(var(--gray-150))!important;}#mermaid-diagram-rnct .attributeBoxOdd{fill:hsl(var(--white))!important;}#mermaid-diagram-rnct .label-container,#mermaid-diagram-rnct rect.actor{fill:hsl(var(--white))!important;stroke:hsl(var(--gray-400))!important;}#mermaid-diagram-rnct line{stroke:hsl(var(--gray-400))!important;}#mermaid-diagram-rnct :root{--mermaid-font-family:var(--font-geist-sans);}Dimension TablesFact Tableschannel_iddate_keymessage_idfct_messages (Fact)fct_image_detections (Fact)dim_channels (Dimension)dim_dates (Dimension)
```

- **`fct_messages`:** The central fact table, containing granular message data and foreign keys to dimensions.
- **`fct_image_detections`:** A supplementary fact table, linking object detection results to specific messages.
- **`dim_channels`:** Provides descriptive attributes for each Telegram channel.
- **`dim_dates`:** (Conceptual) Provides time-based attributes for flexible temporal analysis.


## 9. Challenges and Future Improvements

### Challenges Encountered

- **PostgreSQL Connectivity:** Initial issues with PostgreSQL connectivity led to the adoption of MongoDB as an intermediate raw data store, providing more flexibility for unstructured data before structured loading into PostgreSQL.
- **Telegram API Rate Limits:** Requires careful handling and potential implementation of robust retry mechanisms and back-off strategies.
- **Image Scraping Complexity:** Properly downloading and managing various media types from Telegram messages can be complex. The current `telegram_scraper.py` has a placeholder for this.
- **YOLOv8 Model Selection & Performance:** Choosing the right pre-trained model and optimizing inference for large volumes of images can be challenging.
- **Product/Drug Entity Extraction:** The current API's product identification relies on simple keyword matching. A more sophisticated approach would involve Natural Language Processing (NLP) techniques for named entity recognition within the dbt transformation layer or a dedicated enrichment step.
- **Data Quality & Validation:** Ensuring data consistency and accuracy across all pipeline stages, especially when dealing with diverse and unstructured raw data.
- **Orchestration Debugging:** Troubleshooting issues within a containerized Dagster environment can require careful log inspection.


### Future Improvements

- **Enhanced Telegram Scraper:** Implement full image and video downloading capabilities, and more robust error handling for rate limits and diverse message types.
- **Advanced NLP for Product Identification:** Integrate a dedicated NLP service or dbt models with text analysis capabilities to accurately identify and categorize medical products/drugs from message text.
- **Incremental Loading:** Implement incremental loading strategies for all stages (MongoDB to PostgreSQL, dbt models) to process only new or changed data, improving efficiency and reducing processing time.
- **Data Quality Framework:** Integrate a dedicated data quality framework (e.g., Great Expectations) for more comprehensive testing and validation throughout the pipeline.
- **Monitoring & Alerting:** Set up detailed monitoring for pipeline health, data quality, and API performance, with alerts for anomalies.
- **Scalability:** Explore options for scaling individual components (e.g., distributed scraping, parallel dbt runs, horizontally scaling FastAPI).
- **Authentication & Authorization:** Implement secure authentication and authorization for the FastAPI endpoints.
- **CI/CD Integration:** Automate testing, building, and deployment of the pipeline components using CI/CD pipelines.


---

