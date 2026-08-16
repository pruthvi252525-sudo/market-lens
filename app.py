import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

st.set_page_config(page_title="Market Lens | Live Tracker", layout="wide")

@st.cache_data(ttl=300)
def load_data():
    db_url = st.secrets.get("DATABASE_URL")
    if not db_url:
        st.error("Database connection secret 'DATABASE_URL' is missing.")
        return pd.DataFrame()
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url)
    query = "SELECT id, quote, author, tags, scraped_at FROM market_data ORDER BY scraped_at DESC"
    return pd.read_sql(query, engine)

st.title("📊 Market Lens: Automated Data Dashboard")
df = load_data()

if df.empty:
    st.info("No records found in database. Trigger the scraper workflow to populate data.")
else:
    # Top KPI Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", len(df))
    col2.metric("Unique Entities / Authors", df["author"].nunique())
    col3.metric("Latest Ingestion", pd.to_datetime(df["scraped_at"]).max().strftime("%Y-%m-%d %H:%M UTC"))

    st.markdown("---")

    # Filters
    author_list = ["All"] + sorted(df["author"].dropna().unique().tolist())
    selected_author = st.selectbox("Filter by Author", author_list)
    
    filtered_df = df if selected_author == "All" else df[df["author"] == selected_author]

    # Visualizations
    col_chart, col_table = st.columns([1, 1])

    with col_chart:
        top_authors = df["author"].value_counts().head(10).reset_index()
        top_authors.columns = ["Author", "Count"]
        fig = px.bar(top_authors, x="Count", y="Author", orientation="h", title="Top 10 Most Frequent Authors")
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.subheader("Data Explorer")
        st.dataframe(
            filtered_df[["author", "quote", "tags", "scraped_at"]],
            use_container_width=True,
            height=400
        )