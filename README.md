# Text-to-SQL Assistant

Convert plain English into SQL queries and execute them on a MySQL database — powered by a **local LLM via Ollama**. No API keys. No cloud. Runs entirely on your laptop.


##  Tech Stack
| LLM | Ollama (qwen2.5:3b) — local inference |
| Database | MySQL |
| Orchestration | LangChain |
| UI | Streamlit |
| Visualization | Plotly |
| Language | Python |

## ✨ Features
- **Natural language to SQL** — just ask in plain English
- **Conversational memory** — follow-up questions retain context
- **Multi-table JOIN support** — queries across related tables
- **Self-healing queries** — if SQL fails, LLM auto-fixes and retries
- **On-demand visualization** — bar, pie, line, scatter, histogram, box, funnel
- **Persistent query history** — saved across sessions
- **Auto schema detection** — reads live DB structure, no hardcoding
- **100% local** — no API keys, no internet required


## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/text-to-sql.git
cd text-to-sql
```

### 2. Install dependencies
```bash
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3. Setup MySQL database
```bash
mysql -u root -p < sample_db.sql
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and add your MySQL credentials
```

### 5. Pull Ollama model
```bash
ollama pull qwen2.5:3b
ollama serve
```

### 6. Run
```bash
cd app
streamlit run main.py
```

## 💬 Example Queries

| Natural Language | Feature Tested |
|---|---|
| `Show all employees` | Basic SELECT |
| `Show employees from Hyderabad` | Filtering |
| `Show each employee with their department name` | JOIN |
| `List departments where total salary exceeds budget` | Aggregation + HAVING |
| `Increase salary of all HR employees by 3000` | UPDATE |
| `Show total salary by department as a bar chart` | Visualization |
| `Visualize employees per city as a pie chart` | Pie chart |
| `Show salary distribution as a histogram` | Histogram |
| `Among engineers, who has the highest salary?` | Conversational memory |

