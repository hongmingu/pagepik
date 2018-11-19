$(function () {
    $.ajax({
        url: '/re/url/', type: 'post', dataType: 'json', cache: false,
        data: {
            url_id: $('#id').html(),
            last_id: $('#last_id').html(),
        },
        success: function (data) {
            if (data.res === 1){
                var _keyword = ''
                $.each(data.output, function (key, value) {
                    _keyword = _keyword + '<span>'+value.keyword+'</span>' +
                        '<span>☆★</span><span>'+value.reg_count+'</span>' +
                        '<span>△▲</span><span>'+value.up_count+'</span>'
                        '<span></span><span>'+value.down_count+'</span>'
                })
                $('#keyword_list').append(_keyword)
            }
            if (data.last === null){
                $('#keyword_more').addClass('hidden')
            } else {
                $('#keyword_more').removeClass('hidden')
            }
        }
    })

})

$(function () {
    $('#pop_menu').click(function (e) {
        e.preventDefault()
        $('#modal_pop_menu').modal('show')
    })

    $("#modal_pop_menu").on("shown.bs.modal", function () {
        var source = $('#link_source').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + source;
        $('#modal_pop_menu_input').val(path).select();
    }).on("hidden.bs.modal", function () {
        $('#clicked_post_id').html('')
        $('#modal_pop_menu_input').val('')
    });

    $('#modal_pop_menu_copy').click(function (e) {
        e.preventDefault()
        var source = $('#link_source').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + source;
        $('#modal_pop_menu_input').val(path).select();
        document.execCommand('Copy')
    })
    $('#modal_pop_menu_locate').click(function (e) {
        e.preventDefault()
        var source = $('#link_source').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + source;
        location.href=path
    })
})
