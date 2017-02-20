tinymce.init({
	selector: 'textarea',
	height: 500,
	menubar: false,
	plugins: [
		'advlist autolink lists link image charmap print preview anchor',
		'searchreplace visualblocks code fullscreen nonbreaking',
		'insertdatetime media table contextmenu paste code'
	],
	nonbreaking_force_tab: true,
	toolbar: 'undo redo | insert | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
	content_css: 'ib/tinymce/js/tinymce/skins/lightgray/skin.min.css',
});

//new QWebChannel(qt.webChannelTransport, function (channel) {
    // now you retrieve your object
//    var Dtext = channel.objects.DocumentText
//});
//socket= new WebSocket('ws://127.0.0.1:1302/');


/*function sendMessage(message) {
	socket.onopen= function() {
		socket.send(message);
	};
	socket.onmessage= function(s) {
		/*for (item in s) {
			alert(item);
		}*
		alert(s.data);
	};
}*/

//sendMessage("Hi");
