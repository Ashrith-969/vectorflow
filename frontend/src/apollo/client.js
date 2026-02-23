import { ApolloClient, InMemoryCache, createHttpLink, ApolloLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { onError } from '@apollo/client/link/error';

let token = null;

export const setToken = (t) => { token = t; };
export const getToken = () => token;

const httpLink = createHttpLink({
  uri: '/graphql',
});

const authLink = setContext((_, { headers }) => ({
  headers: {
    ...headers,
    ...(token ? { authorization: `Bearer ${token}` } : {}),
  },
}));

const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors) {
    for (const err of graphQLErrors) {
      if (err.extensions?.classification === 'UNAUTHORIZED') {
        setToken(null);
        window.location.href = '/login';
      }
    }
  }
  if (networkError) {
    console.error('[Network error]:', networkError);
  }
});

const client = new ApolloClient({
  link: ApolloLink.from([errorLink, authLink, httpLink]),
  cache: new InMemoryCache(),
  defaultOptions: {
    watchQuery: { fetchPolicy: 'network-only' },
    query: { fetchPolicy: 'network-only' },
  },
});

export default client;
