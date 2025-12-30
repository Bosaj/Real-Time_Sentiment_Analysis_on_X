document.addEventListener("DOMContentLoaded", function () {
    const wrapper = document.querySelector(".wrapper");
    if (!wrapper) return;

    const editableInput = wrapper.querySelector(".editable");
    const readonlyInput = wrapper.querySelector(".readonly");
    const placeholder = wrapper.querySelector(".placeholder");
    const counter = wrapper.querySelector(".counter");
    const button = wrapper.querySelector("#tweetButton");

    // UI Helper: Update Counter & Validation
    function validated(element) {
        let text;
        let maxLength = 100;
        let currentlength = element.innerText.length;

        if (currentlength <= 0) {
            placeholder.style.display = "block";
            counter.style.display = "none";
            button.classList.remove("active");
        } else {
            placeholder.style.display = "none";
            counter.style.display = "block";
            button.classList.add("active");
        }

        counter.innerText = maxLength - currentlength;

        if (currentlength > maxLength) {
            let overText = element.innerText.substr(maxLength);
            overText = `<span class="highlight">${overText}</span>`;
            text = element.innerText.substr(0, maxLength) + overText;
            readonlyInput.style.zIndex = "1";
            counter.style.color = "#e0245e";
            button.classList.remove("active");
        } else {
            readonlyInput.style.zIndex = "-1";
            counter.style.color = "#333";
            text = element.innerText;
        }

        readonlyInput.innerHTML = text;
    }

    if (editableInput) {
        editableInput.onfocus = () => { placeholder.style.color = "#c5ccd3"; };
        editableInput.onblur = () => { placeholder.style.color = "#98a5b1"; };
        editableInput.onkeyup = (e) => validated(e.target);
        editableInput.onkeypress = (e) => { validated(e.target); placeholder.style.display = "none"; };
    }

    // --- STREAMING QUEUE LOGIC ---
    let tweetQueue = [];
    let isProcessing = false;
    let isStreaming = false;
    let streamXhr = null; // For downloading CSV
    let sseSource = null; // For listening to results

    const streamButton = document.getElementById("streamCSVButton");
    const stopButton = document.getElementById("stopStreamButton");
    const statusText = document.querySelector(".bottom p");

    if (streamButton && stopButton) {
        streamButton.addEventListener("click", startStream);
        stopButton.addEventListener("click", stopStream);
    }

    function startStream() {
        if (isStreaming) return;
        isStreaming = true;
        tweetQueue = [];

        // UI Updates
        streamButton.style.display = "none";
        stopButton.style.display = "inline-block";
        if (statusText) statusText.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading CSV...';

        // 1. Start SSE Listener to catch results
        setupSSEListener();

        // 2. Fetch CSV and Populate Queue
        streamXhr = new XMLHttpRequest();
        streamXhr.open("GET", "/stream_csv", true);

        let lastSuccessfulData = "";
        streamXhr.onprogress = function (event) {
            if (!isStreaming) return;
            const receivedData = event.currentTarget.response.slice(lastSuccessfulData.length);
            const lines = receivedData.split('\n').filter(line => line.trim());

            lines.forEach(line => {
                try {
                    const content = JSON.parse(line);
                    tweetQueue.push(content.content);
                } catch (e) {
                    console.log("JSON Parse error:", e);
                }
            });

            lastSuccessfulData = event.currentTarget.response;

            // Trigger processing if not already running
            if (!isProcessing && tweetQueue.length > 0) {
                processQueue();
            }
        };

        streamXhr.onloadend = function () {
            console.log("CSV Download Complete. Total tweets:", tweetQueue.length);
        };

        streamXhr.send();
    }

    function stopStream() {
        isStreaming = false;
        isProcessing = false;
        tweetQueue = []; // Clear queue

        if (streamXhr) { streamXhr.abort(); streamXhr = null; }
        if (sseSource) { sseSource.close(); sseSource = null; }

        streamButton.style.display = "inline-block";
        stopButton.style.display = "none";

        if (statusText) statusText.innerText = "Stream stopped.";

        // Clear inputs
        if (editableInput) editableInput.innerText = "";
        if (readonlyInput) readonlyInput.innerText = "";
        if (placeholder) placeholder.style.display = "block";
    }

    function setupSSEListener() {
        if (sseSource) sseSource.close();

        // Determine correct stream endpoint based on configuration passed to HTML
        let modelType = "spark"; // Default
        const wrapper = document.querySelector(".wrapper");
        if (wrapper && wrapper.dataset.modelType) {
            modelType = wrapper.dataset.modelType;
        }

        // Select endpoint: 'groq' -> _llm, otherwise standard
        // Note: APP_CONFIG['model_type'] values are 'spark' or 'groq' (from ai_config.html)
        const streamUrl = (modelType === 'groq') ? "/stream_inserts_llm" : "/stream_inserts";
        console.log("📡 Connecting to EventStream:", streamUrl);

        sseSource = new EventSource(streamUrl);

        sseSource.onmessage = function (event) {
            const data = JSON.parse(event.data);
            if (data.tracking_id && isProcessing) {
                handleResult(data);
            }
        };

        sseSource.onerror = function (err) {
            console.error("EventSource failed:", err);
            // Optional: Retry logic or notify user
        };
    }

    function processQueue() {
        if (!isStreaming || tweetQueue.length === 0) {
            if (isStreaming && tweetQueue.length === 0 && !streamXhr) {
                // Queue empty and download done
                stopStream();
            }
            return;
        }

        isProcessing = true;
        const currentTweet = tweetQueue.shift();
        const trackingId = crypto.randomUUID();

        // UI: Show Tweet
        if (editableInput) {
            editableInput.innerText = currentTweet;
            validated(editableInput); // Update counter/placeholder
        }
        if (statusText) statusText.innerHTML = `<i class="fas fa-circle-notch fa-spin"></i> Processing (${tweetQueue.length} left)...`;

        // Send
        fetch("/produce_tweets", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tweetContent: currentTweet, tracking_id: trackingId })
        })
            .then(res => res.json())
            .then(data => {
                console.log("Sent:", trackingId);
                // Now we WAIT for sseSource.onmessage to trigger handleResult

                // Cleanup/Timeout if prediction takes too long (e.g. 15s)
                setTimeout(() => {
                    if (isProcessing && isStreaming) {
                        // Timeout hit
                        console.warn("Timeout waiting for result:", trackingId);
                        handleResult({ tracking_id: trackingId, sentiment_label: "Timeout" });
                    }
                }, 10000); // 10s timeout
            })
            .catch(err => {
                console.error("Send error:", err);
                isProcessing = false;
                // Retry or skip? Skip for now.
                setTimeout(processQueue, 1000);
            });
    }

    function handleResult(data) {
        // Setup visual feedback
        const sentiment = data.sentiment_label || "Unknown";
        let color = "#666";
        let icon = "";

        if (sentiment === "Positive") { color = "var(--success)"; icon = "check-circle"; }
        else if (sentiment === "Negative") { color = "var(--danger)"; icon = "times-circle"; }
        else { color = "var(--warning)"; icon = "minus-circle"; }

        if (statusText) {
            statusText.innerHTML = `<span style="color:${color}; font-weight:bold"><i class="fas fa-${icon}"></i> ${sentiment}</span>`;
        }

        // Wait a bit so user can see the result, then process next
        isProcessing = false;
        setTimeout(() => {
            if (isStreaming) processQueue();
        }, 1500); // 1.5s delay to read result
    }

    // Manual Twist Post
    if (button) {
        button.addEventListener("click", function () {
            var tweetContent = readonlyInput.innerText;
            fetch("/produce_tweets", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ tweetContent: tweetContent })
            })
                .then(res => {
                    if (res.ok) {
                        editableInput.innerText = '';
                        placeholder.style.display = "block";
                        readonlyInput.innerHTML = '';
                        button.classList.remove("active");
                    }
                });
        });
    }
});
