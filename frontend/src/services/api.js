const API_BASE_URL = "http://127.0.0.1:8000";

export async function fetchPlan(searchData) {
  const response = await fetch(`${API_BASE_URL}/plan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      origin: searchData.origin,
      destination: searchData.destination,
      budget: Number(searchData.budget),
      travelers: Number(searchData.travelers),
      start_date: searchData.start_date,
      end_date: searchData.end_date,
    }),
  });

  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;

    try {
      const errorData = await response.json();

      if (errorData.detail) {
        errorMessage = errorData.detail;
      }
    } catch {
      // Keep the default error message
    }

    throw new Error(errorMessage);
  }

  return await response.json();
}