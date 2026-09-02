from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
import re

llm = OllamaLLM(model="qwen2.5:3b")

prompt_template = PromptTemplate(
    input_variables=["schema", "history", "question"],
    template="""You are an expert MySQL query generator.

Database Schema:
{schema}

Conversation History:
{history}

Rules:
- Return ONLY the raw SQL query
- No markdown, no backticks, no explanation
- Use JOINs when data spans multiple tables
- Use table.column format when joining tables
- Always prefix columns with their table name (e.g. employees.salary, projects.start_date)
- Date columns in employees: joining_date. Date columns in projects: start_date, end_date
- Never use a column name that doesn't exist in the schema above
- Never add WHERE filters unless the user explicitly asks to filter
- If user asks for ALL departments or total/summary data, do NOT filter by any department name
- Never use dot notation in aliases (e.g. use AS salary, NOT AS employees.salary)
- Never add LIMIT unless the user asks for a specific number of results
- Keep aliases simple single words with no special characters
Current Question: {question}
SQL:"""
)

fix_template = PromptTemplate(
    input_variables=["schema", "sql", "error"],
    template="""You are an expert MySQL debugger.

Database Schema:
{schema}

This SQL query failed:
{sql}

Error:
{error}

Fix the SQL query. Return ONLY the corrected raw SQL. No explanation, no markdown, no backticks.
Fixed SQL:"""
)

def clean_sql(text):
    return re.sub(r"```sql|```", "", text).strip()

def generate_sql(schema, question, chat_history: list):
    history_text = ""
    for msg in chat_history[-6:]:
        if msg["role"] == "user":
            history_text += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            history_text += f"Assistant: {msg['content']}\n"

    chain = prompt_template | llm
    response = chain.invoke({
        "schema": schema,
        "history": history_text or "None",
        "question": question
    })
    return clean_sql(response)

def fix_sql(schema, sql, error):
    chain = fix_template | llm
    response = chain.invoke({
        "schema": schema,
        "sql": sql,
        "error": error
    })
    return clean_sql(response)