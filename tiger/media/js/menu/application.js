var App = {
    sections: new Sections(menu.sections),
    views: {},
    init: function () {
        this.controller = new MenuController;
        Backbone.history.start();
    }
};
App.init();
