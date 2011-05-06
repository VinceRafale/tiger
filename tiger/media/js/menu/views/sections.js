var SectionView = Backbone.View.extend({
    tagName: "div",

    initialize: function () {
        _.bindAll(this, "render"); 
    },

    render: function () {
        var template = _.template($("#section-list").text()),
            context = this.model.attributes;
        $(this.el).html(template(context));
        return this;
    }
});


var SectionListView = Backbone.View.extend({
    tagName: "div",
    id: "sectionList",

    initialize: function () {
        _.bindAll(this, "render", "renderOne"); 
    },

    render: function () {
        var self = this; 

        this.collection.each(function(section) {
            self.renderOne(section);    
        });

        return this;
    },

    renderOne: function (section) {
        var view = new SectionView({model: section}),
            contents = view.render().el;
        $(this.el).append(contents);
    }
});

var SectionDetailView = Backbone.View.extend({
    tagName: "div",
    id: "sectionDetail",

    initialize: function () {
        _.bindAll(this, "render"); 
    },

    render: function () {
        var template = _.template("<h1><%= name %></h1><p><%= description %></p><ul id='items'></ul>"),
            context = this.model.attributes;
        $(this.el).html(template(context));
        this.itemList = new ItemListView({collection: this.model.items, el: this.$("ul#items"), section: this.model});
        this.itemList.render();
        return this;
    },
});
