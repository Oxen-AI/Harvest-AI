from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import httpx
import uvicorn
import json
app = FastAPI()

# Custom function to stream the response from the target API
async def stream_api_response(url: str, data: dict, headers: dict):
    """
    Makes a streaming request to another API and yields the responses.
    """
    accumulated_content = ""  # Initialize accumulator string
    async with httpx.AsyncClient() as client:
        async with client.stream('POST', url, json=data, headers=headers) as response:
            if response.status_code != 200:
                error_detail = await response.aread()
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"API request failed: {error_detail.decode()}"
                )

            # Stream the response chunks
            async for chunk in response.aiter_bytes():
                # Decode the chunk and parse as JSON so that we can get the content
                raw_data = chunk.decode()
                chunk_json = json.loads(raw_data)
                print("Got chunk: ", chunk_json)
                content = chunk_json.get('message', {}).get('content', '')
                accumulated_content += content
                yield raw_data  # Yield the raw chunk for streaming

                # If this is the final chunk, save the accumulated content
                if chunk_json.get('done', False) and chunk_json.get('done_reason', '') == 'stop':
                    print("🎉 Final chunk received")
                    print(accumulated_content)

async def forward_request(request: Request, url: str):
    """
    Forwards a request to the target server and returns the response.
    Handles both streaming and non-streaming requests.
    """
    try:
        json_data = await request.json()
        print("Got request: ", json_data)

        if 'stream' not in json_data or json_data.get('stream', True):
            return StreamingResponse(
                stream_api_response(url, json_data, {}),
                media_type='text/event-stream'
            )

        # Forward the request to the target server
        async with httpx.AsyncClient() as client:
            # 11434 is the default port for Ollama
            response = await client.post(
                url,
                json=json_data
            )
            # Return the response from the target server
            return_json = response.json()
            print("Got response: ", return_json)
            return return_json
    except Exception as e:
        # Catch any errors and return a 500 error
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# Setup the generate endpoint
@app.post("/api/generate")
async def generate(request: Request):
    return await forward_request(request, "http://localhost:11434/api/generate")

# Setup the chat completion endpoint
@app.post("/api/chat")
async def chat_completion(request: Request):
    return await forward_request(request, "http://localhost:11434/api/chat")

if __name__ == "__main__":
    # Run the FastAPI server on port 11435
    uvicorn.run(app, host="0.0.0.0", port=11435)

