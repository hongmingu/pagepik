$(function () {
    if ($('#search_word').html() === '') {
        $('#content_user').append('<div class="h4">need search word</div>')
        $('#content_bridge').append('<div class="h4">need search word</div>')
        $('#content_keyword').append('<div class="h4">need search word</div>')
        $('#content_general').append('<div class="h4">need search word</div>')
    } else {
        $.ajax({
            url: '/re/search/all/', type: 'post', dataType: 'json', cache: false,
            data: {
                search_word: $('#search_word').html()
            },
            success: function (data) {
                console.log(data)
                if (data.res === 1) {
                    //post set
                    if (data.user_output.length === 0) {
                        $('#content_user').append('<div class="h4">no results</div>')
                        $('#more_user').addClass('hidden')
                    } else {
                        $('#more_user').removeClass('hidden')
                        $.each(data.user_output, function (key, value) {
                            var appender = '<div class="search_user_wrapper">' +
                                '<span class="search_user_username">' + value.username + '</span>' +
                                '<span class="search_user_textname">' + value.user_text_name + '</span>' +
                                '</div>'
                            $('#content_user').append(appender)
                        })
                    }

                    //user set

                    if (data.bridge_output.length === 0) {
                        if($('#user_id')===''){
                            $('#content_bridge').append('<a href="/"><div class="h4">need to login</div></a>')
                        }
                        $('#content_bridge').append('<div class="h4">no results</div>')
                        $('#more_bridge').addClass('hidden')


                    } else {
                        $('#more_bridge').removeClass('hidden')
                        $.each(data.bridge_output, function (key, value) {
                            var keyword = ''
                            $.each(value.keyword_output, function (key, value) {
                                keyword = keyword + '<span class="search_bridge_keyword">' + value + '</span>'
                            })
                            var appender = '<div class="search_bridge_wrapper">' +
                                '<div>' +
                                '<span class="search_bridge_username">' + value.username + '</span>' +
                                '<a href="/object/' + value.id + '/"><span class="search_bridge_more">more</span></a>' +
                                '</div>' +
                                '<div><span class="search_bridge_url"></span></div>' +
                                '<div class="search_bridge_keyword_wrapper">' + keyword + '</div>' +
                                '</div>'

                            $('#content_bridge').append(appender)

                        })
                    }

                    if (data.keyword_output.length === 0) {
                        $('#content_keyword').append('<div class="h4">no results</div>')
                        $('#more_keyword').addClass('hidden')


                    } else {
                        $('#more_keyword').removeClass('hidden')
                        $.each(data.keyword_output, function (key, value) {
                            var appender = '<a href="/search/all/?q=' + value + '">' +
                                '<span class="search_keyword">' + value + '</span>' +
                                '</a>'
                            $('#content_keyword').append(appender)
                        })
                    }


                    if (data.url_output.length === 0) {
                        $('#content_url').append('<div class="h4">no results</div>')
                        $('#more_url').addClass('hidden')


                    } else {
                        $('#more_url').removeClass('hidden')
                        $.each(data.url_output, function (key, value) {
                            var appender = '<div id="url_wrapper_' + value + '">' +
                                '<script defer>' +
                                '    search_url_populate("' + value + '")' +
                                '<' + '/script>' +
                                '</div>'
                            $('#content_url').append(appender)
                        })
                    }

                }


            }
        })
    }


})