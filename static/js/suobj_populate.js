var suobj_populate = function suobj_populate(id) {
    $(function () {
        $.ajax({
            url: '/re/suobj/populate/', type: 'post', dataType: 'json', cache: false,
            data: {
                suobj_id: id,
            },
            success: function (data) {
                if (data.res === 1) {
                    var user_id = $('#user_id').html()
                    var srks = ''
                    $.each(data.output.srk_output, function (index, value) {
                        srks = srks + '<span class="pop_srk">' + value + '</span>'
                    })
                    var suobj_help = ''
                    if (data.output.suobj_help === 'true') {
                        suobj_help = '<a href=""><span class="pop_helped" id="pop_help_' + data.output.suobj_id + '">helped</span></a>'
                    } else {
                        suobj_help = '<a href=""><span class="pop_helpful" id="pop_help_' + data.output.suobj_id + '">helpful</span></a>'
                    }
                    var help_count = '<a href=""><span class="pop_help_count" id="pop_help_count_' + data.output.suobj_id + '">' + data.output.help_count + '</span></a><span class="pop_help_text">helps</span>'

                    var comment_more_load = '<a href=""><div class="pop_comment_more_load hidden" id="pop_comment_more_load_' + id + '" align="center">more load</div></a>'
                    if (data.output.comment_count > 3) {
                        comment_more_load = '<a href=""><div class="pop_comment_more_load" id="pop_comment_more_load_' + id + '" align="center">more load</div></a>'
                    }
                    var comment_textarea = '<div align="center"><form><div class="input-group input-group-sm">' +
                        '<textarea class="form-control pop_comment_textarea" id="pop_comment_textarea_' + id + '" placeholder="a comment"></textarea>' +
                        '<div class="input-group-btn">' +
                        '<button class="btn btn-default" id="pop_comment_btn_' + id + '">' +
                        '<i class="glyphicon glyphicon-send"></i>' +
                        '</button></div>' +
                        '</div>' +
                        '</form>' +
                        '</div>'
                    var comments = ''
                    var suobj_user_id = data.output.user_id
                    var end_comment_id = ''
                    $.each(data.output.comment_output, function (key, value) {
                        var delete_btn = ''
                        if (value.comment_user_id === user_id || suobj_user_id === user_id) {
                            delete_btn = '<a href=""><span class="glyphicon glyphicon-remove pop_comment_delete" data-u="' + value.comment_id + '"></span></a>'
                        }
                        comments = comments + '<div id="pop_comment_wrapper_' + value.comment_id + '">' +
                            '<div><a href="/' + value.comment_username + '/"><span class="pop_comment_username">' + value.comment_username + '</span></a></div>' +
                            '<div class="pop_comment_content"><span class="pop_comment_text">' + value.comment_text + '</span><span class="pop_comment_created">' + date_differ(value.comment_created) + '</span>' + delete_btn + '</div>' +
                            '</div>'
                        end_comment_id = value.comment_id
                    })
                    var end_comment = '<div class="hidden" id="end_comment_' + id + '">' + end_comment_id + '</div>'

                    var appender = $('<div id="pop_' + id + '">' +
                        '<div align="right"><a href=""><span class="glyphicon glyphicon-option-horizontal pop_menu"></span></a></div>' +
                        '<div><a href="/' + data.output.username + '/"><span class="pop_username">' + data.output.username + '</span></a></div>' +
                        '<div class="pop_title_wrapper"><a href="' + data.output.url + '" target="_blank" rel="noopener noreferrer"><span class="pop_title">' + data.output.title + '</span></a></div>' +
                        '<div><a href="' + data.output.url + '" target="_blank" rel="noopener noreferrer"><span class="pop_url">' + data.output.url + '</span></a></div>' +
                        '<a href="/url/' + data.output.url_id + '/"><div class="pop_public_info_wrapper"><span class="pop_public_info clickable">url info</span></div></a>' +
                        '<div align="right"><span class="pop_created">' + date_differ(data.output.created) + '</span></div>' +
                        '<div class="srk_list">' + srks + '</div>' +
                        '<div>' + help_count + suobj_help + '</div>' +
                        '<div><span class="pop_comment">comment</span><span class="pop_comment_count">' + data.output.comment_count + '</span></div>' +
                        '<div id="pop_comment_list_' + id + '">' + comments + '</div>' +//여기서 이것의 차일드 중 마지막 값의 uuid 를 이용하여 이것 다음 코멘트를
                        comment_more_load +
                        '<div id="pop_new_comment_list_' + id + '"></div>' +
                        comment_textarea +
                        end_comment +
                        '</div>')


                    appender.find('.pop_menu').on('click', function (e) {
                        e.preventDefault()
                        $('#clicked_suobj_id').html(id)
                        $('#modal_pop_menu').modal('show')
                    })
                    appender.find('#pop_help_' + data.output.suobj_id).on('click', function (e) {
                        e.preventDefault()
                        if ($('#user_id').html() === '') {
                            $('#modal_need_login_pop').modal('show')
                            return false;
                        }
                        $.ajax({
                            url: '/re/suobj/help/', type: 'post', dataType: 'json', cache: false,
                            data: {
                                suobj_id: id,
                            },
                            success: function (data) {
                                if (data.res === 1) {
                                    var cur_count = parseInt($('#pop_help_count_' + id).html())
                                    if (data.result === 'help') {
                                        $('#pop_help_' + id).removeClass('pop_helpful').addClass('pop_helped').html('helped')
                                        $('#pop_help_count_' + id).html(cur_count + 1)
                                    } else if (data.result === 'cancel') {
                                        $('#pop_help_' + id).removeClass('pop_helped').addClass('pop_helpful').html('helpful')
                                        $('#pop_help_count_' + id).html(cur_count - 1)
                                    }
                                }
                            }
                        })
                    })
                    appender.find('#pop_help_count_' + id).on('click', function (e) {
                        e.preventDefault()
                        if ($('#user_id').html() === '') {
                            $('#modal_need_login_pop').modal('show')
                            return false;
                        }
                        $('#clicked_suobj_id').html(id)
                        $('#modal_help').modal('show')
                    })
                    appender.find('#pop_comment_more_load_' + id).on('click', function (e) {
                        e.preventDefault()
                        $.ajax({
                            url: '/re/comment/more/load/', type: 'post', dataType: 'json', cache: false,
                            data: {
                                suobj_id: id,
                                end_comment_id: $('#end_comment_' + id).html(),
                            },
                            success: function (s_data) {
                                if (s_data.res === 1) {
                                    var _comment = ''
                                    $.each(s_data.output, function (s_key, s_value) {
                                        var delete_btn = ''
                                        if (s_value.comment_user_id === user_id || user_id === suobj_user_id) {
                                            delete_btn = '<a href=""><span class="glyphicon glyphicon-remove pop_comment_delete" data-u="' + s_value.comment_id + '"></span></a>'
                                        }
                                        _comment = _comment + '<div id="pop_comment_wrapper_' + s_value.comment_id + '">' +
                                            '<div><a href="/' + s_value.comment_username + '/"><span class="pop_comment_username">' + s_value.comment_username + '</span></a></div>' +
                                            '<div class="pop_comment_content"><span class="pop_comment_text">' + s_value.comment_text + '</span><span class="pop_comment_created">' + date_differ(s_value.comment_created) + '</span>' + delete_btn + '</div>' +
                                            '</div>'
                                    })
                                    var _comment_appender = $(_comment)
                                    _comment_appender.find('.pop_comment_delete').on('click', function (e) {
                                        e.preventDefault()
                                        var delete_comment_id = $(this).attr('data-u')
                                        $.ajax({
                                            url: '/re/comment/delete/', type: 'post', dataType: 'json', cache: false,
                                            data: {
                                                suobj_id: id,
                                                comment_id: delete_comment_id,
                                            },
                                            success: function (ss_data) {
                                                if (ss_data.res === 1) {
                                                    $('#pop_comment_wrapper_' + delete_comment_id).replaceWith('<div class="h5">removed</div>')
                                                }
                                            }
                                        })
                                    })
                                    $('#pop_comment_list_' + id).append(_comment_appender)

                                    if (s_data.end === null) {
                                        $('#pop_comment_more_load_' + id).addClass('hidden')
                                        $('#end_comment_' + id).html('')

                                    } else {
                                        $('#pop_comment_more_load_' + id).removeClass('hidden')
                                        $('#end_comment_' + id).html(s_data.end)
                                    }
                                }
                            }
                        })
                    })

                    appender.find('.pop_comment_delete').on('click', function (e) {
                        e.preventDefault()
                        if ($('#user_id').html() === '') {
                            $('#modal_need_login_pop').modal('show')
                            return false;
                        }
                        var delete_comment_id = $(this).attr('data-u')
                        $.ajax({
                            url: '/re/comment/delete/', type: 'post', dataType: 'json', cache: false,
                            data: {
                                suobj_id: id,
                                comment_id: delete_comment_id,
                            },
                            success: function (s_data) {
                                if (s_data.res === 1) {
                                    $('#pop_comment_wrapper_' + delete_comment_id).replaceWith('<div class="h5">removed</div>')
                                }
                            }
                        })
                    })
                    appender.find('#pop_comment_textarea_' + id).on('keypress', function (e) {
                        if ($('#user_id').html() === '') {
                            $('#modal_need_login_pop').modal('show')
                            return false;
                        }

                        if (e.keyCode == 13 && !e.shiftKey) {
                            var text = $('#pop_comment_textarea_' + id).val()
                            text = text.trim()
                            if (text === '') {
                                return false;
                            }
                            if (1000 < text.length) {
                                alert('too long')
                                return false;
                            }
                            $.ajax({
                                url: '/re/comment/add/', type: 'post', dataType: 'json', cache: false,
                                data: {
                                    suobj_id: id,
                                    text: text,
                                },
                                success: function (s_data) {
                                    if (s_data.res === 1) {
                                        var _comment_appender = $('<div id="pop_new_comment_wrapper_' + s_data.comment_id + '">' +
                                            '<div class="pop_new_comment_content"><span class="pop_new_comment_text">' + s_data.comment_text + '</span><a href=""><span class="glyphicon glyphicon-remove pop_new_comment_delete" data-u="' + s_data.comment_id + '"></span></a></div>' +
                                            '</div>');

                                        _comment_appender.find('.pop_new_comment_delete').on('click', function (e) {
                                            e.preventDefault()
                                            var delete_comment_id = $(this).attr('data-u')
                                            $.ajax({
                                                url: '/re/comment/delete/',
                                                type: 'post',
                                                dataType: 'json',
                                                cache: false,
                                                data: {
                                                    suobj_id: id,
                                                    comment_id: delete_comment_id,
                                                },
                                                success: function (ss_data) {
                                                    if (ss_data.res === 1) {
                                                        $('#pop_new_comment_wrapper_' + delete_comment_id).replaceWith('<div class="h5">removed</div>')
                                                    }
                                                }
                                            })
                                        })
                                        $('#pop_new_comment_list_' + id).append(_comment_appender)
                                        $('#pop_comment_textarea_' + id).val('')
                                    }
                                }
                            })

                        }
                    })

                    appender.find('#pop_comment_btn_' + id).on('click', function (e) {
                        e.preventDefault()

                        if ($('#user_id').html() === '') {
                            $('#modal_need_login_pop').modal('show')
                            return false;
                        }
                        var text = $('#pop_comment_textarea_' + id).val()
                        text = text.trim()
                        if (text === '') {
                            return false;
                        }
                        if (1000 < text.length) {
                            alert('too long')
                            return false;
                        }
                        $.ajax({
                            url: '/re/comment/add/', type: 'post', dataType: 'json', cache: false,
                            data: {
                                suobj_id: id,
                                text: text,
                            },
                            success: function (s_data) {

                                if (s_data.res === 1) {
                                    var _comment_appender = $('<div id="pop_new_comment_wrapper_' + s_data.comment_id + '">' +
                                        '<div class="pop_new_comment_content"><span class="pop_new_comment_text">' + s_data.comment_text + '</span><a href=""><span class="glyphicon glyphicon-remove pop_new_comment_delete" data-u="' + s_data.comment_id + '"></span></a></div>' +
                                        '</div>');

                                    _comment_appender.find('.pop_new_comment_delete').on('click', function (e) {
                                        e.preventDefault()
                                        var delete_comment_id = $(this).attr('data-u')
                                        $.ajax({
                                            url: '/re/comment/delete/', type: 'post', dataType: 'json', cache: false,
                                            data: {
                                                suobj_id: id,
                                                comment_id: delete_comment_id,
                                            },
                                            success: function (ss_data) {
                                                if (ss_data.res === 1) {
                                                    $('#pop_new_comment_wrapper_' + delete_comment_id).replaceWith('<div class="h5">removed</div>')
                                                }
                                            }
                                        })
                                    })
                                    $('#pop_new_comment_list_' + id).append(_comment_appender)
                                    $('#pop_comment_textarea_' + id).val('')
                                }
                            }
                        })

                    })

                    $('#suobj_wrapper_' + id).append(appender)
                }
            }
        })
    })
}

$(function () {
    $("#modal_pop_menu").on("shown.bs.modal", function () {
        var clicked_suobj = $('#clicked_suobj_id').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + '/object/' + clicked_suobj +'/';
        $('#modal_pop_menu_input').val(path).select();
    }).on("hidden.bs.modal", function () {
        $('#clicked_suobj_id').html('')
        $('#modal_pop_menu_input').val('')
    });

    $('#modal_pop_menu_copy').click(function (e) {
        e.preventDefault()
        var clicked_suobj = $('#clicked_suobj_id').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + '/object/' + clicked_suobj +'/';
        $('#modal_pop_menu_input').val(path).select();
        document.execCommand('Copy')
    })
    $('#modal_pop_menu_locate').click(function (e) {
        e.preventDefault()
        var clicked_suobj = $('#clicked_suobj_id').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + '/object/' + clicked_suobj +'/';
        location.href = path
    })
})
$(function () {
    var height = $(window).height();
    $('.modal-body').css('max-height', height - 120);
    $(window).on('resize', function () {

        if ($(window).height() != height) {
            height = $(window).height();
            $('.modal-body').css('max-height', height - 120);
        }
    });
})
$(function () {

    $("#modal_help").on("shown.bs.modal", function () {
        var height = $(window).height();
        $('.modal-body').css('max-height', height - 120);
        $(window).on('resize', function () {
            if ($(window).height() != height) {
                height = $(window).height();
                $('.modal-body').css('max-height', height - 120);
            }
        });

        var clicked_id = $('#clicked_suobj_id').html()

        $.ajax({
            url: '/re/help/list/', type: 'post', dataType: 'json', cache: false,
            data: {
                suobj_id: clicked_id,
                next_user_id: $('#next_user_id').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    $.each(data.output, function (key, value) {
                        var appender = '<div class="modal_unit_wrapper"><a href="/' + value.username + '/">\n' +
                            '<img class="modal_img" src="' + value.photo + '">\n' +
                            '<span class="modal_username">' + value.username + '</span>\n' +
                            '</a></div>'
                        $('#modal_help_list').append(appender)
                    })
                }
                if (data.next === null) {
                    $('#modal_help_more').addClass('hidden')
                } else {
                    $('#modal_help_more').removeClass('hidden')
                }

            }
        })
    }).on("hidden.bs.modal", function () {
        $('#modal_help_list').empty()
        $('#next_user_id').html('')
        $('#clicked_suobj_id').html('')

    });

    $('#modal_help_more').click(function (e) {
        e.preventDefault()

        $.ajax({
            url: '/re/help/list/', type: 'post', dataType: 'json', cache: false,
            data: {
                suobj_id: clicked_id,
                next_user_id: $('#next_user_id').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    $.each(data.output, function (key, value) {
                        var appender = '<div class="modal_unit_wrapper"><a href="/' + value.username + '/">\n' +
                            '<img class="modal_img" src="' + value.photo + '">\n' +
                            '<span class="modal_username">' + value.username + '</span>\n' +
                            '</a></div>'
                        $('#modal_help_list').append(appender)
                    })
                }
                if (data.next === null) {
                    $('#modal_help_more').addClass('hidden')
                } else {
                    $('#modal_help_more').removeClass('hidden')
                }

            }
        })
    })
})
// more load 구현