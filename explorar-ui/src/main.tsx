import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'



import { ChakraProvider, extendTheme } from '@chakra-ui/react'


const config = {
  initialColorMode: 'dark',
  useSystemColorMode: true,
}

const theme = extendTheme({ config })


ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ChakraProvider theme={theme}>
      <App />
    </ChakraProvider>
  </React.StrictMode>,
)
