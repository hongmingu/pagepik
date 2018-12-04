$(function () {
    $.ajax({
        url: '/re/home/', type: 'post', dataType: 'json', cache: false,
        data: {
            user_id: $('#user_id').html(),
            end_id: $('#end_id').html()
        },
        success: function (data) {
            console.log(data)

        }
    })

})