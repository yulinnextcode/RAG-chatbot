const { merge } = require('webpack-merge');
const common = require('./webpack.config.js');
const webpack = require('webpack');

module.exports = merge(common, {
  mode: 'development',
  devtool: 'inline-source-map',
  devServer: {
    static: './dist',
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env': JSON.stringify({
        TTL: 180000,
        SESSION_EXPIRATION_WARNING_PERIOD: 90000,
        RESPONSE_TIMEOUT:5000
      }),
    }),
  ],
});