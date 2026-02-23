import { gql } from '@apollo/client';

export const SEARCH = gql`
  query Search($query: String!, $limit: Int, $filters: FilterInput) {
    search(query: $query, limit: $limit, filters: $filters) {
      results {
        id
        documentId
        title
        snippet
        score
        metadata {
          category
          tags
        }
      }
      totalCount
      query
    }
  }
`;

export const ASK = gql`
  query Ask($question: String!, $maxSources: Int) {
    ask(question: $question, maxSources: $maxSources) {
      answer
      sources {
        documentId
        title
        snippet
        relevance
      }
      confidence
      question
    }
  }
`;

export const ME = gql`
  query Me {
    me {
      id
      email
      role
      createdAt
    }
  }
`;

export const USERS = gql`
  query Users {
    users {
      id
      email
      role
      createdAt
    }
  }
`;
