
import { graphql } from 'graphql';
import { schema } from './_lib/schema.js';

export default async function handler(req, res) {
  // CORS support
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Handle GraphiQL (GET request)
  if (req.method === 'GET') {
    res.setHeader('Content-Type', 'text/html');
    res.send(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Members Visualization GraphQL API</title>
        <link href="https://cdn.jsdelivr.net/npm/graphiql@3.0.6/graphiql.min.css" rel="stylesheet" />
        <script crossorigin src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
        <script crossorigin src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
        <script crossorigin src="https://cdn.jsdelivr.net/npm/graphiql@3.0.6/graphiql.min.js"></script>
      </head>
      <body style="margin: 0;">
        <div id="graphiql" style="height: 100vh;"></div>
        <script>
          const fetcher = (graphQLParams) =>
            fetch('/api/graphql', {
              method: 'post',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(graphQLParams),
            }).then((response) => response.json());
          
          ReactDOM.render(
            React.createElement(GraphiQL, { fetcher: fetcher }),
            document.getElementById('graphiql'),
          );
        </script>
      </body>
      </html>
    `);
    return;
  }

  // Handle GraphQL query (POST request)
  if (req.method === 'POST') {
    const { query, variables } = req.body || {};

    if (!query) {
      res.status(400).json({ errors: [{ message: 'Query is required' }] });
      return;
    }

    try {
      const result = await graphql({
        schema,
        source: query,
        variableValues: variables,
      });

      res.status(200).json(result);
    } catch (error) {
      console.error(error);
      res.status(500).json({ errors: [{ message: 'Internal Server Error' }] });
    }
    return;
  }

  res.status(405).json({ error: 'Method Not Allowed' });
}
