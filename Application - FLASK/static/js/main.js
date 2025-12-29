document.addEventListener("DOMContentLoaded", function () {
    // Only run on pages with tweet input
    const wrapper = document.querySelector(".wrapper");
    if (!wrapper) return;

    const editableInput = wrapper.querySelector(".editable");
    const readonlyInput = wrapper.querySelector(".readonly");
    const placeholder = wrapper.querySelector(".placeholder");
    const counter = wrapper.querySelector(".counter");
    const button = wrapper.querySelector("#tweetButton");

    if (!editableInput) return; // Exit if no editable input

    editableInput.onfocus = () => {
        placeholder.style.color = "#c5ccd3";
    };

    editableInput.onblur = () => {
        placeholder.style.color = "#98a5b1";
    };

    editableInput.onkeyup = (e) => {
        let element = e.target;
        validated(element);
    };

    editableInput.onkeypress = (e) => {
        let element = e.target;
        validated(element);
        placeholder.style.display = "none";
    };

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

    // Tweet Button
    if (button) {
        button.addEventListener("click", function () {
            var tweetContent = readonlyInput.innerText;
            console.log("Tweet Content:", tweetContent);

            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/produce_tweets", true);
            xhr.setRequestHeader("Content-Type", "application/json");

            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {
                    console.log("AJAX Response:", xhr.responseText);
                    if (xhr.status === 200) {
                        console.log("Tweet posted successfully!");
                        editableInput.innerText = '';
                        placeholder.style.display = "block";
                        readonlyInput.innerHTML = '';
                        button.classList.remove("active");
                    } else {
                        console.error("Error during AJAX request:", xhr.status);
                    }
                }
            };

            xhr.send(JSON.stringify({ tweetContent: tweetContent }));
        });
    }

    // Stream Control Logic
    const streamButton = document.getElementById("streamCSVButton");
    const stopButton = document.getElementById("stopStreamButton");

    if (streamButton && stopButton) {
        let streamXhr = null;
        let isStreaming = false;

        streamButton.addEventListener("click", function () {
            startStream();
        });

        stopButton.addEventListener("click", function () {
            stopStream();
        });

        function startStream() {
            isStreaming = true;
            streamButton.style.display = "none";
            stopButton.style.display = "inline-block";

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
                        editableInput.innerText = content.content;
                        readonlyInput.innerText = content.content;
                        placeholder.style.display = "none";

                        setTimeout(function () {
                            if (isStreaming) sendTweet(content.content);
                        }, 3000);

                        lastSuccessfulData += line + "\n";
                    } catch (e) {
                        console.log("Error parsing JSON:", e);
                    }
                });
            };

            streamXhr.onloadend = function () {
                if (isStreaming) {
                    stopStream();
                }
            };

            streamXhr.send();
        }

        function stopStream() {
            isStreaming = false;
            if (streamXhr) {
                streamXhr.abort();
                streamXhr = null;
            }

            streamButton.style.display = "inline-block";
            stopButton.style.display = "none";
            console.log("Stream stopped by user.");
        }

        function sendTweet(tweetContent) {
            if (!isStreaming) return;

            console.log("Sending tweet:", tweetContent);

            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/produce_tweets", true);
            xhr.setRequestHeader("Content-Type", "application/json");

            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {
                    console.log("AJAX Response:", xhr.responseText);
                    if (xhr.status === 200) {
                        console.log("Tweet posted successfully!");
                        editableInput.innerText = '';
                        readonlyInput.innerText = '';
                        placeholder.style.display = "block";
                    } else {
                        console.error("Error during AJAX request:", xhr.status);
                    }
                }
            };

            xhr.send(JSON.stringify({ tweetContent: tweetContent }));
        }
    }
});
