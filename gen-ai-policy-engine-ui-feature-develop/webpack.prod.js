const { merge } = require('webpack-merge');
const common = require('./webpack.config.js');
const webpack = require('webpack');

module.exports = (env) => merge(common, {
  mode: 'production',
  plugins: [
    new webpack.DefinePlugin({
      'process.env': JSON.stringify({BACKEND_API_URL:env.BACKEND_API_URL})
    }),
    new webpack.ProvidePlugin({
      process: 'process/browser.js',
    }),
  ],
});