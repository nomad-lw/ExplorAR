import React from 'react';
import { Box, Grid, GridItem, Flex, Center, IconButton } from '@chakra-ui/react';
import { Link as ReactRouterLink } from 'react-router-dom'
import { Link as ChakraLink } from '@chakra-ui/react'
// import { FiLogIn, FiLogOut } from 'react-icons/fi';
import { SettingsIcon } from '@chakra-ui/icons';
import SearchBar from '../components/SearchBar';
import SearchResultCard from '../components/SearchResultCard';
import dummy from '../data/dummy.json';
import { ConnectButton } from 'arweave-wallet-kit';
// import gql from 'graphql-tag';
// import useGraphQLQuery from '../hooks/useGraphQLQuery';

// const SEARCH_QUERY = gql`
//   query SearchQuery($query: String!) {
//     search(query: $query) {
//       txid
//       title
//       description
//       type
//       markers
//       tags {
//         key
//         value
//       }
//     }
//   }
// `;


const SearchPage: React.FC = () => {

    // import dummy data from json file located in src/data/searchResults.json
    const searchResults = dummy['results'];

    
    // perform search query

    // const handleSearch = (query: string) => {
    //     // Search for query using HTTP GET request
    //     res 
    // };

    // React.useEffect(() => {
    //     handleSearch('initialQuery');
    //   }, []);

    return (
        <>
            <Grid p={5} bg='gray.500' templateColumns="repeat(10, 1fr)" gap={2}>
                <GridItem colSpan={4} colStart={2}>
                    <SearchBar onSearch={() => {}} />
                </GridItem>
                <GridItem colSpan={1} colStart={9} colEnd={11} p={4}>
                    <Flex>
                        <ConnectButton />
                        <Center>
                            <ChakraLink as={ReactRouterLink} to='/home'>
                                <IconButton aria-label='Settings' icon={<SettingsIcon />} colorScheme='white' variant='outline' m={2} />
                            </ChakraLink>
                        </Center>
                    </Flex>
                </GridItem>
            </Grid>
            {/* results */}
            <Grid p={4} templateColumns="repeat(10, 1fr)" gap={2}>
                <GridItem maxW="container.lg" p={4} colSpan={8} colStart={2}>
                    <Box>
                        {searchResults.map((result, index) => (
                            <SearchResultCard key={index} {...result} />
                        ))}
                    </Box>
                </GridItem>
            </Grid>
        </>
    );
};

export default SearchPage;
