class this.MenuController extends Backbone.Controller
    routes:
        "": "sectionList",
        "section/:id": "sectionDetail",
        "section/:id/item/:id": "itemDetail",
        "section/:id/item/:id/order": "orderItem"
        "review": "reviewOrder"

    sectionList: ->
        view = new SectionListView {collection: App.sections}
        $("#container").children().remove()
        $("#container").append view.render().el
        $("#container").prepend('<h1>Our Menu</h1>');

    sectionDetail: (sectionId) ->
        section = App.sections.get sectionId
        view = new SectionDetailView {model: section}
        container = $('#container')
        #if container.children().length
            #container.children().anim {translate3d: '-100%, 0, 0'}, .15, 'ease-in',() ->
                #container.children().remove()
                #container.css('-webkit-transform', 'translate3d(100%,0,0)').append( view.render().el ).anim {translate3d: '0,0,0'}, .15, 'ease-in'
        #else
        container.children().remove()
        container.append view.render().el
        
    itemDetail: (sectionId, itemId) ->
        section = App.sections.get sectionId
        item = section.items.get itemId
        view = new ItemDetailView {model: item, section:section}
        $("#container").children().remove()
        $("#container").append view.render().el

    reviewOrder: ->
        view = new CartView {collection: App.cart}
        $("#container").children().remove()
        $("#container").append view.render().el

    
