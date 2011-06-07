var Section = Backbone.Model.extend({
    initialize: function () {
        this.items = new Items(this.get("items"));
    }
});

var Sections = Backbone.Collection.extend({
    model: Section
});
