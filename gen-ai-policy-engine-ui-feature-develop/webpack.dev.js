const { merge } = require('webpack-merge');
const common = require('./webpack.config.js');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = merge(common, {
  mode: 'development',
  devtool: 'inline-source-map',
  devServer: {
    static: './dist',
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env': JSON.stringify({
        BACKEND_API_URL: "http://localhost:8888",
        TTL: 180000,
        SESSION_EXPIRATION_WARNING_PERIOD: 90000,
      }),
    }),
    new webpack.ProvidePlugin({
      process: 'process/browser.js',
    }),
    new HtmlWebpackPlugin({
      filename: 'index.html',
      template: 'public/dev.html'
    })
  ],
});