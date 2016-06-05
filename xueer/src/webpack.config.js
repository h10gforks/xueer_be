var webpack = require("webpack");
var path = require('path');
var ExtractTextPlugin =require('extract-text-webpack-plugin');

var isProduction = function(){
	return process.env.NODE_ENV === 'production';
};

var devConfig = {
	cache: true,
	entry: {
		main: './js/main.js',
		banner: './js/banner.js',
		comment: './js/comment.js',
		search: './js/search.js',
		course: './js/course.js',
		vendor: ["jquery", "react", "react-dom","react-addons-css-transition-group"]
	},
	output: {
		filename: "[name].bundle.js",
		path: path.join(__dirname,'../static/x_d/js')
	},
	module: {
		loaders: [
			{
				test: /(\.jsx|\.js)$/,
				loader: 'babel?presets[]=es2015&presets[]=react',
				exclude: /node_modules/
			},
			{
				test: /\.scss$/,
  				loader: ExtractTextPlugin.extract("style","css!sass")
			},
			{
				test: /\.json$/,
				loader: 'json'
			},
			{
		        test: /\.html$/,
       			loader: 'url?name=[name].[ext]'
			}
		]
	},
	resolve: {
		root: __dirname,
		extensions: ['','.js','.jsx','scss','css','png','jpg','jpeg']
	},
	plugins: [
	  new webpack.NoErrorsPlugin(),
	  new webpack.optimize.OccurenceOrderPlugin(),
	  new ExtractTextPlugin("../css/[name].css"),
	  new webpack.optimize.CommonsChunkPlugin(/* chunkName= */"vendor", /* filename= */"vendor.bundle.js")
	],
	devtool: isProduction()?null:'source-map',
};

module.exports = devConfig;
