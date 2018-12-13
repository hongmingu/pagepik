$(function () {
    if ($('#search_word').html() === '') {
        $('#content_result').append('<div class="h4">no results</div>')
    } else {
        $.ajax({
            url: '/re/search/user/', type: 'post', dataType: 'json', cache: false,
            data: {
                search_word: $('#search_word').html(),
                end_id: $('#end_id').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    //user set
                    if (data.output.length === 0) {
                        $('#content_result').append('<div class="h4">end result</div>')

                    } else {
                        $.each(data.output, function (key, value) {
                            var appender = '<div class="search_user_wrapper">\n' +
                                '<div class="search_user_img_wrapper"><a href="/' + value.username + '/"><img class="search_user_img_small clickable" src="' + value.user_photo + '"></a></div>\n' +
                                '<div class="search_user_detail_wrapper"><a href="/' + value.username + '/"><span class="search_user_detail_username clickable">' + value.username + '</span></a><span> <span><a href="/' + value.username + '/"><span class="search_user_detail_name clickable">' + value.user_text_name + '</span></a></div>\n' +
                                '</div>'
                            $('#content_result').append(appender)

                        })
                    }

                    if (data.end === null) {
                        $('#more_load').addClass('hidden')
                        $('#end_id').html('')
                    } else {
                        $('#more_load').removeClass('hidden')
                        $('#end_id').html(data.end)
                    }
                }


            }
        })
    }

    $('#more_load').on('click', function (e) {
        e.preventDefault()
        $.ajax({
            url: '/re/search/user/', type: 'post', dataType: 'json', cache: false,
            data: {
                search_word: $('#search_word').html(),
                end_id: $('#end_id').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    //user set
                    if (data.output.length === 0) {
                        $('#content_result').append('<div class="h4">end result</div>')

                    } else {
                        $.each(data.output, function (key, value) {
                            var appender = '<div class="search_user_wrapper">\n' +
                                '<div class="search_user_img_wrapper"><a href="/' + value.username + '/"><img class="search_user_img_small clickable" src="' + value.user_photo + '"></a></div>\n' +
                                '<div class="search_user_detail_wrapper"><a href="/' + value.username + '/"><span class="search_user_detail_username clickable">' + value.username + '</span></a><span> <span><a href="/' + value.username + '/"><span class="search_user_detail_name clickable">' + value.user_text_name + '</span></a></div>\n' +
                                '</div>'
                            $('#content_result').append(appender)

                        })
                    }

                    if (data.end === null) {
                        $('#more_load').addClass('hidden')
                        $('#end_id').html('')
                    } else {
                        $('#more_load').removeClass('hidden')
                        $('#end_id').html(data.end)
                    }
                }
            }
        })
    })
})