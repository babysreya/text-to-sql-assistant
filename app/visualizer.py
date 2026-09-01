import pandas as pd
import plotly.express as px

def auto_visualize(columns, rows, chart_type="bar"):
    if not rows or not columns:
        return None

    df = pd.DataFrame(rows, columns=columns)

    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            pass

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    text_cols = df.select_dtypes(include='object').columns.tolist()
    date_cols = [c for c in df.columns if 'date' in c.lower()]

    if not numeric_cols:
        return None

    x = text_cols[0] if text_cols else None
    y = numeric_cols[0] if numeric_cols else None
    date_col = date_cols[0] if date_cols else None

    if chart_type == "pie":
        if x and y:
            return px.pie(df, names=x, values=y,
                         title=f"{y} by {x}",
                         template="plotly_dark")

    elif chart_type == "line":
        x_axis = date_col or x
        if x_axis and y:
            return px.line(df, x=x_axis, y=y,
                          title=f"{y} over {x_axis}",
                          template="plotly_dark",
                          markers=True)

    elif chart_type == "scatter":
        if len(numeric_cols) >= 2:
            return px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                             color=x if x else None,
                             title=f"{numeric_cols[1]} vs {numeric_cols[0]}",
                             template="plotly_dark")
        elif x and y:
            return px.scatter(df, x=x, y=y,
                             title=f"{y} vs {x}",
                             template="plotly_dark")

    elif chart_type == "area":
        x_axis = date_col or x
        if x_axis and y:
            return px.area(df, x=x_axis, y=y,
                          title=f"{y} over {x_axis}",
                          template="plotly_dark")

    elif chart_type == "histogram":
        if y:
            return px.histogram(df, x=y,
                               title=f"Distribution of {y}",
                               template="plotly_dark")

    elif chart_type == "box":
        if x and y:
            return px.box(df, x=x, y=y,
                         title=f"{y} distribution by {x}",
                         template="plotly_dark")
        elif y:
            return px.box(df, y=y,
                         title=f"Distribution of {y}",
                         template="plotly_dark")

    elif chart_type == "funnel":
        if x and y:
            return px.funnel(df, x=y, y=x,
                            title=f"{y} funnel by {x}",
                            template="plotly_dark")

    # Default — bar
    if x and y and df[x].nunique() <= 20:
        fig = px.bar(df, x=x, y=y,
                    title=f"{y} by {x}",
                    color=x,
                    template="plotly_dark",
                    text_auto=True)
        fig.update_layout(showlegend=False)
        return fig

    return None