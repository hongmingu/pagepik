$(function () {

    $('#suobj_delete').click(function (e) {
        e.preventDefault()
        $.ajax({
            url: '/re/profile/suobj/delete/', type: 'post', dataType: 'json', cache: false,
            data: {
                suobj_id: $('#suobj_to_delete').html(),
            },
            success: function (data) {
                if (data.res === 1) {
                    $('#suobj_wrapper_with_modi_' + $('#suobj_to_delete').html()).replaceWith('<div>removed</div>')
                    $('#modal_suobj_delete').modal('hide')
                }
            }
        })

    })

    $("#modal_suobj_delete").on("shown.bs.modal", function () {

    }).on("hidden.bs.modal", function () {
        $('#suobj_to_delete').html('')
    })
});
$(function () {

    $.ajax({
        url: '/re/profile/suobj/', type: 'post', dataType: 'json', cache: false,
        data: {
            chosen_user_id: $('#chosen_user_id').html(),
            last_suobj_id: $('#last_suobj_id').html()
        },
        success: function (data) {
            var _modifier = ''
            var chosen_user_id = $('#chosen_user_id').html()
            var user_id = $('#user_id').html()
            $.each(data.output, function (key, value) {

                if (chosen_user_id === user_id) {
                    _modifier = '<div align="right"><a href="/update/url/' + value.id + '/"><span class="user_profile_post_update">update</span></a><span>  </span><a href=""><span class="profile_suobj_delete">delete</span></a></div>'
                }
                var appender = '<div id="suobj_wrapper_with_modi_' + value.id + '">' +
                    '<div class="row div_base" id="suobj_wrapper_' + value.id + '">' +
                    '<script defer>' +
                    '    suobj_populate("' + value.id + '")' +
                    '<' + '/script>' +
                    '</div>' + _modifier +
                    '</div>'
                var jq_appender = $(appender)
                jq_appender.find('.profile_suobj_delete').on('click', function (e) {
                    e.preventDefault()
                    $('#suobj_to_delete').html(value.id)
                    $('#modal_suobj_delete').modal('show')
                })
                $('#user_profile_suobj_list').append(jq_appender)
            })
            if (data.last === null) {
                $('#profile_more_load').addClass('hidden')
            } else {
                $('#profile_more_load').removeClass('hidden')
            }

        }
    })
})