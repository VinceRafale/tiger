var App = {
    sections: new Sections(),
    views: {},
    init: function () {
        _.each(sectionIds, function (sectionId) {
            $.get("/menu/section/" + sectionId + ".json", function (data) {
                var section = new Section(JSON.parse(data));
                App.sections.add(section);
                if (!App.controller) {
                    this.controller = new MenuController;
                    Backbone.history.start();
                }
            }, "json");
        });

    }
};
App.init();
