# Strawberry GraphQL model for the explorar-node service

import strawberry
from strawberry.types import Info
from typing import List, Optional
from search import SearchClient
from strawberry.fastapi import GraphQLRouter
import json

search_client = SearchClient()

@strawberry.type
class Tag:
    '''
    Tag
    '''
    key: str
    value: str

@strawberry.type
class SearchResult:
    '''
    Search result
    '''
    txid: str
    title: str
    description: str
    type: str
    tags: List[Tag]
    markers: List[str]

@strawberry.type
class Query:
    '''
    Query
    '''
    @strawberry.field
    def search(self, info: Info, query: str) -> List[SearchResult]:
        '''
        Search
        '''
        print(f"Searching for {query}")
        # res = search_client.search(query)
        # print pretty
        res = []
        for hit in search_client.search(query):
            doc = hit['_source']
            # print(json.dumps(hit, indent=4))
            tags = []
            for tag in doc['tags']:
                tags.append(Tag(key=tag['name'], value=tag['value']))
            res.append(SearchResult(
                txid=doc['txid'],
                title= doc['title'] if 'title' in doc else 'Title unavailable',
                description=doc['description'] if 'description' in doc else 'Description unavailable',
                type=doc['type'] if 'type' in doc else 'Unknown',
                tags=tags,
                markers=doc['markers'] if 'markers' in doc else []
            ))
        # print(json.dumps(res, indent=4))
        return res
    
    @strawberry.field
    def get(self, info: Info, txid: str) -> Optional[SearchResult]:
        '''
        Get
        '''
        return search_client.get(txid)
    

schema = strawberry.Schema(query=Query)
router = GraphQLRouter(schema=schema)

