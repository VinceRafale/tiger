class this.MenuController extends Backbone.Controller
    routes:
        "": "sectionList",
        "section/:id": "sectionDetail",
        "section/:id/item/:id": "itemDetail",
        "section/:id/item/:id/order": "orderItem"

    sectionList: ->
        view = new SectionListView {collection: App.sections}
        $("#container").children().remove()
        $("#container").append view.render().el

    sectionDetail: (sectionId) ->
        section = App.sections.get sectionId
        view = new SectionDetailView {model: section}
        $("#container").children().remove()
        $("#container").append view.render().el
    
    itemDetail: (sectionId, itemId) ->
        section = App.sections.get sectionId
        item = section.items.get itemId
        view = new ItemDetailView {model: item}
        $("#container").children().remove()
        $("#container").append view.render().el

    orderItem: (sectionId, itemId) ->
        section = App.sections.get sectionId
        item = section.items.get itemId
        view = new OrderItemView {model: item}
        $("#container").children().remove()
        $("#container").append view.render().el
