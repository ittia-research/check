"""
Default HTML page.
It will fetch the same url with streaming header and process response as JSON.
If `stage` in response is `wait`, skip this part; else display the response with MARKDOWN formatting.

Purpose of this setup:
  - Display multiple stages.
  - Avoid CloudFlare 524 error when use CloudFlare as CDN.
"""
html_browser = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fact-check</title>
</head>
<body>
    <div id="content"></div>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
        async function fetchData() {
            try {
                const response = await fetch(window.location.href, {
                    headers: {
                        "Accept": "text/markdown"
                    }
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    let part = decoder.decode(value, { stream: true });

                    try {
                        const message = JSON.parse(part);
                        if (message.stage != "wait") {
                            document.getElementById('content').innerHTML = marked.parse(message.content);
                        }
                    } catch (e) {
                        console.error("Error parsing JSON:", e);
                    }
                }
            } catch (error) {
                document.getElementById('content').innerHTML = `Streaming failed: ${error}`;
            }
        }

        fetchData();
    </script>
</body>
</html>
"""

            # // Update display text with error message if fetch failed 
            # if (!response.ok) {
            #     document.getElementById('content').innerHTML = `Error ${response.status}: Processing failed`;
            #     return;
            # }