var ChoiceSet = Backbone.Model.extend({
    initialize: function () {
        this.choices = new Choices(this.get("choices"));
    }
});

var ChoiceSets = Backbone.Collection.extend({
    model: ChoiceSet
});

