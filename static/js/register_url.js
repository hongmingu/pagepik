$(function () {

    $('#url_input').on("keypress", function (e) {
        /* ENTER PRESSED*/
        if (e.keyCode == 13 && !e.shiftKey) {
            if ($('#check').html() === 'waiting...') {
                return false
            }
            $('#url_example_wrapper').empty()
            var url = $('#url_input').val()

            if (url.replace(/ /g, '') === '') {
                $('#url_clue').html('url cannot be empty')

                return false
            }
            $('#url_clue').html('')
            $('#first_url').html('')
            $('#check').html('waiting...')
            $.ajax({
                url: '/re/check/url/', type: 'post', dataType: 'json', cache: false,
                data: {
                    url: url
                },
                success: function (data) {
                    $('#check').html('check')
                    if (data.res === 1) {
                        if (data.output.length === 0) {
                            $('#url_clue').html('cannot find url')
                            return false
                        }
                        if ($('#url_example_wrapper').hasClass('hidden')) {
                            $('.url_example_wrapper').removeClass('hidden')
                        }
                        var append_array = []

                        $.each(data.output, function (key, value) {
                            if (value.in_not_301 === 'true') {
                                append_array.push(value)
                            } else {
                                append_array.unshift(value)
                            }
                        })
                        $.each(append_array, function (key, value) {
                            var appender = $('<a href="">' +
                                '<div class="url_example clickable">' +
                                '<div class="url_example_title">' + value.title + '</div>' +
                                '<div class="url_example_url">' + value.url + '</div>' +
                                '</div>' +
                                '</a>')
                            appender.on('click', function (e) {
                                e.preventDefault()
                                if (value.user_has_it !== 'false') {
                                    var scheme = window.location.protocol == "https:" ? "https://" : "http://";
                                    var update_location = scheme + window.location.host + "/update/url/" + data.id + '/';
                                    location.href = update_location
                                }
                                $('#discrete_loc').html(value.loc)
                                $('#discrete_scheme').html(value.discrete_scheme)
                                $('#in_not_301').html(value.in_not_301)
                                $('#is_discrete').html(value.is_discrete)
                                $('#loc').html(value.loc)
                                $('#scheme').html(value.scheme)
                                $('#title').html(value.title)
                                $('#url').html(value.url)
                                $('#add_keyword_title').html(value.title)
                                $('#add_keyword_url').html(value.url)
                                $('#url_check_wrapper').remove()
                                $('#url_example_wrapper').remove()
                                $('#init_url').html(data.init_url)

                                if ($('#add_keyword_wrapper').hasClass('hidden')) {
                                    $('#add_keyword_wrapper').removeClass('hidden')
                                }
                            })
                            $('#url_example_wrapper').append(appender)
                            var sub_appender = '<div align="right">' +
                                '<a href="' + value.url + '" target="_blank" rel="noopener noreferrer">' +
                                '<span class="clickable url_example_enter">enter url<span>' +
                                '</a>' +
                                '</div>'
                            $('#url_example_wrapper').append(sub_appender)

                        })
                        $('#url_example_wrapper').append()

                    } else if (data.res === 0) {
                        if (data.message === 'unable') {
                            $('#url_clue').html('url is unable to check')
                        }
                    }

                }
            });

            return false;
        }

    })
    $('#check').click(function (e) {
        if ($('#check').html() === 'waiting...') {
            return false
        }
        e.preventDefault()
        $('#url_example_wrapper').empty()
        var url = $('#url_input').val()

        if (url.replace(/ /g, '') === '') {
            $('#url_clue').html('url cannot be empty')

            return false
        }
        $('#url_clue').html('')
        $('#first_url').html('')
        $('#check').html('waiting...')
        $.ajax({
            url: '/re/check/url/', type: 'post', dataType: 'json', cache: false,
            data: {
                url: url
            },
            success: function (data) {
                $('#check').html('check')
                if (data.res === 1) {
                    if (data.output.length === 0) {
                        $('#url_clue').html('cannot find url')
                        return false
                    }
                    if ($('#url_example_wrapper').hasClass('hidden')) {
                        $('.url_example_wrapper').removeClass('hidden')
                    }
                    var append_array = []

                    $.each(data.output, function (key, value) {
                        if (value.in_not_301 === 'true') {
                            append_array.push(value)
                        } else {
                            append_array.unshift(value)
                        }
                    })
                    $.each(append_array, function (key, value) {
                        var appender = $('<a href="">' +
                            '<div class="url_example clickable">' +
                            '<div class="url_example_title">' + value.title + '</div>' +
                            '<div class="url_example_url">' + value.url + '</div>' +
                            '</div>' +
                            '</a>')
                        appender.on('click', function (e) {
                            e.preventDefault()
                            if (value.user_has_it !== 'false') {
                                var scheme = window.location.protocol == "https:" ? "https://" : "http://";
                                var update_location = scheme + window.location.host + "/update/url/" + data.id + '/';
                                location.href = update_location
                            }
                            $('#discrete_loc').html(value.loc)
                            $('#discrete_scheme').html(value.discrete_scheme)
                            $('#in_not_301').html(value.in_not_301)
                            $('#is_discrete').html(value.is_discrete)
                            $('#loc').html(value.loc)
                            $('#scheme').html(value.scheme)
                            $('#title').html(value.title)
                            $('#url').html(value.url)
                            $('#add_keyword_title').html(value.title)
                            $('#add_keyword_url').html(value.url)
                            $('#url_check_wrapper').remove()
                            $('#url_example_wrapper').remove()
                            $('#init_url').html(data.init_url)

                            if ($('#add_keyword_wrapper').hasClass('hidden')) {
                                $('#add_keyword_wrapper').removeClass('hidden')
                            }
                        })
                        $('#url_example_wrapper').append(appender)
                        var sub_appender = '<div align="right">' +
                            '<a href="' + value.url + '" target="_blank" rel="noopener noreferrer">' +
                            '<span class="clickable url_example_enter">enter url<span>' +
                            '</a>' +
                            '</div>'
                        $('#url_example_wrapper').append(sub_appender)

                    })
                    $('#url_example_wrapper').append()

                } else if (data.res === 0) {
                    if (data.message === 'unable') {
                        $('#url_clue').html('url is unable to check')
                    }
                }

            }
        });

    })
    $('#add_keyword').click(function (e) {
        e.preventDefault()
        var input = $.trim($('#keyword_input').val())

        if (input.replace(/ /g, '') === '') {
            $('#keyword_clue').html('keyword cannot be empty')

            return false
        }
        if (input.length > 2048) {
            $('#keyword_clue').html('keyword is too long')
            return false
        }
        var exist = false
        if ($('.added_keyword').length > 30) {
            $('#keyword_clue').html('keyword count cannot be over 30')
            return false
        }

        $('.added_keyword').each(function () {
            if (input === $(this).html()) {
                exist = true
            }
        })
        if (exist === true) {
            $('#keyword_clue').html('keyword cannot be the same')

            return false
        }

        var uuid = generate_uuid()
        var added_keyword = $('<span class="added_keyword_wrapper" id="added_keyword_wrapper_' + uuid + '"><span class="added_keyword">' + input + '</span><a href=""><span class="glyphicon glyphicon-remove keyword_delete"></span></a></span>')

        added_keyword.find('.keyword_delete').on('click', function (e) {
            e.preventDefault()
            $('#added_keyword_wrapper_' + uuid).remove()
        })
        $('#added_keyword_container').append(added_keyword)
        $('#keyword_input').val('')
        $('#keyword_clue').html('')

    })
    $('#keyword_input').on("keypress", function (e) {
        /* ENTER PRESSED*/
        if (e.keyCode == 13 && !e.shiftKey) {
            var input = $.trim($('#keyword_input').val())

            if (input.replace(/ /g, '') === '') {
                $('#keyword_clue').html('keyword cannot be empty')

                return false
            }
            if (input.length > 2048) {
                $('#keyword_clue').html('keyword is too long')
                return false
            }
            var exist = false
            if ($('.added_keyword').length > 30) {
                $('#keyword_clue').html('keyword count cannot be over 30')
                return false
            }

            $('.added_keyword').each(function () {
                if (input === $(this).html()) {
                    exist = true
                }
            })
            if (exist === true) {
                $('#keyword_clue').html('keyword cannot be the same')

                return false
            }

            var uuid = generate_uuid()
            var added_keyword = $('<span class="added_keyword_wrapper" id="added_keyword_wrapper_' + uuid + '"><span class="added_keyword">' + input + '</span><a href=""><span class="glyphicon glyphicon-remove keyword_delete"></span></a></span>')

            added_keyword.find('.keyword_delete').on('click', function (e) {
                e.preventDefault()
                $('#added_keyword_wrapper_' + uuid).remove()
            })
            $('#added_keyword_container').append(added_keyword)
            $('#keyword_input').val('')
            $('#keyword_clue').html('')
            return false;
        }

    })
    $('#complete_keyword').click(function (e) {

        e.preventDefault()

        if ($('#complete_keyword').html() === 'waiting...') {
            return false
        }

        if ($('.added_keyword').length === 0) {
            $('#keyword_clue').html('need some keyword')
            return false
        }
        var send_array = []
        $('.added_keyword').each(function () {
            send_array.push($(this).html())
        })

        $('#complete_keyword').html('waiting...')
        $.ajax({
            url: '/re/register/url/', type: 'post', dataType: 'json', cache: false,
            data: {
                discrete_loc: $('#discrete_loc').html(),
                discrete_scheme: $('#discrete_scheme').html(),
                in_not_301: $('#in_not_301').html(),
                is_discrete: $('#is_discrete').html(),
                loc: $('#loc').html(),
                scheme: $('#scheme').html(),
                title: $('#title').html(),
                url: $('#url').html(),
                init_url: $('#init_url').html(),
                keyword_list: send_array
            },
            success: function (data) {
                $('#complete_keyword').html('complete')
                if (data.res === 1) {
                    var scheme = window.location.protocol == "https:" ? "https://" : "http://";
                    var update_location = scheme + window.location.host + '/' + $('#user_username').html() + '/';
                    location.href = update_location
                }
            }
        });

    })
});
