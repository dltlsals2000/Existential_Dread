# Existential Dread

## Project Design

1. Periodically fetch Reddit posts and store them in S3.
  - Should have used Amazon Lambda and Eventbridge, but due to Reddit blocking AWS IPs, had to run it locally.
2. Fetch authoritative sources (https://www.alberta.ca) and store text in S3.
  - Use `Titan Text Embeddings v2` embedding model to convert the data to vectors and store them in Amazon OpenSearch Serverless.
3. RAG approach: input a Reddit post and retrieve relevant data from Opensearch using semantic search and feed them to Amazon Bedrock.
4. Bedrock will verify the post. If it's verified as important post, its id is stored in S3. Otherwise, nothing happens.
5. Frontend service will fetch the ids of verified posts from S3 and fetch them to show them as important posts.