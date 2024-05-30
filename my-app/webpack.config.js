const path = require('path');
const Dotenv = require('dotenv-webpack');

module.exports = {
  entry: './src/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
  },
  plugins: [
    new Dotenv({
      path: './.env', // Path to your .env file
      safe: false, // Load .env.example (defaults to "false" which does not use dotenv-safe)
      allowEmptyValues: true, // Allow empty variables (e.g. `FOO=`) (defaults to "false")
    }),
  ],
};
