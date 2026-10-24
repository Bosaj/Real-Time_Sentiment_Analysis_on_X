# FAQ

**Why 82% accuracy and not higher?**
Four-class sentiment classification (Positive/Negative/Neutral/Irrelevant) on noisy, short-form tweet text using a TF-IDF + Logistic Regression pipeline is a reasonably strong result for this approach; deep learning models (BERT, RoBERTa) listed under Future Enhancements in the README would likely do better at the cost of much higher latency, which matters for a "real-time" system.

**Does this connect to the live Twitter/X API?**
Not currently — the "Kafka Producer" streams tweets from a CSV dataset or manual web-form input, simulating a live stream. Twitter API v2 integration for genuinely live tweets is listed as a future enhancement, not implemented.

**Is there a real credential anywhere in this repository?**
No. An earlier commit had a live MongoDB connection string in a tracked `.env` file; it has been removed from tracking and the exposed credential should be treated as rotated/invalidated. Only `.env.example` with placeholder values (`MONGO_URI`, `GROQ_API_KEY`) is tracked going forward. If you're setting this up yourself, supply your own values in a local, git-ignored `.env`.

**What's the Groq/LLM path for?**
It's an optional alternative classification path (gated behind `GROQ_API_KEY`) alongside the primary Spark MLlib model — useful for comparison, not required to run the core pipeline.

**Why does the project need both Kafka and Spark?**
Kafka handles the message queue/streaming transport (decoupling tweet ingestion from processing), while Spark Streaming + MLlib does the actual preprocessing and classification at scale. Removing either would mean either no real streaming semantics (without Kafka) or no distributed processing (without Spark).

**Why doesn't CI spin up the full stack (Kafka, Spark, MongoDB)?**
Running that infrastructure needs a stateful, multi-service environment that isn't practical on a shared, ephemeral CI runner. CI instead validates that the code is syntactically correct, dependencies install, and notebooks are well-formed — a lighter but still useful safety net.
