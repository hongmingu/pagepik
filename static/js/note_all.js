$(function () {
    $.ajax({
        url: '/re/note/all/', type: 'post', dataType: 'json', cache: false,
        data: {
            end_id: $('#end_id').html()
        },
        success: function (data) {
            console.log(data)
            $.each(data.output, function (key, value) {
                var appender;
                switch (value.notice_kind) {
                    case 1001:
                        appender = '<div class="note_wrapper">' +
                            '<div class="note_img_wrapper">' +
                            '<a href="/' + value.notice_value.username + '/"><img class="note_img_small clickable" src="' + value.notice_value.user_photo + '"></a>' +
                            '</div>' +
                            '<div class="note_text_wrapper">' +
                            '<a href="/' + value.notice_value.username + '/"><span class="note_text_username clickable">' + value.notice_value.username + '</span></a>' +
                            '<span class="note_text_explain">new bridge</span>' +
                            '</div>' +
                            '</div>'
                        //bridge
                        break;
                    case 1002:
                        appender = '<div class="note_wrapper">' +
                            '<div class="note_img_wrapper">' +
                            '<a href="/' + value.notice_value.username + '/">' +
                            '<img class="note_img_small clickable" src="' + value.notice_value.user_photo + '"></a>' +
                            '</div>' +
                            '<div class="note_text_wrapper">' +
                            '<a href="/' + value.notice_value.username + '/"><span class="note_text_username clickable">' + value.notice_value.username + '</span></a>' +
                            '<span class="note_text_explain">found it helpful</span>' +
                            '<a href="/object/' + value.notice_value.suobj_id + '/"><span class="note_text_title clickable">' + value.notice_value.title + '</span></a></div>' +
                            '</div>'
                        //help
                        break;
                    case 1003:
                        appender = '<div class="note_wrapper">' +
                            '<div class="note_img_wrapper"><a href="/' + value.notice_value.username + '/"><img class="note_img_small clickable" src="' + value.notice_value.user_photo + '"></a></div>' +
                            '<div class="note_text_wrapper"><a href="/' + value.notice_value.username + '/"><span class="note_text_username clickable">' + value.notice_value.username + '</span></a>' +
                            '<span class="note_text_explain">comment: </span>' +
                            '<a href="/object/' + value.notice_value.obj_id + '/"><span class="note_text_comment clickable">' + value.notice_value.comment_text + '</span></a>' +
                            '</div>' +
                            '</div>'
                        //comment
                        break;
                    default:
                        break;
                }
                $('#content').append(appender)

            })
            if (data.end === null) {
                $('#more_load').addClass('hidden')
                $('#end_id').html('')
            } else {
                $('#more_load').removeClass('hidden')
                $('#end_id').html(data.end)
            }

        }
    })

    $('#more_load').click(function (e) {
        e.preventDefault()
        $.ajax({
            url: '/re/note/all/', type: 'post', dataType: 'json', cache: false,
            data: {
                end_id: $('#end_id').html()
            },
            success: function (data) {
                $.each(data.output, function (key, value) {
                    var appender;
                    switch (value.notice_kind) {
                        case 1001:
                            appender = '<div class="note_wrapper">' +
                                '<div class="note_img_wrapper">' +
                                '<a href="/' + value.notice_value.username + '/"><img class="note_img_small clickable" src="' + value.notice_value.user_photo + '"></a>' +
                                '</div>\n' +
                                '<div class="note_text_wrapper">' +
                                '<span class="note_text_explain">bridge from</span>' +
                                '<a href="/' + value.notice_value.username + '/"><span class="note_text_username clickable">' + value.notice_value.username + '</span></a>' +
                                '</div>' +
                                '</div>'
                            //bridge
                            break;
                        case 1002:
                            appender = '<div class="note_wrapper">' +
                                '<div class="note_img_wrapper">' +
                                '<a href="/' + value.notice_value.username + '/">' +
                                '<img class="note_img_small clickable" src="' + value.notice_value.user_photo + '"></a>' +
                                '</div>' +
                                '<div class="note_text_wrapper">' +
                                '<a href="/' + value.notice_value.username + '/"><span class="note_text_username clickable">' + value.notice_value.username + '</span></a>' +
                                '<span class="note_text_explain">found it helpful</span>' +
                                '<a href="/object/' + value.notice_value.suobj_id + '/"><span class="note_text_title clickable">' + value.notice_value.title + '</span></a></div>' +
                                '</div>'
                            //help
                            break;

                        case 1003:
                            appender = '<div class="note_wrapper">' +
                                '<div class="note_img_wrapper"><a href="/' + value.notice_value.username + '/"><img class="note_img_small clickable" src="' + value.notice_value.user_photo + '"></a></div>' +
                                '<div class="note_text_wrapper"><a href="/' + value.notice_value.username + '/"><span class="note_text_username clickable">' + value.notice_value.username + '</span></a>' +
                                '<span class="note_text_explain">comment: </span>' +
                                '<a href="/object/' + value.notice_value.obj_id + '/"><span class="note_text_comment clickable">' + value.notice_value.comment_text + '</span></a>' +
                                '</div>' +
                                '</div>'
                            //comment
                            break;
                        default:
                            break;
                    }
                    $('#content').append(appender)

                })
                if (data.end === null) {
                    $('#more_load').addClass('hidden')
                    $('#end_id').html('')
                } else {
                    $('#more_load').removeClass('hidden')
                    $('#end_id').html(data.end)
                }

            }
        })
    })
})