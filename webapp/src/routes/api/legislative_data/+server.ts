import type { RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({request}) => {
    try {
        const requestData = await request.json();

        const res = await fetch('http://127.0.0.1:8000/fetch_all_states_rag_parallel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData), // Pass the received body forward
        });

        if (!res.ok) {
            throw new Error(`Failed to fetch: ${res.statusText}`);
        }
        const data = await res.json();
        return jsonResponse(data);
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' },
        });
    }
};

// Optionally handle GET to return an error instead of "Method Not Allowed"
export const GET: RequestHandler = async () => {
    return new Response(JSON.stringify({ error: "Use POST instead of GET" }), {
        status: 405, // Method Not Allowed
        headers: { 'Content-Type': 'application/json' },
    });
};

const jsonResponse = (data: any) =>
    new Response(JSON.stringify(data), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
    });
