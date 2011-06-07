var Item = Backbone.Model.extend({
    initialize: function () {
        this.extras = new Extras(this.get("extras"));
        this.prices = new Variants(this.get("prices"));
        this.choice_sets = new ChoiceSets(this.get("choices"));
    }
});

var Items = Backbone.Collection.extend({
    model: Item
});
