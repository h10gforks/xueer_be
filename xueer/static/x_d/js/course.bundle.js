webpackJsonp([3],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	'use strict';
	
	/**
	 * course.js
	 */
	var $ = __webpack_require__(22);
	
	var course = {};
	
	course.init = function () {
		var $like_btn = $('.like_bt');
		$like_btn.click(function () {
			$.post({
				url: '/api/v1.0/courses/' + $like_btn.data('cid') + '/like/',
				headers: {
					Authorization: 'Basic ZXlKcFpDSTZNVEo5LkQxSTYzaGtjOXQzS0trZjdtRS00WkdrZjdnczo='
				},
				data: {
					cid: $like_btn.data('cid')
				}
			}).done(function (res) {
				$('.like .num').html(res.likes + '人');
			});
		});
	};
	
	course.commentLike = function () {};
	
	course.init();

/***/ }
]);
//# sourceMappingURL=course.bundle.js.map