$(function () {
    if ($('#search_word').html() === '') {
        $('#content_result').append('<div class="h4">no results</div>')
    } else {
        $.ajax({
            url: '/re/search/bridge/', type: 'post', dataType: 'json', cache: false,
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
                            var keyword = ''
                            $.each(value.keyword_output, function (key, value) {
                                keyword = keyword + '<span class="search_suobj_keyword">' + value + '</span>'
                            })
                            var appender = '<div class="search_suobj_wrapper div_base">' +
                                '<div>' +
                                '<a href="/' + value.username + '/"><span class="search_suobj_username">' + value.username + '</span></a>' +
                                '<a href="/object/' + value.id + '/"><span class="search_suobj_detail">detail</span></a>' +
                                '</div>' +
                                '<a href="/object/' + value.id + '/">' +
                                '<div><span class="search_suobj_title">' + value.title + '</span></div>' +
                                '<div><span class="search_suobj_url">' + value.url + '</span></div>' +
                                '</a>' +
                                '<div class="search_suobj_keyword_wrapper">' + keyword + '</div>' +
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
            url: '/re/search/bridge/', type: 'post', dataType: 'json', cache: false,
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
                            var keyword = ''
                            $.each(value.keyword_output, function (key, value) {
                                keyword = keyword + '<span class="search_suobj_keyword">' + value + '</span>'
                            })
                            var appender = '<div class="search_suobj_wrapper div_base">' +
                                '<div>' +
                                '<a href="/' + value.username + '/"><span class="search_suobj_username">' + value.username + '</span></a>' +
                                '<a href="/object/' + value.id + '/"><span class="search_suobj_detail">detail</span></a>' +
                                '</div>' +
                                '<a href="/object/' + value.id + '/">' +
                                '<div><span class="search_suobj_title">' + value.title + '</span></div>' +
                                '<div><span class="search_suobj_url">' + value.url + '</span></div>' +
                                '</a>' +
                                '<div class="search_suobj_keyword_wrapper">' + keyword + '</div>' +
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