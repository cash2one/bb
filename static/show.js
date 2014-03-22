$("li").mouseover(function() {
    $.get("/hub_eval" + $(this).find("a").attr("href"), function(data) {
        $("li").attr("title", data);  // todo: $("li") is bad
    }, "text");
});
