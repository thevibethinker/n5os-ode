ATTACH '/home/workspace/Datasets/zo-hotline-calls/data.duckdb' AS zo;
ATTACH '/home/workspace/Datasets/career-hotline-calls/data.duckdb' AS career;
ATTACH '/home/workspace/Datasets/vibe-pill-calls/data.duckdb' AS pill;

-- Core integrity checks
SELECT
  'zo' AS dataset,
  COUNT(*) AS total,
  SUM(CASE WHEN id IS NULL OR id = '' THEN 1 ELSE 0 END) AS bad_id,
  SUM(CASE WHEN started_at IS NULL THEN 1 ELSE 0 END) AS null_start,
  SUM(CASE WHEN duration_seconds < 0 THEN 1 ELSE 0 END) AS negative_duration,
  SUM(CASE WHEN ended_at IS NOT NULL AND started_at IS NOT NULL AND ended_at < started_at THEN 1 ELSE 0 END) AS reversed_time,
  SUM(CASE WHEN ended_at = started_at AND COALESCE(duration_seconds, 0) > 0 THEN 1 ELSE 0 END) AS zero_span_with_duration,
  SUM(CASE WHEN topics_discussed IS NULL OR TRIM(topics_discussed) = '' THEN 1 ELSE 0 END) AS null_or_blank_topics
FROM zo.calls
UNION ALL
SELECT
  'career',
  COUNT(*),
  SUM(CASE WHEN id IS NULL OR id = '' THEN 1 ELSE 0 END),
  SUM(CASE WHEN started_at IS NULL THEN 1 ELSE 0 END),
  SUM(CASE WHEN duration_seconds < 0 THEN 1 ELSE 0 END),
  SUM(CASE WHEN ended_at IS NOT NULL AND started_at IS NOT NULL AND ended_at < started_at THEN 1 ELSE 0 END),
  SUM(CASE WHEN ended_at = started_at AND COALESCE(duration_seconds, 0) > 0 THEN 1 ELSE 0 END),
  SUM(CASE WHEN topics_discussed IS NULL OR TRIM(topics_discussed) = '' THEN 1 ELSE 0 END)
FROM career.calls
UNION ALL
SELECT
  'pill',
  COUNT(*),
  SUM(CASE WHEN id IS NULL OR id = '' THEN 1 ELSE 0 END),
  SUM(CASE WHEN started_at IS NULL THEN 1 ELSE 0 END),
  SUM(CASE WHEN duration_seconds < 0 THEN 1 ELSE 0 END),
  SUM(CASE WHEN ended_at IS NOT NULL AND started_at IS NOT NULL AND ended_at < started_at THEN 1 ELSE 0 END),
  SUM(CASE WHEN ended_at = started_at AND COALESCE(duration_seconds, 0) > 0 THEN 1 ELSE 0 END),
  SUM(CASE WHEN topics_discussed IS NULL OR TRIM(topics_discussed) = '' THEN 1 ELSE 0 END)
FROM pill.calls;

-- ET rollup sanity (canonical source aggregate)
WITH unified AS (
  SELECT 'zo-hotline' AS hotline, started_at, duration_seconds FROM zo.calls
  UNION ALL
  SELECT 'career-hotline', started_at, duration_seconds FROM career.calls
  UNION ALL
  SELECT 'vibe-pill', started_at, duration_seconds FROM pill.calls
)
SELECT
  CAST(started_at - INTERVAL 5 HOUR AS DATE) AS date_et,
  hotline,
  COUNT(*) AS calls,
  ROUND(COALESCE(AVG(duration_seconds), 0), 1) AS avg_seconds
FROM unified
GROUP BY date_et, hotline
ORDER BY date_et DESC, hotline;
