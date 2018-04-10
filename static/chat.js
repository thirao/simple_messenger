// 受信済メッセージ一覧
var messageBuffer =[];

// user name
var user = null;
var wshost = location.host;
var ws = new WebSocket("ws://"+ wshost + "/ws/");

var xhr = new XMLHttpRequest();
xhr.open('GET', '/user', true);
xhr.withCredentials = true;
xhr.onreadystatechange = function(){
    // 本番用
    if (xhr.readyState === 4 && xhr.status === 200){
      console.log(xhr.response);
      user = xhr.response;
    }
};
xhr.send(null);

// メッセージ表示のデザイン
function messageComponent(msgs) {
    // domへメッセージ追加
    for(i=0;i<msgs.length;i++){
        if (msgs[i]['to'] == user){
            var ret = '<div class="panel panel-default" style="width:55%;margin-right:auto;"> <div class="panel-body">'
            + msgs[i]['message']
            + "</div></div>";
            $('div#text_field').append(ret);
        }else{
            var ret = '<div class="panel panel-default" style="width:55%;margin-left:auto;background-color:aqua;"> <div class="panel-body">'
            + msgs[i]['message']
            + "</div></div>";
            $('div#text_field').append(ret);
        }
    }
}

// ボタン押下時の送信処理
function sendbutton() {
    /// 送信雛形
    var msg = {};
    createMessage(document.getElementById("msgbody").value,'thirao' , document.getElementById("to_send").value, msg);
    ws.send(JSON.stringify(msg));
};

// メッセージ送信処理
function createMessage(message, from, to, ret) {
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
    while (dom_obj) dom_obj.removeChild(dom_obj.firstChild);
}

window.onload = function(){
    var delete_dom = document.getElementById('chatroom_list');
    delete_dom.addEventListener("click",function(){ delete_elem("text_field")}, false);

    // websocketコネクション開始時
    ws.onopen = function() {
        var msg ={};
        // ws.send(JSON.stringify(msg));
    };

    //websocket メッセージ受信
    ws.onmessage = function (evt) {
        console.log(evt.data);
        msg = JSON.parse(evt.data);
        messageBuffer.push(msg);
        messageComponent(msg);
    };

}
