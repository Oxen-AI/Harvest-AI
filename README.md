# Harvest-AI

A simple proxy server for "harvesting" LLM responses like a good farmer does 🐂 🌾

## Usage

```bash
python main.py
```

## Why?

There are many reasons you may want to setup a proxy between a product or service and a Local LLM. 

- **Security**: You may want a layer of security between your product or service and the LLM.
- **Filtering**: You may want to filter the LLM responses to ensure they are appropriate.
- **Cost/Performance**: You may want to save money by routing requests to different LLMs based on some criteria.
- **Customization**: You may want to customize the LLM response to fit your needs or API specification.
- **Data Collection**: You may want to collect data from the LLM responses for your own use.

In this case we will be optimizing for the Data Collection use case.

## How it works

This proxy server will forward requests to the LLM and return the response. It will also collect the request and response data and store it in a database.

## Contributing

TODO: Different database adapters...
TODO: Different LLM provider adapters...