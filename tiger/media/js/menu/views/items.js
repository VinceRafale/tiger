var ItemView = Backbone.View.extend({
    tagName: "li",

    initialize: function () {
        _.bindAll(this, "render"); 
    },

    render: function () {
        var template = _.template($("#item-list").text()),
            context = this.model.attributes;
        context.section_id = this.options.section.id;
        $(this.el).html(template(context));
        return this;
    }
});


var ItemListView = Backbone.View.extend({
    initialize: function () {
        _.bindAll(this, "render", "renderOne"); 
    },

    render: function () {
        var self = this; 

        this.collection.each(function(item) {
            self.renderOne(item);    
        });

        return this;
    },

    renderOne: function (item) {
        var view = new ItemView({model: item, section: this.options.section}),
            contents = view.render().el;
        $(this.el).append(contents);
    }
});


var ItemDetailView = Backbone.View.extend({
    tagName: "div",
    id: "itemDetail",

    events: {
        "click #toggle-name": "toggleName"
    },

    initialize: function () {
        _.bindAll(this, "render", "toggleName"); 
    },

    render: function () {
        var item = this.model,
            template = _.template($("#order-item").text()),
            context = item.attributes;
        context.choice_sets = item.choice_sets; 
        context.extras = item.extras; 
        context.prices = item.prices; 
        context.ordering = App.ordering;
        $(this.el).html(template(context));
        return this;
    },

    toggleName: function (e) {
        var nameTag = this.$("#add-name");
        e.preventDefault();
        nameTag.show();
    }
});
