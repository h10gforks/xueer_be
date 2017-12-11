webpackJsonp([2],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/**
	 * search.js
	 *
	 * authored by zindex
	 */
	
	'use strict';
	
	var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();
	
	var _react = __webpack_require__(54);
	
	var _react2 = _interopRequireDefault(_react);
	
	var _reactDom = __webpack_require__(34);
	
	var _reactDom2 = _interopRequireDefault(_reactDom);
	
	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
	
	function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
	
	function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }
	
	function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }
	
	var $ = __webpack_require__(22);
	
	var SearchBox = function SearchBox(props) {
		return _react2.default.createElement('input', { id: 'inputBox', type: 'text', className: 'input', placeholder: '课程名、标签', onFocus: props.onFocusHandler, onBlur: props.onBlurHandler, onChange: props.onChangeHandler });
	};
	
	var PopBox = function PopBox(props) {
		var styles = {
			show: {
				display: "block"
			},
			hide: {
				display: "none"
			}
		};
		return _react2.default.createElement(
			'div',
			{ style: !props.isFocus && !props.isBoxClicked ? styles.hide : styles.show, className: 'pop_box' },
			props.children
		);
	};
	
	var PopList = function PopList(props) {
		var styles = {
			show: {
				display: "block"
			},
			hide: {
				display: "none"
			}
		};
		return _react2.default.createElement(
			'div',
			{ style: props.hasResult ? styles.show : styles.hide, className: 'pop_list' },
			props.children
		);
	};
	
	var PopListItem = function PopListItem(props) {
		return _react2.default.createElement(
			'a',
			{ className: 'item', href: '/course/' + props.data.id + '/' },
			props.data.title
		);
	};
	
	var TagBox = function TagBox(props) {
		return _react2.default.createElement(
			'div',
			{ className: 'tag' },
			_react2.default.createElement(
				'a',
				{ href: '/search/?keywords=' + props.data },
				props.data
			)
		);
	};
	
	var HotTags = function HotTags(props) {
		var styles = {
			show: {
				display: "block"
			},
			hide: {
				display: "none"
			}
		};
		return _react2.default.createElement(
			'div',
			{ style: props.isTyping && props.hasResult ? styles.hide : styles.show, className: 'hot_tags' },
			_react2.default.createElement(
				'div',
				{ className: 'tag_title', onClick: props.onClickHandler },
				_react2.default.createElement(
					'a',
					{ href: '/login' },
					'大家都在搜'
				)
			),
			_react2.default.createElement(
				'div',
				{ className: 'tag_list' },
				props.children
			)
		);
	};
	
	var SearchComponent = function (_React$Component) {
		_inherits(SearchComponent, _React$Component);
	
		function SearchComponent() {
			_classCallCheck(this, SearchComponent);
	
			var _this = _possibleConstructorReturn(this, Object.getPrototypeOf(SearchComponent).call(this));
	
			_this.state = {
				isFocus: false,
				isBoxClicked: false,
				isTyping: false,
				hasResult: false,
				list: [],
				hot_tags: []
			};
			_this._onFocusHandler = _this._onFocusHandler.bind(_this);
			_this._onBlurHandler = _this._onBlurHandler.bind(_this);
			_this._onChangeHandler = _this._onChangeHandler.bind(_this);
			_this._onMouseDownHandler = _this._onMouseDownHandler.bind(_this);
			return _this;
		}
	
		_createClass(SearchComponent, [{
			key: 'componentDidMount',
			value: function componentDidMount() {
				var _this2 = this;
	
				window.addEventListener('mousedown', this._onMouseDownHandler, true);
				$.get("/api/v1.0/search/hot/").done(function (res) {
					_this2.setState({ hot_tags: JSON.parse(res) });
				});
			}
		}, {
			key: '_onFocusHandler',
			value: function _onFocusHandler() {
				this.setState({ isFocus: true });
				this.setState({ isBoxClicked: false });
			}
		}, {
			key: '_onMouseDownHandler',
			value: function _onMouseDownHandler(e) {
				if (_reactDom2.default.findDOMNode(this).contains(e.target)) {
					if (e.target.id !== "inputBox") {
						this.setState({ isBoxClicked: true });
					}
				} else {
					this.setState({ isBoxClicked: false });
				}
			}
		}, {
			key: '_onBlurHandler',
			value: function _onBlurHandler(e) {
				this.setState({ isFocus: false });
			}
		}, {
			key: '_onChangeHandler',
			value: function _onChangeHandler(e) {
				var val = e.target.value,
				    that = this;
				if (val !== "") {
					this.setState({ isTyping: true });
					var url = "/api/v1.0/search/?page=1&per_page=20&keywords=" + encodeURIComponent(val);
					$.get(url).done(function (data) {
						var l_data = JSON.parse(data);
						if (l_data.length) {
							that.setState({ list: JSON.parse(data), hasResult: true });
						} else {
							that.setState({ hasResult: false });
						}
					}).fail(function () {});
				} else {
					this.setState({ isTyping: false, hasResult: false });
				}
			}
		}, {
			key: 'render',
			value: function render() {
				var pop_list = [];
				var hot_tags = [];
				this.state.list.map(function (x, i) {
					return pop_list.push(_react2.default.createElement(PopListItem, { key: i, data: x, id: i }));
				});
				this.state.hot_tags.map(function (x, i) {
					return hot_tags.push(_react2.default.createElement(TagBox, { key: i, data: x, id: i }));
				});
				return _react2.default.createElement(
					'div',
					{ className: 'search_container' },
					_react2.default.createElement(
						PopBox,
						{ isFocus: this.state.isFocus, isBoxClicked: this.state.isBoxClicked },
						_react2.default.createElement(
							HotTags,
							{ isTyping: this.state.isTyping, hasResult: this.state.hasResult },
							hot_tags
						),
						_react2.default.createElement(
							PopList,
							{ hasResult: this.state.hasResult },
							pop_list
						)
					),
					_react2.default.createElement(SearchBox, { onFocusHandler: this._onFocusHandler, onBlurHandler: this._onBlurHandler, onChangeHandler: this._onChangeHandler })
				);
			}
		}]);
	
		return SearchComponent;
	}(_react2.default.Component);
	
	//init search box
	
	
	if (document.querySelector(".search_component_inject")) {
		_reactDom2.default.render(_react2.default.createElement(SearchComponent, null), document.querySelector(".search_component_inject"));
	}

/***/ }
]);
//# sourceMappingURL=search.bundle.js.map