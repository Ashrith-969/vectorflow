import { gql } from '@apollo/client';

export const LOGIN = gql`
  mutation Login($input: LoginInput!) {
    login(input: $input) {
      token
      user {
        id
        email
        role
        createdAt
      }
    }
  }
`;

export const REGISTER = gql`
  mutation Register($input: RegisterInput!) {
    register(input: $input) {
      token
      user {
        id
        email
        role
        createdAt
      }
    }
  }
`;

export const INGEST = gql`
  mutation Ingest($input: IngestInput!) {
    ingest(input: $input) {
      documentId
      title
      chunkCount
      status
      message
    }
  }
`;

export const BULK_INGEST = gql`
  mutation BulkIngest($input: BulkIngestInput!) {
    bulkIngest(input: $input) {
      total
      successful
      failed
      results {
        documentId
        title
        chunkCount
        status
        message
      }
    }
  }
`;

export const DELETE_DOCUMENT = gql`
  mutation DeleteDocument($documentId: ID!) {
    deleteDocument(documentId: $documentId) {
      success
      message
    }
  }
`;

export const ASSIGN_ROLE = gql`
  mutation AssignRole($input: AssignRoleInput!) {
    assignRole(input: $input) {
      success
      message
      user {
        id
        email
        role
        createdAt
      }
    }
  }
`;
