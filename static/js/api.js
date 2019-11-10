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
resp : [{"order_id": 11, "discount": 0, "total_price": 1020, "coupon": "", "created_at": "2019/10/24 14:59", "products": [{"product": "\u6df1\u5c64\u808c\u8089\u653e\u9b06", "quantity": 1}], "record_id": 1},...]
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

/*
取得用戶優惠券列表
resp : [{"id": 2, "name": "\u597d\u53cb\u4ecb\u7d39\u79ae", "expired_at": "", "available": false}, ...]
*/
function get_member_record( callback, phone ){
	$.ajax({
		type: 'GET',
		url: '/member/coupon/member_coupons/',
		data: {'phone':phone},
		success: function(resp, textStatus, jqXHR){
			callback(resp);
		}
	});
}

/*
新增用戶優惠券
resp : {"id": 4, "name": "好友介紹禮", "desc": "介紹新朋友", "expired_at": "2019/10/31 00:00:00", "used_at": "", "available": true}
*/
function get_member_record( callback, phone, coupon_id, expired_dt=undefined ){
	$.ajax({
		type: 'POST',
		url: '/member/coupon/member_gain/',
		data: {'phone':phone, 'coupon_id':coupon_id, 'expired_dt':expired_dt},
		success: function(resp, textStatus, jqXHR){
			callback(resp);
		}
	});
}

/*
修改用戶優惠券
resp : {"id": 4, "name": "好友介紹禮", "desc": "介紹新朋友", "expired_at": "2019/10/31 00:00:00", "used_at": "", "available": true}
*/
function get_member_record( callback, phone, ct_id, available=undefined, expired_dt=undefined ){
	$.ajax({
		type: 'POST',
		url: '/member/coupon/member_update/',
		data: {'phone':phone, 'ct_id':ct_id, 'available':available, 'expired_dt':expired_dt},
		success: function(resp, textStatus, jqXHR){
			callback(resp);
		}
	});
}

/*
取得用戶身體狀態紀錄
resp : {"id": 1, "title": "tt", "detail": "dd", "homework": "hh", "head": true, "neck": false, "shoulder": false, "chest": false, "waist": false, "belly": false, "pelvis": true, "legs": false, "knees": false, "member": "Bliss Chen", "operator": "Test admin"}
*/
function get_member_record( callback, record_id ){
	$.ajax({
		type: 'GET',
		url: '/member/record/detail/',
		data: {'record_id':record_id},
		success: function(resp, textStatus, jqXHR){
			callback(resp);
		}
	});
}

/*
修改用戶身體狀態紀錄
resp : {"id": 1, "title": "tt", "detail": "dd", "homework": "hh", "head": true, "neck": false, "shoulder": false, "chest": false, "waist": false, "belly": false, "pelvis": true, "legs": false, "knees": false, "member": "Bliss Chen", "operator": "Test admin"}
*/
function get_member_record( callback, record_id, title, detail, homework, head=false, neck=false, shoulder=false, chest=false, waist=false, belly=false, pelvis=false, legs=false, knees=false){
	$.ajax({
		type: 'POST',
		url: '/member/record/modify/',
		data: {
			'record_id':record_id,
			'title':title,
			'detail':detail,
			'homework':homework,
			'head':head,
			'neck':neck,
			'shoulder':shoulder,
			'chest':chest,
			'waist':waist,
			'belly':belly,
			'pelvis':pelvis,
			'legs':legs,
			'knees':knees
			},
		success: function(resp, textStatus, jqXHR){
			callback(resp);
		}
	});
}