$(function () {
    $.ajax({
        url: '/re/bridge/feed/', type: 'post', dataType: 'json', cache: false,
        data: {
            end_id: $('#end_id').html()
        },
        success: function (data) {
            console.log(data)
            $.each(data.output, function (key, value) {
                var appender = ''
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
                    var appender = ''
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