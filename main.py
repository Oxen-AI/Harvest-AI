from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import httpx
import uvicorn
import json
from harvest.jsonl_db import JSONLDB

app = FastAPI()
db = JSONLDB()  # Initialize our database handler

# Custom function to stream the response from the target API
async def stream_api_response(model: str, url: str, data: dict, headers: dict):
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
                    messages = data['messages']
                    messages.append({"role": "assistant", "content": accumulated_content})
                    # Save the completed chat to the database
                    await db.add(model, messages)

async def forward_request(request: Request, url: str):
    """
    Forwards a request to the target server and returns the response.
    Handles both streaming and non-streaming requests.
    """
    try:
        json_data = await request.json()
        print("Got request: ", json_data)

        # Make sure that the request has a model
        if 'model' not in json_data:
            raise HTTPException(
                status_code=400,
                detail="Model is required"
            )
        
        if 'messages' not in json_data:
            raise HTTPException(
                status_code=400,
                detail="Messages are required"
            )
        
        model = json_data['model']
        messages = json_data['messages']

        if 'stream' not in json_data or json_data.get('stream', True):
            return StreamingResponse(
                stream_api_response(model, url, json_data, {}),
                media_type='text/event-stream'
            )

        # Handle non-streaming request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=json_data)
            return_json = response.json()
            print("Got response: ", return_json)
            
            # Save the chat to the database for non-streaming requests
            messages.append(return_json['message'])
            
            await db.add(model, messages)
            
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

# Add a new endpoint to retrieve chat history
@app.get("/api/history")
async def get_history(limit: int = 100):
    """Retrieve chat history from the database."""
    return await db.get_chat_history(limit)

if __name__ == "__main__":
    # Run the FastAPI server on port 11435
    uvicorn.run(app, host="0.0.0.0", port=11435)

