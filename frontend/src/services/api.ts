const BASE_URL = "http://localhost:8080";

export async function searchFiles(query: string, topK: number = 5) {
  const res = await fetch(`${BASE_URL}/search?query=${encodeURIComponent(query)}&top_k=${topK}`);
  return res.json();
}

export async function startIndexing(directory: string) {
  const res = await fetch(`${BASE_URL}/index`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ folder_path: directory }),
  });
  return res.json();
}
