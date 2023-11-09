import { HashRouter } from "react-router-dom";
import { Routes, Route } from "react-router-dom";
import { ArweaveWalletKit } from "arweave-wallet-kit";
import { ApolloClient, InMemoryCache, ApolloProvider } from '@apollo/client';


// import Home from "./views/Home";
import SearchPage from "./views/SearchPage";


const client = new ApolloClient({
  uri: 'https://127.0.0.1/graphql',
  cache: new InMemoryCache(),
});

function App() {
  // const [count, setCount] = useState(0)

  return (
    <>
      <ArweaveWalletKit
        config={{
          permissions: ["ACCESS_ADDRESS", "SIGN_TRANSACTION"],
          ensurePermissions: true,
          appInfo: {
            name: "Explorar",
          }
        }}
      >
        <ApolloProvider client={client}>
          <HashRouter>
            <Routes>
              <Route path="/" element={<SearchPage />} />
            </Routes>
          </HashRouter>
        </ApolloProvider>
      </ArweaveWalletKit>
    </>
  )
}

export default App
