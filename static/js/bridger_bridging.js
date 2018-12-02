$(function () {
    var height = $(window).height();
    $('.modal-body').css('max-height', height - 120);
    $(window).on('resize', function () {

        if ($(window).height() != height) {
            height = $(window).height();
            $('.modal-body').css('max-height', height - 120);
        }
    });
})
$(function () {
    if($('#user_id').html()!==$('#chosen_user_id').html()){
        if($('#bridge').hasClass('hidden')){
            $('#bridge').removeClass('hidden')
        }
    }

    $('#bridge').click(function (e) {
        e.preventDefault()
        if ($('#user_id').html() === '') {
            $('#modal_need_login_bridge').modal('show')
            return false;
        }
        $.ajax({
            url: '/re/bridge/add/', type: 'post', dataType: 'json', cache: false,
            data: {
                user_id: $('#chosen_user_id').html()
            },
            success: function (data) {
                if (data.result === 'true') {
                    $('#bridge_text').html('now bridging <span class="glyphicon glyphicon-ok"></span>')
                    var count_bridger = parseInt($('#count_bridger').html()) + 1
                    $('#count_bridger').html(count_bridger)
                } else {
                    $('#bridge_text').html('bridge')
                    var count_bridger = parseInt($('#count_bridger').html()) - 1
                    $('#count_bridger').html(count_bridger)
                }
            }
        })
    })

    $("#modal_bridging").on("shown.bs.modal", function () {
        var height = $(window).height();
        $('.modal-body').css('max-height', height - 120);
        $(window).on('resize', function () {
            if ($(window).height() != height) {
                height = $(window).height();
                $('.modal-body').css('max-height', height - 120);
            }
        });

        var chosen_user_id = $('#chosen_user_id').html()

        $.ajax({
            url: '/re/bridging/list/', type: 'post', dataType: 'json', cache: false,
            data: {
                user_id: $('#chosen_user_id').html(),
                next_user_id: $('#next_user_id').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    $.each(data.output, function (key, value) {
                        var appender = '<div class="modal_unit_wrapper"><a href="/' + value.username + '/">\n' +
                            '<img class="modal_img" src="' + value.photo + '">\n' +
                            '<span class="modal_username">' + value.username + '</span>\n' +
                            '</a></div>'
                        $('#modal_bridging_list').append(appender)
                    })
                }
                if (data.next === null) {
                    $('#modal_bridging_more').addClass('hidden')
                } else {
                    $('#modal_bridging_more').removeClass('hidden')
                }

            }
        })
    }).on("hidden.bs.modal", function () {
        $('#modal_bridging_list').empty()
        $('#next_user_id').html('')

    });

    $('#modal_bridging_more').click(function (e) {
        e.preventDefault()
        var chosen_user_id = $('#chosen_user_id').html()

        $.ajax({
            url: '/re/bridging/list/', type: 'post', dataType: 'json', cache: false,
            data: {
                user_id: $('#chosen_user_id').html(),
                next_user_id: $('#next_user_id').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    $.each(data.output, function (key, value) {
                        var appender = '<div class="modal_unit_wrapper"><a href="/' + value.username + '/">\n' +
                            '<img class="modal_img" src="' + value.photo + '">\n' +
                            '<span class="modal_username">' + value.username + '</span>\n' +
                            '</a></div>'
                        $('#modal_bridging_list').append(appender)
                    })
                }
                if (data.next === null) {
                    $('#next_user_id').html('')
                    $('#modal_bridging_more').addClass('hidden')
                } else {
                    $('#next_user_id').html(data.next)
                    $('#modal_bridging_more').removeClass('hidden')
                }

            }
        })
    })

    $("#modal_bridger").on("shown.bs.modal", function () {

        var height = $(window).height();
        $('.modal-body').css('max-height', height - 120);
        $(window).on('resize', function () {

            if ($(window).height() != height) {
                height = $(window).height();
                $('.modal-body').css('max-height', height - 120);
            }
        });
        var chosen_user_id = $('#chosen_user_id').html()

        $.ajax({
            url: '/re/bridger/list/', type: 'post', dataType: 'json', cache: false,
            data: {
                user_id: $('#chosen_user_id').html(),
                next_user_id: $('#next_user_id').html()
            },
            success: function (data) {
                console.log(data)
                if (data.res === 1) {
                    $.each(data.output, function (key, value) {
                        var appender = '<div class="modal_unit_wrapper"><a href="/' + value.username + '/">\n' +
                            '<img class="modal_img" src="' + value.photo + '">\n' +
                            '<span class="modal_username">' + value.username + '</span>\n' +
                            '</a></div>'
                        $('#modal_bridger_list').append(appender)
                    })
                }
                if (data.next === null) {
                    $('#next_user_id').html('')
                    $('#modal_bridger_more').addClass('hidden')
                } else {
                    $('#next_user_id').html(data.next)
                    $('#modal_bridger_more').removeClass('hidden')
                }

            }
        })
    }).on("hidden.bs.modal", function () {
        $('#modal_bridger_list').empty()
        $('#next_user_id').html('')
    });

    $('#modal_bridger_more').click(function (e) {
        e.preventDefault()
        var chosen_user_id = $('#chosen_user_id').html()

        $.ajax({
            url: '/re/bridger/list/', type: 'post', dataType: 'json', cache: false,
            data: {
                user_id: $('#chosen_user_id').html(),
                next_user_id: $('#next_user_id').html()
            },
            success: function (data) {
                console.log(data)
                if (data.res === 1) {
                    $.each(data.output, function (key, value) {
                        var appender = '<div class="modal_unit_wrapper"><a href="/' + value.username + '/">\n' +
                            '<img class="modal_img" src="' + value.photo + '">\n' +
                            '<span class="modal_username">' + value.username + '</span>\n' +
                            '</a></div>'
                        $('#modal_bridger_list').append(appender)
                    })
                }
                if (data.next === null) {
                    $('#next_user_id').html('')
                    $('#modal_bridger_more').addClass('hidden')
                } else {
                    $('#next_user_id').html(data.next)
                    $('#modal_bridger_more').removeClass('hidden')
                }

            }
        })
    })

    $('#count_bridging').click(function (e) {
        e.preventDefault()
        $('#modal_bridging').modal('show')
    })
    $('#count_bridger').click(function (e) {
        e.preventDefault()
        $('#modal_bridger').modal('show')
    })
})
