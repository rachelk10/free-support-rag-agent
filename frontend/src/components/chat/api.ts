export interface ContactResponse {
  request_id: string;
  status: string;
  final_output?: string;
  category?: string;
  output_type?: string;
  retry_count: number;
  needs_human: boolean;
}

const DEFAULT_API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function sendContactMessage(
  message: string,
): Promise<ContactResponse> {
  const response = await fetch(`${DEFAULT_API_BASE_URL}/contact`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const bodyText = await response.text();
    throw new Error(`API error ${response.status}: ${bodyText}`);
  }

  return response.json();
}
