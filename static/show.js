$(document).ready(function() {
    $("ul li a").one("mouseover", function(event) {
        var $a = $(this);
        $.ajax({
            url: "/hub_eval" + $a.attr("href"),
            dataType: "text",
            success: function(data) {
                $a.attr("title", data);
            },
        });
    });
});
