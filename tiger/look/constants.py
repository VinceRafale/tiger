FONT_ARIAL = 'Frutiger, "Frutiger Linotype", Univers, Calibri, "Gill Sans", "Gill Sans MT", "Myriad Pro", Myriad, "DejaVu Sans Condensed", "Liberation Sans", "Nimbus Sans L", Tahoma, Geneva, "Helvetica Neue", Helvetica, Arial, sans-serif'
FONT_GARAMOND = '"Palatino Linotype", Palatino, Palladio, "URW Palladio L", "Book Antiqua", Baskerville, "Bookman Old Style", "Bitstream Charter", "Nimbus Roman No9 L", Garamond, "Apple Garamond", "ITC Garamond Narrow", "New Century Schoolbook", "Century Schoolbook", "Century Schoolbook L", Georgia, serif'
FONT_GEORGIA = 'Constantia, "Lucida Bright", Lucidabright, "Lucida Serif", Lucida, "DejaVu Serif", "Bitstream Vera Serif", "Liberation Serif", Georgia, serif'
FONT_IMPACT = 'Impact, Haettenschweiler, "Franklin Gothic Bold", Charcoal, "Helvetica Inserat", "Bitstream Vera Sans Bold", "Arial Black", sans-serif'
FONT_MONOSPACE = 'Consolas, "Andale Mono WT", "Andale Mono", "Lucida Console", "Lucida Sans Typewriter", "DejaVu Sans Mono", "Bitstream Vera Sans Mono", "Liberation Mono", "Nimbus Mono L", Monaco, "Courier New", Courier, monospace'
FONT_TIMES = 'Cambria, "Hoefler Text", Utopia, "Liberation Serif", "Nimbus Roman No9 L Regular", Times, "Times New Roman", serif'
FONT_TREBUCHET = '"Segoe UI", Candara, "Bitstream Vera Sans", "DejaVu Sans", "Bitstream Vera Sans", "Trebuchet MS", Verdana, "Verdana Ref", sans-serif'
FONT_VERDANA = 'Corbel, "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", "DejaVu Sans", "Bitstream Vera Sans", "Liberation Sans", Verdana, "Verdana Ref", sans-serif'

FONT_CHOICES = (
    (FONT_ARIAL, 'Arial'),
    (FONT_GARAMOND, 'Garamond'),
    (FONT_GEORGIA, 'Georgia'),
    (FONT_IMPACT, 'Impact'),
    (FONT_MONOSPACE, 'Monospace'),
    (FONT_TIMES, 'Times New Roman'),
    (FONT_TREBUCHET, 'Trebuchet'),
    (FONT_VERDANA, 'Verdana'),
)

DEFAULT_CSS = """
#masthead h2 {
    font-size:37px;
    margin:23px 0;
}

#menuWrap {
    border-top:3px solid #301613;
    border-bottom:4px solid #301613;
    margin-bottom:20px;
    height:34px;
}

#mainWrap, #sidebarWrap {
    border:1px solid rgba(0,0,0,0.25);
    -moz-border-radius:5px;
    -webkit-border-radius:5px;
    border-radius:5px;
}

#main, #sidebar {
    margin:12px;
}

#newsitems li, #menuitems li{
    -moz-border-radius:5px;
    -webkit-border-radius:5px;
    border-radius:5px;
}

#menu a, #menuitems li a {font-size:14px; font-weight:bold; text-transform:uppercase; text-decoration:none; }
a.lightlink:hover {color:#fff;}

a#viewCart {margin-right:12px;}
a.add.top {font-weight:bold; text-transform:uppercase; text-decoration:none; margin-bottom:10px;}
#orderForm {
    border:none;
    padding:20px;
    margin-bottom:15px;
}
#orderForm h3 {
    margin-bottom:5px;
}
form input {
    border: 1px grey solid;
}

#orderPreview td {border-top:1px grey solid;}
#orderPreview td ul {margin-bottom:0;}
#orderPreview td.remove, #orderPreview tr.total td.remove {border-top:none;}
a.button:hover {text-decoration:underline;}
form.send label {display:block;}
.footer {background-color:black; color:white;}
#masthead h2 {
    font-size:37px;
    margin:23px 0;
}

#menuWrap {
    border-top:3px solid #301613;
    border-bottom:4px solid #301613;
    margin-bottom:20px;
    height:34px;
}

#mainWrap, #sidebarWrap {
    border:1px solid rgba(0,0,0,0.25);
    -moz-border-radius:5px;
    -webkit-border-radius:5px;
    border-radius:5px;
}

#main, #sidebar {
    margin:12px;
}

#menuitems li{
    -moz-border-radius:5px;
    -webkit-border-radius:5px;
    border-radius:5px;
}

#menu a, #menuitems li a {font-size:14px; font-weight:bold; text-transform:uppercase; text-decoration:none; }
a.lightlink:hover {color:#fff;}

a#viewCart {margin-right:12px;}
a.add.top {font-weight:bold; text-transform:uppercase; text-decoration:none; margin-bottom:10px;}
#orderForm {
    border:none;
    padding:20px;
    margin-bottom:15px;
}
#orderForm h3 {
    margin-bottom:5px;
}
form input {
    border: 1px grey solid;
}

#orderPreview td {border-top:1px grey solid;}
#orderPreview td ul {margin-bottom:0;}
#orderPreview td.remove, #orderPreview tr.total td.remove {border-top:none;}
a.button:hover {text-decoration:underline;}
form.send label {display:block;}
.footer {background-color:black; color:white;}

#masthead h2 {
    font-size:37px;
    margin:23px 0;
}

#menuWrap {
    border-top:3px solid #301613;
    border-bottom:4px solid #301613;
    margin-bottom:20px;
    height:34px;
}

#mainWrap, #sidebarWrap {
    border:1px solid rgba(0,0,0,0.25);
    -moz-border-radius:5px;
    -webkit-border-radius:5px;
    border-radius:5px;
}

#main, #sidebar {
    margin:12px;
}

#menuitems li{
    -moz-border-radius:5px;
    -webkit-border-radius:5px;
    border-radius:5px;
}

#menu a, #menuitems li a {font-size:14px; font-weight:bold; text-transform:uppercase; text-decoration:none; }
a.lightlink:hover {color:#fff;}

a#viewCart {margin-right:12px;}
a.add.top {font-weight:bold; text-transform:uppercase; text-decoration:none; margin-bottom:10px;}
#orderForm {
    border:none;
    padding:20px;
    margin-bottom:15px;
}
#orderForm h3 {
    margin-bottom:5px;
}
form input {
    border: 1px grey solid;
}

#orderPreview td {border-top:1px grey solid;}
#orderPreview td ul {margin-bottom:0;}
#orderPreview td.remove, #orderPreview tr.total td.remove {border-top:none;}
a.button:hover {text-decoration:underline;}
form.send label {display:block;}
.footer {background-color:black; color:white;}
#orderPreview tr.total td {border-top:4px solid;}
#submit, #pay {
    border:none;
    float:right;
}
a.add, #submit, #pay {
    -moz-border-radius:4px;
    -webkit-border-radius:4px;
    padding:4px 8px;
}
a.button {font-size:16px; padding:4px; text-decoration:none;
-moz-border-radius:5px;
-webkit-border-radius:5px;
}
"""


DEFAULT_PRE_BASE = """
<div class="wrapper">
    <div id="masthead">
        <div class="container_12">
            <div id="menu" class="grid_8">
            {% block logo %}{% endblock %}
            </div>
            <div id="search" class="grid_4">
            <h4>Menu search</h4>
            {% block search %}{% endblock %}
            </div>
        </div> 
    </div>
    <div id="menuWrap">
        <div class="container_12">
            <div id="menu" class="grid_8">
            {% block menu %}{% endblock %}
            </div>
            <div class="grid_4">
            </div>
        </div> 
    </div>
    <div id="content" class="container_12">
        <div id="mainWrap" class="grid_8 alpha">
        <div id="main">
        {% block messages %}{% endblock %}

        {% block content %}{% endblock %}
        </div>
        </div>
        <div id="sidebarWrap" class="grid_4 omega">
        <div id="sidebar">
            {% block cart %}{% endblock %}

            {% block sections %}{% endblock %}

            {% block contact %}{% endblock %}

            {% block pdf %}{% endblock %}

            {% block social %}{% endblock %}

            {% block mail %}{% endblock %}
        </div>
        </div>
    </div>
<div class="shim"></div>
</div>
<div class="footer">
    <div class="container_12">
        {% block footer %}{% endblock %}
    </div> 
</div>
"""

TEMPLATE_TAG_ESCAPES = (
    ('{%', '{% templatetag openblock %}'),
    ('%}', '{% templatetag closeblock %}'),
    ('{{', '{% templatetag openvariable %}'),
    ('}}', '{% templatetag closevariable %}'),
    ('{#', '{% templatetag opencomment %}'),
    ('#}', '{% templatetag closecomment %}'),
)

REQUIRED_BLOCKS = (
    'logo',
    'search',
    'menu',
    'content',
    'messages',
    'cart',
    'sections',
    'contact',
    'pdf',
    'social',
    'mail',
    'footer',
)
