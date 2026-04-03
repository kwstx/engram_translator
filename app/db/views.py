from sqlalchemy import text
from app.db.session import engine

async def create_evolution_feature_views():
    """
    Creates PostgreSQL views that aggregate execution histories into a feature store.
    This serves as the the 'simple PostgreSQL views' requested for the tool evolution feedback loop.
    """
    view_sql = """
    CREATE OR REPLACE VIEW tool_execution_stats_v1 AS
    SELECT 
        tool_id,
        backend_selected,
        COUNT(*) AS total_executions,
        AVG(CASE WHEN success = TRUE THEN 1.0 ELSE 0.0 END) AS success_rate,
        AVG(latency_ms) AS avg_latency_ms,
        AVG(token_cost_actual) AS avg_token_cost,
        MAX(created_at) AS last_execution_at
    FROM tool_routing_decisions
    GROUP BY tool_id, backend_selected;

    CREATE OR REPLACE VIEW tool_evolution_signals_v1 AS
    SELECT 
        t.id AS tool_id,
        t.name,
        v.backend_selected,
        v.success_rate,
        v.avg_latency_ms,
        v.total_executions,
        (SELECT AVG(score) FROM tool_feedback f WHERE f.tool_id = t.id) AS avg_user_rating,
        (SELECT COUNT(*) FROM tool_feedback f WHERE f.tool_id = t.id) AS total_feedback_count
    FROM tool_registry t
    LEFT JOIN tool_execution_stats_v1 v ON t.id = v.tool_id;
    """
    async with engine.begin() as conn:
        await conn.execute(text(view_sql))
