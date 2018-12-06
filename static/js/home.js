$(function () {
    $.ajax({
        url: '/re/home/', type: 'post', dataType: 'json', cache: false,
        data: {
            user_id: $('#user_id').html(),
            end_id: $('#end_id').html()
        },
        success: function (data) {
            console.log(data)
            if (data.res === 1) {
                $.each(data.output, function (key, value) {
                    var obj_type = ''
                    if (value.obj_type === 'help') {
                        obj_type = '<div>' +
                            '<a href="/' + value.username + '/">' +
                            '<span class="home_pop_username">' + value.username + '</span>' +
                            '</a>' +
                            '<span class="home_pop_help">found this helpful</span>' +
                            '</div>'

                    } else if (value.obj_type === 'keyword') {
                        obj_type = '<div>' +
                            '<span class="home_pop_by">by keyword: </span>' +
                            '<span class="home_pop_keyword">' + value.keyword + '</span>' +
                            '</div>'
                    }
                    if (!($('#obj_' + value.id).length > 0)) {
                        var suobj = '<div class="row div_base" id="suobj_wrapper_' + value.id + '">' +
                            '<script defer>' +
                            '    suobj_populate("' + value.id + '")' +
                            '<' + '/script>' +
                            '</div>'
                        var appender = '<div id="obj_' + value.id + '">' + obj_type + suobj + '</div>'
                        $('#content').append(appender)
                    }
                })

            }

        }
    })

    $('#more_load').click(function (e) {
        e.preventDefault()

        $.ajax({
            url: '/re/home/', type: 'post', dataType: 'json', cache: false,
            data: {
                user_id: $('#user_id').html(),
                end_id: $('#end_id').html()
            },
            success: function (data) {
                console.log(data)
                if (data.res === 1) {
                    $.each(data.output, function (key, value) {
                        var obj_type = ''
                        if (value.obj_type === 'help') {
                            obj_type = '<div>' +
                                '<a href="/' + value.username + '/">' +
                                '<span class="home_pop_username">' + value.username + '</span>' +
                                '</a>' +
                                '<span class="home_pop_help">found this helpful</span>' +
                                '</div>'

                        } else if (value.obj_type === 'keyword') {
                            obj_type = '<div>' +
                                '<span class="home_pop_by">by keyword: </span>' +
                                '<span class="home_pop_keyword">' + value.keyword + '</span>' +
                                '</div>'
                        }
                        if (!($('#obj_' + value.id).length > 0)) {
                            var suobj = '<div class="row div_base" id="suobj_wrapper_' + value.id + '">' +
                                '<script defer>' +
                                '    suobj_populate("' + value.id + '")' +
                                '<' + '/script>' +
                                '</div>'
                            var appender = '<div id="obj_' + value.id + '">' + obj_type + suobj + '</div>'
                            $('#content').append(appender)
                        }
                    })

                }

            }
        })
    })

})