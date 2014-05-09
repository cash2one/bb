$(document).ready(function() {
    $("ul").children().children().on("mouseover", function() {
        var a = $(this);
        if (!a.attr("title")) {
            a.off("mouseover");
            $.get("/hub_eval" + a.attr("href"), function(data) {
                a.attr("title", data);
            }, "text");
        }
    });
});
