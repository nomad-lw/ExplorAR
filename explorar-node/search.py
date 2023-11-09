#!/usr/bin/env python3

import os
import sys
import time
import json
from dotenv import load_dotenv
import asyncio
from elasticsearch import Elasticsearch

class SearchClient:
    """
    Search client class
    """

    def __init__(self):
        """
        Constructor
        """
        load_dotenv()
        self.client = Elasticsearch(
            "http://" + os.getenv("ELASTICSEARCH_HOST") + ":" + os.getenv("ELASTICSEARCH_PORT"),
            api_key=os.getenv("ELASTICSEARCH_API_KEY"),
        )
        # API key should have cluster monitor rights
        self.client.info()
        print("Initialized ES client: Elasticsearch version:", self.client.info()["version"]["number"])

    def search(self, query):
        """
        Search
        """
        # search
        res = self.client.search(
            index="search-artx",
            q=query,
        )
        # return the results
        return res["hits"]["hits"]
    
if __name__ == "__main__":
    load_dotenv()
    search_client = SearchClient()
    # search
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = "redstone"
    res = search_client.search(query)
    # print the results
    print(json.dumps(res, indent=4))