require(["jquery", "dashboard/menu_items/init"], function ($, MenuManager) {
  module("Main Menu Manager", {
    setup: function () {
      MenuManager.init();
    },
    teardown: function () {
      $("#menu-manager").empty();
    }
  });

  test('Clicking "New Menu Item" adds a menu item form', function () {
    $("a.new-menu-item").click();
    eq($("form.new").length, 1);
  });

  test('Clicking "cancel" in the new menu item form removes the form', function () {
    $("a.new-menu-item").click();
    $("form.new a.cancel").click();
    eq($("form.new").length, 0);
  });

  test('Clicking "save" in the new menu item form saves the form data to the server', function () {
  });

  test('Clicking "save" in the new menu item form removes the form from the DOM', function () {
  });

  test('Clicking "save" in the new menu item form adds the new menu item to the menu items collection', function () {
  });

  test('A URL menu item is rendered with its URL in span.info', function () {
  });

  test('An upload menu item is rendered with its file name in span.info', function () {
  });

  test('A page menu item is rendered with its first 10 words in span.info', function () {
  });

  test('A menu menu item is rendered with "Your Restaurant\'s Menu" in span.info', function () {
  });

  test('The edit link on a URL menu item makes the URL editable inline', function () {
  });

  test('The cancel link on a URL menu item reverts to the default rendering', function () {
  });

  test('The save link on a URL menu item sends a PUT to the server', function () {
  });

  test('The save link on a URL menu item reverts to the default rendering with the new data', function () {
  });

  test('The edit link on a upload menu item creates an inline upload form', function () {
  });

  test('The cancel link on a upload menu item reverts to the default rendering', function () {
  });

  test('The save link on a upload menu item POSTs to an iframe', function () {
  });

  test('The save link on a upload menu item reverst to the default rendering with the new data', function () {
  });

  test('The edit link on a page menu item points to an edit URL for that page content', function () {
  });

  test('A menu menu item has no edit link', function () {
  });

  test('Clicking "delete" on a menu item sends a DELETE to the server', function () {
  });

  test('Clicking "delete" on a menu item removes it from the menu item collection', function () {
  });

  test('Clicking "delete" removes the menu item from the DOM', function () {
  });
});
