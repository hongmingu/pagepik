$(function () {
    $.ajax({
        url: '/re/bridge/feed/', type: 'post', dataType: 'json', cache: false,
        data: {
            end_id: $('#end_id').html()
        },
        success: function (data) {
            console.log(data)
            $.each(data.output, function (key, value) {
                var obj_type = ''
                if (value.obj_type === 'help') {
                    obj_type = '<div>' +
                        '<a href="/' + value.username + '/">' +
                        '<span class="home_pop_username">' + value.username + '</span>' +
                        '</a>' +
                        '<span class="home_pop_help">found this helpful</span>' +
                        '</div>'
                }
                var suobj = '<div class="row div_base" id="suobj_wrapper_' + value.id + '">' +
                    '<script defer>' +
                    '    suobj_populate("' + value.id + '")' +
                    '<' + '/script>' +
                    '</div>'
                var appender = '<div id="obj_' + value.id + '">' + obj_type + suobj + '</div>'
                $('#content').append(appender)
            })
            if (data.end === null) {
                $('#more_load').addClass('hidden')
                $('#end_id').html('')
            } else {
                $('#more_load').addClass('hidden')
                $('#end_id').html(data.end)
            }

        }
    })

    $('#more_load').click(function (e) {
        e.preventDefault()
        $.ajax({
            url: '/re/bridge/feed/', type: 'post', dataType: 'json', cache: false,
            data: {
                end_id: $('#end_id').html()
            },
            success: function (data) {
                console.log(data)
                $.each(data.output, function (key, value) {
                    var obj_type = ''
                    if (value.obj_type === 'help') {
                        obj_type = '<div>' +
                            '<a href="/' + value.username + '/">' +
                            '<span class="home_pop_username">' + value.username + '</span>' +
                            '</a>' +
                            '<span class="home_pop_help">found this helpful</span>' +
                            '</div>'
                    }
                    var suobj = '<div class="row div_base" id="suobj_wrapper_' + value.id + '">' +
                        '<script defer>' +
                        '    suobj_populate("' + value.id + '")' +
                        '<' + '/script>' +
                        '</div>'
                    var appender = '<div id="obj_' + value.id + '">' + obj_type + suobj + '</div>'
                    $('#content').append(appender)
                })
                if (data.end === null) {
                    $('#more_load').addClass('hidden')
                    $('#end_id').html('')
                } else {
                    $('#more_load').addClass('hidden')
                    $('#end_id').html(data.end)
                }

            }
        })
    })
})