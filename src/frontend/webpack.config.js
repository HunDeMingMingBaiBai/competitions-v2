var path = require("path")
var webpack = require("webpack");
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const devMode = true;

module.exports = {
    mode: "development",
    devtool: "cheap-module-source-map",
    entry: [
        // "webpack-dev-server/client?http://localhost:5000",
        "webpack/hot/only-dev-server",
        "babel-polyfill",
        "./src/index"
    ],
    resolve: {
        alias: {
            '@labelstudio': path.join(__dirname, "src"),
        }
    },
    output: {
        path: path.join(__dirname, "dist"),
        filename: "bundle.js",
        publicPath: "/static/"
    },
    plugins: [
        new webpack.HotModuleReplacementPlugin(),
        new webpack.NoEmitOnErrorsPlugin()
    ],
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                loader: 'babel-loader',
                include: path.join(__dirname, "src")
            },
            {
                /** image loader */
                test: /\.(png|jpe?g|gif|svg)$/,
                loader: 'url-loader',
                options: {
                    limit: 10000,
                    fallback: require.resolve('file-loader'),
                }
            },
            {
                /** css stylesheet loader */
                test: /\.css/,
                exclude: path.join(__dirname, 'node_modules'),
                use: [devMode ? 'style-loader' : MiniCssExtractPlugin.loader, 'css-loader']
            },
            {
                /** less stylesheet loader */
                test: /\.less$/,
                include: path.join(__dirname, 'src'),
                use: [
                    devMode
                        ? {
                            loader: 'style-loader',
                        }
                        : MiniCssExtractPlugin.loader,
                    {
                        loader: 'css-loader'
                    },
                    {
                        loader: 'less-loader'
                    }
                ]
            }
        ]
    }
}
