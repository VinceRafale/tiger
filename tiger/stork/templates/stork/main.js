var swatchSet = {{ swatch_json|safe }},
    fontSet   = {{ font_json|safe }};
function setCss(styleTagSelector, css) {
    styleTag = $(styleTagSelector)[0];
    if (styleTag.styleSheet) {
        styleTag.styleSheet.cssText = css;
    } else {
        styleTag.innerHTML = css;
    }
}

function setColor(pickerSelector, styleTagSelector, inputSelector, cssTemplate, hex) {
    previewCss = "";
    if (cssTemplate instanceof Array) {
        for (i=0; i < cssTemplate.length; i++) {
            previewCss += cssTemplate[i] + hex + ";}";
        }
    } else {
        previewCss = cssTemplate + hex + ";}";
    }
    setCss(styleTagSelector, previewCss);
    $(inputSelector).val(hex);
    $(pickerSelector + ' div').css('backgroundColor', '#' + hex);
}

function addColorPicker(pickerSelector, styleTagSelector, inputSelector, cssTemplate) {
    $(pickerSelector).ColorPicker({
        onChange: function (hsb, hex, rgb) {
            setColor(pickerSelector, styleTagSelector, inputSelector, cssTemplate, hex);
            modified = true;
        }
    });
}
$(function () {
    var modified = false;

    // Ajax image upload handling
    $("#toolbar input[type=file]").change(function () {
        wrap = $(this).closest("form");
        wrap.find("p.spinner").fadeIn('fast');
        wrap[0].submit();
        modified = true;
    });
    $("div.remove a.remove").click(function () {
        form = $(this).closest("form");
        $.post($(this).attr("href"), form.find(":hidden").serialize(), function (data) {
            form.find("div.form").show();
            form.find("div.remove").hide();
            setCss(data.style_tag, data.css);
            if (data['delete']) {
                hiddenDelete = $("<input type='hidden' value='1' />");
                hiddenDelete.attr("name", data.component + '-delete');
                form.find("div.remove").append(hiddenDelete);
            }
        }, "json");
        return false;
    });
    $("#toolbar :checkbox").click(function () {
        checked = $(this).is(":checked");
        fieldName = $(this).attr("name");
        name = fieldName.substr(0, fieldName.length - "-tiling".length);
        $.post("/dashboard/stork/image/" + name + "/get/", $.param({tiling: checked || ''}), function (data) {
            setCss(data.style_tag, data.css);
        }, "json");
    });
    $("iframe").load(function () {
        dataString = window['imgjson'].document.getElementsByTagName('body')[0].innerHTML;
        if (!dataString)
            return;
        data = JSON.parse(dataString);
        setCss(data.style_tag, data.css);
        form = $("form." + data.component);
        form.find("p.spinner").fadeOut('slow', function () {
            form.find("div.form").hide();
            form.find("div.remove").show();
            form.find("div.remove a.view").attr("href", data.url);
            if (form.find("input[name$='stale']")) {
                form.find("input[name$='stale']").remove();
            }
        });
    });

    $.each(fontSet, function(i, data) {
        $(data.selector).change(function () {
            selected = $(this).val();
            css_url = data.link + '~' + selected + '.css';
            styleTag = data.styleTagId;
            $.get(css_url, function (data) {
                setCss(styleTag, data);
            }, "text");
            modified = true;
        });
    });
    
    for (i=0; i < swatchSet.length; i++) {
        addColorPicker(swatchSet[i][0], swatchSet[i][1], swatchSet[i][2], swatchSet[i][3]);
    }

    $("div.tab_content.css button.preview").click(function () {
        tab = $(this).closest("div.tab_content");
        styleTagId = tab.find("div").attr("rel");
        css = tab.find("textarea").val();
        setCss(styleTagId, css);
        modified = true;
    });

    $("div.tab_content.html button.html").click(function () {
        $(this).closest('form').submit();
    });

    $("div.tab_content.html button.revert").click(function () {
        htmlForm = $(this).closest('form');
        $(htmlForm).attr("action", $(this).attr("rel"));
        htmlForm.submit();
    });

    $("#save").click(function () {
        postData = $("#toolbar :input").not("[type='file']").serialize();
        $.post("/dashboard/stork/save/", postData, function (data) {
            window.location.href = '/dashboard/look/back/';
        }, "text");
        modified = false;
    });

    $("div.wrapper a").click(function () {
        if (modified) {
            c = confirm("You have unsaved style changes.  Click OK to abandon them or Cancel and then Save to save them.");
            if (!c) {
                return false;
            }
        }
    });
});
