-- Canonical hotline dashboard query contract
-- Sources:
--   Datasets/zo-hotline-calls/data.duckdb
--   Datasets/career-hotline-calls/data.duckdb
--   Datasets/vibe-pill-calls/data.duckdb
-- Excluded from default aggregates:
--   Datasets/vapi-calls/data.duckdb

ATTACH '/home/workspace/Datasets/zo-hotline-calls/data.duckdb' AS zo;
ATTACH '/home/workspace/Datasets/career-hotline-calls/data.duckdb' AS career;
ATTACH '/home/workspace/Datasets/vibe-pill-calls/data.duckdb' AS pill;

WITH unified AS (
  SELECT 'zo-hotline' AS hotline, started_at, duration_seconds FROM zo.calls
  UNION ALL
  SELECT 'career-hotline' AS hotline, started_at, duration_seconds FROM career.calls
  UNION ALL
  SELECT 'vibe-pill' AS hotline, started_at, duration_seconds FROM pill.calls
),
windowed AS (
  SELECT
    hotline,
    started_at,
    duration_seconds,
    CAST(started_at - INTERVAL 5 HOUR AS DATE) AS date_et
  FROM unified
  WHERE started_at >= (NOW() - (14 * INTERVAL 1 DAY))
)
SELECT
  date_et,
  hotline,
  COUNT(*) AS calls,
  ROUND(COALESCE(AVG(duration_seconds), 0), 1) AS avg_seconds
FROM windowed
GROUP BY date_et, hotline
ORDER BY date_et DESC, hotline;
