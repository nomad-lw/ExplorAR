// SearchResultCard.tsx
import React from 'react';
import { Box, Heading, Text, Link } from '@chakra-ui/react';
import { ExternalLinkIcon } from '@chakra-ui/icons'

interface SearchResultCardProps {
    title: string;
    description: string;
    txid: string;
    // Add more properties as needed
}

const SearchResultCard: React.FC<SearchResultCardProps> = ({ title, description, txid }) => {
    return (
        <Box p={4} borderWidth="1px" borderRadius="lg" overflow="hidden" mb={4}>
            <Heading as="h2" size="md" mb={2}>
                {title}
            </Heading>
            <Text color="gray.600">{description}</Text>
            {/* Add more content or properties as needed */}
            <Link href={"https://viewblock.io/arweave/tx/"+txid} isExternal>
                Viewblock <ExternalLinkIcon mx='2px' />
            </Link>
            {/* if markers contains "NFT", render the following Link */}
            
        </Box>
    );
};

export default SearchResultCard;
