/**
 * @file production config
 * @author liguanlin<liguanlin@4paradigm.com>
 */
/* eslint-disable */

const webpack = require('webpack');
const path = require('path');
const { merge } = require('webpack-merge');
const base = require('./webpack.base.config.js');
const CopyWebpackPlugin = require('copy-webpack-plugin');

function resolve(dir) {
    return path.resolve('./', dir);
}

module.exports = merge(base, {
    mode: 'production',
    output: {
        path: resolve('dist/'),
        filename: '[name].[hash:10].js'
    },
    optimization: {
        splitChunks: {
            chunks: 'all',
            automaticNameDelimiter: '-'
        }
    },
    devtool: false,
    plugins: [
        new CopyWebpackPlugin({
            patterns: [{
                from: 'src/opencv.js',
            }]
        })
    ],
});
