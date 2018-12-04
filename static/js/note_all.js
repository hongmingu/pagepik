$(function () {
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
                        appender = '<div class="note_wrapper">\n' +
                            '<div class="note_img_wrapper">' +
                            '<a href="/' + value.notice_value.username + '/"><img class="note_img_small clickable" src="' + value.notice_value.user_photo + '"></a>' +
                            '</div>\n' +
                            '<div class="note_text_wrapper">' +
                            '<a href="/' + value.notice_value.username + '/"><span class="note_text_username clickable">' + value.notice_value.username + '</span></a>' +
                            'follow you.' +
                            '</div>\n' +
                            '</div>'
                        //follow
                        break;
                    case 1002:
                        appender = '<div class="note_wrapper">\n' +
                            '<div class="note_img_wrapper"><a href="/' + value.notice_value.username + '/"><img class="note_img_small clickable" src="' + value.notice_value.user_photo + '"></a></div>\n' +
                            '<div class="note_text_wrapper"><a href="/' + value.notice_value.username + '/"><span class="note_text_username clickable">' + value.notice_value.username + '</span></a>follow your <a href="/post/' + value.notice_value.post_id + '/"><span class="note_text_post clickable">post</span></a></div>\n' +
                            '</div>'
                        //post_follow
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
                            appender = '<div class="note_wrapper">\n' +
                                '<div class="note_img_wrapper">' +
                                '<a href="/' + value.notice_value.username + '/"><img class="note_img_small clickable" src="' + value.notice_value.user_photo + '"></a>' +
                                '</div>\n' +
                                '<div class="note_text_wrapper">' +
                                '<a href="/' + value.notice_value.username + '/"><span class="note_text_username clickable">' + value.notice_value.username + '</span></a>' +
                                'follow you.' +
                                '</div>\n' +
                                '</div>'
                            //bridge
                            break;
                        case 1002:
                            appender = '<div class="note_wrapper">\n' +
                                '<div class="note_img_wrapper"><a href="/' + value.notice_value.username + '/"><img class="note_img_small clickable" src="' + value.notice_value.user_photo + '"></a></div>\n' +
                                '<div class="note_text_wrapper"><a href="/' + value.notice_value.username + '/"><span class="note_text_username clickable">' + value.notice_value.username + '</span></a>follow your <a href="/post/' + value.notice_value.post_id + '/"><span class="note_text_post clickable">post</span></a></div>\n' +
                                '</div>'
                            //help
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