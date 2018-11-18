var suobj_populate = function suobj_populate(id) {
    $(function () {
        $.ajax({
            url: '/re/suobj/populate/', type: 'post', dataType: 'json', cache: false,
            data: {
                suobj_id: id,
            },
            success: function (data) {
                //{'user_id', 'username', 'gross(포스트의)', 'date(포스트의)', 'created', 'obj_id', ['comment_username', 'comment_text', 'comment_user_id', 'comment_created', 'comment_id']}
                if (data.res === 1) {
                    console.log(data)
                    var user_id = $('#user_id').html()
                    var srks = ''
                    $.each(data.output.srk_output, function (index, value) {
                        srks = srks + '<span class="pop_srk">'+value+'</span>'
                    })
                    var appender = $('<div id="pop_'+id+'">' +
                        '<div align="right"><a href=""><span class="glyphicon glyphicon-option-horizontal pop_menu"></span></a></div>' +
                        '<div><a href="/'+data.output.username+'/"><span class="pop_username">'+data.output.username+'</span></a></div>' +
                        '<div><a href="'+data.output.url+'"><span class="pop_title">'+data.output.title+'</span></a></div>' +
                        '<div><a href="'+data.output.url+'"><span class="pop_url">'+data.output.url+'</span></a></div>' +
                        '<a href="/url/'+data.output.url_id+'/"><div class="pop_info"></div></a>' +
                        '<div align="right"><span class="pop_created">'+date_differ(data.output.created)+'</span></div>' +
                        '<div class="srk_list">'+srks+'</div>' +
                        '</div>')


                    appender.find('.pop_menu').on('click', function (e) {
                        e.preventDefault()
                        if ($('#user_id').html() === '') {
                            $('#modal_need_login_pop').modal('show')
                            return false;
                        }
                        $('#clicked_suobj_id').html(id)
                        $('#modal_pop_menu').modal('show')
                    })


                    $('#suobj_wrapper_' + id).append(appender)
                }
            }
        })
    })
}

$(function () {
    $("#modal_pop_menu").on("shown.bs.modal", function () {
        var clicked_post = $('#clicked_suobj_id').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + '/url/obj/' + clicked_post;
        $('#modal_pop_menu_input').val(path).select();
    }).on("hidden.bs.modal", function () {
        $('#clicked_post_id').html('')
        $('#modal_pop_menu_input').val('')
    });

    $('#modal_pop_menu_copy').click(function (e) {
        e.preventDefault()
        var clicked_post = $('#clicked_suobj_id').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + '/url/obj/' + clicked_post;
        $('#modal_pop_menu_input').val(path).select();
        document.execCommand('Copy')
    })
    $('#modal_pop_menu_locate').click(function (e) {
        e.preventDefault()
        var clicked_post = $('#clicked_suobj_id').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + '/url/obj/' + clicked_post;
        location.href=path
    })
})

// more load 구현