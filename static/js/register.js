$(function(){

	var error_name = false;
	var error_password = false;
	var error_check_password = false;
	var error_email = false;
	var error_check = false;
	var error_mobile = false;
	document.getElementById('zphone').disabled = true;


	$('#user_name').blur(function() {
		check_user_name();
	});

	$('#pwd').blur(function() {
		check_pwd();
	});

	$('#cpwd').blur(function() {
		check_cpwd();
	});

	$('#email').blur(function() {
		check_email();
	});

	$('#mobile').blur(function() {
		check_mobile();
	});

	$('#allow').click(function() {
		if($(this).is(':checked'))
		{
			error_check = false;
			$(this).siblings('span').hide();
		}
		else
		{
			error_check = true;
			$(this).siblings('span').html('请勾选同意');
			$(this).siblings('span').show();
		}
	});


	function check_user_name(){
		var len = $('#user_name').val().length;
		if(len<5||len>20)
		{
			$('#user_name').next().html('请输入5-20个字符的用户名')
			$('#user_name').next().show();
			error_name = true;
		}
		else
		{
			$('#user_name').next().hide();
			error_name = false;
		}
	}

	function check_pwd(){
		var len = $('#pwd').val().length;
		if(len<8||len>20)
		{
			$('#pwd').next().html('密码最少8位，最长20位')
			$('#pwd').next().show();
			error_password = true;
		}
		else
		{
			$('#pwd').next().hide();
			error_password = false;
		}		
	}


	function check_cpwd(){
		var pass = $('#pwd').val();
		var cpass = $('#cpwd').val();

		if(pass!=cpass)
		{
			$('#cpwd').next().html('两次输入的密码不一致')
			$('#cpwd').next().show();
			error_check_password = true;
		}
		else
		{
			$('#cpwd').next().hide();
			error_check_password = false;
		}		
		
	}

	function check_email(){
		var re = /^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;

		if(re.test($('#email').val()))
		{
			$('#email').next().hide();
			error_email = false;
		}
		else
		{
			$('#email').next().html('你输入的邮箱格式不正确')
			$('#email').next().show();
			error_email = true;
		}

	}


	$('#reg_form').submit(function() {
		check_user_name();
		check_pwd();
		check_cpwd();
		check_email();
		check_mobile();

		if(error_name == false && error_password == false && error_check_password == false && error_email == false && error_check == false && error_mobile == false)
		{
			return true;
		}
		else
		{
			return false;
		}

	});

	$('#zphone').click(
		function(){
		//发送验证码
		$.get('/user/send_message', {mobile:$('#mobile').val()}, function(msg) {
			alert(jQuery.trim(msg.msg));
			if(msg.msg=='提交成功'){
				RemainTime();
			}
		});
	})

	//按钮倒计时
	var iTime = 60;
	sTime = ''
	function RemainTime(){
		if (iTime == 0) {
			document.getElementById('zphone').disabled = false;
			sTime="获取验证码";
			iTime = 60;
			document.getElementById('zphone').value = sTime;
			return;
		}else{
			document.getElementById('zphone').disabled = true;
			sTime="重新发送(" + iTime + ")";
			iTime--;
		}
		setTimeout(function() { RemainTime() },1000)
		document.getElementById('zphone').value = sTime;
	}

	// 检查用户输入的手机号是否合法
	function check_mobile() {

		var re = /^1[345678]\d{9}$/; //校验手机号

		if(re.test($('#mobile').val()))
		{
			$('#mobile').next().hide();
			error_mobile = false;
			document.getElementById('zphone').disabled = false;
		}
		else
		{
			$('#mobile').next().html('你输入的手机格式不正确')
			$('#mobile').next().show();
			error_mobile = true;
			document.getElementById('zphone').disabled = true;
		}
	}





})