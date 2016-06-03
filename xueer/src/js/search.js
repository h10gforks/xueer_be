/**
 * search.js
 *
 * authored by zindex
 */

'use strict';

import React from 'react';
import ReactDOM from 'react-dom';
const $ = require("jquery");

const SearchBox = (props) => {
	return <input id="inputBox" type="text" className="input" placeholder="课程名、标签" onFocus={props.onFocusHandler}  onBlur={props.onBlurHandler} onChange={props.onChangeHandler}/>
}

const PopBox = (props) => {
		const styles = { 
			show:{
				display:"block"
			},
			hide:{
				display:"none"
			}
		}
		return <div style={((!props.isFocus)&&(!props.isBoxClicked))?styles.hide:styles.show} className="pop_box">{ props.children }</div>
}

const PopList = (props) => {
		var styles = {
			show:{
				display:"block"
			},
			hide:{
				display:"none"
			}
		}
		return <div style={props.hasResult?styles.show:styles.hide} className="pop_list">{ props.children }</div>
}

const PopListItem = (props) => {
	return <a className="item" href={ props.data.url }>{ props.data.title }</a>
}

const TagBox = (props) => {
	return <div className="tag"><a href={ props.data.url }>{ props.data.title }</a></div>
}

const HotTags = (props) => {
	var styles = {
			show:{
				display:"block"
			},
			hide:{
				display:"none"
			}
		}
		return <div style={props.isTyping&&props.hasResult?styles.hide:styles.show} className="hot_tags">
			   	<div className="tag_title" onClick={props.onClickHandler} ><a href="/login">大家都在搜</a></div>
			   	<div className="tag_list">
					{ props.children }
			   	</div>
			   </div>
}



class SearchComponent extends React.Component{
	constructor(){
		super();
		this.state = {
			isFocus:false,
			isBoxClicked:false,
			isTyping:false,
			hasResult:false,
			list:[]
		};
		this._onFocusHandler = this._onFocusHandler.bind(this);
		this._onBlurHandler = this._onBlurHandler.bind(this);
		this._onChangeHandler = this._onChangeHandler.bind(this);
		this._onMouseDownHandler = this._onMouseDownHandler.bind(this);
	}
	componentDidMount() {
    	window.addEventListener('mousedown', this._onMouseDownHandler, true);
	}
	_onFocusHandler(){
		this.setState({isFocus:true})
		this.setState({isBoxClicked:false})
	}
	_onMouseDownHandler(e){
		if (ReactDOM.findDOMNode(this).contains(e.target)){
			if (e.target.id !== "inputBox"){
				this.setState({isBoxClicked:true})
			}
		}else{
			this.setState({isBoxClicked:false})
		}
	}
	_onBlurHandler(e){
		this.setState({isFocus:false})
	}
	_onChangeHandler(e){
		var val = e.target.value,
		that = this;
		if(val !== ""){
			this.setState({isTyping:true})
			var url = "http://121.41.6.148:5050/api/v1.0/search/?page=1&per_page=20&keywords=" + encodeURIComponent(val)
			$.get(url).done(function(data){
				var l_data = JSON.parse(data);
				if(l_data.length){
					that.setState({list:JSON.parse(data),hasResult:true})
				}else{
					that.setState({hasResult:false})
				}
			}).fail(function(){
			})
		}else{
			this.setState({isTyping:false,hasResult:false})
		}
	}
	render(){
		var pop_list = [];
		this.state.list.map((x,i) => pop_list.push(<PopListItem key={i} data={x} id={i} />));
		return <div className="search_container">
					<PopBox isFocus={this.state.isFocus} isBoxClicked={this.state.isBoxClicked} >
						<HotTags isTyping={this.state.isTyping} hasResult={this.state.hasResult}>

						</HotTags>
						<PopList hasResult={this.state.hasResult}>
							{pop_list}
						</PopList>
					</PopBox>
					<SearchBox onFocusHandler={this._onFocusHandler} onBlurHandler={this._onBlurHandler} onChangeHandler={this._onChangeHandler}></SearchBox>
			   </div>
	}
}

//init search box
if (document.querySelector(".search_component_inject")){
	ReactDOM.render( <SearchComponent/> , document.querySelector(".search_component_inject"));
}
