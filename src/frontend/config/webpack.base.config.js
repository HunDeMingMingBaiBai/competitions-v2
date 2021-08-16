var path = require("path")
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const devMode = true;

function resolve(dir) {
  return path.resolve('./', dir);
};

module.exports = {
    entry: [
        // "webpack-dev-server/client?http://localhost:5000",
        // "webpack/hot/only-dev-server",
        "babel-polyfill",
        path.resolve('./', "src")
    ],
    resolve: {
        alias: {
            '@labelstudio': path.resolve('./', "src"),
        }
    },
    output: {
        path: resolve("dist"),
        filename: '[name].[hash:10].js'
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                loader: 'babel-loader',
                include: path.resolve('./', "src"),
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
                exclude: path.resolve('./', 'node_modules'),
                use: [devMode ? 'style-loader' : MiniCssExtractPlugin.loader, 'css-loader']
            },
            {
                /** less stylesheet loader */
                test: /\.less$/,
                include: path.resolve('./', 'src'),
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
    },
    plugins: [
      new MiniCssExtractPlugin({
          filename: 'style/[name].[hash].css'
      }),
      new HtmlWebpackPlugin({
          template: resolve('src/index.html'),
          inject: true,
          minify: {
              collapseWhitespace: true
          },
          cache: false
      })
    ],
}
