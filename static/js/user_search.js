$(function () {
    if ($('#search_word').html() === '') {
        $('#content_result_keyword').append('<div class="h4">no results</div>')
    } else {
        $.ajax({
            url: '/re/user/search/keyword/', type: 'post', dataType: 'json', cache: false,
            data: {
                search_word: $('#search_word').html(),
                user_id: $('#chosen_user_id').html(),
                order: $('#order').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    if (data.output.length === 0) {
                        $('#content_result_keyword').append('<div class="h4">end results</div>')
                    } else {
                        $.each(data.output, function (key, value) {
                            var appender = '<div>' +
                                '<a href="/search/all/?q=' + value + '">' +
                                '<span class="search_keyword">' + value + '</span>' +
                                '</a>' +
                                '</div>'
                            $('#content_result_keyword').append(appender)

                        })
                    }

                    if (data.end === "true") {
                        $('#more_load_keyword').addClass('hidden')
                    } else if (data.end === "false") {
                        $('#more_load_keyword').removeClass('hidden')
                    }
                    $('#order').html(data.order)
                }


            }
        })
    }

    $('#more_load_keyword').on('click', function (e) {
        e.preventDefault()
        $.ajax({
            url: '/re/user/search/keyword/', type: 'post', dataType: 'json', cache: false,
            data: {
                search_word: $('#search_word').html(),
                user_id: $('#chosen_user_id').html(),
                order: $('#order').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    //user set
                    if (data.output.length === 0) {
                        $('#content_result_keyword').append('<div class="h4">end results</div>')

                    } else {
                        $.each(data.output, function (key, value) {
                            var appender = '<div>' +
                                '<a href="/search/all/?q=' + value + '">' +
                                '<span class="search_keyword">' + value + '</span>' +
                                '</a>' +
                                '</div>'
                            $('#content_result_keyword').append(appender)

                        })
                    }

                    if (data.end === "true") {
                        $('#more_load_keyword').addClass('hidden')
                    } else if (data.end === "false") {
                        $('#more_load_keyword').removeClass('hidden')
                    }
                    $('#order').html(data.order)
                }


            }
        })
    })

    if ($('#search_word').html() === '') {
        $('#content_result_suobj').append('<div class="h4">no results</div>')
    } else {
        $.ajax({
            url: '/re/user/search/suobj/', type: 'post', dataType: 'json', cache: false,
            data: {
                search_word: $('#search_word').html(),
                user_id: $('#chosen_user_id').html(),
                end_id: $('#end_id').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    //user set
                    if (data.output.length === 0) {
                        $('#content_result_suobj').append('<div class="h4">end result</div>')

                    } else {
                        $.each(data.output, function (key, value) {
                            var keyword = ''
                            $.each(value.keyword_output, function (key, value) {
                                keyword = keyword + '<span class="search_suobj_keyword">' + value + '</span>'
                            })
                            var appender = '<div class="search_suobj_wrapper">' +
                                '<div>' +
                                '<a href="/' + value.username + '/"><span class="search_suobj_username">' + value.username + '</span></a>' +
                                '<a href="/object/' + value.id + '/"><span class="search_suobj_detail">detail</span></a>' +
                                '</div>' +
                                '<a href="' + value.url + '">' +
                                '<div><span class="search_suobj_title">' + value.title + '</span></div>' +
                                '<div><span class="search_suobj_url">' + value.url + '</span></div>' +
                                '</a>' +
                                '<div class="search_suobj_keyword_wrapper">' + keyword + '</div>' +
                                '</div>'
                            $('#content_result_suobj').append(appender)

                        })
                    }

                    if (data.end === null) {
                        $('#more_load_suobj').addClass('hidden')
                        $('#end_id').html('')
                    } else {
                        $('#more_load_suobj').removeClass('hidden')
                        $('#end_id').html(data.end)
                    }
                }


            }
        })
    }

    $('#more_load_suobj').on('click', function (e) {
        e.preventDefault()
        $.ajax({
            url: '/re/user/search/suobj/', type: 'post', dataType: 'json', cache: false,
            data: {
                search_word: $('#search_word').html(),
                user_id: $('#chosen_user_id').html(),
                end_id: $('#end_id').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    //user set
                    if (data.output.length === 0) {
                        $('#content_result_suobj').append('<div class="h4">end result</div>')

                    } else {
                        $.each(data.output, function (key, value) {
                            var keyword = ''
                            $.each(value.keyword_output, function (key, value) {
                                keyword = keyword + '<span class="search_suobj_keyword">' + value + '</span>'
                            })
                            var appender = '<div class="search_suobj_wrapper">' +
                                '<div>' +
                                '<a href="/' + value.username + '/"><span class="search_suobj_username">' + value.username + '</span></a>' +
                                '<a href="/object/' + value.id + '/"><span class="search_suobj_detail">detail</span></a>' +
                                '</div>' +
                                '<a href="' + value.url + '">' +
                                '<div><span class="search_suobj_title">' + value.title + '</span></div>' +
                                '<div><span class="search_suobj_url">' + value.url + '</span></div>' +
                                '</a>' +
                                '<div class="search_suobj_keyword_wrapper">' + keyword + '</div>' +
                                '</div>'
                            $('#content_result_suobj').append(appender)

                        })
                    }

                    if (data.end === null) {
                        $('#more_load_suobj').addClass('hidden')
                        $('#end_id').html('')
                    } else {
                        $('#more_load_suobj').removeClass('hidden')
                        $('#end_id').html(data.end)
                    }
                }


            }
        })
    })
})