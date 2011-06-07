var ExtraView = Backbone.View.extend({
    tagName: "li",

    initialize: function () {
        _.bindAll(this, "render"); 
    },

    render: function () {
        var template = _.template($("#extra").text()),
            context = {extra: this.model, i: this.options.i};
        $(this.el).html(template(context));
        return this;
    }
});

var ExtraListView = Backbone.View.extend({
    tagName: "ul",

    initialize: function () {
        _.bindAll(this, "render", "renderOne"); 
    },

    render: function () {
        var self = this; 

        this.collection.each(function(extra, i) {
            self.renderOne(extra, i);    
        });

        return this;
    },

    renderOne: function (extra, i) {
        var view = new ExtraView({model: extra, i: i}),
            contents = view.render().el;
        $(this.el).append(contents);
    }
});
