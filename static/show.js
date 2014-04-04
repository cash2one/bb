$(document).ready(function() {
        $("a").mouseover(function() {
            var a = $(this);
            $.get("/hub_eval" + a.attr("href"), function(data) {
                a.attr("title", data);
                }, "text");
            });
        });
