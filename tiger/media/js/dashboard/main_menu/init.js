require.config({
  baseUrl: "/static/js",
  paths: {
    jquery: "vendor/jquery-1.7.1",
    underscore: "vendor/underscore",
    backbone: "vendor/backbone",
    app: "dashboard/main_menu"
  }
});

require(["app/models", "app/views"], function(models, views) {
  var data = document.getElementById("menu-items-data").innerHTML,
      parsedData = JSON.parse(data),
      MenuItems = new models.MenuItems(parsedData),
      view = new views.MenuItemsView({collection: MenuItems});

  view.render();
});
