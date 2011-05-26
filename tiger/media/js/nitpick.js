(function() {
  var ColorMath, Proxy, template;
  var __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  }, __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  ColorMath = (function() {
    function ColorMath() {}
    ColorMath.hexToRGB = function(hex) {
      hex = parseInt(((hex.indexOf('#')) > -1 ? hex.substring(1) : hex), 16);
      return {
        r: hex >> 16,
        g: (hex & 0x00FF00) >> 8,
        b: hex & 0x0000FF
      };
    };
    ColorMath.hexToHSB = function(hex) {
      console.log(this.hexToRGB(hex));
      return this.rgbToHSB(this.hexToRGB(hex));
    };
    ColorMath.rgbToHSB = function(rgb) {
      var delta, hsb, max, min;
      hsb = {
        h: 0,
        s: 0,
        b: 0
      };
      min = Math.min(rgb.r, rgb.g, rgb.b);
      max = Math.max(rgb.r, rgb.g, rgb.b);
      delta = max - min;
      hsb.b = max;
      hsb.s = max !== 0 ? 255 * delta / max : 0;
      if (hsb.s !== 0) {
        if (rgb.r === max) {
          hsb.h = (rgb.g - rgb.b) / delta;
        } else if (rgb.g === max) {
          hsb.h = 2 + (rgb.b - rgb.r) / delta;
        } else {
          hsb.h = 4 + (rgb.r - rgb.g) / delta;
        }
      } else {
        hsb.h = -1;
      }
      hsb.h *= 60;
      if (hsb.h < 0) {
        hsb.h += 360;
      }
      hsb.s *= 100 / 255;
      hsb.b *= 100 / 255;
      return hsb;
    };
    ColorMath.hsbToRGB = function(hsb) {
      var h, rgb, s, t1, t2, t3, v;
      rgb = {};
      h = Math.round(hsb.h);
      s = Math.round(hsb.s * 255 / 100);
      v = Math.round(hsb.b * 255 / 100);
      if (s === 0) {
        rgb.r = rgb.g = rgb.b = v;
      } else {
        t1 = v;
        t2 = (255 - s) * v / 255;
        t3 = (t1 - t2) * (h % 60) / 60;
        if (h === 360) {
          h = 0;
        }
        if (h < 60) {
          rgb.r = t1;
          rgb.b = t2;
          rgb.g = t2 + t3;
        } else if (h < 120) {
          rgb.g = t1;
          rgb.b = t2;
          rgb.r = t1 - t3;
        } else if (h < 180) {
          rgb.g = t1;
          rgb.r = t2;
          rgb.b = t2 + t3;
        } else if (h < 240) {
          rgb.b = t1;
          rgb.r = t2;
          rgb.g = t1 - t3;
        } else if (h < 300) {
          rgb.b = t1;
          rgb.g = t2;
          rgb.r = t2 + t3;
        } else if (h < 360) {
          rgb.r = t1;
          rgb.g = t2;
          rgb.b = t1 - t3;
        } else {
          rgb.r = 0;
          rgb.g = 0;
          rgb.b = 0;
        }
      }
      return {
        r: Math.round(rgb.r),
        g: Math.round(rgb.g),
        b: Math.round(rgb.b)
      };
    };
    ColorMath.hsbToHex = function(hsb) {
      return this.rgbToHex(this.hsbToRGB(hsb));
    };
    ColorMath.rgbToHex = function(rgb) {
      var hex;
      hex = [rgb.r.toString(16), rgb.g.toString(16), rgb.b.toString(16)];
      $.each(hex, function(nr, val) {
        if (val.length === 1) {
          return hex[nr] = '0' + val;
        }
      });
      return hex.join('');
    };
    return ColorMath;
  })();
  template = "<div class=\"colorpicker_nav\">\n    <a class=\"colorpicker_accept\" href=\"#\">&#x2714;</a>\n    <a class=\"colorpicker_cancel\" href=\"#\">&#x2718;</a>\n</div>\n<div class=\"colorpicker_color\" style=\"background-color: rgb(255, 0, 0); \">\n    <div>\n        <div></div>\n    </div>\n    <div class=\"alpha_channel\"></div>\n</div>\n\n<div class=\"colorpicker_hue\">\n    <div style=\"top: 150px; \">\n    </div>\n</div>\n\n<div class=\"colorpicker_fields\">\n    <div class=\"rgb_row\">\n        <div class=\"colorpicker_rgb_r\">\n        <label>R</label>\n        <input class=\"rgb\" type=\"text\" maxlength=\"3\" size=\"3\" value=\"<%= r %>\" />\n        </div>\n        <div class=\"colorpicker_rgb_g\">\n        <label>G</label>\n        <input class=\"rgb\" type=\"text\" maxlength=\"3\" size=\"3\" value=\"<%= g %>\" />\n        </div>\n        <div class=\"colorpicker_rgb_b\">\n        <label>B</label>\n        <input class=\"rgb\" type=\"text\" maxlength=\"3\" size=\"3\" value=\"<%= b %>\" />\n        </div>\n        <div class=\"colorpicker_rgb_a\">\n        <label>A</label>\n        <input class=\"rgb\" type=\"text\" maxlength=\"3\" size=\"3\" value=\"<%= a %>\" /><label>%</label>\n        </div>\n    </div>\n\n    <div class=\"hex_row\">\n        <div class=\"button_wrap\">\n        <a href=\"#\"></a>\n        </div>\n        <div>\n            <label>#</label>\n            <input class=\"hex\" type=\"text\" maxlength=\"6\" size=\"6\" value=\"<%= hex %>\">\n        </div>\n    </div>\n\n    </div>\n</div>";
  Proxy = (function() {
    __extends(Proxy, Backbone.Events);
    function Proxy() {
      Proxy.__super__.constructor.apply(this, arguments);
    }
    return Proxy;
  })();
  this.ColorPicker = (function() {
    __extends(ColorPicker, Backbone.View);
    function ColorPicker() {
      this.clearOpacity = __bind(this.clearOpacity, this);
      this.changeAlpha = __bind(this.changeAlpha, this);
      this.upSelector = __bind(this.upSelector, this);
      this.moveSelector = __bind(this.moveSelector, this);
      this.downSelector = __bind(this.downSelector, this);
      this.upHue = __bind(this.upHue, this);
      this.moveHue = __bind(this.moveHue, this);
      this.downHue = __bind(this.downHue, this);
      this.change = __bind(this.change, this);
      this.setHex = __bind(this.setHex, this);
      this.setRGB = __bind(this.setRGB, this);
      this.getRGB = __bind(this.getRGB, this);
      this.setHue = __bind(this.setHue, this);
      this.setPalette = __bind(this.setPalette, this);
      this.render = __bind(this.render, this);
      this.blur = __bind(this.blur, this);
      this.accept = __bind(this.accept, this);
      this.cancel = __bind(this.cancel, this);
      this.close = __bind(this.close, this);
      this.open = __bind(this.open, this);
      ColorPicker.__super__.constructor.apply(this, arguments);
    }
    ColorPicker.prototype.tagName = "div";
    ColorPicker.prototype.className = "colorpicker";
    ColorPicker.prototype.events = {
      "mousedown div.colorpicker_hue": "downHue",
      "mousedown div.colorpicker_color": "downSelector",
      "change input": "change",
      "keyup div.colorpicker_rgb_a input": "changeAlpha",
      "click div.button_wrap a": "clearOpacity",
      "click a.colorpicker_cancel": "cancel",
      "click a.colorpicker_accept": "accept"
    };
    ColorPicker.prototype.onChange = function() {};
    ColorPicker.prototype.onCancel = function() {};
    ColorPicker.prototype.onAccept = function() {};
    ColorPicker.prototype.initialize = function() {
      var a, b, button, g, r, _ref;
      _ref = this.options, r = _ref.r, g = _ref.g, b = _ref.b, a = _ref.a, button = _ref.button;
      this.hsb = ColorMath.rgbToHSB({
        r: r,
        g: g,
        b: b
      });
      this.original_hsb = _.clone(this.hsb);
      this.original_alpha = this.alpha = a;
      $(button).click(this.open);
      this.render();
      this.$("div.colorpicker_rgb_a input").val(a).trigger("keyup");
      $("body").append(this.el);
      this.close();
      return Proxy.bind("open", __bind(function(sender) {
        if (this.open && sender !== this) {
          return this.cancel(true);
        }
      }, this));
    };
    ColorPicker.prototype.open = function(e) {
      var left, m, pos, target, top, viewPort;
      if (e) {
        e.preventDefault();
      }
      target = e.target;
      pos = $(target).offset();
      m = document.compatMode === 'CSS1Compat';
      viewPort = {
        l: window.pageXOffset || (m ? document.documentElement.scrollLeft : document.body.scrollLeft),
        t: window.pageYOffset || (m ? document.documentElement.scrollTop : document.body.scrollTop),
        w: window.innerWidth || (m ? document.documentElement.clientWidth : document.body.clientWidth),
        h: window.innerHeight || (m ? document.documentElement.clientHeight : document.body.clientHeight)
      };
      top = pos.top + target.offsetHeight;
      left = pos.left;
      if (top + 175 > viewPort.t + viewPort.h) {
        top -= target.offsetHeight + 175;
      }
      if (left + 320 > viewPort.l + viewPort.w) {
        left -= 320;
      }
      $(this.el).css({
        left: left + 'px',
        top: top + 'px'
      });
      $(this.el).show();
      Proxy.trigger("open", this);
      this.open = true;
      return ($(document)).bind("mousedown", this.blur);
    };
    ColorPicker.prototype.close = function() {
      $(this.el).hide();
      return this.open = false;
    };
    ColorPicker.prototype.cancel = function(e) {
      var hsb;
      hsb = this.hsb;
      hsb = _.extend({}, this.original_hsb);
      this.$("div.colorpicker_rgb_a input").val(this.original_alpha).trigger("keyup");
      this.alpha = this.original_alpha;
      console.log(hsb, this.original_hsb);
      this.hsb = hsb;
      this.change(e);
      return this.close();
    };
    ColorPicker.prototype.accept = function() {
      this.original_hsb = _.clone(this.hsb);
      this.original_alpha = this.$("div.colorpicker_rgb_a input").val();
      this.close();
      return this.onAccept.call(this, this.getRGB(), ColorMath.hsbToHex(this.hsb), this.alpha);
    };
    ColorPicker.prototype.blur = function(e) {
      var el, target;
      target = e.target;
      el = this.el;
      if (target !== el && $(el).find(target).length === 0) {
        ($(document)).unbind("mousedown");
        return this.close();
      }
    };
    ColorPicker.prototype.render = function() {
      var context, _template;
      _template = _.template(template);
      context = ColorMath.hsbToRGB(this.hsb);
      context.hex = ColorMath.hsbToHex(this.hsb);
      context.a = this.original_alpha;
      $(this.el).html(_template(context));
      this.change();
      return this;
    };
    ColorPicker.prototype.setPalette = function() {
      var hsb;
      hsb = this.hsb;
      this.$('div.colorpicker_color').css('backgroundColor', '#' + (ColorMath.hsbToHex({
        h: hsb.h,
        s: 100,
        b: 100
      })));
      return this.$('div.colorpicker_color div div').css({
        left: parseInt(150 * hsb.s / 100, 10),
        top: parseInt(150 * (100 - hsb.b) / 100, 10)
      });
    };
    ColorPicker.prototype.setHue = function() {
      var hsb;
      hsb = this.hsb;
      return this.$('div.colorpicker_hue div').css('top', parseInt(150 - 150 * hsb.h / 360, 10));
    };
    ColorPicker.prototype.getRGB = function() {
      var rgb_row;
      rgb_row = this.$('div.rgb_row input');
      return {
        r: parseInt(rgb_row.eq(0).val(), 10),
        g: parseInt(rgb_row.eq(1).val(), 10),
        b: parseInt(rgb_row.eq(2).val(), 10)
      };
    };
    ColorPicker.prototype.setRGB = function() {
      var rgb;
      rgb = ColorMath.hsbToRGB(this.hsb);
      return this.$('div.rgb_row input').eq(0).val(rgb.r).end().eq(1).val(rgb.g).end().eq(2).val(rgb.b).end();
    };
    ColorPicker.prototype.setHex = function() {
      return this.$('input.hex').val(ColorMath.hsbToHex(this.hsb));
    };
    ColorPicker.prototype.change = function(e) {
      var target, targetClass;
      if (e) {
        target = $(e.target);
        targetClass = target.attr('class');
        if (targetClass === 'hex') {
          this.hsb = ColorMath.hexToHSB(target.val());
        } else if (targetClass === "rgb") {
          this.hsb = ColorMath.rgbToHSB(this.getRGB());
        }
      }
      this.setRGB();
      this.setHex();
      this.setPalette();
      this.setHue();
      if (e) {
        return this.onChange.call(this, this.getRGB(), ColorMath.hsbToHex(this.hsb), this.alpha);
      }
    };
    ColorPicker.prototype.downHue = function(e) {
      var current;
      e.preventDefault();
      current = {
        y: $(e.target).offset().top
      };
      $(document).bind('mouseup', current, this.upHue);
      return $(document).bind('mousemove', current, this.moveHue);
    };
    ColorPicker.prototype.moveHue = function(e) {
      e.preventDefault();
      this.hsb.h = parseInt(360 * ((150 - (Math.max(0, Math.min(150, e.pageY - e.data.y)))) / 150), 10);
      return this.change(e);
    };
    ColorPicker.prototype.upHue = function(e) {
      e.preventDefault();
      this.setRGB();
      this.setHex();
      $(document).unbind('mouseup', this.upHue);
      return $(document).unbind('mousemove', this.moveHue);
    };
    ColorPicker.prototype.downSelector = function(e) {
      var current;
      e.preventDefault();
      current = {
        pos: $(e.target).offset()
      };
      $(document).bind('mouseup', current, this.upSelector);
      return $(document).bind('mousemove', current, this.moveSelector);
    };
    ColorPicker.prototype.moveSelector = function(e) {
      e.preventDefault();
      this.hsb.b = parseInt(100 * ((150 - (Math.max(0, Math.min(150, e.pageY - e.data.pos.top)))) / 150), 10);
      this.hsb.s = parseInt(100 * (Math.max(0, Math.min(150, e.pageX - e.data.pos.left))) / 150, 10);
      return this.change(e);
    };
    ColorPicker.prototype.upSelector = function(e) {
      e.preventDefault();
      this.setRGB();
      this.setHex();
      $(document).unbind('mouseup', this.upSelector);
      return $(document).unbind('mousemove', this.moveSelector);
    };
    ColorPicker.prototype.changeAlpha = function(e) {
      var adjusted, alpha, key_code;
      alpha = Number($(e.target).val());
      key_code = e.keyCode;
      if (key_code === 38 || key_code === 40) {
        adjusted = true;
        if (key_code === 38) {
          alpha += 1;
        } else if (key_code === 40) {
          alpha -= 1;
        }
      }
      if (alpha > 100) {
        alpha = 100;
      } else if (alpha < 0) {
        alpha = 0;
      }
      if (adjusted != null) {
        $(e.target).val(alpha);
      }
      this.alpha = alpha;
      this.$("div.alpha_channel").fadeTo(0, (100 - alpha) / 100);
      return this.change(e);
    };
    ColorPicker.prototype.clearOpacity = function(e) {
      e.preventDefault();
      return this.$("div.colorpicker_rgb_a input").val("0").trigger("keyup");
    };
    return ColorPicker;
  })();
}).call(this);
