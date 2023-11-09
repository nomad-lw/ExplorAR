#!/usr/bin/env python3

import os
import sys
import time
import json
from dotenv import load_dotenv
import asyncio
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from frontier import Frontier
from indexer import Indexer
import requests
# scrapy



class Crawler:
    """
    Crawler class
    """

    def __init__(self):
        """
        Constructor
        """
        load_dotenv()
        self.frontier = Frontier()
        # graphql client
        self.transport = AIOHTTPTransport(
            url=os.getenv("ARWEAVE_GQL_HOST") + "/graphql",
            headers={"User-Agent": "Python-arweave"},
        )
        self.gql = Client(transport=self.transport, fetch_schema_from_transport=True)
        # indexer, frontier
        self.indexer = Indexer()
        self.frontier = Frontier()
    
    def get_tx_data(self, tx):
        """
        Get the data for a TX
        """
        # get the data via HTTP
        query = "https://" + os.getenv("GATEWAY_HOST") + "/" + tx["txid"]
        print("Crawler: Getting data for TX:", query)
        response = requests.get(query)
        # check the status code
        if response.status_code != 200:
            print("Crawler: Error getting data for TX:", tx["txid"])
            return None
        # return the data
        return response.text

    def crawl(self, block_no=None):
        """
        The main crawl function
        
        A crawler should:
        - Get a url/tx from frontier
        - get metadata for the url/tx
        - get data for the url/tx if it is a content tx
        - index the data
        - update the frontier
        """
        # get the next TX from the frontier
        if block_no is None:
            tx = self.frontier.get_next_tx()
        else:
            tx = self.frontier.get_next_tx(int(block_no))
        if tx is None:
            print("Crawler: No TXs to crawl")
            return
        # get the metadata for the TX
        query = """
        query {
            transaction(id: "%s") {
                id
                tags {
                    name
                    value
                }
            }
        }
        """ % (
            tx["txid"]
        )
        result = self.gql.execute(gql(query))
        # get the tags
        tags = result["transaction"]["tags"]
        # look for the Content-Type tag
        content_type = None
        for tag in tags:
            if tag["name"] == "Content-Type":
                content_type = tag["value"]
                break
        # if the content type is text/html, get the data and index it using scrapy
        content =  None
        if content_type == "text/html":
            # get the data via HTTP
            data = self.get_tx_data(tx)
            # truncate the data upto 50KB
            content = data[:50000]
        # index the document
        doc = {
            "txid": tx["txid"],
            "tags": tags,
            "content": content
        }
        self.indexer.index_document(doc)
        # mark the TX as crawled
        self.frontier.mark_tx_crawled(tx)

    def crawl_lifecycle(self, block_no=None):
        """
        Crawl lifecycle
        """
        crawler = Crawler()
        print("Crawler: Init crawl lifecycle")
        while True:
            crawler.crawl(block_no)


def main(block_no=None):
    # load_dotenv()
    crawler = Crawler()
    crawler.crawl_lifecycle(block_no)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        block_no = sys.argv[1]
        main(block_no)
    else:
        main()