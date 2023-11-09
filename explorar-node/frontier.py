#!/usr/bin/env python3

"""
frontier.py

This file contains the frontier class, which is responsible for managing the frontier of the crawler.
A frontier is a queue of URLs to be crawled. The frontier is responsible for managing the queue, and
for ensuring that URLs are not crawled more than once.

The file also contains a function to populate the frontier with seed URLs. This function is called


All URLs are stored in a mongodb database. The database has a single collection, called "urls".
Each document in the collection has the following fields:
- url: URL of the page
- block_no: Block number of the page/artx
- crawled_at: Timestamp of when the document was crawled

The frontier has two methods:
- get_next_url(): Returns the next URL to crawl
- mark_url_crawled(url): Marks the URL as crawled

"""

import os
import sys
import time
import json
from dotenv import load_dotenv
import asyncio
import datetime
from pymongo import MongoClient

# graphql client
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport


class Frontier:
    """
    Frontier class
    """

    def __init__(self):
        """
        Constructor
        """
        load_dotenv()
        self.client = None
        self.db = None
        self.collection = None
        self.init_db()
        self.test_db()

    def init_db(self):
        """
        Initialize the database connection
        """
        # connect to the client, using the environment variables MONGODB_HOST, MONGODB_PORT, MONGODB_DATABASE, MONGODB_USER and MONGODB_PASSWORD
        self.client = MongoClient(
            "mongodb://"
            + os.getenv("MONGODB_USER")
            + ":"
            + os.getenv("MONGODB_PASSWORD")
            + "@"
            + os.getenv("MONGODB_HOST")
            + ":"
            + os.getenv("MONGODB_PORT")
        )
        # connect to server
        self.client.server_info()
        print("Frontier: Connected to MongoDB server")
        # get database, print collection names
        try:
            self.db = self.client[os.getenv("MONGODB_DATABASE")]
            print("Database:", self.db)
            # print("Collections:", self.db.list_collection_names())
        except:
            print("Error getting database")
            sys.exit(1)
        # get collection, if it doesn't exist, create it
        try:
            self.collection = self.db["artx"]
            print("Collection exists:", self.collection)
        except:
            print("Error getting collection")
            sys.exit(1)

    def test_db(self):
        """
        Test the database connection
        """
        print("MongoDB version:", self.client.server_info()["version"])

    def ingest_txs(self, txs):
        """
        Ingest a list of TXs/URLs into the frontier
        """
        for tx in txs:
            # if the URL is not in the database, add it
            if self.collection.count_documents({"txid": tx["id"]}) == 0:
                # add the URL to the database
                self.collection.insert_one(
                    {
                        "txid": tx["id"],
                        "block_no": tx["block_no"],
                        "crawled_at": None,
                    }
                )
                print("Frontier: Added URL to database:", tx["id"])
            else:
                print("Frontier: URL already in database:", tx["id"])
        print("Frontier: Ingested", len(txs), "URLs")

    def get_next_tx(self, block_no=None, repeat=False):
        """
        Get the next TX to crawl
        """
        # find the oldest TX that has not been crawled
        query = {"crawled_at": None}
        if block_no is not None:
            query["block_no"] = int(block_no)
        tx = self.collection.find_one(query, sort=[("block_no", 1)])
        if tx is None:
            print("Frontier: No TXs to crawl")
            return None
        else:
            print("Frontier: Next TX to crawl:", tx["txid"])
            return tx

    def mark_tx_crawled(self, tx):
        """
        Mark a TX as crawled
        """
        # mark the TX as crawled
        self.collection.update_one(
            {"txid": tx["txid"]}, {"$set": {"crawled_at": datetime.datetime.now()}}
        )
        print("Frontier: Marked TX as crawled:", tx["txid"])


def populate_frontier(frontier, block_no=None):
    """
    Populate the frontier with seed URLs (arweave TXs)
    by connecting to the arweave node using graphql and
    querying for the latest block number, then querying
    for the latest 1000 blocks, and ingesting all the TXs
    in those blocks into the frontier.

    """
    # get the frontier
    if frontier is None:
        frontier = Frontier()
    # connect to the arweave node
    load_dotenv()
    # initialize graphql client
    transport = AIOHTTPTransport(
        url=os.getenv("ARWEAVE_GQL_HOST") + "/graphql",
        headers={"User-Agent": "Python-arweave"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)
    print("Connected to Arweave node")
    # get the latest block number
    query = """
    query {
        blocks(first: 1) {
            edges {
                node {
                    height
                }
            }
        }
    }
    """
    result = client.execute(gql(query))
    # get the block number
    height = None
    if block_no is None:
        height = result["blocks"]["edges"][0]["node"]["height"]
    else:
        height = int(block_no)
    print("Block number:", height)
    # get the transactions for the latest 50 blocks
    for i in range(height, height - 50, -1):
        print("Getting transactions for block", i)
        query = (
            """
        query {
            transactions(block: {min: """
            + str(i)
            + """, max: """
            + str(i)
            + """}, first: 100) {
                edges {
                    node {
                        id
                        block {
                            height
                        }
                    }
                    cursor
                }
                pageInfo {
                    hasNextPage
                }
            }
        }
        """
        )
        while True:
            result = client.execute(gql(query))
            # get the transactions
            txs = []
            for tx in result["transactions"]["edges"]:
                txs.append(
                    {"id": tx["node"]["id"], "block_no": tx["node"]["block"]["height"]}
                )
            # ingest the transactions into the frontier
            frontier.ingest_txs(txs)
            # if there is a next page, get the next page
            if result["transactions"]["pageInfo"]["hasNextPage"]:
                query = (
                    """
                query {
                    transactions(block: {min: """
                    + str(i)
                    + """, max: """
                    + str(i)
                    + """}, first: 100, after: \""""
                    + tx["cursor"]
                    + """\") {
                        edges {
                            node {
                                id
                                block {
                                    height
                                }
                            }
                            cursor
                        }
                        pageInfo {
                            hasNextPage
                        }
                    }
                }
                """
                )
            else:
                break
    frontier.ingest_txs(txs)


if __name__ == "__main__":
    frontier = Frontier()
    print("Frontier initialized")
    print("Frontier test passed")
    if len(sys.argv) > 1:
        block_no = sys.argv[1]
        populate_frontier(frontier, block_no)
    else:
        populate_frontier(frontier)
