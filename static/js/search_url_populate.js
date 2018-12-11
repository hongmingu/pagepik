var search_url_populate = function search_url_populate(id) {
    var con_id = id
    $(function () {
        $.ajax({
            url: '/re/url/populate/', type: 'post', dataType: 'json', cache: false,
            data: {
                url_id: id,
            },
            success: function (data) {
                if (data.res === 1) {
                    var appender = '<div align="right">' +
                        '<a href=""><span class="glyphicon glyphicon-option-horizontal" id="pop_menu_' + id + '"></span></a>' +
                        '</div>' +
                        '<a href="' + data.full_url + '" target="_blank" rel="noopener noreferrer">' +
                        '<div>' +
                        '<div>' + data.full_url + '</div><div>' + data.title + '</div>' +
                        '</div>' +
                        '</a>' +
                        '<div id="keyword_list_' + id + '"></div>' +
                        '<div class="hidden" id="last_url_keyword_' + id + '"></div>' +
                        '<a href=""><div class="hidden" id="keyword_more_' + id + '">more load</div></a>'
                    $('#url_wrapper_' + id).append(appender)

                    $.ajax({
                        url: '/re/url/keyword/', type: 'post', dataType: 'json', cache: false,
                        data: {
                            url_id: id,
                            last_id: $('#last_url_keyword_' + id).html(),
                        },
                        success: function (data) {
                            console.log(data)
                            if (data.res === 1) {
                                $.each(data.output, function (key, value) {
                                    var id = value.keyword_id
                                    var _keyword = ''
                                    var _register = ''
                                    var _up = ''
                                    var _down = ''
                                    if (value.register === 'true') {
                                        _register = '<span class="url_pop_reg" id="url_pop_reg_' + id + '">★</span>'
                                    }
                                    else {
                                        _register = '<span class="url_pop_reg" id="url_pop_reg_' + id + '">☆</span>'
                                    }
                                    if (value.up === 'true') {
                                        _up = '<a href=""><span class="url_pop_up" id="url_pop_up_' + id + '">▲</span></a>'
                                    }
                                    else {
                                        _up = '<a href=""><span class="url_pop_up" id="url_pop_up_' + id + '">△</span></a>'
                                    }

                                    if (value.down === 'true') {
                                        _down = '<a href=""><span class="url_pop_down" id="url_pop_down_' + id + '">▼</span></a>'
                                    }
                                    else {
                                        _down = '<a href=""><span class="url_pop_down" id="url_pop_down_' + id + '">▽</span></a>'
                                    }


                                    _keyword = '<span class="url_pop_keyword_wrapper">' +
                                        '<span class="url_pop_keyword">' + value.keyword + '</span>' +
                                        _register +
                                        '<span class="url_pop_reg_count" id="url_pop_reg_count_' + id + '">' + value.reg_count + '</span>' +
                                        _up +
                                        '<span class="url_pop_up_count" id="url_pop_up_count_' + id + '">' + value.up_count + '</span>' +
                                        _down +
                                        '<span class="url_pop_down_count" id="url_pop_down_count_' + id + '">' + value.down_count + '</span>' +
                                        '</span>'


                                    $('#keyword_list_' + con_id).append(_keyword)

                                    $('#url_pop_up_' + id).on('click', function (e) {
                                        e.preventDefault()

                                        if ($('#user_id').html() === '') {
                                            $('#modal_need_login_pop').modal('show')
                                            return false;
                                        }
                                        $.ajax({
                                            url: '/re/url/keyword/up/',
                                            type: 'post',
                                            dataType: 'json',
                                            cache: false,
                                            data: {
                                                url_keyword_id: id,
                                            },
                                            success: function (data) {
                                                if (data.res === 1) {
                                                    if (data.result === 'up') {
                                                        $('#url_pop_up_' + id).html('▲')
                                                        var up_count = $('#url_pop_up_count_' + id).html()
                                                        $('#url_pop_up_count_' + id).html(parseInt(up_count) + 1)

                                                        if ($('#url_pop_down_' + id).html() === '▼') {
                                                            $('#url_pop_down_' + id).html('▽')
                                                            var down_count = $('#url_pop_down_count_' + id).html()
                                                            $('#url_pop_down_count_' + id).html(parseInt(down_count) - 1)
                                                        }

                                                    } else if (data.result === 'cancel') {
                                                        $('#url_pop_up_' + id).html('△')
                                                        var up_count = $('#url_pop_up_count_' + id).html()
                                                        $('#url_pop_up_count_' + id).html(parseInt(up_count) - 1)
                                                    }
                                                }

                                            }
                                        })
                                    })

                                    $('#url_pop_down_' + id).on('click', function (e) {
                                        e.preventDefault()
                                        if ($('#user_id').html() === '') {
                                            $('#modal_need_login_pop').modal('show')
                                            return false;
                                        }
                                        $.ajax({
                                            url: '/re/url/keyword/down/',
                                            type: 'post',
                                            dataType: 'json',
                                            cache: false,
                                            data: {
                                                url_keyword_id: id,
                                            },
                                            success: function (data) {
                                                if (data.res === 1) {
                                                    if (data.result === 'down') {
                                                        $('#url_pop_down_' + id).html('▼')
                                                        var down_count = $('#url_pop_down_count_' + id).html()
                                                        $('#url_pop_down_count_' + id).html(parseInt(down_count) + 1)

                                                        if ($('#url_pop_up_' + id).html() === '▲') {
                                                            $('#url_pop_up_' + id).html('△')
                                                            var up_count = $('#url_pop_up_count_' + id).html()
                                                            $('#url_pop_up_count_' + id).html(parseInt(up_count) - 1)
                                                        }

                                                    } else if (data.result === 'cancel') {
                                                        $('#url_pop_down_' + id).html('▽')
                                                        var down_count = $('#url_pop_down_count_' + id).html()
                                                        $('#url_pop_down_count_' + id).html(parseInt(down_count) - 1)
                                                    }
                                                }

                                            }
                                        })

                                    })
                                })

                                if (data.last === null) {
                                    $('#keyword_more_' + id).addClass('hidden')
                                    $('#last_url_keyword_' + id).html('')
                                } else {
                                    $('#keyword_more_' + id).removeClass('hidden')
                                    $('#last_url_keyword_' + id).html(data.last)
                                }
                            }

                        }
                    })

                    $('#keyword_more_' + id).click(function (e) {
                        e.preventDefault()
                        $.ajax({
                            url: '/re/url/keyword/', type: 'post', dataType: 'json', cache: false,
                            data: {
                                url_id: id,
                                last_id: $('#last_url_keyword_' + id).html(),
                            },
                            success: function (data) {
                                if (data.res === 1) {
                                    $.each(data.output, function (key, value) {
                                        var id = value.keyword_id
                                        var _keyword = ''
                                        var _register = ''
                                        var _up = ''
                                        var _down = ''
                                        if (value.register === 'true') {
                                            _register = '<span class="url_pop_reg" id="url_pop_reg_' + id + '">★</span>'
                                        }
                                        else {
                                            _register = '<span class="url_pop_reg" id="url_pop_reg_' + id + '">☆</span>'
                                        }
                                        if (value.up === 'true') {
                                            _up = '<a href=""><span class="url_pop_up" id="url_pop_up_' + id + '">▲</span></a>'
                                        }
                                        else {
                                            _up = '<a href=""><span class="url_pop_up" id="url_pop_up_' + id + '">△</span></a>'
                                        }

                                        if (value.down === 'true') {
                                            _down = '<a href=""><span class="url_pop_down" id="url_pop_down_' + id + '">▼</span></a>'
                                        }
                                        else {
                                            _down = '<a href=""><span class="url_pop_down" id="url_pop_down_' + id + '">▽</span></a>'
                                        }


                                        _keyword = '<span class="url_pop_keyword_wrapper">' +
                                            '<span class="url_pop_keyword">' + value.keyword + '</span>' +
                                            _register +
                                            '<span class="url_pop_reg_count" id="url_pop_reg_count_' + id + '">' + value.reg_count + '</span>' +
                                            _up +
                                            '<span class="url_pop_up_count" id="url_pop_up_count_' + id + '">' + value.up_count + '</span>' +
                                            _down +
                                            '<span class="url_pop_down_count" id="url_pop_down_count_' + id + '">' + value.down_count + '</span>' +
                                            '</span>'


                                        $('#keyword_list_' + con_id).append(_keyword)

                                        $('#url_pop_up_' + id).on('click', function (e) {
                                            e.preventDefault()

                                            if ($('#user_id').html() === '') {
                                                $('#modal_need_login_pop').modal('show')
                                                return false;
                                            }
                                            $.ajax({
                                                url: '/re/url/keyword/up/',
                                                type: 'post',
                                                dataType: 'json',
                                                cache: false,
                                                data: {
                                                    url_keyword_id: id,
                                                },
                                                success: function (data) {
                                                    if (data.res === 1) {
                                                        if (data.result === 'up') {
                                                            $('#url_pop_up_' + id).html('▲')
                                                            var up_count = $('#url_pop_up_count_' + id).html()
                                                            $('#url_pop_up_count_' + id).html(parseInt(up_count) + 1)

                                                            if ($('#url_pop_down_' + id).html() === '▼') {
                                                                $('#url_pop_down_' + id).html('▽')
                                                                var down_count = $('#url_pop_down_count_' + id).html()
                                                                $('#url_pop_down_count_' + id).html(parseInt(down_count) - 1)
                                                            }

                                                        } else if (data.result === 'cancel') {
                                                            $('#url_pop_up_' + id).html('△')
                                                            var up_count = $('#url_pop_up_count_' + id).html()
                                                            $('#url_pop_up_count_' + id).html(parseInt(up_count) - 1)
                                                        }
                                                    }

                                                }
                                            })
                                        })

                                        $('#url_pop_down_' + id).on('click', function (e) {
                                            e.preventDefault()
                                            if ($('#user_id').html() === '') {
                                                $('#modal_need_login_pop').modal('show')
                                                return false;
                                            }
                                            $.ajax({
                                                url: '/re/url/keyword/down/',
                                                type: 'post',
                                                dataType: 'json',
                                                cache: false,
                                                data: {
                                                    url_keyword_id: id,
                                                },
                                                success: function (data) {
                                                    if (data.res === 1) {
                                                        if (data.result === 'down') {
                                                            $('#url_pop_down_' + id).html('▼')
                                                            var down_count = $('#url_pop_down_count_' + id).html()
                                                            $('#url_pop_down_count_' + id).html(parseInt(down_count) + 1)

                                                            if ($('#url_pop_up_' + id).html() === '▲') {
                                                                $('#url_pop_up_' + id).html('△')
                                                                var up_count = $('#url_pop_up_count_' + id).html()
                                                                $('#url_pop_up_count_' + id).html(parseInt(up_count) - 1)
                                                            }

                                                        } else if (data.result === 'cancel') {
                                                            $('#url_pop_down_' + id).html('▽')
                                                            var down_count = $('#url_pop_down_count_' + id).html()
                                                            $('#url_pop_down_count_' + id).html(parseInt(down_count) - 1)
                                                        }
                                                    }

                                                }
                                            })

                                        })
                                    })

                                    if (data.last === null) {
                                        $('#keyword_more_' + id).addClass('hidden')
                                        $('#last_url_keyword_' + id).html('')
                                    } else {
                                        $('#keyword_more_' + id).removeClass('hidden')
                                        $('#last_url_keyword_' + id).html(data.last)
                                    }
                                }

                            }
                        })

                    })
                    $('#pop_menu_' + id).click(function (e) {
                        e.preventDefault()
                        $('#search_link_source').html('/url/' + id + '/')
                        $('#modal_pop_menu').modal('show')
                    })


                }
            }
        })


    })
}
$(function () {


})

$(function () {


    $("#modal_pop_menu").on("shown.bs.modal", function () {
        var source = $('#search_link_source').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + source;
        $('#modal_pop_menu_input').val(path).select();
    }).on("hidden.bs.modal", function () {
        $('#link_source').html('')
        $('#modal_pop_menu_input').val('')
    });

    $('#modal_pop_menu_copy').click(function (e) {
        e.preventDefault()
        var source = $('#search_link_source').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + source;
        $('#modal_pop_menu_input').val(path).select();
        document.execCommand('Copy')
    })
    $('#modal_pop_menu_locate').click(function (e) {
        e.preventDefault()
        var source = $('#search_link_source').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + source;
        location.href = path
    })
})
