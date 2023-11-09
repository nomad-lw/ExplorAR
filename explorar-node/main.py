#!/usr/bin/env python3

import os
import sys
import time
import json
from dotenv import load_dotenv
import asyncio
import uvicorn
import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL
from search import SearchClient
from model import schema


app = FastAPI()
app.include_router(schema.router, prefix="/graphql")
search_client = SearchClient()


@app.get("/")
async def root():
    '''
    Root endpoint
    '''
    return {"message": "ExplorAR API", "version": "0.0.1"}

@app.get("/search")
async def search(query: str):
    '''
    Search

    Retuns a JSON object with the search results in format:
        txid: str
        title: str
        description: str
        type: str
        tags: List[Tag]
        markers: List[str]
    '''
    print(f"Searching for {query}")
    # res = search_client.search(query)
    # print pretty
    res = []
    for hit in search_client.search(query):
        doc = hit['_source']
        print(hit)
        res.append({
            "txid": doc['txid'],
            "title": doc['title'] if 'title' in doc else 'Title unavailable',
            "description": doc['description'] if 'description' in doc else 'Description unavailable',
            "type": doc['type'] if 'type' in doc else 'Type unavailable',
            "tags": doc['tags'] if 'tags' in doc else [],
            "markers": doc['markers'] if 'markers' in doc else []
        })
    # return in JSON format
    print(res)
    return json.dumps(res)


if __name__ == "__main__":
    load_dotenv()
    uvicorn.run(app, host="127.0.0.1", port=8000)