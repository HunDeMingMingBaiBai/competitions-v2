const webpack = require('webpack')
const { merge } = require('webpack-merge');
const base = require('./webpack.base.config.js');
const http = require('http');
const connect = require('connect');
const apiMocker = require('connect-api-mocker');

const app = connect();

module.exports = merge(base, {
  mode: "development",
  devtool: "cheap-module-source-map",
  plugins: [
    // eslint-loader try to access this.options which was removed in webpack 4
    // as workaround use LoaderOptionsPlugin
    new webpack.LoaderOptionsPlugin({options: {}}),
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NamedModulesPlugin()
],
  devServer: {
    // publicPath: config.output.publicPath,
    historyApiFallback: true,
    hot: true,
    port: 5002,
    contentBase: './src',
    proxy: [{
        target: 'http://m7-model-gpu21:8082/',
        context: ['/labelstudio']
    }, {
      target: 'http://m7-model-gpu22:8302/',
      context: ['/predict']
    }],
    // before: function(app) {
    //   app.use('/labelstudio', apiMocker('./mocks/labelstudio'));
    // },
  }
});
