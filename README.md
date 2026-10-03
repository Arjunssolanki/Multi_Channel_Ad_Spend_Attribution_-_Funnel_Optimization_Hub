# Multi-Channel Ad Spend Attribution & Funnel Optimization Hub

## 📊 Executive Project Summary

### Project Objective

Direct-to-Consumer brands face compounding financial losses due to blind marketing spend distribution across siloed ad networks. Lacking an integrated, event-driven verification framework leads to miscalculated customer acquisition costs and hidden funnel drop-offs. The primary objective of this system is to ingest fragmented clickstream events and campaign spending logs from a global cloud infrastructure layer to programmatically calculate cross-channel multi-touch attribution models and measure granular checkout step velocity metrics.

### System Solution Strategy

This engineering blueprint implements an asynchronous, serverless hybrid cloud pipeline to centralize multi-touch consumer pathways into an actionable relational database lakehouse.

- **Event-Driven Gateway:** Leverages a serverless cloud computing layer triggered immediately upon landing file mutations inside an object storage repository.
- **Data Transport Tunneling:** Employs a secure public network tunnel to forward structured incoming JSON transaction files to an internal microservice cluster.
- **Defensive Data Transformation:** Utilizes algorithmic string manipulation to isolate raw time-zone patterns, strip case anomalies, and clean missing properties.
- **Mathematical Modeling:** Window-functions consecutive session steps to balance conversion credit using First-Touch, Last-Touch, and exponential Time-Decay attribution matrices.

---

## 🏛️ Comprehensive Architecture & Data Flow

```text
  [ Raw Logs Upload ] ──► [ Amazon S3 Data Lake ]
                                 │
                                 ▼ (Object Creation Event)
                          [ AWS Lambda Trigger ]
                                 │
                                 ▼ (Secure Network Forwarding)
                          [ Ngrok Proxy Tunnel ]
                                 │
                                 ▼ (Inbound Payload Processing)
                          [ FastAPI Application ]
                                 │
                                 ▼ (Defensive String Transformation)
                          [ Pandas Ingestion Engine ]
                                 │
                                 ▼ (Truncate & Bulk-Load Transactions)
                          [ Local MySQL Instances ]
                                 │
                        ┌────────┴────────┐
                        ▼                 ▼
             [ Attribution Engine ]    [ Funnel Velocity Tracking ]
              (First, Last, Decay)      (Sequential Session Nesting)
```

---

## 🗄️ Database Storage Architecture

The underlying storage tier utilizes a relational structural layout to maintain separation of concerns between media operational expenditures and user-driven session histories.

### 1. Table: `marketing_spend_logs`

Tracks daily capital injections distributed to third-party ad networks at a granular marketing campaign identifier level.

- `log_id` (Integer, Primary Key, Auto-Increment)
- `campaign_id` (Variable Character Space)
- `channel` (Variable Character Space)
- `spend_date` (Date Format)
- `ad_spend` (Decimal Currency Allocation)
- `impressions` (Integer Tracking Total Views)
- `clicks` (Integer Tracking Ad Traffic Actions)

### 2. Table: `web_clickstream_logs`

Captures every chronological milestone event recorded during an active customer browsing window on the digital platform.

- `click_id` (Integer, Primary Key, Auto-Increment)
- `user_id` (Variable Character Space)
- `session_id` (Variable Character Space Unique Per Visit)
- `timestamp` (Date-Time Explicit Timestamp Normalized to UTC)
- `traffic_source` (Variable Character Space Mapping UTM Sources)
- `page_type` (Variable Character Space Categorizing Flow Level)
- `revenue` (Decimal Financial Conversion Value)

---

## 🚀 Architectural Project Milestones

### Milestone 1: Automated Infrastructure Ingestion Core

- Configured cloud file tracking monitors to intercept unstructured object storage uploads within the targeted bucket.
- Deployed an operational event handler script using cloud environment configuration records to maintain strict security practices.
- Initialized an asynchronous web server application framework to accept live cloud traffic payloads without dropping pipeline packages.

### Milestone 2: Multi-Touch Analytical Modeling Engine

- Constructed algorithmic calculation modules to parse relative user tracking segments across multi-touch touchpoints.
- Engineered mathematical attribution logic defining First-Touch introduction weights, Last-Touch closure credits, and custom Time-Decay allocations based on exponential hourly distance parameters.
- Joined calculation matrices against active historical expenditure files to isolate real Customer Acquisition Cost and Return on Ad Spend valuations.

### Milestone 3: Sequential Funnel Velocity Tracker

- Designed an analytics application using unique sequential session isolation rules to map out platform checkout paths accurately.
- Defensively handled missing transaction entries to establish logical conversion percentages and positive drop-off tracking boundaries across all user paths.
- Computed aggregate velocity matrices tracking the exact minutes spent navigating from discovery screens to final payment records.

---

## ⚡ Serverless Cloud Engine Config (`lambda_function.py`)

This programmatic controller runs within an isolated environment script runtime in the cloud, automatically capturing data warehouse movements to trigger local processing layers.

```python
import json
import urllib.request
import os

def lambda_handler(event, context):
    base_url = os.environ.get("NGROK_URL", "https://ngrok-free.app")
    webhook_url = f"{base_url.rstrip('/')}/webhook/s3-update"

    payload = {
        "event_source": "aws_s3_notification",
        "details": event
    }

    headers = {
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode("utf-8")
            return {
                "statusCode": 200,
                "body": res_body
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }
```

---

## ⚙️ Environment Configuration Template (`.env`)

Create a hidden profile block inside the root directory using professional placeholders to insulate computational configurations:

```text
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_secure_database_password
DB_NAME=attribution_data_lake

AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=your-analytical-data-lake-bucket-name
```

---

## 🏁 How to Run the Project

Follow these execution steps sequentially from your terminal workspace:

### 1. Set Up Environment & Dependencies

Initialize the local environment directory structure and install the package matrices:

```bash
python -m venv attribution_env
attribution_env\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Creation

Ensure your local relational database service engine is up and running, then execute the setup utility to apply schemas:

```bash
python init_db.py
```

### 3. Launching the Core Pipeline Architecture

Open two separate terminal prompt sessions to establish the live data ingestion web gateway:

- **Terminal Session 1 (Launch FastAPI Service Engine):**

  ```bash
  uvicorn ingest_pipeline:app --host 127.0.0.1 --port 8000 --reload
  ```

- **Terminal Session 2 (Expose Proxy Networking Bridge):**
  ```bash
  ngrok http 8000
  ```

### 4. Continuous Ingestion Test Loop

Open a third terminal window prompt to mock transactional logging data changes and synchronize with the cloud:

- **Generate fresh raw logs and push them to the cloud:**
  ```bash
  python generate_raw_source.py
  python upload_to_s3.py
  ```

The live network pipeline catches the upload trigger automatically via AWS Lambda routing and pushes datasets straight to your MySQL instance.

### 5. Running Analytical Computations

Execute the respective data modeling scripts directly to track real-time marketing attribution returns or user journey path metrics:

- **Compute Marketing Return and Customer Acquisition Matrices:**

  ```bash
  python attribution_models.py
  ```

- **Evaluate Granular Drop-offs and Checkout Funnel Velocity Metrics:**
  ```bash
  python funnel_analytics.py
  ```
  ## 📉 Analytical Baseline & Executive Performance Insights

Below are the actual data matrices calculated programmatically by the attribution engine and funnel tracking modules during the live production simulation run.

### 1. Executive Multi-Channel Marketing Attribution Matrix

| Channel        | Ad Spend  | Clicks | First-Touch Rev | Last-Touch Rev | Time-Decay Rev |
| :------------- | :-------- | :----- | :-------------- | :------------- | :------------- |
| **Affiliate**  | ₹5,873.78 | 22,522 | ₹1,477.02       | ₹1,195.92      | ₹1,230.51      |
| **Google Ads** | ₹6,648.18 | 30,190 | ₹397.18         | ₹678.28        | ₹643.69        |
| **Meta Ads**   | ₹4,129.54 | 19,830 | ₹799.02         | ₹799.02        | ₹799.02        |

#### Senior Attribution Analysis

- **The Top-of-Funnel Affiliate Engine:** Affiliate campaigns heavily dominate **First-Touch Revenue (₹1,477.02)** compared to Last-Touch. This explicitly proves that your Affiliate network functions as a powerful top-of-funnel introduction channel that drives initial product discovery, even though users settle on other paths before checking out.
- **The Lower-Funnel Google Ads Closer:** Google Ads exhibits strong **Last-Touch optimization (₹678.28)** over First-Touch (₹397.18). This demonstrates that Google Ads successfully captures high-intent intent later in the customer browsing window to seal the conversion.
- # **Meta Ads Consistency:** Meta Ads yields identical performance across all models (₹799.02), signaling shorter, linear user paths where customers discover and convert entirely within a single social session window.
  | Channel        | Ad Spend  | Clicks | First-Touch Rev | Last-Touch Rev | Time-Decay Rev |
  | :------------- | :-------- | :----- | :-------------- | :------------- | :------------- |
  | **Affiliate**  | ₹5,873.78 | 22,522 | ₹1,477.02       | ₹1,195.92      | ₹1,230.51      |
  | **Google Ads** | ₹6,648.18 | 30,190 | ₹397.18         | ₹678.28        | ₹643.69        |
  | **Meta Ads**   | ₹4,129.54 | 19,830 | ₹799.02         | ₹799.02        | ₹799.02        |

#### Senior Attribution Analysis

- **The Top-of-Funnel Affiliate Engine:** Affiliate campaigns heavily dominate **First-Touch Revenue (₹1,477.02)** compared to Last-Touch. This explicitly proves that your Affiliate network functions as a powerful top-of-funnel introduction channel that drives initial product discovery, even though users settle on other paths before checking out.
- **The Lower-Funnel Google Ads Closer:** Google Ads exhibits strong **Last-Touch optimization (₹678.28)** over First-Touch (₹397.18). This demonstrates that Google Ads successfully captures high-intent intent later in the customer browsing window to seal the conversion.
- **Meta Ads Consistency:** Meta Ads yields identical performance across all models (₹799.02), signaling shorter, linear user paths where customers discover and convert entirely within a single social session window.
  > > > > > > > cf4a2efa7556277330e0e9335503f413fa93bf3c

---

### 2. Digital Marketing Conversion Funnel & Velocity Matrix

| Journey Stage                            | Active Sessions | Step Conversion Rate | Phase Drop-Off Rate |
| :--------------------------------------- | :-------------- | :------------------- | :------------------ |
| **Stage 1: Landing Page Visits**         | 31 sessions     | Baseline (100.00%)   | 0.00%               |
| **Stage 2: Added Items to Cart**         | 8 sessions      | 25.81%               | 74.19%              |
| **Stage 3: Payment Confirmations**       | 3 sessions      | 37.50%               | 62.50%              |
| **Overall Funnel Conversion Efficiency** | **3 sessions**  | **9.68%**            | **90.32%**          |

#### User Journey Funnel Velocity

- **Average Browsing Velocity (Landing Page ──► Cart):** 8.88 minutes
- **Average Checkout Velocity (Cart ──► Payment Confirmation):** 2.33 minutes

#### Senior Funnel Optimization Analysis

- **High Intent Velocity:** Users take an average of 8.88 minutes evaluating items on the landing page before committing to a cart action. Once an item is in the cart, the conversion speed accelerates dramatically to just 2.33 minutes. This lightning-fast checkout velocity indicates that the final payment steps have negligible friction.
- **Strategic Growth Leverage:** The primary leakage point is the initial selection phase where 74.19% of visitors bounce before adding anything to a cart. Because the checkout stage converts efficiently at 37.50%, marketing resources should focus heavily on optimizing landing page copy, product imagery, and social proof components rather than reworking the checkout flow.

## ⚙️ Enterprise MLOps Governance & Container Infrastructure

To transition this pipeline from a local runtime script to a resilient, production-ready enterprise cluster, the system integrates robust metric persistence layers, model tracking, and complete platform isolation.

### 1. Database Persistence Schemas

Instead of executing volatile in-memory operations, the final analytical data blocks are automatically pushed back into dedicated MySQL reporting schemas. This allows business intelligence architectures (such as Power BI or Tableau) to perform direct query updates seamlessly.

- `summary_attribution_metrics`: Persists multi-touch model returns alongside exact ad expenditures.
- `summary_funnel_metrics`: Logs granular session counts, conversion flags, and user drop-off limits.
- `summary_efficiency_metrics`: Tracks localized performance factors mapping Cost Per Click (CPC) and Cost Per Acquisition (CPA).

---

### 2. MLOps Experiment Tracking (`MLflow`)

The application integrates an analytical orchestrator engine to govern pipeline runs. Every invocation automatically captures shifting marketing returns, velocity milestones, and cost efficiency attributes to log them into a visual, centralized governance space.

- **Experiment Container**: `Multi_Channel_Marketing_Hub`
- **Log Run Execution Target**: `Full_Marketing_Audit_Execution`
- **Tracked Parameters & Analytics Metrics**:
  - Baseline Top-of-Funnel Visibility Volumes (`funnel_landing_sessions`)
  - Dynamic Conversion Vectors (`funnel_cart_conversion_pct`, `funnel_checkout_conversion_pct`)
  - Step Transition Speeds (`velocity_avg_minutes_to_cart`, `velocity_avg_minutes_to_payment`)
  - Marketing Capital Performance (`efficiency_meta_ads_cpc`, `efficiency_google_ads_cpa`)

---

### 3. Application Containerization Platform (`Docker`)

The entire application footprint—including its native compilation headers, FastAPI asynchronous servers, and calculation models—is bundled inside a lightweight, cross-platform containerized environment. This shields the project from local dependency variance, guaranteeing identical pipeline results across any cloud or environment provider.

### 🐳 Running via the Container Platform (Docker Ecosystem)

Instead of starting local web processes and dependency virtual environments manually, the entire environment can be compiled, linked, and run inside an isolated sandbox container.

Ensure **Docker Desktop** is active on your machine, then run the corresponding orchestrator commands in your terminal:

- **Build the Image and Start the Container Network:**

  ```bash
  docker compose up --build
  ```

- **Run the Container Cluster in Detached Mode (Runs quietly in the background):**

  ```bash
  docker compose up -d
  ```

- **Verify the Live State of Container Processes:**

  ```bash
  docker compose ps
  ```

- **Inspect Real-Time Execution Logs Inside the Container Environment:**

  ```bash
  docker compose logs -f
  ```

- **Shut Down the Container Network and Clean Up Isolated Bridges:**
  ```bash
  docker compose down
  ```

Once the container finishes building and initializes, your FastAPI ingestion gateway will be fully live on `http://localhost:8000`. You can proceed immediately to route live network tunnels via Ngrok (`ngrok http 8000`) to pipe events into the containerized cluster.

#### Container Strategy Configuration Components:

- `Dockerfile`: Pulls an optimized system layer, provisions compiling tool headers via `build-essential` to handle computational extensions, applies custom setup metadata via `pyproject.toml`, and exposes network gateway routes.
- `docker-compose.yml`: Maps network bridges dynamically, sets isolated operational ports (`8000:8000`), binds secure system profiles (`.env`), and enforces automated recovery rules (`restart: always`).
- # `.dockerignore`: Blocks heavy development files, virtual directories (`attribution_env/`), analytical system metrics tracking caches (`mlruns/`), and document layouts (`*.docx`, `*.doc`) from bloating the image, resulting in high-speed compilation runs.
  | Journey Stage                            | Active Sessions | Step Conversion Rate | Phase Drop-Off Rate |
  | :--------------------------------------- | :-------------- | :------------------- | :------------------ |
  | **Stage 1: Landing Page Visits**         | 31 sessions     | Baseline (100.00%)   | 0.00%               |
  | **Stage 2: Added Items to Cart**         | 8 sessions      | 25.81%               | 74.19%              |
  | **Stage 3: Payment Confirmations**       | 3 sessions      | 37.50%               | 62.50%              |
  | **Overall Funnel Conversion Efficiency** | **3 sessions**  | **9.68%**            | **90.32%**          |

#### User Journey Funnel Velocity

- **Average Browsing Velocity (Landing Page ──► Cart):** 8.88 minutes
- **Average Checkout Velocity (Cart ──► Payment Confirmation):** 2.33 minutes

#### Senior Funnel Optimization Analysis

- **High Intent Velocity:** Users take an average of 8.88 minutes evaluating items on the landing page before committing to a cart action. Once an item is in the cart, the conversion speed accelerates dramatically to just 2.33 minutes. This lightning-fast checkout velocity indicates that the final payment steps have negligible friction.
- **Strategic Growth Leverage:** The primary leakage point is the initial selection phase where 74.19% of visitors bounce before adding anything to a cart. Because the checkout stage converts efficiently at 37.50%, marketing resources should focus heavily on optimizing landing page copy, product imagery, and social proof components rather than reworking the checkout flow.

> > > > > > > cf4a2efa7556277330e0e9335503f413fa93bf3c
