"""
The return of requests from browser.
It will fetch the same url with markdown header and process content in the streams as markdown.
If `stage` in the stream in `wait`, this stream will be skipped.

Purpose of this setup:
  - Render multiple stages as markdown.
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
                console.log(part)

                try {
                    const message = JSON.parse(part);
                    if (message.stage != "wait") {
                        document.getElementById('content').innerHTML = marked.parse(message.content);
                    }
                } catch (e) {
                    console.error("Error parsing JSON:", e);
                }
            }
        }

        fetchData();
    </script>
</body>
</html>
"""
