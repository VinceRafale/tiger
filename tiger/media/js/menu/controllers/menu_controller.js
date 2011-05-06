var MenuController = Backbone.Controller.extend({
    routes: {
        "": "sectionList",
        "section/:id": "sectionDetail",
        "section/:id/item/:id": "itemDetail"
    },

    sectionList: function () {
        var view = App.views.section_list || (App.views.section_list = new SectionListView({collection: App.sections}));
        $("#container").children().remove();
        $("#container").append(view.render().el);
    },

    sectionDetail: function(sectionId) {
        var section = App.sections.get(sectionId),
            view = new SectionDetailView({model: section});
        $("#container").children().remove();
        $("#container").append(view.render().el);
    },
    
    itemDetail: function(sectionId, itemId) {
        var section = App.sections.get(sectionId),
            item = section.items.get(itemId),
            view = new ItemDetailView({model: item});
        $("#container").children().remove();
        $("#container").append(view.render().el);
    }
});
