// SimpleSearchBar.tsx
import React, { useState, ChangeEvent, KeyboardEvent } from 'react';
import { Input, InputGroup, InputRightElement } from '@chakra-ui/react';
import { SearchIcon, CloseIcon } from '@chakra-ui/icons';

interface SearchBarProps {
    onSearch: (query: string) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
    const [query, setQuery] = useState('');


    const handleSearch = (event: ChangeEvent<HTMLInputElement>) => {
        onSearch(event.target.value);
        setQuery(event.target.value);
    }

    const handleOnChange = (event: ChangeEvent<HTMLInputElement>) => {
        setQuery(event.target.value);

    }

    const handleKeyPress = (event: KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            handleSearch(event as unknown as ChangeEvent<HTMLInputElement>);
        }
    }

    return (
        <InputGroup bg='white' mt={5} borderRadius={5} w='100%' >
            <Input
                type="text"
                placeholder="Search"
                value={query}
                onChange={handleOnChange}
                onKeyDown={handleKeyPress}
                h='50px'
            />
            <InputRightElement pointerEvents="none" h='100%'>
                {query && <CloseIcon color="gray.400" onClick={() => setQuery('')} />}
                <SearchIcon color="gray.500" m={3} mr={8} />
            </InputRightElement>
        </InputGroup>
    );
};

export { SearchBar };

export default SearchBar;
