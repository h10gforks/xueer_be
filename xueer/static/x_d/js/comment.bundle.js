webpackJsonp([4],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	'use strict';
	
	var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();
	
	var _react = __webpack_require__(54);
	
	var _react2 = _interopRequireDefault(_react);
	
	var _reactDom = __webpack_require__(34);
	
	var _reactDom2 = _interopRequireDefault(_reactDom);
	
	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
	
	function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
	
	function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }
	
	function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; } /**
	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * comment.js
	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                *
	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                * authored by zindex
	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                */
	
	/**
	 * React component for Comment Box
	 */
	
	
	//var  ReactCSSTransitionGroup = require('../node_modules/react/lib/ReactCSSTransitionGroup');
	var ReactCSSTransitionGroup = __webpack_require__(55);
	
	var TagDeletable = function (_React$Component) {
		_inherits(TagDeletable, _React$Component);
	
		function TagDeletable() {
			_classCallCheck(this, TagDeletable);
	
			var _this = _possibleConstructorReturn(this, Object.getPrototypeOf(TagDeletable).call(this));
	
			_this.state = { show: false };
			return _this;
		}
	
		_createClass(TagDeletable, [{
			key: 'render',
			value: function render() {
				var _this2 = this;
	
				var showStyle = { display: 'block' };
				return _react2.default.createElement(
					'span',
					{ className: 'tag va_item cp tag_warpper',
						onClick: function onClick() {
							return _this2.props._onClickedHandler(_this2.props.data, _this2.props.id || null);
						},
						onMouseEnter: function onMouseEnter() {
							return _this2.setState({ show: true });
						},
						onMouseLeave: function onMouseLeave() {
							return _this2.setState({ show: false });
						} },
					this.props.data,
					_react2.default.createElement(
						'span',
						{ className: 'tag tag_overlay', style: this.state.show ? showStyle : null },
						'删除'
					)
				);
			}
		}]);
	
		return TagDeletable;
	}(_react2.default.Component);
	
	var Tag = function Tag(props) {
		return _react2.default.createElement(
			'span',
			{ className: 'tag va_item cp tag_warpper',
				onClick: function onClick() {
					return props._onClickedHandler(props.data, props.id || null);
				} },
			props.data
		);
	};
	
	var Tags = function Tags(props) {
		return _react2.default.createElement(
			'div',
			{ className: 'tags va_item space' },
			props.children
		);
	};
	
	var HotTags = function HotTags(props) {
		return _react2.default.createElement(
			'div',
			{ className: 'hot_tags margin_auto space' },
			props.children
		);
	};
	
	var NewTag = function (_React$Component2) {
		_inherits(NewTag, _React$Component2);
	
		function NewTag() {
			_classCallCheck(this, NewTag);
	
			var _this3 = _possibleConstructorReturn(this, Object.getPrototypeOf(NewTag).call(this));
	
			_this3._onKeyDownHandler = _this3._onKeyDownHandler.bind(_this3);
			return _this3;
		}
	
		_createClass(NewTag, [{
			key: '_onClickHandler',
			value: function _onClickHandler() {
				var value = this.refs.input.value;
				if (value) {
					this.props._onClickedHandler(value);
				}
				this.refs.input.value = null;
			}
		}, {
			key: '_onKeyDownHandler',
			value: function _onKeyDownHandler(e) {
				if (e.keyCode == 32) {
					e.preventDefault();
					this.props._onAddHandler(e.target.value);
					e.target.value = null;
					e.target.focus();
				}
				//if(e.key == "Backspace" && e.target.value == ""){
				//	this._onRemoveDataHandler();
				//}
			}
		}, {
			key: 'render',
			value: function render() {
				return _react2.default.createElement(
					'div',
					{ className: 'new_tag va_item' },
					_react2.default.createElement('input', { type: 'text', className: 'new_tag_input', placeholder: '输入标签，用空格间隔', ref: 'input', onKeyDown: this._onKeyDownHandler })
				);
			}
		}]);
	
		return NewTag;
	}(_react2.default.Component);
	
	//main box component
	
	
	var CommentBox = function (_React$Component3) {
		_inherits(CommentBox, _React$Component3);
	
		function CommentBox() {
			_classCallCheck(this, CommentBox);
	
			var _this4 = _possibleConstructorReturn(this, Object.getPrototypeOf(CommentBox).call(this));
	
			_this4.state = { tags: [] };
			_this4._onAddDataHandler = _this4._onAddDataHandler.bind(_this4);
			_this4._onDeleteDataHandler = _this4._onDeleteDataHandler.bind(_this4);
			return _this4;
		}
	
		_createClass(CommentBox, [{
			key: '_onAddDataHandler',
			value: function _onAddDataHandler(val) {
				var arr = this.state.tags;
				for (var i = 0; i < arr.length; i++) {
					if (arr[i] === val) {
						alert("请勿重复添加！");
						return;
					}
				}
				this.setState({ tags: this.state.tags.concat(val) });
			}
		}, {
			key: '_onDeleteDataHandler',
			value: function _onDeleteDataHandler(val, id) {
				console.log(val, id);
				var temp_arr = this.state.tags;
				temp_arr.splice(id, 1);
				this.setState({ tags: temp_arr });
			}
		}, {
			key: 'render',
			value: function render() {
				var _this5 = this;
	
				var hot_tags = [],
				    current_tags = [];
				this.props.hot_tags.map(function (x, i) {
					return hot_tags.push(_react2.default.createElement(Tag, { key: i, data: x, _onClickedHandler: _this5._onAddDataHandler }));
				});
				this.state.tags.map(function (x, i) {
					return current_tags.push(_react2.default.createElement(TagDeletable, { key: i, data: x, id: i, _onClickedHandler: _this5._onDeleteDataHandler }));
				});
				return _react2.default.createElement(
					'div',
					null,
					_react2.default.createElement('textarea', { className: 'textarea', name: 'body' }),
					_react2.default.createElement(
						'div',
						{ className: 'tags_box space' },
						_react2.default.createElement(
							Tags,
							null,
							_react2.default.createElement(
								ReactCSSTransitionGroup,
								{ transitionName: 'tags', transitionAppearTimeout: 300, transitionEnterTimeout: 300, transitionLeaveTimeout: 300 },
								current_tags
							)
						),
						_react2.default.createElement(NewTag, { _onClickedHandler: this._onAddDataHandler, _onAddHandler: this._onAddDataHandler })
					),
					_react2.default.createElement(
						'div',
						{ className: 'tag_head' },
						'热门标签，点击直接添加'
					),
					_react2.default.createElement(
						HotTags,
						{ _onAddHandler: this._onAddDataHandler },
						hot_tags
					),
					_react2.default.createElement('input', { type: 'text', name: 'tags', value: this.state.tags.join(" "), className: 'comment_tags_input' }),
					_react2.default.createElement(
						'button',
						{ type: 'submit', className: 'submit_bt tc margin_auto' },
						'发布评论'
					)
				);
			}
		}]);
	
		return CommentBox;
	}(_react2.default.Component);
	
	//init comment box
	
	
	if (document.querySelector(".comment_box_x")) {
		var tags = document.querySelector(".comment_box_x").innerHTML.split(" ");
		_reactDom2.default.render(_react2.default.createElement(CommentBox, { hot_tags: tags }), document.querySelector(".comment_box_x"));
	}

/***/ }
]);
//# sourceMappingURL=comment.bundle.js.map