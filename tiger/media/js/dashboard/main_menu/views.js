define(function (require) {
  var Backbone = require("backbone"),
      _ = require("underscore"),
      $ = require("jquery"),
      __ui = require("order!jquery-ui.min"),
      models = require("app/models"),
      Proxy,
      ControlsView,
      MenuItemFormView,
      MenuItemView,
      MenuItemsView,
      pageItemTemplate = require("text!app/templates/page.html"),
      nonPageItemTemplate = require("text!app/templates/non-page.html");

  require("text!app/templates/url-form.html");
  require("text!app/templates/url.html");

  Proxy = {};

  ControlsView = Backbone.View.extend({
    el: $("span.buttons"),
    events: {
      "click a.new-link": "newLink"
    },
    initialize: function () {
      _.bindAll(this, "newLink");
    },
    newLink: function () {
      Proxy.trigger("new-item", "url");
      return false;
    }
  });

  MenuItemFormView = Backbone.View.extend({
    tagName: "li",
    events: {
      "click a.save": "save",
      "click a.cancel": "cancel"
    },
    initialize: function () {
      _.bindAll(this, "save", "cancel");
    },
    render: function () {
      var template = _.template(require("text!app/templates/url-form.html"));
      this.el.innerHTML = template(this.model.toJSON());
      return this;
    },
    save: function () {
      var self = this, 
          values = this.$("input").serializeArray(),
          data = _.reduce(values, function (obj, val) {
            obj[val.name] = val.value;
            return obj;
          }, {});
      data.link_type = 'url';
      this.model.save(data, {
        success: function (model, response) {
          Proxy.trigger("created", model);
          self.remove();
        }
      });
    },
    cancel: function () {
      this.remove();
    }
  });

  MenuItemView = Backbone.View.extend({
    tagName: "li",
    events: {
      "click a.delete": "destroy"
    },
    initialize: function () {
      _.bindAll(this, "destroy");
    },
    render: function () {
      var m = this.model,
          linkType = m.get("linkType"),
          t = _.template((linkType === "page" || linkType === "url") ? require("text!app/templates/" + linkType + ".html") : nonPageItemTemplate);

      this.el.innerHTML = t(m.toJSON());
      $(this.el).attr("id", "mi-" + m.id);
      return this;
    },
    destroy: function () {
      var self = this;
      this.model.destroy({
        success: function(model, response) {
          $(self.el).fadeOut(function () {self.remove(); });
        }
      });
      return false;
    }
  });

  MenuItemsView = Backbone.View.extend({
    el: $("#menu-items ul"),
    initialize: function () {
      _.bindAll(this, "showForm", "created", "render");
      this.collection.bind("add", this.render);
      this.collection.bind("remove", this.render);
      Proxy.on("new-item", this.showForm);
      Proxy.on("created", this.created);
    },
    render: function () {
      var el = this.el;
      $(el).empty();
      this.collection.each(function(menuItem) {
        $(el).append(new MenuItemView({model: menuItem}).render().el); 
      });
      $(this.el).sortable({
          stop: function(event, ui) { 
              item_ids = $(this).sortable('toArray');
              if (item_ids.length > 1) {
                  $.post("menu-items/reorder/", $.param({
                      item_ids: item_ids
                  }, true));
              }
          },
          cancel: "a"
      });
      return this;
    },
    showForm: function (name) {
      var menuItem = new models.MenuItem({});
      menuItem.url = './menu-items';
      $(this.el).prepend(new MenuItemFormView({model: menuItem}).render().el);
    },
    created: function (model) {
      this.collection.add(model);
    }
  });

  _.extend(Proxy, Backbone.Events);

  return {
    ControlsView: ControlsView,
    MenuItemsView: MenuItemsView  
  };
});
