// 受信済メッセージ一覧
var messageBuffer =[];

// メッセージ相手一覧
var user_list = new Set();

// web socket コネクション
var wshost = location.host;
var ws = new WebSocket("ws://"+ wshost + "/ws/");

// 自分のuser name
var user = null;
// 相手のユーザー名
var myuser = null;

var xhr = new XMLHttpRequest();
xhr.open('GET', '/user', true);
xhr.withCredentials = true;
xhr.onreadystatechange = function(){
    if (xhr.readyState === 4 && xhr.status === 200){
      user = xhr.response;
    }
};
xhr.send(null);

// チャット画面(右)の生成
function messageComponent(msgs) {
    console.log("Message Creating");

    // メッセージ追加
    for(i=0,l=msgs.length;i<l;i++){
        if (msgs[i]['to'] == user && msgs[i]['from'] == myuser){
            console.log("Other Message: ");
            var date = new Date(Number(msgs[i]['date']));
            var ret = '<div style="width:55%;margin-right:auto;margin-bottom:5px;text-align:right;">'+
            '<div class="panel panel-default" style="margin-bottom:0px;text-align:left;"><div class="panel-body">'+
            '<p style="word-wrap:break-word;margin:0;">'
            + msgs[i]['message']
            +'</p></div></div><div style="color:silver">'+
            (date.getMonth()+1) + '/'+(date.getDate()+1) +' '+(date.getHours()+1)+ ':'+(date.getMinutes()+1)+
            '</div></div>';
            $('div#text_field').append(ret);
        }else if(msgs[i]['from'] == user && msgs[i]['to'] == myuser){
            console.log("My Message: ");
            var date = new Date(Number(msgs[i]['date']));
            var ret = '<div style="width:55%;margin-left:auto;margin-bottom:5px;text-align:right;">'+
            '<div class="panel panel-default" style="margin-bottom:0px;text-align:left;background-color:skyblue">'+
            '<div class="panel-body"><p style="word-wrap:break-word;margin:0;">'
            + msgs[i]['message']
            +'</p></div></div><div style="color:silver">'+
            (date.getMonth()+1) + '/'+(date.getDate()+1) +' '+(date.getHours()+1)+ ':'+(date.getMinutes()+1)+
            '</div></div>';

            $('div#text_field').append(ret);
        }
    }
}

// 送信ボタン押下時の送信処理
function sendbutton() {
    var msg = {};
    createMessage(document.getElementById("msgbody").value, user , myuser, msg);
    ws.send(JSON.stringify(msg));
    document.getElementById("msgbody").value = "";
};

// 送信メッセージ作成
function createMessage(message, from, to, ret) {
    // cookie からuser取得
    function get_username() {
    var cookie = document.cookie.split(';');
        for(i=0,l=cookie.length;i<l;i++) {
            val = cookie[i].split("=");
            val[0] = val[0].replace(/^\s+|\s+$/g, "");
            if(val[0] == 'username'){
               return val[1];
            }
        }
    return "NoName";
}

    if(to == null){return null;}
    var date = new Date;
    ret['date'] = date.getTime();
    ret['from'] = get_username();
    ret['to'] = to;
    ret['message'] = message;
}



function ToggleRoomList(){
    //

    var rlist = document.getElementById('left_mnu').style.visibility;
    console.log(rlist =='hidden');
    if(rlist =='hidden'){
        document.getElementById('left_mnu').style.visibility = "visible";
    }else{
        document.getElementById('left_mnu').style.visibility = "hidden";
    }
}





// chat画面メッセージ削除
function delete_elem(cls_name){
    var dom_obj = document.getElementById(cls_name);
    //console.log(dom_obj);
    try{
    while (dom_obj) dom_obj.removeChild(dom_obj.firstChild);
    }catch(e){ console.error("element delete error")}
}

// 左メニューのチャット相手一覧
function create_left_menu(){
    //初回時ユーザ読み込み終わりまで遅延

        console.log(messageBuffer.length);
    if (user==null ){
        setTimeout(this.create_left_menu,1000);
        return null;
    }

    // ルーム一覧を作成
    for(i=0,l=messageBuffer.length;i<l;i++){
        if(messageBuffer[i]['from'] != user){
         //console.log("from"+messageBuffer[i]['from']);
            user_list.add(messageBuffer[i]['from']);

        }
        if(messageBuffer[i]['to'] != user){
        //console.log(messageBuffer[i]['to']);
            user_list.add(messageBuffer[i]['to']);
        }
    }

    // ルーム一覧を削除
    delete_elem('chatroom_list');

    user_list.forEach(function(d){
/*        var ret = '<div class="media"> '+
	    '<div class="media-body"> ' +
		'<h4 class="media-heading">'+ d +'</h4>' +
		'内容。これはサンプル。' +
	'</div></div>';*/
        var ret = '<a class="list-group-item" style="text-align:center" href="javascript:void(0)" value="' + d +'">' + d + '</a>';
        $('div#chatroom_list').append(ret);
    })
}

//左メニューのチャット相手追加
function createNewChatRoom(){
    var n = document.getElementById('new_chat_user').value;
    if(n ==null || n.length==0 || n == user){
        console.error("Error");
        return null;
    }else{
    user_list.add(n);
    create_left_menu();
    }
}


window.onload = function(){
    //左メニューのチャット相手選択
    var room_select = document.getElementById('chatroom_list');
    room_select.addEventListener("click",function(e){
    // chat画面のクリア
        delete_elem('text_field');
    // 相手ユーザをセット
        myuser = e.target.innerHTML;
    // 指定のユーザでチャット画面を描画
        messageComponent(messageBuffer);
        document.getElementById("text_form").style.visibility="visible";
    });

    // websocketコネクション開始時
    ws.onopen = function() {
    };

    //websocket メッセージ受信
    ws.onmessage = function (evt) {
        //console.log("Websoket OnMessage: " + evt.data);
        msg = JSON.parse(evt.data);
        // バッファにいれる
        Array.prototype.push.apply(messageBuffer,msg);
        //左メニュー
        create_left_menu();
        // 描画
        if (myuser!=null){
            messageComponent(msg);
        }
    };
}
window.onbeforeunload = function(){
    ws.close();
}