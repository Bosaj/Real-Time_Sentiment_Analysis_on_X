/**
 * Health check controller for Real-Time_Sentiment_Analysis_on_X
 */
function getHealthStatus() {
  return {
    service: 'Real-Time_Sentiment_Analysis_on_X',
    status: 'UP',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  };
}

module.exports = { getHealthStatus };
