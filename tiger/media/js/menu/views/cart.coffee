class CartView extends Backbone.View
    tagName: "div"

    initialize: ->
        @collection.bind "refresh", @render

    render: =>
        template = _.template $("#review-order").text()
        @el.innerHTML = template {}

        @collection.each (section) =>
            @renderOne section

        return this

    renderOne: (line_item) =>
        view = new LineItemView {model: line_item}
        contents = view.render().el
        @$("table").append contents


class LineItemView extends Backbone.View
    tagName: "tr"

    events:
        "click a": "removeItem"

    render: =>
        template = _.template $("#line-item-template").text()
        context = @model.attributes
        _.extend context, {
            item: @model.item
            total: @model.total
            price: @model.price
        }
        console.log context
        $(@el).html(template context)
        return this

    removeItem: (e) =>
        e.preventDefault()
        $.get (($ e.target).attr "href"), (data) =>
            App.cart.refresh (JSON.parse data)
