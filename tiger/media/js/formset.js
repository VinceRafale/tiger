// provides lists of names for form inputs
var formSnippets = {
    'price-points': ["description", "price"],
    'extras': ["name", "price"],
    'side-groups': ["name", "price"],
    'sides': ["name", "price"],
};

function getForm(addAnchor) {
    initial = {};
    action = $(addAnchor).attr("rel");
    if (arguments.length > 1) {
        initial = arguments[1];
        action = arguments[2];
    }
    fieldKey = $(addAnchor).attr("id") || 'sides';
    inputs = formSnippets[fieldKey];
    fakeForm = '<li class="form' + ((arguments[1]) ? ' populated' : '') + '">';
    $.each(inputs, function () {
        titleCase = this[0].toUpperCase() + this.slice(1);
        fakeForm += '<label for="' + this + '">' + titleCase + ' <input type="text" id="id_' + this + '" name="' + this + '" value="' + (initial[this] || '') + '" /></label>';
    });
    fakeForm += '<a class="inline-save" href="#" rel="' + action + '">Save</a> <a class="inline-cancel" href="#">Cancel</a><div class="clear"></div></li>';
    return fakeForm;
}

$(function () {
    $("a.submit").click(function () {
        $("form").submit();
    });

    $("#price-points").click(function () {
        listTag = $(this).prev();
        if (!$(listTag).find("li.form").length) {
            $(listTag).append($(getForm(this)));
        } else {
            $(listTag).find("input:first").focus();
        }
        return false;
    });

    $("#extras").click(function () {
        listTag = $(this).prev();
        if (!$(listTag).find("li.form").length) {
            $(listTag).append($(getForm(this)));
        } else {
            $(listTag).find("input:first").focus();
        }
        return false;
    });

    $("#side-groups").click(function () {
        trgt = this;
        $.post($(this).attr("rel"), {}, function (data) {
            if (data['success']) {
                markup = $('<li><ul>' + getForm(trgt) + '</ul>' + data['row'] + '</li>');
                $("ul.group-wrap").append(markup); 
                $("ul.group-wrap > li.empty").remove();
            }
        }, "json");
        return false;
    });

    $("a.inline-cancel").live("click", function () {
        if ($(this).parent().hasClass("populated")) {
            $(this).parent().prev().show();
        }
        $(this).parent().slideUp("fast", function () { $(this).remove(); });
            
        return false;
    });

    $("a.inline-save").live("click", function () {
        trgt = this;
        action = $(trgt).attr("rel");
        params = $(this).parent().find(":input").serialize();
        selector = '[rel="' + action + '"]';
        $.post(action, params, function (data) {
            errors = data['errors'];
            if (errors) {
                $(trgt).parent().find(":input").each(function () {
                    if (errors[$(this).attr("name")]) {
                        $(this).addClass("error");
                        if (!$(this).next().hasClass("msg")) {
                            $(this).after('<span class="msg">' + errors[$(this).attr("name")][0] + '</span>');
                        }
                    } else {
                        $(this).removeClass("error");
                        $(this).parent().find('span.msg').remove();
                    }
                });
            } else {
                $(trgt).parent().replaceWith(data['new_row']);
                $(selector).prev().find("li.empty").remove();
            }
        }, "json");
        return false;
    });

    $("a.edit").live("click", function () {
        trgt = this;
        addAnchor = $(this).closest("div").find("a.add");
        $.get($(this).attr("rel"), {}, function (data) {
            $(trgt).parent().parent().after(getForm(addAnchor, data, $(trgt).attr("rel")));
            $(trgt).parent().parent().hide();
        }, "json");
        return false;
    });

    $("a.delete").live("click", function () {
        c = confirm('Are you sure you want to delete this item?  This action cannot be undone.');
        if (c) {
            trgt = this;
            action = $(this).attr("rel");
            $.post(action, $.param({delete: true}), function (data) {
                if (data['deleted']) {
                    selector = '[rel="' + action + '"]';
                    containingList = $(selector).parent().parent().parent();
                    $(selector).parent().parent().remove();
                    if (!$(containingList).children().length) {
                        $(containingList).append('<li class="empty">No ' + $(containingList).closest("div").find("h3").text().toLowerCase() + ' defined.</li>');
                    }
                } else {
                    $(selector).insertAfter('<span class="fail">An error occurred.</span>');
                    $("span.fail").delay(1500).fadeOut("fast", function () { $(this).remove(); });
                }
            }, "json");
        }
        return false;
    });

    $("ul.group-wrap a.add").live("click", function () {
        nestedList = $(this).prev();
        if (!$(nestedList).find("li.form").length) {
            $(nestedList).append($(getForm(this)));
        } else {
            $(nestedList).find("input:first").focus();
        }
        return false;
    });
});

