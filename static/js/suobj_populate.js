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

                    var appender = $('<div id="pop_' + id + '">' +
                        '<div align="right"><a href=""><span class="glyphicon glyphicon-option-horizontal pop_menu"></span></a></div>' +
                        '<div><a href="/' + data.output.username + '/"><span class="pop_username">' + data.output.username + '</span></a></div>' +
                        '<div class="pop_title_wrapper"><a href="' + data.output.url + '" target="_blank" rel="noopener noreferrer"><span class="pop_title">' + data.output.title + '</span></a></div>' +
                        '<div><a href="' + data.output.url + '" target="_blank" rel="noopener noreferrer"><span class="pop_url">' + data.output.url + '</span></a></div>' +
                        '<a href="/url/' + data.output.url_id + '/"><div class="pop_public_info_wrapper"><span class="pop_public_info clickable">url info</span></div></a>' +
                        '<div align="right"><span class="pop_created">' + date_differ(data.output.created) + '</span></div>' +
                        '<div class="srk_list">' + srks + '</div>' +
                        '<div>' + help_count + suobj_help + '</div>' +
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
        var path = scheme + '://' + window.location.host + '/object/' + clicked_post;
        $('#modal_pop_menu_input').val(path).select();
    }).on("hidden.bs.modal", function () {
        $('#clicked_post_id').html('')
        $('#modal_pop_menu_input').val('')
    });

    $('#modal_pop_menu_copy').click(function (e) {
        e.preventDefault()
        var clicked_post = $('#clicked_suobj_id').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + '/object/' + clicked_post;
        $('#modal_pop_menu_input').val(path).select();
        document.execCommand('Copy')
    })
    $('#modal_pop_menu_locate').click(function (e) {
        e.preventDefault()
        var clicked_post = $('#clicked_suobj_id').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + '/object/' + clicked_post;
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