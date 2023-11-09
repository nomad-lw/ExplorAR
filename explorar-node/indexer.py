#!/usr/bin/env python3

import os
import sys
import time
import json
from dotenv import load_dotenv
import asyncio
import datetime
from elasticsearch import Elasticsearch
from frontier import Frontier

client = None

def get_elastic_client():
    global client
    if client is None:
        load_dotenv()
        client = Elasticsearch(
            "http://" + os.getenv("ELASTICSEARCH_HOST") + ":" + os.getenv("ELASTICSEARCH_PORT"),
            api_key=os.getenv("ELASTICSEARCH_API_KEY"),
        )
        # API key should have cluster monitor rights
        client.info()
        print("Initialized ES client: Elasticsearch version:", client.info()["version"]["number"])
    return client


class Indexer:
    """
    Indexer class
    """

    def __init__(self):
        """
        Constructor
        """
        self.client = get_elastic_client()
        self.index_name = "search-artx"
        # self.index_settings = {
        #     "settings": {
        #         "number_of_shards": 1,
        #         "number_of_replicas": 0,
        #         "analysis": {
        #             "analyzer": {
        #                 "default": {
        #                     "type": "custom",
        #                     "tokenizer": "standard",
        #                     "filter": ["lowercase", "stop", "snowball"],
        #                 }
        #             }
        #         },
        #     },
        #     "mappings": {
        #         "properties": {
        #             "content": {"type": "text"},
        #             "txid": {"type": "text"},
        #             "tags": {"type": "text"},
                    
        #         }
        #     },
        # }
        # self.init_index()

    def init_index(self):
        """
        Initialize the index
        """
        if not self.client.indices.exists(self.index_name):
            self.client.indices.create(
                index=self.index_name, body=self.index_settings
            )
            print("Indexer: Created index", self.index_name)
        else:
            print("Indexer: Index", self.index_name, "already exists")

    def index_document(self, doc):
        """
        Index a document
        """
        print("Indexer: Indexing document:", doc)
        self.client.index(index=self.index_name, body=doc, id=doc["txid"])

    def update_document(self, doc):
        """
        Update a document
        """
        print("Indexer: Updating document:", doc)
        self.client.update(index=self.index_name, id=doc["txid"], doc=doc)

def index_lifecycle():
    """
    Index lifecycle
    """
    indexer = Indexer()
    frontier = Frontier()
    while True:
        print("Indexer: Index lifecycle")
        tx = frontier.get_next_tx()
        if tx is None:
            print("Indexer: No transactions to index")
            time.sleep(1)
            continue
        else:
            print("Indexer: Indexing transaction:", tx["txid"])
            indexer.index_document(tx)

# expects a elasticsearch document as input, returns an updated document in tuple
def local_index_ANS110(document):
    # check if the document's metadata is ANS-110 compliant
    """
        ANS-110 compliant metadata:
            "tags": {
                "Title"*: str,
                "Type"*: str,
                "Description": str,
                "Topic": str
            }
    """
    metadata = document['_source']['tags']
    # check for required fields
    title = None
    type = None
    description = None
    topics = []
    for tag in metadata:
        if tag['name'] == 'Title':
            title = tag['value']
        elif tag['name'] == 'Type':
            type = tag['value']
        elif tag['name'] == 'Description':
            description = tag['value']
        elif "Topic:" in tag['name']:
            topics.append(tag['value'])
    if title is None or type is None:
        print("Indexer: Document is not ANS-110 compliant")
        return (False, document)
    # update the document
    document['_source']['title'] = title
    document['_source']['type'] = type
    document['_source']['description'] = description
    document['_source']['topics'] = topics
    if 'markers' not in document['_source']:
        document['_source']['markers'] = ["ANS-110"]
    else:
        if "ANS-110" not in document['_source']['markers']:
            document['_source']['markers'].append("ANS-110")
    # # remove the old tags
    # del document['_source']['tags']
    print("Indexer: Document is ANS-110 compliant")
    print(json.dumps(document, indent=4))
    # sys.exit()
    return (True, document)

def index_Misc(document):
    """
        Index: NFTs and UDLs
        Defining NFTs as docs with ANS-110 mdata + ContentType: "image/*"
        UDLs as docs with ANS-110 mdata + tag: "License"
    """
    metadata = document['_source']['tags']
    # check for required fields
    if 'ANS-110' in document['_source']['markers']:
        for tag in metadata:
            if tag['name'] == 'ContentType':
                if "image" in tag['value']:
                    # It's an NFT!
                    document['_source']['markers'].append("NFT")
            if tag['name'] == 'License':
                # It's a UDL!
                document['_source']['markers'].append("UDL")
                


def deep_index():
    indexer = Indexer()
    while True:
        # get all documents from elasticsearch, in batches of 10,000, using the scroll API
        documents = indexer.client.search(
            index=indexer.index_name,
            scroll="2m",
            size=10000,
            body={"query": {"match_all": {}}},
        )
        # get the scroll ID
        sid = documents["_scroll_id"]
        # get the first batch of documents
        hits = documents["hits"]["hits"]
        # while there is a batch of documents
        while len(hits):
            # for each document
            for hit in hits:
                # get the document ID
                txid = hit["_id"]
                # run local_index_ANS110
                (is_ANS110, document) = local_index_ANS110(hit)
                index_NFT(document)
                # update the document
                if is_ANS110:
                    indexer.update_document(document['_source'])
            # get the next batch of documents
            documents = indexer.client.scroll(scroll_id=sid, scroll="2m")
            # get the scroll ID
            sid = documents["_scroll_id"]
            # get the next batch of documents
            hits = documents["hits"]["hits"]







    # number of documents
    num_docs = documents["hits"]["total"]["value"]
    print(f"Found {num_docs} documents")




def main():
    global client
    load_dotenv()

    # client = get_elastic_client()

    indexer = Indexer()
    frontier = Frontier()

    deep_index()




if __name__ == "__main__":
    main()
