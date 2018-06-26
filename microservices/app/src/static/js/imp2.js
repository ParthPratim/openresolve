class chatData{
    constructor(sender , msg_textbox , timestamp , cno,element){
        this.sender = sender
        this.msg_textbox = msg_textbox
        this.timestamp = timestamp
        this.cno = cno
        this.element = element
    }
    addToUI(tempsent){
        var cdata = Cookie.read("hasura_auth_uikit")
        if(cdata){
            cdata =  JSON.parse(cdata)
            if(cdata['user_info']['username'].localeCompare(this.sender) == 0 || tempsent == true){
                var elem = $('<div class="imchat col s8 your-text"><div class="chat-sender col s12"><span>You</span></div><div class="chat-text col s12"><span class="flow-text">'+this.msg_textbox+'</span></div><span class="chat-timestamp">'+this.timestamp+'</span><input name="cno" type="hidden" value="'+this.cno+'"></div>')
                }
            else{
                var elem = $('<div class="imchat col s8"><div class="chat-sender col s12"><span>'+this.sender+'</span></div><div class="chat-text col s12"><span class="flow-text">'+this.msg_textbox+'</span></div><span class="chat-timestamp">'+this.timestamp+'</span><input name="cno" type="hidden" value="'+this.cno+'"></div>')
                }
        }
        $('.imchats').append(elem)
        $('.imchats').scrollTop($('.imchats')[0].scrollHeight);
        this.elemet = elem
    }
}

class IM{

    constructor(){
        this.chatArr = []
        this.currChats = []
        this.assert_storage()
        var obj = this
        var fetch_msgs = function(){
            var currArr = []
            obj.chats_extractor()
            var fetchmsgs = $.ajax({
                type : 'get',
                url : 'https://app.enamor68.hasura-app.io/im/fetchmsgs?issueid='+$('input[name=issue-id]').val(),
                success : function(response){
                    var resp = JSON.parse(response)
                    for(var i = 0 ; i < resp.length ; i++){
                        currArr.push(new chatData(resp[i].username,resp[i].chatmsg,resp[i].timestamp,resp[i].cno,null))
                    }
                    var length = obj.chatArr.length;
                    if(length == 0){
                        for(var i = 0 ; i < currArr.length ; i++){
                            currArr[i].addToUI();
                        }
                        obj.chatArr = currArr;
                    }
                    else{
                        $(obj.chatArr[length-1].element).remove()                        
                        obj.chatArr.pop()
                        for(var i = length-1 ; i < currArr.length ; i++){
                            currArr[i].addToUI()
                            obj.chatArr.push(currArr[i])
                        }

                    }
                    setTimeout(fetch_msgs,2000);
                },
                error : function(xhr){
                    console.log(xhr.statusText);
                }
            })

            };
        fetch_msgs()
    }
    newChat(){
        'use strict';
        var msg_txtbox = $('input[name=msg-txtbox]').val()
        var issue_id = $('input[name=issue-id]').val()
        var pdata = {
            chat_msg : msg_txtbox,
            issueid : issue_id
        }
        $('input[name=msg-txtbox]').val(" ");
        var send_message = $.ajax({
            type : 'post',
            url : "https://app.enamor68.hasura-app.io/im/newmsg",
            data : pdata,
            success : function(response){

            },
            error : function(xhr){
                console.log("ERROR : "+xhr.statusText)
            }
        });
    }

    chats_extractor(){
        'use strict';
        var chats = $('.imchat')
        var len = chats.length
        var obj = this
        obj.chatArr = []
        chats.each(function(index,element){
            var chat_text = ($(element).find('.chat-text .flow-text').text())
            var sender = ($(element).find('.chat-sender span').text())
            var timestamp = ($(element).find('.chat-timestamp').text())
            var cno = ($(element).find('input[name=cno]').text())
            obj.chatArr.push(new chatData(sender,chat_text,timestamp,cno,element))
        })
    }

    len(arr) {
        var count = 0;
        for (var k in arr) {
            if (arr.hasOwnProperty(k)) {
                count++;
            }
        }
        return count;
    }
    fetchChats(obj){
        var currChats = obj.latestChats($('input[name=issue-id]').val())

        /*for(var i = 0; i < currChats.length ; i++){
                console.log(currChats[0]['sender'] +"PING PONG")
            }*/
        }


    assert_storage(){
        for(var i = 0 ; i  < this.chatArr.length ; i++){
            //console.log(this.chatArr[i]['timestamp'])
        }
    }
}

var im = new IM();

var Cookie = {
    read : function(cookiename){
        cookie_data = document.cookie
        cookies = cookie_data.split(';');
        for(i = 0 ; i <  cookies.length; i++){
            cookie = cookies[i];
            ceql = cookie.indexOf('=');
            cookie_name = cookie.substring(0,ceql);
            rcookie_data = cookie.substring(ceql+1);
            if(cookie_name.localeCompare(cookiename) == 0){
                return rcookie_data;
            }
        }
    }
}

$('#imp-mod').submit(function(){
    im.newChat()
    return false
});

$('#begin-edit').click(tryToEdit);

function tryToEdit(){
    var issue = $('input[name=issue-id]').val()
    var try_edit = $.ajax({
        type : "get",
        url : "https://app.enamor68.hasura-app.io/ill_edit/"+issue,
        success : function(response){
            try{
                jersp = JSON.parse(response)
                if(jersp.editor){
                    $('.curr-editor').html(jersp.editor)
                    $('#begin-edit').removeClass("waves-effect waves-light submit").addClass('disabled')
                    $('#request-abort').removeClass("waves-effect waves-light submit").removeClass('disabled');
                    $('#finish-edit').show();
                }
            }catch(err){
                makeToast(response)
            }
        }
    })
    }

function fetcheditor(){
    var issue = $('input[name=issue-id]').val()
    $.ajax({
        type : "get",
        url : "https://app.enamor68.hasura-app.io/issue_editor/"+issue,
        success : function(response){
            try{
                d = JSON.parse(response)
                if(d.editor){
                    if(d.editor.localeCompare(JSON.parse(Cookie.read("hasura_auth_uikit"))['user_info']['username']) == 0){
                        if($('.curr-editor').html().localeCompare("You") != 0){
                            console.log("CP : A")
                            LoadAbortRequests()
                        }

                        $('.curr-editor').html("You")
                        $('#finish-edit').show()
                        $('#begin-edit').addClass("waves-effect waves-light submit").addClass('disabled')
                        $('#request-abort').addClass("waves-effect waves-light submit").addClass('disabled')

                        setTimeout(updateSource,2000)
                    }
                    else{
                        $('.curr-editor').html(d.editor)
                        $('#finish-edit').hide()
                        $('#request-abort').removeClass("waves-effect waves-light submit").removeClass('disabled')
                        $('#begin-edit').addClass("waves-effect waves-light submit").addClass('disabled')
                        setTimeout(loadRecentSource,2000)
                    }
                }
                else{
                    $('.curr-editor').html("None")
                    $('#finish-edit').hide()
                    $('#request-abort').addClass("waves-effect waves-light submit").addClass('disabled')
                    $('#begin-edit').removeClass("waves-effect waves-light submit").removeClass('disabled')
                }
            }catch(err){
                $('.curr-editor').html(""); 
            }
            setTimeout(fetcheditor,2000)
        }
    })

}

fetcheditor()

$('#request-abort').click(function(){
    $.ajax({
        type : 'get',
        url : 'https://app.enamor68.hasura-app.io/requestAbort/'+$('input[name=issue-id]').val(),
        success : function(response){
            try{
                jresp = JSON.parse(response)
                if(jresp['status'].localeCompare("sent") == 0)
                    makeToast("Your request has been sent")
                else
                    makeToast("Failed to send request")
            }catch(exp){
                makeToast(response)
            }
        }
    })
})

function LoadAbortRequests(){
    $.ajax({
        type : 'get',
        url : 'https://app.enamor68.hasura-app.io/abort_requests/'+$('input[name=issue-id]').val(),
        success : function(response){
            jresp = JSON.parse(response)
            ar_users = ""
            if(jresp.length > 0 ){
                for(var  i = 0 ;  i < jresp.length ;i++){
                    ar_users += jresp[i].username+((i < jresp.length-1)?',':'')
                }
                $('.ar_body').html(ar_users+" requested you to abort editing")
                $('.modal').modal('open')
                $('.modal-content input').val(ar_users)
            }
            else{
                console.log("CP : B")
                setTimeout(LoadAbortRequests,2000)
            }
        }
    })   
}

$('.modal-accept').click(function(){
    ar_users = $('.modal-content input').val()
    $.ajax({
        type : 'post',
        url : 'https://app.enamor68.hasura-app.io/actionabort/'+$('input[name=issue-id]').val()+'/1' ,
        data : {ar_users : ar_users},
        success : function(response){
            console.log("ABORT REQUEST : ACCEPTED")
            console.log("CP : C")
            setTimeout(LoadAbortRequests,2000)
        },
        error : function(xhr){
            console.log("ABORT REQUEST : NO-STATUS")
        }
    })
    //ACCEPT ALL ABORTS
})

$('.modal-decline').click(function(){
    ar_users = $('.modal-content input').val()
    $.ajax({
        type : 'post',
        url : 'https://app.enamor68.hasura-app.io/actionabort/'+$('input[name=issue-id]').val()+'/0' ,
        data : {ar_users : ar_users},
        success : function(response){
            console.log("ABORT REQUEST : ACCEPTED")
            console.log("CP : D")
            setTimeout(LoadAbortRequests,2000)
        },
        error : function(xhr){
            console.log("ABORT REQUEST : NO-STATUS")
        }
    })
    //ACCEPT ALL ABORTS
})

$('#finish-edit').click(function(){
    $.ajax({
        type:'get',
        url:'https://app.enamor68.hasura-app.io/finish_edit/'+$('input[name=issue-id]').val(),
        success:function(response){
            status = JSON.parse(response)
            if(status['status'].localeCompare("edit_finished") == 0){
                console.log("FINISHED EDITING");
                fetcheditor()
            }
            else{
                console.log("FAILED TO FINISH EDITING: TRY AGAIN")
            }
        }
    })
})


var src_now = ""

function updateSource(){
    if(CodeEditor.getText().localeCompare(src_now) == 0)
        return false;
    src_now = CodeEditor.getText();
    $.ajax({
        type : "post",
        url : "https://app.enamor68.hasura-app.io/source_update/"+$('input[name=issue-id]').val(),
        data : {source_code : CodeEditor.getText() , line_num : CodeEditor.getCursor().row+1},
        success : function(response){
            u_s =JSON.parse(response)
            if(u_s['status'].localeCompare("updated") == 0){
                console.log("Updated Source")
            }
            else{
                console.log("Source not updated")
            }
        }
    })
}

function loadRecentSource(){
    $.ajax({
        type : "get",
        url : "https://app.enamor68.hasura-app.io/load_source/"+$('input[name=issue-id]').val(),
        success : function(response){
            code = JSON.parse(response)
            CodeEditor.editText(code["source_code"])
            CodeEditor.setCursor(code["line_num"])
        }
    })
}