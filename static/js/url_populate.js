$(function () {
    $.ajax({
        url: '/re/url/', type: 'post', dataType: 'json', cache: false,
        data: {
            url_id: $('#id').html(),
            last_id: $('#last_id').html(),
        },
        success: function (data) {
            console.log(data)
            if (data.res === 1){


                $.each(data.output, function (key, value) {
                    var id = value.keyword_id
                    var _keyword = ''
                    var _register = ''
                    var _up = ''
                    var _down = ''
                    if(value.register === 'true'){
                        _register = '<span class="url_pop_reg" id="url_pop_reg_'+id+'">★</span>'
                    }
                    else {
                        _register = '<span class="url_pop_reg" id="url_pop_reg_'+id+'">☆</span>'
                    }
                    if(value.up === 'true'){
                        _up = '<a href=""><span class="url_pop_up" id="url_pop_up_'+id+'">▲</span></a>'
                    }
                    else {
                        _up = '<a href=""><span class="url_pop_up" id="url_pop_up_'+id+'">△</span></a>'
                    }

                    if(value.down === 'true'){
                        _down = '<a href=""><span class="url_pop_down" id="url_pop_down_'+id+'">▼</span></a>'
                    }
                    else {
                        _down = '<a href=""><span class="url_pop_down" id="url_pop_down_'+id+'">▽</span></a>'
                    }


                    _keyword = '<span>'+value.keyword+'</span>' +
                        _register +
                        '<span id="url_pop_reg_count_'+id+'">'+value.reg_count+'</span>' +
                        _up +
                        '<span id="url_pop_up_count_'+id+'">'+value.up_count+'</span>' +
                        _down +
                        '<span id="url_pop_down_count_'+id+'">'+value.down_count+'</span>'


                    $('#keyword_list').append(_keyword)

                    $('#url_pop_up_'+id).on('click', function (e) {
                        e.preventDefault()

                        $.ajax({
                            url: '/re/url/keyword/up/', type: 'post', dataType: 'json', cache: false,
                            data: {
                                url_keyword_id: id,
                            },
                            success: function (data) {
                                if(data.res === 1){
                                    if(data.result ==='up'){
                                        $('#url_pop_up_'+id).html('▲')
                                        var up_count = $('#url_pop_up_count_'+id).html()
                                        $('#url_pop_up_count_'+id).html(parseInt(up_count)+1)

                                        if($('#url_pop_down_'+id).html()==='▼'){
                                            $('#url_pop_down_'+id).html('▽')
                                            var down_count = $('#url_pop_down_count_'+id).html()
                                            $('#url_pop_down_count_'+id).html(parseInt(down_count)-1)
                                        }

                                    } else if(data.result === 'cancel'){
                                        $('#url_pop_up_'+id).html('△')
                                        var up_count = $('#url_pop_up_count_'+id).html()
                                        $('#url_pop_up_count_'+id).html(parseInt(up_count)-1)
                                    }
                                }

                            }
                        })
                    })

                    $('#url_pop_down_'+id).on('click', function (e) {
                        e.preventDefault()

                        $.ajax({
                            url: '/re/url/keyword/down/', type: 'post', dataType: 'json', cache: false,
                            data: {
                                url_keyword_id: id,
                            },
                            success: function (data) {
                                if(data.res === 1){
                                    if(data.result ==='down'){
                                        $('#url_pop_down_'+id).html('▼')
                                        var down_count = $('#url_pop_down_count_'+id).html()
                                        $('#url_pop_down_count_'+id).html(parseInt(down_count)+1)

                                        if($('#url_pop_up_'+id).html()==='▲'){
                                            $('#url_pop_up_'+id).html('△')
                                            var up_count = $('#url_pop_up_count_'+id).html()
                                            $('#url_pop_up_count_'+id).html(parseInt(up_count)-1)
                                        }

                                    } else if(data.result === 'cancel'){
                                        $('#url_pop_down_'+id).html('▽')
                                        var down_count = $('#url_pop_down_count_'+id).html()
                                        $('#url_pop_down_count_'+id).html(parseInt(down_count)-1)
                                    }
                                }

                            }
                        })

                    })
                })



            }
            if (data.last === null){
                $('#keyword_more').addClass('hidden')
            } else {
                $('#keyword_more').removeClass('hidden')
            }
        }
    })

})

$(function () {
    $('#pop_menu').click(function (e) {
        e.preventDefault()
        $('#modal_pop_menu').modal('show')
    })

    $("#modal_pop_menu").on("shown.bs.modal", function () {
        var source = $('#link_source').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + source;
        $('#modal_pop_menu_input').val(path).select();
    }).on("hidden.bs.modal", function () {
        $('#clicked_post_id').html('')
        $('#modal_pop_menu_input').val('')
    });

    $('#modal_pop_menu_copy').click(function (e) {
        e.preventDefault()
        var source = $('#link_source').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + source;
        $('#modal_pop_menu_input').val(path).select();
        document.execCommand('Copy')
    })
    $('#modal_pop_menu_locate').click(function (e) {
        e.preventDefault()
        var source = $('#link_source').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + source;
        location.href=path
    })
})
