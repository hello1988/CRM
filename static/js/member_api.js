/*
取得用戶優惠券
resp : [{id: 3, name: "好友介紹禮", desc: "介紹新朋友", expired_at: ""},
{id: 1, name: "好友介紹禮", desc: "介紹新朋友", expired_at: "2019/12/31"},...]
*/
function get_member_coupons( callback ){
	$.ajax({
		type: 'GET',
		url: '/member/info/coupon',
		success: function(resp, textStatus, jqXHR){
			callback(resp);
		}
	});
}


/*消費紀錄優惠券
resp : [{order_id: 2, discount: 100, total_price: 4100, coupon: "", created_at: "2019/10/23 05:19", products:[{product: "Ayni Touch", quantity: 1},...]}, ...]
*/
function get_member_record( callback, end_dt=undefined ){
	$.ajax({
		type: 'GET',
		url: '/member/info/record',
		data:{'end_dt':end_dt},
		success: function(resp, textStatus, jqXHR){
			callback(resp);
		}
	});
}