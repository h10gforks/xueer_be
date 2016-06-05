/**
 * course.js
 */
const $ = require('jquery');

const course = {}

course.init = () => {
  let $like_btn = $('.like_bt');
	$like_btn.click(() => {
		$.post({
			url: '/api/v1.0/courses/' + $like_btn.data('cid') +'/like/',
			headers: {
				Authorization: 'Basic ZXlKcFpDSTZNVEo5LkQxSTYzaGtjOXQzS0trZjdtRS00WkdrZjdnczo='
			},
			data: {
        cid: $like_btn.data('cid')
			}
		}).done((res) => {
			$('.like .num').html(res.likes + '人');
		})
	})
}


course.commentLike = () => {}

course.init();
