from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
import os

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建 static 目录
if not os.path.exists("static"):
    os.makedirs("static")

# HTML 内容
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JAV Search</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .line-clamp-2 {
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
    </style>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <!-- Search Bar -->
        <div class="mb-8">
            <div class="flex gap-4">
                <input type="text" 
                       id="searchInput"
                       class="w-full md:w-1/2 px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:border-blue-500"
                       placeholder="Search JAV...">
                <button onclick="performSearch()" 
                        class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none">
                    Search
                </button>
            </div>
        </div>

        <!-- Results Grid -->
        <div id="resultsGrid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            <!-- Cards will be dynamically inserted here -->
        </div>

        <!-- Loading Indicator -->
        <div id="loadingIndicator" class="hidden">
            <div class="flex justify-center items-center p-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        </div>
    </div>

    <script>
        // Card template function
        function createCard(item) {
            return `
                <div class="bg-white rounded-lg shadow-md overflow-hidden">
                    <div class="aspect-w-3 aspect-h-4 relative">
                        <img class="w-full h-64 object-cover" 
                             src="${item.image_urls[0]}" 
                             alt="${item.code}"
                             onerror="this.src='https://via.placeholder.com/300x400?text=No+Image'">
                        <div class="absolute top-2 left-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded">
                            <span class="text-sm font-semibold">${item.code}</span>
                        </div>
                    </div>

                    <div class="p-4">
                        <h3 class="text-lg font-semibold mb-2 line-clamp-2">
                            ${item.descriptions[0]}
                        </h3>

                        <div class="mb-2">
                            <span class="text-sm text-gray-600">Actresses:</span>
                            <span class="text-sm text-blue-600">${item.actresses.join(', ')}</span>
                        </div>

                        <div class="flex flex-wrap gap-1 mb-3">
                            ${item.tags.map(tag => 
                                `<span class="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">${tag}</span>`
                            ).join('')}
                        </div>

                        <div class="flex flex-col gap-2">
                            ${item.downloads.map((link, index) => 
                                `<a href="${link}" 
                                    target="_blank" 
                                    class="text-sm text-blue-600 hover:underline">
                                    Download Link ${index + 1}
                                </a>`
                            ).join('')}
                        </div>
                    </div>
                </div>
            `;
        }

        // Search functionality
        async function performSearch() {
            const searchInput = document.getElementById('searchInput');
            const resultsGrid = document.getElementById('resultsGrid');
            const loadingIndicator = document.getElementById('loadingIndicator');
            const query = searchInput.value.trim();

            if (!query) return;

            // Show loading indicator
            loadingIndicator.classList.remove('hidden');
            resultsGrid.innerHTML = '';

            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();

                // Hide loading indicator
                loadingIndicator.classList.add('hidden');

                // Display results
                if (data.length === 0) {
                    resultsGrid.innerHTML = '<div class="col-span-full text-center text-gray-500">No results found</div>';
                    return;
                }

                const cardsHTML = data.map(item => createCard(item)).join('');
                resultsGrid.innerHTML = cardsHTML;

            } catch (error) {
                console.error('Error fetching data:', error);
                loadingIndicator.classList.add('hidden');
                resultsGrid.innerHTML = '<div class="col-span-full text-center text-red-500">Error loading results</div>';
            }
        }

        // Handle Enter key press
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });

        // Initial search on page load
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('q')) {
            document.getElementById('searchInput').value = urlParams.get('q');
            performSearch();
        }
    </script>
</body>
</html>
"""

# 将 HTML 内容写入文件
with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# API 代理端点
@app.get("/api/search")
async def search(q: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://app.laisky.com/jav/search",
                params={"q": q},
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=str(e))

# 根路由返回 index.html
@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

# 挂载静态文件到 /static 路径
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
