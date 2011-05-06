var Item = Backbone.Model.extend({
    initialize: function () {
        this.extras = new Extras(this.get("extras"));
        this.variants = new Variants(this.get("extras"));
        this.choice_sets = new ChoiceSets(this.get("choice_sets"));
    }
});

var Items = Backbone.Collection.extend({
    model: Item
});
