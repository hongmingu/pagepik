$(function () {
    if ($('#search_word').html() === '') {
        $('#content_result').append('<div class="h4">no results</div>')
    } else {
        $.ajax({
            url: '/re/search/url/', type: 'post', dataType: 'json', cache: false,
            data: {
                search_word: $('#search_word').html(),
                order: $('#order').html()
            },
            success: function (data) {
                console.log(data)
                if (data.res === 1) {
                    //user set
                    if (data.output.length === 0) {
                        $('#content_result').append('<div class="h4">end results</div>')

                    } else {
                        $.each(data.output, function (key, value) {
                            var appender = '<div id="url_wrapper_' + value + '">' +
                                '<script defer>' +
                                '    search_url_populate("' + value + '")' +
                                '<' + '/script>' +
                                '</div>'
                            $('#content_result').append(appender)

                        })
                    }

                    if (data.end === "true") {
                        $('#more_load').addClass('hidden')
                    } else if (data.end === "false") {
                        $('#more_load').removeClass('hidden')
                    }
                    $('#order').html(data.order)
                }


            }
        })
    }

    $('#more_load').on('click', function (e) {
        e.preventDefault()
        $.ajax({
            url: '/re/search/url/', type: 'post', dataType: 'json', cache: false,
            data: {
                search_word: $('#search_word').html(),
                order: $('#order').html()
            },
            success: function (data) {
                console.log(data)
                if (data.res === 1) {
                    //user set
                    if (data.output.length === 0) {
                        $('#content_result').append('<div class="h4">end results</div>')

                    } else {
                        $.each(data.output, function (key, value) {
                            var appender = '<div id="url_wrapper_' + value + '">' +
                                '<script defer>' +
                                '    search_url_populate("' + value + '")' +
                                '<' + '/script>' +
                                '</div>'
                            $('#content_result').append(appender)


                        })
                    }

                    if (data.end === "true") {
                        $('#more_load').addClass('hidden')
                    } else if (data.end === "false") {
                        $('#more_load').removeClass('hidden')
                    }
                    $('#order').html(data.order)
                }


            }
        })
    })
})