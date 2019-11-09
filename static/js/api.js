/*
取得用戶資訊
resp : {birth: '1988/12/25', name: 'Bliss Chen', points: 5000, 
coupon_info{id:{id: 1, percentage: 0.85, value: 0}}, 
coupons:[{id: 1, name: "好友介紹禮", expired_at: "2019/12/31"},]
}
*/
function get_member_info( callback, phone ){
	$.ajax({
		type: 'POST',
		url: '/member/trans/query_member/',
		data: {'phone':phone},
		success: function(resp, textStatus, jqXHR){
			callback(resp);
		}
	});
}

/*
取得用戶消費紀錄
resp : 
*/
function get_member_record( callback, phone ){
	$.ajax({
		type: 'GET',
		url: '/member/trans/record/',
		data: {'phone':phone},
		success: function(resp, textStatus, jqXHR){
			callback(resp);
		}
	});
}
