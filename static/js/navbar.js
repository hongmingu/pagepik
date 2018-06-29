    $(document).ready(function () {
        var width = $(window).width();
        if (!(width>=768)){
            if(!$("#nav_div_ul_li_search").length){
                $("#nav_div_ul_li_bsearch").after('<li id="nav_div_ul_li_search"><a class="padding_15_i" href="#" id="nav_div_ul_li_a_search"><i class="glyphicon glyphicon-search"></i></a></li>')
                $("#nav_div_ul_li_a_search").click(function () {
                   if ($("#nav_search").length) {
                       $("#nav_search").remove();
                   }
                   else {
                    $('body').append('<nav class="navbar navbar-default navbar-fixed-top navbar_search_base top_50" id="nav_search">\n' +
                        '    <div class="container-fluid padding_right_0 padding_left_0 desktop_display_none">\n' +
                        '        <form class="navbar-form navbar_search_form_base width_100_i margin_auto">\n' +
                        '        <div class="input-group input-group-sm">\n' +
                        '            <input class="form-control" placeholder="Search" id="searchbar" type="text">\n' +
                        '            <div class="input-group-btn">\n' +
                        '                <i class="btn btn-default"><i class="glyphicon glyphicon-search"></i>\n' +
                        '                </i>\n' +
                        '            </div>\n' +
                        '        </div>\n' +
                        '        </form>\n' +
                        '    </div>\n' +
                        '</nav>')
                   }
               });
            }
        }

        $(window).on('resize', function(){
            if($(this).width() != width){
                width = $(this).width();
                console.log(width);
                if(width>=768){
                     if($("#nav_search").length){
                         $("#nav_search").remove()
                     }
                     if($("#nav_div_ul_li_search").length){
                         $("#nav_div_ul_li_search").remove()
                     }
                }
                else {
                    if(!$("#nav_div_ul_li_search").length){
                        $("#nav_div_ul_li_bsearch").after('<li id="nav_div_ul_li_search"><a class="padding_15_i" href="#" id="nav_div_ul_li_a_search"><i class="glyphicon glyphicon-search"></i></a></li>\n')
                        $("#nav_div_ul_li_a_search").click(function () {
                           if ($("#nav_search").length) {
                               $("#nav_search").remove();
                           }
                           else {
                              $('body').append('<nav class="navbar navbar-default navbar-fixed-top navbar_search_base top_50" id="nav_search">\n' +
                                  '    <div class="container-fluid padding_right_0 padding_left_0 desktop_display_none">\n' +
                                  '        <form class="navbar-form navbar_search_form_base width_100_i margin_auto">\n' +
                                  '        <div class="input-group input-group-sm">\n' +
                                  '            <input class="form-control" placeholder="Search" id="searchbar" type="text">\n' +
                                  '            <div class="input-group-btn">\n' +
                                  '                <i class="btn btn-default"><i class="glyphicon glyphicon-search"></i>\n' +
                                  '                </i>\n' +
                                  '            </div>\n' +
                                  '        </div>\n' +
                                  '        </form>\n' +
                                  '    </div>\n' +
                                  '</nav>')
                           }
                       });
                    }
                }
            }
        });

  // do something here
        //$("#a_search_modal").click(function () {
        //    $("#div_modal_search").modal();
        //
        //});
    });