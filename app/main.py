import streamlit as st
import pandas as pd
from db import get_schema, execute_query
from llm import generate_sql, fix_sql
from history import load_history, save_to_history
from visualizer import auto_visualize

st.set_page_config(page_title="Text-to-SQL Assistant", page_icon="🗄️", layout="wide")

# ── Visualization intent detection ──
VIZ_KEYWORDS = [
    "chart", "graph", "plot", "visualize", "visualise",
    "bar", "line", "pie", "scatter", "area", "histogram",
    "distribution", "box", "funnel", "show me a chart", "diagram"
]

def wants_visualization(question: str) -> bool:
    q = question.lower()
    return any(keyword in q for keyword in VIZ_KEYWORDS)

def detect_chart_type(question: str) -> str:
    q = question.lower()
    if "pie" in q:
        return "pie"
    elif "line" in q:
        return "line"
    elif "scatter" in q:
        return "scatter"
    elif "area" in q:
        return "area"
    elif "histogram" in q or "distribution" in q:
        return "histogram"
    elif "box" in q or "box plot" in q:
        return "box"
    elif "funnel" in q:
        return "funnel"
    else:
        return "bar"

# ── Init session state ──
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "schema" not in st.session_state:
    st.session_state.schema = get_schema()

# ── Sidebar ──
with st.sidebar:
    st.title("🗄️ Text-to-SQL")
    st.caption("Local LLM · MySQL · Ollama")

    with st.expander("📋 Database Schema", expanded=False):
        st.code(st.session_state.schema)

    if st.button("🔄 Refresh Schema"):
        st.session_state.schema = get_schema()
        st.success("Schema refreshed!")

    st.divider()
    st.subheader("📜 Query History")
    history = load_history()
    if history:
        for item in reversed(history[-10:]):
            with st.expander(f"🕐 {item['timestamp']}"):
                st.caption(item['question'])
                st.code(item['sql'], language='sql')
                st.caption(f"Rows: {item['rows']}")
    else:
        st.caption("No history yet.")

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# ── Main area ──
st.title("🗄️ Text-to-SQL Assistant")
st.caption("Ask anything in plain English. Say 'visualize as pie/bar/line/scatter/histogram/box/funnel' to get a chart.")

# Render chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sql" in msg:
            st.code(msg["sql"], language="sql")
        if "dataframe" in msg:
            df = pd.DataFrame(msg["dataframe"]["rows"],
                              columns=msg["dataframe"]["columns"])
            st.dataframe(df, use_container_width=True)
            if msg.get("show_chart"):
                fig = auto_visualize(
                    msg["dataframe"]["columns"],
                    msg["dataframe"]["rows"],
                    msg.get("chart_type", "bar")
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

# Chat input
question = st.chat_input("Ask your database anything...")

if question:
    st.session_state.chat_history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    show_chart = wants_visualization(question)
    chart_type = detect_chart_type(question) if show_chart else "bar"

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            sql = generate_sql(
                st.session_state.schema,
                question,
                st.session_state.chat_history
            )

        st.code(sql, language="sql")

        with st.spinner("Running query..."):
            columns, rows, message = execute_query(sql)

        # ── Self-healing ──
        if message and message.startswith("❌"):
            with st.spinner("⚠️ Query failed. Auto-fixing..."):
                fixed_sql = fix_sql(st.session_state.schema, sql, message)

            st.warning("Original query failed. Auto-corrected:")
            st.code(fixed_sql, language="sql")

            with st.spinner("Retrying..."):
                columns, rows, message = execute_query(fixed_sql)

            sql = fixed_sql

        if columns:
            df = pd.DataFrame(rows, columns=columns)
            st.dataframe(df, use_container_width=True)

            if show_chart:
                fig = auto_visualize(columns, rows, chart_type)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.caption("⚠️ Couldn't generate a chart for this data.")

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Found {len(rows)} row(s).",
                "sql": sql,
                "dataframe": {"columns": columns, "rows": rows},
                "show_chart": show_chart,
                "chart_type": chart_type
            })
            save_to_history(question, sql, len(rows))

        elif message:
            if message.startswith("❌"):
                st.error(f"Could not fix the query.\n\n{message}")
            else:
                st.markdown(message)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": message,
                "sql": sql
            })
            save_to_history(question, sql, 0)