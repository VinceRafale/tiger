define(function (require) {
  var Backbone = require("backbone"),
      _ = require("underscore"),
      $ = require("jquery"),
      __ui = require("order!jquery-ui.min"),
      pageItemTemplate = _.template(require("text!app/templates/page.html")),
      nonPageItemTemplate = _.template(require("text!app/templates/non-page.html"));

  var MenuItemView = Backbone.View.extend({
    tagName: "li",
    events: {
      "click a.delete": "destroy"
    },
    init: function () {
      _.bindAll(this, "destroy");
    },
    render: function () {
      var m = this.model,
          t = (!!m.get("page")) ? pageItemTemplate : nonPageItemTemplate;

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

  var MenuItemsView = Backbone.View.extend({
    el: $("#menu-items ul"),
    render: function () {
      var el = this.el;
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
    }
  });

  return {
    MenuItemsView: MenuItemsView  
  };
});
