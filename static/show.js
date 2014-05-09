$(document).ready(function() {
    $("ul li a").one("mouseover", function(event) {
        var $a = $(this);
        console.log(event);
        if (!$a.attr("title")) {
            $.get("/hub_eval" + $a.attr("href"), function(data) {
                $a.attr("title", data);
            }, "text");
        }
    });
});
