$(function () {
    var openedBy;

    $("a.chooser").click(function () {
        $.fancybox({
            'href': $(this).attr("href")
        });
        openedBy = this;
        return false;
    });
    $("a.closing-link").live("click", function () {
        $.fancybox.close();
    });
    $("#images a").live("click", function () {
        var imageId = $(this).attr("id"),
            selectedImg = $(this).children()[0],
            chooser = $(openedBy).closest("div.img-chooser-wrap"),
            chooserLink = chooser.find("a.chooser");
        $.fancybox.close();
        chooser.find("input.chooser-input").val(imageId);
        chooser.find("img").attr("src", selectedImg.src);
        if (chooserLink.text() == 'Add') {
            chooserLink.text('Change');
            chooserLink.after(' <a href="#" class="chooser-remove">Remove</a>');
        }
        return false;
    });
    $("a.chooser-remove").live("click", function () {
        var chooser = $(this).closest("div.img-chooser-wrap"),
            chooserLink = chooser.find("a.chooser");
        chooser.find("input.chooser-input").val('');
        chooser.find("img").attr('src', '/static/img/blank.jpg');
        $(this).prev().text("Add");
        $(this).remove();
        return false;
    });
});
