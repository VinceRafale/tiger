define(function (require) {
  var Backbone = require('backbone'),
      MenuItem, MenuItemCollection, MenuItems;

  MenuItem = Backbone.Model.extend({});

  MenuItems = Backbone.Collection.extend({
    model: MenuItem,
    url: "./menu-items",
    comparator: function(menuItem) {
      return menuItem.get("position");
    }
  });

  return {
    MenuItem: MenuItems,
    MenuItems: MenuItems
  };
});
