$(function () {
    $.ajax({
        url: '/re/update/url/', type: 'post', dataType: 'json', cache: false,
        data: {
            id: $('#id').html(),
        },
        success: function (data) {
            if (data.res === 1) {
                $('#add_keyword_title').html(data.title)
                $('#add_keyword_url').html(data.url)
                $.each(data.keyword_output, function (key, value) {

                    var uuid = generate_uuid()
                    var added_keyword = $('<span class="added_keyword_wrapper" id="added_keyword_wrapper_' + uuid + '"><span class="added_keyword">' + value + '</span><a href=""><span class="glyphicon glyphicon-remove keyword_delete"></span></a></span>')
                    added_keyword.find('.keyword_delete').on('click', function (e) {
                        e.preventDefault()
                        var deleted_keyword = $('<span class="deleted_keyword_wrapper" id="deleted_keyword_wrapper_' + uuid + '"><span class="deleted_keyword">' + value + '</span><a href=""><span class="glyphicon glyphicon-remove keyword_delete"></span></a></span>')

                        deleted_keyword.find('.keyword_delete').on('click', function (e) {
                            e.preventDefault()
                            $('#deleted_keyword_wrapper_' + uuid).remove()
                            if ($('#added_keyword_wrapper_' + uuid).hasClass('added_keyword_wrapper_deleted')) {
                                $('#added_keyword_wrapper_' + uuid).removeClass('added_keyword_wrapper_deleted')
                            }
                        })
                        if (!($('#deleted_keyword_wrapper_' + uuid).length)) {

                            $('#deleted_keyword_container').append(deleted_keyword)

                            if (!($('#added_keyword_wrapper_' + uuid).hasClass('added_keyword_wrapper_deleted'))) {
                                $('#added_keyword_wrapper_' + uuid).addClass('added_keyword_wrapper_deleted')
                            }
                        } else {
                            return false
                        }
                    })
                    $('#added_keyword_container').append(added_keyword)
                })
            }
        }
    });
    $('#refresh_title').click(function (e) {
        if ($('#refresh_title').html() === 'waiting...') {
            return false
        }
        e.preventDefault()
        $('#refresh_title').html('waiting...')
        $.ajax({
            url: '/re/refresh/url/', type: 'post', dataType: 'json', cache: false,
            data: {
                url: $('#add_keyword_url').html(),
            },
            success: function (data) {
                $('#refresh_title').html('refresh title')
                if (data.res === 1) {
                    $('#refresh').html('true')
                    $('#add_keyword_title').html(data.title)
                    $('#title').html(data.title)
                    $('#status_code').html(data.status_code)
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
            var deleted_keyword = $('<span class="deleted_keyword_wrapper" id="deleted_keyword_wrapper_' + uuid + '"><span class="deleted_keyword">' + input + '</span><a href=""><span class="glyphicon glyphicon-remove keyword_delete"></span></a></span>')
            deleted_keyword.find('.keyword_delete').on('click', function (e) {
                e.preventDefault()
                $('#deleted_keyword_wrapper_' + uuid).remove()
                if ($('#added_keyword_wrapper_' + uuid).hasClass('added_keyword_wrapper_deleted')) {
                    $('#added_keyword_wrapper_' + uuid).removeClass('added_keyword_wrapper_deleted')
                }

            })
            if (!($('#deleted_keyword_wrapper_' + uuid).length)) {
                $('#deleted_keyword_container').append(deleted_keyword)

                if (!($('#added_keyword_wrapper_' + uuid).hasClass('added_keyword_wrapper_deleted'))) {
                    $('#added_keyword_wrapper_' + uuid).addClass('added_keyword_wrapper_deleted')
                }
            } else {
                return false
            }
        })
        $('#added_keyword_container').append(added_keyword)
        $('#keyword_input').val('')
        $('#keyword_clue').html('')

    })
    $('#keyword_input').on("keypress", function (e) {
        /* ENTER PRESSED*/
        if (e.keyCode == 13 && !e.shiftKey) {
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
                var deleted_keyword = $('<span class="deleted_keyword_wrapper" id="deleted_keyword_wrapper_' + uuid + '"><span class="deleted_keyword">' + input + '</span><a href=""><span class="glyphicon glyphicon-remove keyword_delete"></span></a></span>')
                deleted_keyword.find('.keyword_delete').on('click', function (e) {
                    e.preventDefault()
                    $('#deleted_keyword_wrapper_' + uuid).remove()
                    if ($('#added_keyword_wrapper_' + uuid).hasClass('added_keyword_wrapper_deleted')) {
                        $('#added_keyword_wrapper_' + uuid).removeClass('added_keyword_wrapper_deleted')
                    }

                })
                if (!($('#deleted_keyword_wrapper_' + uuid).length)) {
                    $('#deleted_keyword_container').append(deleted_keyword)

                    if (!($('#added_keyword_wrapper_' + uuid).hasClass('added_keyword_wrapper_deleted'))) {
                        $('#added_keyword_wrapper_' + uuid).addClass('added_keyword_wrapper_deleted')
                    }
                } else {
                    return false
                }
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
        if ($('.added_keyword').length === $('.deleted_keyword').length) {
            $('#keyword_clue').html('need some keyword. do not delete all keyword.')
            return false
        }

        var send_array = []
        $('.added_keyword').each(function () {
            send_array.push($(this).html())
        })
        var delete_array = []
        $('.deleted_keyword').each(function () {
            delete_array.push($(this).html())
        })

        $('#complete_keyword').html('waiting...')
        $.ajax({
            url: '/re/update/complete/url/', type: 'post', dataType: 'json', cache: false,
            data: {
                id: $('#id').html(),
                refresh: $('#refresh').html(),
                status_code: $('#status_code').html(),
                title: $('#title').html(),
                keyword_list: send_array,
                delete_list: delete_array
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
