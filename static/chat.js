// 受信済メッセージ一覧
var messageBuffer =[];

// メッセージ相手
var user_list = new Set();

// web socket コネクション
var wshost = location.host;
var ws = new WebSocket("ws://"+ wshost + "/ws/");

// 自分のuser name取得
var user = null;
// 相手のユーザー名
var myuser = null;

var xhr = new XMLHttpRequest();
xhr.open('GET', '/user', true);
xhr.withCredentials = true;
xhr.onreadystatechange = function(){
    if (xhr.readyState === 4 && xhr.status === 200){
      console.log(xhr.response);
      user = xhr.response;
    }
};
xhr.send(null);

// チャット画面(右)の生成
function messageComponent(msgs,from_user = null) {
    // domへメッセージ追加
    console.log("Create Message:",msgs );
    console.log("Message Length: ",msgs.length);
    for(i=0;i<msgs.length;i++){
        if (msgs[i]['to'] == user && msgs[i]['from'] == from_user){
            console.log("Other Message: ");
            var ret = '<div class="panel panel-default" style="width:55%;margin-right:auto;"> <div class="panel-body">'
            + msgs[i]['message']
            + "</div></div>";
            $('div#text_field').append(ret);
        }else if(msgs[i]['from'] == user && msgs[i]['to'] == from_user){
            console.log("My Message: ");
            var ret = '<div class="panel panel-default" style="width:55%;margin-left:auto;background-color:aqua;"> <div class="panel-body">'
            + msgs[i]['message']
            + "</div></div>";
            $('div#text_field').append(ret);
        }
    }
}

// ボタン押下時の送信処理
function sendbutton() {
    var msg = {};
    createMessage(document.getElementById("msgbody").value, user , myuser, msg);
    ws.send(JSON.stringify(msg));
};

// メッセージ作成
function createMessage(message, from, to, ret) {
    if(to == null){return null;}
    var date = new Date;
    ret['date'] = date.getTime();
    ret['from'] = get_username();
    ret['to'] = to;
    ret['message'] = message;
}

// cookie からuser取得
function get_username() {
    var cookie = document.cookie.split(';');
        for(i=0;i<cookie.length;i++) {
            val = cookie[i].split("=");
            val[0] = val[0].replace(/^\s+|\s+$/g, "");
            if(val[0] == 'username'){
               return val[1];
            }
        }
return "NoName";
}

// chat画面メッセージ削除
function delete_elem(cls_name){
    var dom_obj = document.getElementById(cls_name);
    //console.log(dom_obj);
    try{
    while (dom_obj) dom_obj.removeChild(dom_obj.firstChild);
    }catch(e){}
}

// left menu 部品
function create_left_menu(){
    for(i=0;i<messageBuffer.length;i++){
        if(messageBuffer[i]['from'] != user){
         //console.log("from"+messageBuffer[i]['from']);
            user_list.add(messageBuffer[i]['from']);

        }
        if(messageBuffer[i]['to'] != user){
        //console.log(messageBuffer[i]['to']);
            user_list.add(messageBuffer[i]['to']);
        }
    }

    delete_elem('chatroom_list');

    user_list.forEach(function(d){
        var ret = '<a class="list-group-item" href="javascript:void(0)" value="' + d +'">' + d + '</a>';
        $('div#chatroom_list').append(ret);
    })
}



window.onload = function(){
    var room_select = document.getElementById('chatroom_list');
    room_select.addEventListener("click",function(e){
    // chat画面のクリア
        delete_elem('text_field');

    // 指定のユーザでチャット画面を描画
        messageComponent(messageBuffer, e.target.innerHTML);

    // 相手ユーザをセット
        myuser = e.target.innerHTML;
    });

    // websocketコネクション開始時
    ws.onopen = function() {
    };

    //websocket メッセージ受信
    ws.onmessage = function (evt) {
        console.log("Websoket OnMessage: " + evt.data);
        msg = JSON.parse(evt.data);
        // バッファにいれる
        Array.prototype.push.apply(messageBuffer,msg);
        // 描画
        messageComponent(msg);
        create_left_menu();
    };
}
