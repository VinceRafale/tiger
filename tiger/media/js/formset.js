// provides lists of names for form inputs
var formSnippets = {
    'price-points': ["description", "price", "schedule"],
    'extras': ["name", "price"],
    'side-groups': ["name", "price"],
    'sides': ["name", "price"],
};

function getForm(addAnchor) {
    initial = {};
    action = $(addAnchor).attr("rel");
    if (arguments.length > 1) {
        initial = arguments[1] || {};
        action = arguments[2] || action;
        noPopulate = arguments[3];
    }
    fieldKey = $(addAnchor).attr("id") || 'sides';
    inputs = formSnippets[fieldKey];
    fakeForm = '<li class="form' + ((arguments[1] && !noPopulate) ? ' populated' : '') + '">';
    $.each(inputs, function () {
        titleCase = this.charAt(0).toUpperCase() + this.slice(1);
        fakeForm += '<label for="' + this + '">' + titleCase + ' ';
        if (this != 'schedule') {
            fakeForm += ' <input type="text" id="id_' + this + '" name="' + this + '" value="' + (initial[this] || '') + '" />';
        } else {
            fakeForm += '<select name="schedule">';
            current = initial[this] || '';
            $("#id_schedule").children().each(function () {
                val = $(this).val();
                if (val == current) {
                    selected = true;
                } else {
                    selected = false;
                }
                fakeForm += '<option ' + (selected ? 'selected ' : '') + 'value="' + val + '">' + $(this).text() + '</option>';
            })
            fakeForm += '</select>';
        }
        fakeForm += '</label>';
    });
    fakeForm += '<a class="inline-save" href="#" rel="' + action + '">Save</a> <a class="inline-cancel" href="#">Cancel</a><div class="clear"></div></li>';
    return fakeForm;
}

$(function () {
    $("a.submit").click(function () {
        $("form").submit();
    });

    $("#price-points").click(function () {
        listTag = $("#price-points-list");
        if (!$(listTag).find("li.form").length) {
            initial = {};
            if (!$(listTag).children().not('.empty').length) {
                initial = {description: "default"};
            }
            $(listTag).append($(getForm(this, initial, null, true)));
        } else {
            $(listTag).find("input:first").focus();
        }
        return false;
    });

    $("#extras").click(function () {
        listTag = $("#extras-list");
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
                markup = $('<li><ul class="item-container">' + getForm(trgt, null, data['add_side_url']) + '</ul>' + data['new_row'] + '</li>');
                $("ul.group-wrap").append(markup); 
                $("ul.group-wrap > li.empty").remove();
            }
        }, "json");
        return false;
    });

    $("ul.group-wrap a.add").live("click", function () {
        listTag = $(this).prev();
        if (!$(listTag).find("li.form").length) {
            $(listTag).append($(getForm(this)));
        } else {
            $(listTag).find("input:first").focus();
        }
        return false;
    });

    $("a.delete-group").live("click", function () {
        c = confirm('Are you sure you want to delete this group?  This action cannot be undone.');
        if (c) {
            trgt = this;
            action = $(this).attr("rel");
            $.post(action, $.param({'delete': true}), function (data) {
                if (data['deleted']) {
                    selector = '[rel="' + action + '"]';
                    containingList = $(selector).parent().parent();
                    $(selector).parent().remove();
                    if (!$(containingList).children().length) {
                        $(containingList).append('<li class="empty">No choice groups defined.</li>');
                    }
                } else {
                    $(selector).insertAfter('<span class="fail">An error occurred.</span>');
                    $("span.fail").delay(1500).fadeOut("fast", function () { $(this).remove(); });
                }
            }, "json");
        }
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
        listTag = $(this).parent().parent();
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
                if ($(trgt).parent().hasClass("populated")) {
                    $(trgt).parent().prev().remove();
                }
                $(trgt).parent().replaceWith(data['new_row']);
                $(listTag).find("li.empty").remove();
                $(listTag).trigger('changeLength');
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
        trgt = this;
        action = $(this).attr("rel");
        selector = '[rel="' + action + '"]';
        containingList = $(selector).parent().parent().parent();
        sectionNamePlural = $(containingList).closest("div").find("h3")[0] 
                            .childNodes[0].textContent // can't use .text() because of anchor
                            .replace(/\s+$/, '') // strip trailing whitespace
                            .toLowerCase();
        sectionNameSingular = sectionNamePlural.substring(0, sectionNamePlural.length - 1);
        c = confirm('Are you sure you want to delete this ' + sectionNameSingular + '?  This action cannot be undone.');
        if (c) {
            $.post(action, $.param({'delete': true}), function (data) {
                if (data['deleted']) {
                    $(selector).parent().parent().remove();
                    if (!$(containingList).children().length) {
                        $(containingList).append('<li class="empty">No ' + sectionNamePlural + ' defined.</li>');
                    }
                    $(containingList).trigger('changeLength');
                } else {
                    $(selector).insertAfter('<span class="fail">An error occurred.</span>');
                    $("span.fail").delay(1500).fadeOut("fast", function () { $(this).remove(); });
                }
            }, "json");
        }
        return false;
    });

    $('ul.group-wrap ul.item-container').live('changeLength', function () {
        upOne = $(this).parent();
        if ($(this).children("li").not(".empty").length == 1) {
            if (!$(this).find("span.errorlist").length) {
                $(upOne).prepend('<span class="errorlist">Choice sets must contain two or more items before they will appear to customers.</span>');
            }
        } else {
            $(upOne).find("span.errorlist").remove();
        }
    });

});

