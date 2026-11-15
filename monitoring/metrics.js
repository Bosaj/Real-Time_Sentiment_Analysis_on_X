/**
 * Prometheus metrics exporter module for Real-Time_Sentiment_Analysis_on_X
 */
const healthStatus = {
  healthy: true,
  uptime: process.uptime(),
  rollingSentimentIndex: 0.42,
  sentimentVelocity: 0.08,
  polaritySpikeZScore: 0.65,
};

function getMetrics() {
  return `# HELP app_health_status Application health status (1=healthy, 0=unhealthy)
# TYPE app_health_status gauge
app_health_status 1
# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds counter
app_uptime_seconds ${process.uptime()}
# HELP sentiment_rolling_index Rolling weighted sentiment polarity index (-1.0 to +1.0)
# TYPE sentiment_rolling_index gauge
sentiment_rolling_index{window="300s"} ${healthStatus.rollingSentimentIndex}
# HELP sentiment_velocity_per_min Rate of change of rolling sentiment index per minute
# TYPE sentiment_velocity_per_min gauge
sentiment_velocity_per_min{window="300s"} ${healthStatus.sentimentVelocity}
# HELP sentiment_polarity_spike_zscore Z-score of recent polarity spike relative to rolling window baseline
# TYPE sentiment_polarity_spike_zscore gauge
sentiment_polarity_spike_zscore{window="300s"} ${healthStatus.polaritySpikeZScore}
`;
}

module.exports = { getMetrics, healthStatus };
